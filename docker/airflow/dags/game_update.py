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