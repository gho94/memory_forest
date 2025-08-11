
# common/config.py
import os
from datetime import timedelta
import pendulum

# Timezone 설정
LOCAL_TZ = pendulum.timezone("Asia/Seoul")

# 데이터베이스 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'database': os.getenv('DB_NAME', 'memory_forest'),
    'user': os.getenv('DB_USER', 'kcc'),
    'password': os.getenv('DB_PASSWORD', 'kcc'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

# 서비스 URL 설정
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://ai-service:8000')
SPRING_BOOT_URL = os.getenv('SPRING_BOOT_URL', 'http://backend:8080')

# 네이버 API 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 경로 설정
DATA_BASE_PATH = "/opt/airflow/data"
MODEL_BASE_PATH = "/opt/airflow/models"
MODEL_SAVE_PATH = f"{MODEL_BASE_PATH}/word2vec_custom.model"
BACKUP_MODEL_PATH = f"{MODEL_BASE_PATH}/word2vec_custom_backup.model"

# 기본 DAG 설정
DEFAULT_ARGS = {
    'owner': 'memory-forest',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 타임아웃 설정
TIMEOUTS = {
    'health_check': timedelta(minutes=2),
    'data_collection': timedelta(hours=3),
    'model_training': timedelta(hours=2),
    'game_processing': timedelta(minutes=30),
    'system_management': timedelta(minutes=10)
}

# 배치 크기 설정
BATCH_SIZES = {
    'game_processing': 50,
    'model_training': 100,
    'reprocessing': 20
}