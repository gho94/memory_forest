"""
Memory Forest Utils 패키지 초기화
"""

# 버전 정보
__version__ = "1.0.0"
__author__ = "Memory Forest Team"

# 공통 모듈들을 위한 import
from .database import db_manager
from .ai_service import ai_client
from .model_manager import model_manager

# 편의 함수들
from .ai_service import (
    check_ai_service_health,
    analyze_game_with_ai,
    reload_ai_model,
    get_ai_service_info
)

from .model_manager import (
    get_current_model_info,
    create_model_backup,
    list_model_backups,
    restore_model_from_backup,
    reload_ai_service_model,
    check_system_health
)

__all__ = [
    # 클래스들
    'db_manager',
    'ai_client',
    'model_manager',
    
    # 편의 함수들
    'check_ai_service_health',
    'analyze_game_with_ai', 
    'reload_ai_model',
    'get_ai_service_info',
    'get_current_model_info',
    'create_model_backup',
    'list_model_backups',
    'restore_model_from_backup',
    'reload_ai_service_model',
    'check_system_health'
]