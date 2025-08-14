"""
Memory Forest Airflow DAG 공통 설정
컴팩트한 버전 - 두 가지 핵심 기능에 집중
"""

import os
from typing import Dict, List
from datetime import timedelta
import pendulum

# Timezone 설정
LOCAL_TZ = pendulum.timezone("Asia/Seoul")

# 데이터베이스 설정 - init.sql과 일치
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'database': os.getenv('DB_NAME', 'memory_forest'),
    'user': os.getenv('DB_USER', 'kcc'),
    'password': os.getenv('DB_PASSWORD', 'kcc'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': False
}

# AI 서비스 설정
AI_SERVICE_CONFIG = {
    'base_url': os.getenv('AI_SERVICE_URL', 'http://ai-service:8000'),
    'timeout': int(os.getenv('AI_SERVICE_TIMEOUT', '60')),
    'max_retries': int(os.getenv('AI_SERVICE_MAX_RETRIES', '3')),
    'retry_delay': int(os.getenv('AI_SERVICE_RETRY_DELAY', '5'))
}

# AI 상태 코드 (game_detail.ai_status_code) - init.sql 기준
AI_STATUS_CODES = {
    'WAITING': 'B20005',      # 대기중 - AI 분석 대기
    'PROCESSING': 'B20006',   # 진행중 - AI 분석 중
    'COMPLETED': 'B20007',    # 완료 - AI 분석 완료
    'FAILED': 'B20008',       # 실패 - AI 분석 실패
}

# 네이버 API 설정 (기존 코드 호환성)
NAVER_API_CONFIG = {
    'client_id': os.getenv("NAVER_CLIENT_ID"),
    'client_secret': os.getenv("NAVER_CLIENT_SECRET"),
    'base_url': 'https://openapi.naver.com/v1'
}

# 모델 관리 설정
MODEL_CONFIG = {
    'model_path': '/opt/airflow/models/word2vec_custom.model',
    'backup_path': '/opt/airflow/models/word2vec_custom_backup.model',
    'training_data_path': '/opt/airflow/data/training',
    'missing_words_marker': '%모델%'  # 모델에 없는 단어 마커
}

# 기본 DAG 설정
DEFAULT_ARGS = {
    'owner': 'memory-forest',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
    'start_date': pendulum.datetime(2024, 1, 1, tz=LOCAL_TZ)
}

# 배치 처리 설정
BATCH_CONFIG = {
    'retry_games_batch_size': int(os.getenv('RETRY_GAMES_BATCH_SIZE', '20')),
    'model_training_batch_size': int(os.getenv('MODEL_TRAINING_BATCH_SIZE', '50')),
    'max_concurrent_requests': int(os.getenv('MAX_CONCURRENT_REQUESTS', '5')),
}

# 모델 관리 설정
MODEL_CONFIG = {
    'model_path': os.getenv('MODEL_PATH', '/opt/airflow/models/word2vec_custom.model'),
    'backup_path': os.getenv('BACKUP_MODEL_PATH', '/opt/airflow/models/word2vec_custom_backup.model'),
    'training_data_path': os.getenv('TRAINING_DATA_PATH', '/opt/airflow/data/training'),
    'missing_words_marker': os.getenv('MISSING_WORDS_MARKER', '%모델%')
}

# 스케줄 설정 - 두 가지 주요 기능에 집중
SCHEDULES = {
    'retry_failed_games': os.getenv('RETRY_SCHEDULE', '*/10 * * * *'),
    'train_missing_words': os.getenv('TRAINING_SCHEDULE', '0 3 * * *'),
}