"""
Memory Forest Utils 패키지 초기화
컴팩트한 버전 - 핵심 기능에 집중
"""

__version__ = "2.0.0"
__author__ = "Memory Forest Team"

# 핵심 모듈 import
from .database import DatabaseManager
from .ai_service import AIServiceClient
from .text_processor import TextProcessor
from .naver_api import NaverAPIClient

# 전역 인스턴스 생성
db_manager = DatabaseManager()
ai_client = AIServiceClient()
text_processor = TextProcessor()
naver_client = NaverAPIClient()

__all__ = [
    'DatabaseManager',
    'AIServiceClient', 
    'TextProcessor',
    'NaverAPIClient',
    'db_manager',
    'ai_client',
    'text_processor',
    'naver_client'
]