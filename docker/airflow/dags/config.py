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

# init.sql common_codes 테이블의 상태 코드 정의
STATUS_CODES = {
    # 게임 생성 상태 (B200xx)
    'PENDING': 'B20010',      # 대기
    'PROCESSING': 'B20011',   # 진행중
    'COMPLETED': 'B20012',    # 완료
    'PAUSED': 'B20013',       # 중단
    'ERROR': 'B20014',        # 오류
    'CANCELLED': 'B20015',    # 취소
    
    # 게임 플레이 상태 (B201xx)
    'GAME_READY': 'B20110',   # 게임 준비
    'GAME_PLAYING': 'B20111', # 게임 진행중
    'GAME_FINISHED': 'B20112', # 게임 완료
    'GAME_TIMEOUT': 'B20113'   # 게임 시간초과
}

# 난이도 코드 정의 (D100xx)
DIFFICULTY_CODES = {
    'D10001': 'EASY',      # 초급
    'D10002': 'NORMAL',    # 중급  
    'D10003': 'HARD',      # 고급
    'D10004': 'EXPERT'     # 전문가
}

# 사용자 타입 코드 (A100xx)
USER_TYPE_CODES = {
    'A10001': 'PATIENT',   # 환자
    'A10002': 'FAMILY',    # 가족
    'A10003': 'ADMIN',     # 관리자
    'A10004': 'DOCTOR'     # 의료진
}

# 카테고리 코드 (C100xx)
CATEGORY_CODES = {
    'C10001': 'FAMILY',    # 가족
    'C10002': 'FOOD',      # 음식
    'C10003': 'TRAVEL',    # 여행
    'C10004': 'HOBBY',     # 취미
    'C10005': 'DAILY',     # 일상
    'C10006': 'ANIMAL',    # 동물
    'C10007': 'NATURE'     # 자연
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