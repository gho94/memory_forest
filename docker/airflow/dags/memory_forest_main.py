"""
Memory Forest 메인 AI 처리 DAG
init.sql 스키마와 AI 서비스에 최적화된 주기적 게임 분석 - 연결 오류 수정
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pendulum
import logging
import time
from typing import Dict, List

# 로컬 모듈 import
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DAG_DEFAULT_ARGS, BATCH_SIZES, AI_STATUS_CODES, RETRY_RULES
from utils.database import db_manager
from utils.ai_service import ai_client

# 한국 시간대 설정
local_tz = pendulum.timezone("Asia/Seoul")
logger = logging.getLogger(__name__)

def check_system_health(**context):
    """시스템 전체 상태 확인 - 연결 오류 수정"""
    logger.info("=== 시스템 상태 확인 시작 ===")
    
    health_status = {
        "ai_service": False,
        "database": False,
        "overall": False
    }
    
    try:
        # AI 서비스 상태 확인
        try:
            health_status["ai_service"] = ai_client.check_health()
            logger.info(f"✅ AI 서비스 상태: {'정상' if health_status['ai_service'] else '비정상'}")
        except Exception as e:
            logger.error(f"❌ AI 서비스 확인 실패: {e}")
            health_status["ai_service"] = False
        
        # 데이터베이스 상태 확인 - 수정된 테스트 함수 사용
        try:
            health_status["database"] = db_manager.test_connection()
            logger.info(f"✅ 데이터베이스 상태: {'정상' if health_status['database'] else '비정상'}")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 확인 실패: {e}")
            health_status["database"] = False
        
        # 전체 상태 판단
        health_status["overall"] = all([
            health_status["ai_service"],
            health_status["database"]
        ])
        
        logger.info(f"📊 시스템 전체 상태: {health_status}")
        
        if not health_status["overall"]:
            # 경고 레벨로 변경 (예외 발생 안함)
            logger.warning("⚠️ 시스템 일부 구성요소에 문제가 있지만 처리를 계속합니다")
            
        return health_status
        
    except Exception as e:
        logger.error(f"❌ 시스템 상태 확인 중 예상치 못한 오류: {e}")
        # 오류가 있어도 처리 계속 진행
        return {
            "ai_service": False,
            "database": False,
            "overall": False,
            "error": str(e)
        }

def process_pending_games(**context):
    """대기 중인 게임들 AI 분석 처리"""
    logger.info("=== 대기 게임 처리 시작 ===")
    
    batch_size = BATCH_SIZES['pending_games']
    
    try:
        pending_games = db_manager.get_games_by_status('PENDING', batch_size)
    except Exception as e:
        logger.error(f"❌ 대기 게임 조회 실패: {e}")
        return {"processed": 0, "failed": 0, "skipped": 0, "error": "DB 조회 실패"}
    
    if not pending_games:
        logger.info("ℹ️ 처리할 대기 게임이 없습니다.")
        return {"processed": 0, "failed": 0, "skipped": 0}
    
    logger.info(f"🎮 {len(pending_games)}개 대기 게임 처리 시작")
    
    results = {
        "processed": 0,
        "failed": 0,
        "skipped": 0,
        "total": len(pending_games)
    }
    
    for game in pending_games:
        try:
            game_id = game['game_id']
            game_seq = game['game_seq']
            answer_text = game['answer_text']
            
            # 빈 답변 체크
            if not answer_text or answer_text.strip() == '':
                logger.warning(f"⚠️ 빈 답변 스킵: {game_id}/{game_seq}")
                results["skipped"] += 1
                continue
            
            logger.info(f"🔄 게임 처리: {game_id}/{game_seq} - '{answer_text}'")
            
            # 처리 중 상태로 변경
            try:
                db_manager.update_game_ai_result(
                    game_id, game_seq, 'PROCESSING', 
                    f"AI 분석 진행 중 - {answer_text}"
                )
            except Exception as e:
                logger.warning(f"⚠️ 상태 업데이트 실패 (계속 진행): {game_id}/{game_seq} - {e}")
            
            # AI 분석 수행
            try:
                ai_response = ai_client.analyze_game(game)
            except Exception as e:
                logger.error(f"❌ AI 분석 요청 실패: {game_id}/{game_seq} - {e}")
                # 오류 상태로 업데이트
                try:
                    db_manager.update_game_ai_result(
                        game_id, game_seq, 'ERROR',
                        f"AI 분석 요청 실패: {str(e)[:100]}"
                    )
                except:
                    pass
                results["failed"] += 1
                continue
            
            if ai_response.get("status") == "success":
                # AI 분석 성공
                ai_result = ai_response["result"]
                
                # 결과 검증 및 포맷팅
                formatted_result = {
                    'wrong_option_1': str(ai_result.get('wrong_option_1', ''))[:20],
                    'wrong_option_2': str(ai_result.get('wrong_option_2', ''))[:20],
                    'wrong_option_3': str(ai_result.get('wrong_option_3', ''))[:20],
                    'wrong_score_1': int(ai_result.get('wrong_score_1', 0)),
                    'wrong_score_2': int(ai_result.get('wrong_score_2', 0)),
                    'wrong_score_3': int(ai_result.get('wrong_score_3', 0))
                }
                
                # 완료 상태로 업데이트
                try:
                    success = db_manager.update_game_ai_result(
                        game_id, game_seq, 'COMPLETED',
                        f"AI 분석 완료 - 옵션: {formatted_result['wrong_option_1']}, {formatted_result['wrong_option_2']}, {formatted_result['wrong_option_3']}",
                        formatted_result
                    )
                    
                    if success:
                        results["processed"] += 1
                        logger.info(f"✅ 게임 처리 성공: {game_id}/{game_seq}")
                    else:
                        results["failed"] += 1
                        logger.error(f"❌ DB 업데이트 실패: {game_id}/{game_seq}")
                except Exception as e:
                    results["failed"] += 1
                    logger.error(f"❌ 완료 상태 업데이트 실패: {game_id}/{game_seq} - {e}")
                    
            else:
                # AI 분석 실패
                error_msg = ai_response.get("error", "알 수 없는 AI 분석 오류")
                try:
                    db_manager.update_game_ai_result(
                        game_id, game_seq, 'ERROR',
                        f"AI 분석 실패: {error_msg}"
                    )
                except Exception as e:
                    logger.warning(f"⚠️ 실패 상태 업데이트 실패: {game_id}/{game_seq} - {e}")
                
                results["failed"] += 1
                logger.error(f"❌ AI 분석 실패: {game_id}/{game_seq} - {error_msg}")
            
            # 과부하 방지 지연 (1초)
            time.sleep(1.0)
            
        except Exception as e:
            # 예외 발생 시 오류 상태로 변경
            game_id = game.get('game_id', 'UNKNOWN')
            game_seq = game.get('game_seq', 0)
            
            try:
                db_manager.update_game_ai_result(
                    game_id, game_seq, 'ERROR',
                    f"처리 중 시스템 예외: {str(e)[:150]}"
                )
            except:
                pass  # DB 업데이트도 실패하는 경우 로그만 남김
            
            results["failed"] += 1
            logger.error(f"❌ 게임 처리 중 예외: {game_id}/{game_seq} - {e}", exc_info=True)
    
    logger.info(f"=== 대기 게임 처리 완료: {results} ===")
    
    # 처리 결과를 XCom에 저장 (다른 태스크에서 사용 가능)
    context['task_instance'].xcom_push(key='processing_results', value=results)
    
    return results

def monitor_and_alert(**context):
    """처리 결과 모니터링 및 알림"""
    logger.info("=== 처리 결과 모니터링 시작 ===")
    
    try:
        # 이전 태스크 결과 가져오기
        processing_results = context['task_instance'].xcom_pull(
            task_ids='process_pending_games', 
            key='processing_results'
        )
        
        # 전체 통계 조회
        try:
            stats = db_manager.get_processing_statistics()
        except Exception as e:
            logger.error(f"❌ 통계 조회 실패: {e}")
            stats = {
                'status_breakdown': [],
                'difficulty_breakdown': [],
                'today_summary': {
                    'total_processed_today': 0,
                    'completed_today': 0,
                    'failed_today': 0
                }
            }
        
        # 상태별 통계 로깅
        logger.info("=== 현재 시스템 통계 ===")
        status_mapping = {
            'B20005': 'PENDING',
            'B20007': 'COMPLETED', 
            'B20008': 'FAILED'
        }
        
        for stat in stats['status_breakdown']:
            status_code = stat['ai_status_code']
            status_name = status_mapping.get(status_code, status_code)
            logger.info(f"  {status_name}: 전체 {stat['total_count']}개, 오늘 {stat['today_count']}개")
        
        # 오늘의 처리 요약
        today = stats['today_summary']
        logger.info(f"=== 오늘의 처리 현황 ===")
        logger.info(f"  전체 처리: {today['total_processed_today']}개")
        logger.info(f"  성공: {today['completed_today']}개")
        logger.info(f"  실패: {today['failed_today']}개")
        
        # 현재 배치 처리 결과
        if processing_results:
            logger.info(f"=== 현재 배치 처리 결과 ===")
            logger.info(f"  처리 완료: {processing_results['processed']}개")
            logger.info(f"  처리 실패: {processing_results['failed']}개")
            logger.info(f"  건너뜀: {processing_results['skipped']}개")
            
            # 실패율 체크 (20% 이상 실패 시 경고)
            total_attempted = processing_results['processed'] + processing_results['failed']
            if total_attempted > 0:
                failure_rate = (processing_results['failed'] / total_attempted) * 100
                if failure_rate > 20:
                    logger.warning(f"⚠️ 높은 실패율 감지: {failure_rate:.1f}% ({processing_results['failed']}/{total_attempted})")
        
        return {
            "monitoring_completed": True,
            "stats": stats,
            "processing_results": processing_results
        }
        
    except Exception as e:
        logger.error(f"❌ 모니터링 실패: {e}")
        return {"monitoring_completed": False, "error": str(e)}

def cleanup_processing_status(**context):
    """처리 상태 정리 작업"""
    logger.info("=== 처리 상태 정리 시작 ===")
    
    try:
        # 30분 이상 처리 중 상태인 게임들을 오류로 변경
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(buffered=True)
            
            try:
                # 처리 중 상태가 없으므로 대기 상태에서 30분 이상 된 것들 체크
                query = """
                UPDATE game_detail 
                SET ai_status_code = 'B20008',
                    description = '처리 시간 초과로 오류 처리',
                    ai_processed_at = CURRENT_TIMESTAMP
                WHERE ai_status_code = 'B20005' 
                AND ai_processed_at < DATE_SUB(NOW(), INTERVAL 30 MINUTE)
                AND ai_processed_at IS NOT NULL
                """
                
                cursor.execute(query)
                conn.commit()
                
                affected_rows = cursor.rowcount
                if affected_rows > 0:
                    logger.info(f"🧹 처리 시간 초과 게임 {affected_rows}개를 오류 상태로 변경")
                else:
                    logger.info("✅ 처리 시간 초과 게임 없음")
                
                return {"cleaned_up": affected_rows}
                
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ 정리 작업 쿼리 실패: {e}")
                return {"cleaned_up": 0, "error": str(e)}
            finally:
                # 안전한 커서 닫기
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass
                cursor.close()
            
    except Exception as e:
        logger.error(f"❌ 정리 작업 실패: {e}")
        return {"cleaned_up": 0, "error": str(e)}

# DAG 정의
default_args = {
    'owner': DAG_DEFAULT_ARGS['owner'],
    'depends_on_past': DAG_DEFAULT_ARGS['depends_on_past'],
    'start_date': datetime(2024, 1, 1, tzinfo=local_tz),
    'email_on_failure': DAG_DEFAULT_ARGS['email_on_failure'],
    'email_on_retry': DAG_DEFAULT_ARGS['email_on_retry'],
    'retries': DAG_DEFAULT_ARGS['retries'],
    'retry_delay': timedelta(minutes=DAG_DEFAULT_ARGS['retry_delay_minutes']),
    'max_active_runs': DAG_DEFAULT_ARGS['max_active_runs'],
}

dag = DAG(
    'memory_forest_ai_main',
    default_args=default_args,
    description='Memory Forest AI 게임 분석 메인 워크플로우 - 연결 오류 수정',
    schedule_interval='*/30 * * * *',  # 30분마다 실행
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'ai', 'main', 'production']
)

# Task 정의
start_task = DummyOperator(
    task_id='start_processing',
    dag=dag
)

health_check_task = PythonOperator(
    task_id='check_system_health',
    python_callable=check_system_health,
    dag=dag
)

process_games_task = PythonOperator(
    task_id='process_pending_games',
    python_callable=process_pending_games,
    dag=dag
)

monitor_task = PythonOperator(
    task_id='monitor_and_alert',
    python_callable=monitor_and_alert,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_processing_status',
    python_callable=cleanup_processing_status,
    dag=dag
)

end_task = DummyOperator(
    task_id='end_processing',
    dag=dag
)

# Task 의존성 정의
start_task >> health_check_task >> process_games_task >> [monitor_task, cleanup_task] >> end_task