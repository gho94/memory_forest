from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum
import os
import logging
import requests
import mysql.connector
from mysql.connector import Error
from typing import List, Dict

# Airflow 설정
local_tz = pendulum.timezone("Asia/Seoul")

# DB 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'database': os.getenv('DB_NAME', 'memory_forest'),
    'user': os.getenv('DB_USER', 'kcc'),
    'password': os.getenv('DB_PASSWORD', 'kcc'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

# AI 서비스 URL
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://ai-service:8000')

# 상태 코드 정의
STATUS_CODES = {
    'PENDING': 'B20010',    # 대기
    'PROCESSING': 'B20011', # 진행중
    'COMPLETED': 'B20012',  # 완료
    'PAUSED': 'B20013',     # 중단
    'ERROR': 'B20014'       # 오류
}

# 난이도 코드 정의 (예시)
DIFFICULTY_CODES = {
    'D10001': 'EASY',     # 초급
    'D10002': 'NORMAL',   # 중급  
    'D10003': 'HARD',     # 고급
    'D10004': 'EXPERT'    # 전문가
}

def get_db_connection():
    """데이터베이스 연결"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logging.error(f"데이터베이스 연결 실패: {e}")
        return None

def get_games_by_status(status_code: str, limit: int = 50) -> List[Dict]:
    """특정 상태의 게임들을 조회"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            gd.game_id, 
            gd.game_seq, 
            gd.answer_text,
            gd.ai_status,
            gd.description,
            gm.difficulty_level_code,
            gm.game_name
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.ai_status = %s 
        AND gd.answer_text IS NOT NULL 
        AND gd.answer_text != ''
        ORDER BY gd.game_id, gd.game_seq
        LIMIT %s
        """
        cursor.execute(query, (status_code, limit))
        results = cursor.fetchall()
        
        logging.info(f"상태 '{status_code}'인 게임 {len(results)}개 조회")
        return results
        
    except Exception as e:
        logging.error(f"게임 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_game_status(game_id: str, game_seq: int, status: str, description: str = None):
    """게임 상태 업데이트"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        UPDATE game_detail 
        SET ai_status = %s, 
            description = %s,
            ai_processed_at = NOW()
        WHERE game_id = %s AND game_seq = %s
        """
        cursor.execute(query, (status, description, game_id, game_seq))
        connection.commit()
        
        logging.info(f"게임 상태 업데이트: {game_id}-{game_seq} -> {status}")
        return cursor.rowcount > 0
        
    except Exception as e:
        logging.error(f"상태 업데이트 실패: {game_id}-{game_seq}, 에러: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_game_ai_result(game_id: str, game_seq: int, ai_result: Dict):
    """AI 분석 결과 업데이트"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        UPDATE game_detail 
        SET wrong_option_1 = %s,
            wrong_option_2 = %s, 
            wrong_option_3 = %s,
            wrong_score_1 = %s,
            wrong_score_2 = %s,
            wrong_score_3 = %s,
            ai_status = %s,
            description = %s,
            ai_processed_at = NOW()
        WHERE game_id = %s AND game_seq = %s
        """
        
        values = (
            ai_result.get('wrong_option_1', ''),
            ai_result.get('wrong_option_2', ''),
            ai_result.get('wrong_option_3', ''),
            ai_result.get('wrong_score_1', 0.0),
            ai_result.get('wrong_score_2', 0.0), 
            ai_result.get('wrong_score_3', 0.0),
            ai_result.get('ai_status', 'ERROR'),
            ai_result.get('description', ''),
            game_id,
            game_seq
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        return cursor.rowcount > 0
            
    except Exception as e:
        logging.error(f"AI 결과 업데이트 실패: {game_id}-{game_seq}, 에러: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def call_ai_service_with_difficulty(game_data: Dict) -> Dict:
    """난이도별 AI 서비스 호출"""
    try:
        difficulty_code = game_data.get('difficulty_level_code')
        difficulty_level = DIFFICULTY_CODES.get(difficulty_code, 'NORMAL')
        
        # AI 서비스 요청 데이터
        request_data = {
            "gameId": game_data['game_id'],
            "gameSeq": game_data['game_seq'],
            "answerText": game_data['answer_text'],
            "difficultyLevel": difficulty_level  # 난이도 추가
        }
        
        # AI 서비스 호출
        response = requests.post(
            f"{AI_SERVICE_URL}/analyze",
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"AI 분석 성공: {game_data['game_id']}-{game_data['game_seq']}, 난이도: {difficulty_level}")
            return result
        else:
            error_msg = f"AI 서비스 오류: {response.status_code}"
            logging.error(error_msg)
            return {
                "gameId": game_data['game_id'],
                "gameSeq": game_data['game_seq'],
                "aiStatus": "ERROR",
                "description": error_msg
            }
            
    except Exception as e:
        error_msg = f"AI 서비스 호출 실패: {str(e)}"
        logging.error(error_msg)
        return {
            "gameId": game_data['game_id'],
            "gameSeq": game_data['game_seq'],
            "aiStatus": "ERROR",
            "description": error_msg
        }

def process_pending_games(**context):
    """대기 상태 게임 처리"""
    logging.info("=== 대기 상태 게임 처리 시작 ===")
    
    pending_games = get_games_by_status('PENDING')
    if not pending_games:
        logging.info("처리할 대기 게임이 없습니다.")
        return
    
    processed_count = 0
    failed_count = 0
    
    for game in pending_games:
        try:
            # 진행중 상태로 변경
            update_game_status(
                game['game_id'], 
                game['game_seq'], 
                'PROCESSING', 
                'AI 분석 진행중'
            )
            
            # AI 서비스 호출 (난이도별)
            ai_result = call_ai_service_with_difficulty(game)
            
            # 결과에 따른 처리
            if ai_result.get('aiStatus') == 'COMPLETED':
                # 성공: 완료 상태로 업데이트
                update_game_ai_result(game['game_id'], game['game_seq'], {
                    'wrong_option_1': ai_result.get('wrongOption1', ''),
                    'wrong_option_2': ai_result.get('wrongOption2', ''),
                    'wrong_option_3': ai_result.get('wrongOption3', ''),
                    'wrong_score_1': ai_result.get('wrongScore1', 0.0),
                    'wrong_score_2': ai_result.get('wrongScore2', 0.0),
                    'wrong_score_3': ai_result.get('wrongScore3', 0.0),
                    'ai_status': 'COMPLETED',
                    'description': ai_result.get('description', 'AI 분석 완료')
                })
                processed_count += 1
                
            else:
                # 실패: 오류 상태로 업데이트
                update_game_status(
                    game['game_id'], 
                    game['game_seq'], 
                    'ERROR', 
                    ai_result.get('description', 'AI 분석 실패')
                )
                failed_count += 1
                
        except Exception as e:
            logging.error(f"게임 처리 중 예외: {game['game_id']}-{game['game_seq']}, 에러: {e}")
            update_game_status(
                game['game_id'], 
                game['game_seq'], 
                'ERROR', 
                f'처리 중 예외 발생: {str(e)}'
            )
            failed_count += 1
    
    logging.info(f"대기 게임 처리 완료: 성공 {processed_count}개, 실패 {failed_count}개")

def process_paused_games(**context):
    """중단 상태 게임 재처리"""
    logging.info("=== 중단 상태 게임 재처리 시작 ===")
    
    paused_games = get_games_by_status('PAUSED')
    if not paused_games:
        logging.info("재처리할 중단 게임이 없습니다.")
        return
    
    # 중단된 게임을 대기 상태로 되돌려서 재처리
    for game in paused_games:
        update_game_status(
            game['game_id'], 
            game['game_seq'], 
            'PENDING', 
            '중단 상태에서 재처리 대기'
        )
    
    logging.info(f"중단 게임 {len(paused_games)}개를 대기 상태로 변경")

def process_error_games(**context):
    """오류 상태 게임 분석 및 처리"""
    logging.info("=== 오류 상태 게임 분석 시작 ===")
    
    error_games = get_games_by_status('ERROR')
    if not error_games:
        logging.info("분석할 오류 게임이 없습니다.")
        return
    
    retry_count = 0
    skip_count = 0
    
    for game in error_games:
        description = game.get('description', '')
        
        # 오류 유형별 처리
        if '모델에 존재하지 않습니다' in description:
            # 모델에 없는 단어 -> 학습 필요, 일단 스킵
            logging.info(f"모델 학습 필요: {game['game_id']}-{game['game_seq']}, 단어: {game['answer_text']}")
            skip_count += 1
            
        elif 'AI 서비스 연결 실패' in description or 'timeout' in description.lower():
            # 네트워크/연결 오류 -> 재시도
            update_game_status(
                game['game_id'], 
                game['game_seq'], 
                'PENDING', 
                '연결 오류 재시도'
            )
            retry_count += 1
            
        elif '처리 중 예외' in description:
            # 처리 중 예외 -> 재시도 (최대 3회)
            # 재시도 횟수 체크 로직 추가 가능
            update_game_status(
                game['game_id'], 
                game['game_seq'], 
                'PENDING', 
                '예외 발생 재시도'
            )
            retry_count += 1
            
        else:
            # 기타 오류 -> 스킵
            skip_count += 1
    
    logging.info(f"오류 게임 분석 완료: 재시도 {retry_count}개, 스킵 {skip_count}개")

def check_ai_service_health(**context):
    """AI 서비스 상태 확인"""
    try:
        response = requests.get(
            f"{AI_SERVICE_URL}/health",
            timeout=10
        )
        
        if response.status_code == 200:
            health_data = response.json()
            logging.info(f"AI 서비스 상태: {health_data}")
            return True
        else:
            logging.error(f"AI 서비스 비정상: {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"AI 서비스 상태 확인 실패: {e}")
        return False

# DAG 정의
default_args = {
    'owner': 'memory-forest',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1, tzinfo=local_tz),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'game_ai_processing_workflow',
    default_args=default_args,
    description='게임 AI 처리 워크플로우',
    schedule_interval='*/30 * * * *',  # 30분마다 실행
    catchup=False,
    max_active_runs=1,
    tags=['game', 'ai', 'processing']
)

# Task 정의
health_check_task = PythonOperator(
    task_id='check_ai_service_health',
    python_callable=check_ai_service_health,
    dag=dag
)

process_pending_task = PythonOperator(
    task_id='process_pending_games',
    python_callable=process_pending_games,
    dag=dag
)

process_paused_task = PythonOperator(
    task_id='process_paused_games',
    python_callable=process_paused_games,
    dag=dag
)

process_error_task = PythonOperator(
    task_id='process_error_games',
    python_callable=process_error_games,
    dag=dag
)

# Task 의존성 설정
health_check_task >> [process_pending_task, process_paused_task, process_error_task]

# Spring Boot API 연동 함수들
SPRING_BOOT_URL = os.getenv('SPRING_BOOT_URL', 'http://backend:8080')

def call_spring_api(endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
    """Spring Boot API 호출"""
    try:
        url = f"{SPRING_BOOT_URL}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, timeout=30)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=30)
        else:
            raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Spring API 호출 실패: {response.status_code}, {response.text}")
            return {"error": f"API 호출 실패: {response.status_code}"}
            
    except Exception as e:
        logging.error(f"Spring API 호출 예외: {e}")
        return {"error": str(e)}

def sync_game_status_with_spring(**context):
    """Spring Boot와 게임 상태 동기화"""
    logging.info("=== Spring Boot와 게임 상태 동기화 시작 ===")
    
    try:
        # 처리 통계 조회
        stats_response = call_spring_api("/api/games/status/statistics")
        
        if "error" not in stats_response:
            logging.info(f"Spring Boot 게임 처리 통계: {stats_response}")
            
            # 통계 정보를 XCom에 저장 (다른 Task에서 참조 가능)
            context['task_instance'].xcom_push(key='game_statistics', value=stats_response)
        
        # AI 모델 상태 확인
        models_response = call_spring_api("/api/games/status/ai-models")
        
        if "error" not in models_response:
            logging.info(f"AI 모델 상태: {models_response}")
            context['task_instance'].xcom_push(key='ai_models_status', value=models_response)
        
    except Exception as e:
        logging.error(f"Spring Boot 동기화 실패: {e}")

def trigger_difficulty_batch_analysis(**context):
    """난이도별 배치 분석 트리거"""
    logging.info("=== 난이도별 배치 분석 트리거 시작 ===")
    
    difficulties = ['EASY', 'NORMAL', 'HARD', 'EXPERT']
    batch_size = 20  # 난이도별 배치 크기
    
    results = {}
    
    for difficulty in difficulties:
        try:
            # Spring Boot API를 통한 배치 분석 요청
            response = call_spring_api(
                f"/api/games/status/batch-analyze/{difficulty}?limit={batch_size}",
                method='POST'
            )
            
            results[difficulty] = response
            logging.info(f"난이도 '{difficulty}' 배치 분석 요청 결과: {response}")
            
            # 각 난이도 간 처리 간격
            time.sleep(5)
            
        except Exception as e:
            logging.error(f"난이도 '{difficulty}' 배치 분석 실패: {e}")
            results[difficulty] = {"error": str(e)}
    
    # 결과를 XCom에 저장
    context['task_instance'].xcom_push(key='batch_analysis_results', value=results)
    
    logging.info(f"난이도별 배치 분석 트리거 완료: {results}")

def handle_model_updates(**context):
    """모델 업데이트 처리"""
    logging.info("=== 모델 업데이트 처리 시작 ===")
    
    try:
        # 이전 Task에서 AI 모델 상태 가져오기
        ai_models_status = context['task_instance'].xcom_pull(
            task_ids='sync_game_status_with_spring',
            key='ai_models_status'
        )
        
        if ai_models_status and 'models_status' in ai_models_status:
            models_status = ai_models_status['models_status']
            
            # 로드되지 않은 모델들 확인
            failed_models = []
            for difficulty, status in models_status.items():
                if not status.get('loaded', False):
                    failed_models.append(difficulty)
            
            if failed_models:
                logging.warning(f"로드되지 않은 모델들: {failed_models}")
                
                # 실패한 모델들 리로드 시도
                for difficulty in failed_models:
                    try:
                        reload_response = call_spring_api(
                            f"/api/games/status/ai-models/reload/{difficulty}",
                            method='POST'
                        )
                        logging.info(f"모델 '{difficulty}' 리로드 결과: {reload_response}")
                        
                    except Exception as e:
                        logging.error(f"모델 '{difficulty}' 리로드 실패: {e}")
            else:
                logging.info("모든 AI 모델이 정상적으로 로드되어 있습니다.")
        
    except Exception as e:
        logging.error(f"모델 업데이트 처리 실패: {e}")

def cleanup_old_failed_games(**context):
    """오래된 실패 게임들 정리"""
    logging.info("=== 오래된 실패 게임들 정리 시작 ===")
    
    try:
        # 7일 이상 된 실패 게임들을 재처리 대기 상태로 변경
        cutoff_date = datetime.now() - timedelta(days=7)
        
        connection = get_db_connection()
        if not connection:
            logging.error("데이터베이스 연결 실패")
            return
        
        cursor = connection.cursor()
        
        # 오래된 실패 게임들 조회
        query = """
        SELECT DISTINCT game_id
        FROM game_detail 
        WHERE ai_status IN ('FAILED', 'ERROR')
        AND ai_processed_at < %s
        AND answer_text IS NOT NULL 
        AND answer_text != ''
        """
        
        cursor.execute(query, (cutoff_date,))
        old_failed_games = [row[0] for row in cursor.fetchall()]
        
        if old_failed_games:
            logging.info(f"정리 대상 오래된 실패 게임: {len(old_failed_games)}개")
            
            # Spring Boot API를 통한 상태 업데이트
            update_response = call_spring_api(
                "/api/games/status/batch-update",
                method='POST',
                data={
                    "gameIds": old_failed_games,
                    "targetStatus": "PENDING",
                    "description": "오래된 실패 게임 재처리 대상으로 변경",
                    "updatedBy": "airflow_cleanup"
                }
            )
            
            logging.info(f"오래된 실패 게임 정리 결과: {update_response}")
        else:
            logging.info("정리할 오래된 실패 게임이 없습니다.")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        logging.error(f"오래된 실패 게임 정리 실패: {e}")

# 추가 Task 정의
sync_spring_task = PythonOperator(
    task_id='sync_game_status_with_spring',
    python_callable=sync_game_status_with_spring,
    dag=dag
)

trigger_batch_analysis_task = PythonOperator(
    task_id='trigger_difficulty_batch_analysis',
    python_callable=trigger_difficulty_batch_analysis,
    dag=dag
)

handle_model_updates_task = PythonOperator(
    task_id='handle_model_updates',
    python_callable=handle_model_updates,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_failed_games',
    python_callable=cleanup_old_failed_games,
    dag=dag
)

# 업데이트된 Task 의존성 설정
health_check_task >> sync_spring_task
sync_spring_task >> handle_model_updates_task
sync_spring_task >> [process_pending_task, process_paused_task, process_error_task]
[process_pending_task, process_paused_task, process_error_task] >> trigger_batch_analysis_task
trigger_batch_analysis_task >> cleanup_task

# 모니터링 및 알림 Task 추가
def send_processing_summary(**context):
    """처리 결과 요약 및 알림"""
    logging.info("=== 처리 결과 요약 시작 ===")
    
    try:
        # 이전 Task들의 결과 수집
        game_stats = context['task_instance'].xcom_pull(
            task_ids='sync_game_status_with_spring',
            key='game_statistics'
        ) or {}
        
        batch_results = context['task_instance'].xcom_pull(
            task_ids='trigger_difficulty_batch_analysis',
            key='batch_analysis_results'
        ) or {}
        
        # 요약 정보 구성
        summary = {
            "timestamp": datetime.now().isoformat(),
            "game_statistics": game_stats,
            "batch_analysis_results": batch_results,
            "dag_run_id": context['dag_run'].run_id
        }
        
        logging.info(f"게임 AI 처리 워크플로우 요약: {summary}")
        
        # 필요시 여기에 Slack, Email 등 알림 로직 추가
        # send_slack_notification(summary)
        # send_email_notification(summary)
        
    except Exception as e:
        logging.error(f"처리 결과 요약 실패: {e}")

summary_task = PythonOperator(
    task_id='send_processing_summary',
    python_callable=send_processing_summary,
    dag=dag
)

# 최종 Task 의존성
cleanup_task >> summary_task