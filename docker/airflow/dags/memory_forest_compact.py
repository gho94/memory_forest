"""
Memory Forest 컴팩트 DAG
두 가지 핵심 기능에 집중:
1. 실패/대기 상태 게임들의 AI 재분석
2. 모델에 없는 단어들의 학습
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pendulum
import logging
from typing import Dict, List

# 로컬 모듈 import
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_ARGS, AI_STATUS_CODES, SCHEDULES, BATCH_CONFIG, MODEL_CONFIG
from utils import db_manager, ai_client, text_processor

logger = logging.getLogger(__name__)

# DAG 기본 설정
dag_default_args = {
    **DEFAULT_ARGS,
    'start_date': pendulum.datetime(2024, 1, 1, tz=pendulum.timezone("Asia/Seoul")),
}

def retry_failed_games(**context):
    """실패/대기 상태의 게임들을 재분석"""
    logger.info("=== 실패 게임 재처리 시작 ===")
    
    try:
        # 실패/대기 상태 게임들 조회
        failed_games = db_manager.get_failed_games(BATCH_CONFIG['retry_games_batch_size'])
        
        if not failed_games:
            logger.info("재처리할 게임이 없습니다")
            return {
                'total_games': 0,
                'processed': 0,
                'failed': 0,
                'missing_words': 0
            }
        
        logger.info(f"재처리 대상 게임 {len(failed_games)}개 발견")
        
        # 게임들을 처리 중 상태로 표시
        for game in failed_games:
            db_manager.mark_as_processing(game['game_id'], game['game_seq'])
        
        # AI 서비스로 일괄 분석
        analysis_results = ai_client.batch_analyze_games(failed_games)
        
        # 결과 처리
        stats = {
            'total_games': len(failed_games),
            'processed': 0,
            'failed': 0,
            'missing_words': 0
        }
        
        for result in analysis_results:
            game_id = result['game_id']
            game_seq = result['game_seq']
            
            if result['status'] == 'success':
                # AI 분석 성공 - 결과 저장
                if db_manager.update_game_ai_result(game_id, game_seq, result['ai_result']):
                    stats['processed'] += 1
                    logger.info(f"게임 재처리 성공: {game_id}/{game_seq}")
                else:
                    stats['failed'] += 1
                    logger.error(f"게임 결과 저장 실패: {game_id}/{game_seq}")
                    
            elif result['status'] == 'missing_word':
                # 모델에 없는 단어
                missing_word_desc = f"{result['answer_text']}는 {MODEL_CONFIG['missing_words_marker']}에 존재하지 않는 단어입니다"
                if db_manager.update_game_status(
                    game_id, game_seq, 
                    AI_STATUS_CODES['COMPLETED'],  # 완료로 표시하되 설명에 마커 포함
                    missing_word_desc
                ):
                    stats['missing_words'] += 1
                    logger.info(f"모델 누락 단어 표시: {game_id}/{game_seq} - {result['answer_text']}")
                else:
                    stats['failed'] += 1
                    
            else:
                # 분석 실패
                error_msg = result.get('error', 'AI 분석 실패')
                if db_manager.mark_as_failed(game_id, game_seq, error_msg):
                    stats['failed'] += 1
                    logger.error(f"게임 재처리 실패: {game_id}/{game_seq} - {error_msg}")
        
        logger.info(f"재처리 완료: 성공 {stats['processed']}, 실패 {stats['failed']}, 누락단어 {stats['missing_words']}")
        return stats
        
    except Exception as e:
        logger.error(f"재처리 작업 중 오류: {e}")
        return {
            'total_games': 0,
            'processed': 0,
            'failed': 0,
            'missing_words': 0,
            'error': str(e)
        }

def collect_missing_words(**context):
    """모델에 없는 단어들 수집"""
    logger.info("=== 모델 누락 단어 수집 시작 ===")
    
    try:
        # 먼저 디버깅: %모델% 마커가 있는 레코드 확인
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # %모델% 마커가 있는 레코드 개수 확인
                debug_query = """
                SELECT COUNT(*) as count
                FROM game_detail
                WHERE description LIKE %s
                """
                cursor.execute(debug_query, (f'%{MODEL_CONFIG["missing_words_marker"]}%',))
                marker_count = cursor.fetchone()['count']
                logger.info(f"🔍 {MODEL_CONFIG['missing_words_marker']} 마커가 있는 레코드: {marker_count}개")
                
                # 샘플 확인
                if marker_count > 0:
                    sample_query = """
                    SELECT game_id, game_seq, answer_text, description
                    FROM game_detail
                    WHERE description LIKE %s
                    LIMIT 5
                    """
                    cursor.execute(sample_query, (f'%{MODEL_CONFIG["missing_words_marker"]}%',))
                    samples = cursor.fetchall()
                    logger.info(f"📋 샘플 레코드들:")
                    for sample in samples:
                        logger.info(f"  - {sample['game_id']}/{sample['game_seq']}: '{sample['answer_text']}' -> {sample['description']}")
                
                cursor.close()
                
        except Exception as debug_error:
            logger.error(f"디버깅 쿼리 실패: {debug_error}")
        
        # %모델% 마커가 있는 게임들에서 단어 추출
        missing_words = db_manager.extract_training_words(BATCH_CONFIG['model_training_batch_size'])
        
        if not missing_words:
            logger.info("학습할 새로운 단어가 없습니다")
            return {
                'collected_words': 0,
                'cleaned_words': 0,
                'words': []
            }
        
        # 텍스트 처리기로 단어 정제
        cleaned_words = text_processor.clean_word_list(missing_words)
        
        logger.info(f"수집된 단어: {len(missing_words)}개, 정제된 단어: {len(cleaned_words)}개")
        logger.info(f"수집된 단어들: {missing_words[:10]}")
        
        # XCom으로 다음 태스크에 전달
        context['task_instance'].xcom_push(key='missing_words', value=cleaned_words)
        
        return {
            'collected_words': len(missing_words),
            'cleaned_words': len(cleaned_words),
            'words': cleaned_words[:10]  # 로그용으로 처음 10개만
        }
        
    except Exception as e:
        logger.error(f"단어 수집 중 오류: {e}")
        return {
            'collected_words': 0,
            'cleaned_words': 0,
            'words': [],
            'error': str(e)
        }

def train_missing_words(**context):
    """수집된 단어들로 모델 학습"""
    logger.info("=== 모델 학습 시작 ===")
    
    try:
        # 이전 태스크에서 단어 목록 가져오기
        missing_words = context['task_instance'].xcom_pull(
            task_ids='collect_missing_words',
            key='missing_words'
        )
        
        if not missing_words:
            logger.info("학습할 단어가 없습니다")
            return {
                'training_executed': False,
                'words_trained': 0,
                'model_reloaded': False
            }
        
        logger.info(f"모델 학습 시작: {len(missing_words)}개 단어")
        
        # AI 서비스에 학습 요청
        training_success = ai_client.train_missing_words(missing_words)
        
        if training_success:
            logger.info("모델 학습 성공")
            
            # 모델 리로드
            reload_success = ai_client.reload_model()
            
            if reload_success:
                logger.info("모델 리로드 성공")
                
                # 학습된 단어들의 게임 상태를 대기로 변경 (재분석 유도)
                updated_count = 0
                for word in missing_words:
                    games = db_manager.get_missing_word_games(100)  # 해당 단어 게임들 조회
                    for game in games:
                        if word in game['answer_text']:
                            if db_manager.update_game_status(
                                game['game_id'], 
                                game['game_seq'],
                                AI_STATUS_CODES['WAITING'],
                                f'{word} 단어 학습 완료 - 재분석 대기'
                            ):
                                updated_count += 1
                
                logger.info(f"재분석 대기 상태로 변경된 게임: {updated_count}개")
                
                return {
                    'training_executed': True,
                    'words_trained': len(missing_words),
                    'model_reloaded': True,
                    'games_updated': updated_count
                }
            else:
                logger.error("모델 리로드 실패")
                return {
                    'training_executed': True,
                    'words_trained': len(missing_words),
                    'model_reloaded': False
                }
        else:
            logger.error("모델 학습 실패")
            return {
                'training_executed': False,
                'words_trained': 0,
                'model_reloaded': False
            }
            
    except Exception as e:
        logger.error(f"모델 학습 중 오류: {e}")
        return {
            'training_executed': False,
            'words_trained': 0,
            'model_reloaded': False,
            'error': str(e)
        }

def check_system_status(**context):
    """시스템 상태 확인"""
    logger.info("=== 시스템 상태 확인 ===")
    
    try:
        # 데이터베이스 연결 확인
        db_healthy = db_manager.test_connection()
        
        # AI 서비스 상태 확인
        ai_healthy = ai_client.check_health()
        
        # 처리 통계 조회
        stats = db_manager.get_processing_statistics()
        
        # 모델 정보 조회
        model_info = ai_client.get_model_info()
        
        status = {
            'database_healthy': db_healthy,
            'ai_service_healthy': ai_healthy,
            'processing_stats': stats,
            'model_info': model_info,
            'overall_healthy': db_healthy and ai_healthy
        }
        
        if status['overall_healthy']:
            logger.info("✅ 시스템 상태 정상")
        else:
            logger.warning("⚠️ 시스템 일부 구성요소에 문제 있음")
        
        return status
        
    except Exception as e:
        logger.error(f"시스템 상태 확인 중 오류: {e}")
        return {
            'database_healthy': False,
            'ai_service_healthy': False,
            'overall_healthy': False,
            'error': str(e)
        }

# DAG 정의
memory_forest_compact_dag = DAG(
    'memory_forest_compact',
    default_args=dag_default_args,
    description='Memory Forest 컴팩트 버전 - 핵심 기능만 포함',
    schedule_interval=None,  # 수동 실행 또는 외부 트리거
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'compact', 'ai-processing']
)

# 실패 게임 재처리 DAG
retry_dag = DAG(
    'memory_forest_retry_failed',
    default_args=dag_default_args,
    description='실패/대기 게임 재처리',
    schedule_interval=SCHEDULES['retry_failed_games'],  # 10분마다
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'retry', 'ai-processing']
)

# 모델 학습 DAG
training_dag = DAG(
    'memory_forest_train_words',
    default_args=dag_default_args,
    description='모델에 없는 단어 학습',
    schedule_interval=SCHEDULES['train_missing_words'],  # 매일 오전 3시
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'training', 'model']
)

# 태스크 정의 - 재처리 DAG
start_retry = DummyOperator(task_id='start_retry', dag=retry_dag)

check_status_task = PythonOperator(
    task_id='check_system_status',
    python_callable=check_system_status,
    dag=retry_dag
)

retry_games_task = PythonOperator(
    task_id='retry_failed_games',
    python_callable=retry_failed_games,
    dag=retry_dag
)

end_retry = DummyOperator(task_id='end_retry', dag=retry_dag)

# 태스크 정의 - 학습 DAG
start_training = DummyOperator(task_id='start_training', dag=training_dag)

collect_words_task = PythonOperator(
    task_id='collect_missing_words',
    python_callable=collect_missing_words,
    dag=training_dag
)

train_words_task = PythonOperator(
    task_id='train_missing_words',
    python_callable=train_missing_words,
    dag=training_dag
)

end_training = DummyOperator(task_id='end_training', dag=training_dag)

# 의존성 설정
start_retry >> check_status_task >> retry_games_task >> end_retry
start_training >> collect_words_task >> train_words_task >> end_training