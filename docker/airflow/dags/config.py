"""
Memory Forest Airflow DAG 공통 설정
init.sql 데이터베이스 구조와 AI 서비스에 맞춘 설정
"""

import os
from typing import Dict, List

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

# init.sql common_codes 테이블의 실제 상태 코드 정의
# 게임 진행 상태 (B10003 - B2001x)
STATUS_CODES = {
    'PENDING': 'B20010',      # 대기
    'PROCESSING': 'B20011',   # 진행중
    'COMPLETED': 'B20012',    # 완료
    'PAUSED': 'B20013',       # 중단
    'ERROR': 'B20014',        # 오류
}

# 게임 생성 상태 코드 (B10002 - B2000x)
CREATION_STATUS_CODES = {
    'WAITING': 'B20005',      # 대기중
    'CREATING': 'B20006',     # 생성중
    'COMPLETED': 'B20007',    # 완료
    'FAILED': 'B20008',       # 실패
    'CANCELLED': 'B20009'     # 취소
}

# 난이도 코드 정의 (B10001 - B2000x)
DIFFICULTY_CODES = {
    'B20001': 'EASY',      # 초급
    'B20002': 'NORMAL',    # 중급  
    'B20003': 'HARD',      # 고급
    'B20004': 'EXPERT'     # 전문가
}

# 사용자 타입 코드 (A10001 - A2000x)
USER_TYPE_CODES = {
    'A20001': 'PATIENT',   # 환자
    'A20002': 'FAMILY',    # 가족
    'A20003': 'ADMIN',     # 관리자
    'A20004': 'DOCTOR'     # 의료진
}

# 계정 상태 코드 (A10002 - A2000x)
ACCOUNT_STATUS_CODES = {
    'A20005': 'ACTIVE',    # 활성
    'A20006': 'INACTIVE',  # 비활성
    'A20007': 'SUSPENDED', # 정지
    'A20008': 'DELETED',   # 삭제
    'A20009': 'WAITING'    # 대기
}

# 관계 코드 (A10003 - A2001x)
RELATIONSHIP_CODES = {
    'A20010': 'SPOUSE',    # 배우자
    'A20011': 'SON',       # 아들
    'A20012': 'DAUGHTER',  # 딸
    'A20013': 'GRANDSON',  # 손자
    'A20014': 'GRANDDAUGHTER', # 손녀
    'A20015': 'BROTHER',   # 형제
    'A20016': 'SISTER',    # 자매
    'A20017': 'OTHER'      # 기타
}

# 연결 상태 코드 (A10004 - A2001x)
CONNECTION_STATUS_CODES = {
    'A20018': 'CONNECTED',     # 연결됨
    'A20019': 'PENDING',       # 연결 대기
    'A20020': 'DISCONNECTED',  # 연결 해제
    'A20021': 'REJECTED'       # 거부됨
}

# AI 상태 코드 매핑 (실제 DB 컬럼값)
AI_STATUS_CODES = {
    'B20005': 'PENDING',      # 대기중 (ai_status_code)
    'B20007': 'COMPLETED',    # 완료 (ai_status_code)
    'B20008': 'FAILED'        # 실패 (ai_status_code)
}

# Airflow DAG 기본 설정
DAG_DEFAULT_ARGS = {
    'owner': 'memory-forest',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay_minutes': 3,
    'max_active_runs': 1,
}

# 처리 배치 크기 설정
BATCH_SIZES = {
    'pending_games': int(os.getenv('BATCH_SIZE_PENDING', '30')),
    'error_games': int(os.getenv('BATCH_SIZE_ERROR', '20')),
    'daily_summary': int(os.getenv('BATCH_SIZE_SUMMARY', '100'))
}

# 로깅 설정
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_log_size_mb': int(os.getenv('MAX_LOG_SIZE_MB', '100'))
}

# AI 분석 재시도 규칙
RETRY_RULES = {
    'connection_errors': ['연결 실패', '타임아웃', 'ConnectionError', 'timeout'],
    'service_errors': ['HTTP 오류', '서비스 오류', '500', '502', '503'],
    'temporary_errors': ['일시적 오류', 'temporary', 'busy'],
    'permanent_errors': ['모델에 존재하지 않습니다', '지원하지 않는', 'not supported'],
    'max_retry_count': 3,
    'retry_delay_hours': 1
}

# 모니터링 알림 설정
MONITORING_CONFIG = {
    'error_threshold_percentage': float(os.getenv('ERROR_THRESHOLD', '10.0')),
    'pending_threshold_count': int(os.getenv('PENDING_THRESHOLD', '100')),
    'daily_report_hour': int(os.getenv('DAILY_REPORT_HOUR', '9')),
    'health_check_interval_minutes': int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
}