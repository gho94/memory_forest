"""
네이버 API 클라이언트
기존 코드와의 호환성 유지
"""

import logging
import requests
import time
from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NAVER_API_CONFIG

logger = logging.getLogger(__name__)

class NaverAPIClient:
    """네이버 API 통신 클라이언트"""
    
    def __init__(self):
        self.client_id = NAVER_API_CONFIG['client_id']
        self.client_secret = NAVER_API_CONFIG['client_secret']
        self.base_url = NAVER_API_CONFIG['base_url']
        
        if not self.client_id or not self.client_secret:
            logger.warning("네이버 API 인증 정보가 없습니다")
    
    def search_words(self, query: str, display: int = 10) -> Optional[Dict]:
        """네이버 검색 API로 단어 검색"""
        if not self.client_id or not self.client_secret:
            logger.error("네이버 API 인증 정보 없음")
            return None
        
        try:
            url = f"{self.base_url}/search/encyc.json"
            headers = {
                'X-Naver-Client-Id': self.client_id,
                'X-Naver-Client-Secret': self.client_secret
            }
            params = {
                'query': query,
                'display': display,
                'start': 1,
                'sort': 'sim'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"네이버 검색 성공: {query}")
                return result
            else:
                logger.error(f"네이버 검색 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"네이버 API 요청 오류: {e}")
            return None
    
    def get_word_definition(self, word: str) -> Optional[str]:
        """단어의 정의 가져오기"""
        search_result = self.search_words(word, display=1)
        
        if not search_result or not search_result.get('items'):
            return None
        
        item = search_result['items'][0]
        description = item.get('description', '')
        
        # HTML 태그 제거
        import re
        clean_description = re.sub(r'<[^>]+>', '', description)
        
        return clean_description.strip() if clean_description else None
    
    def validate_word_exists(self, word: str) -> bool:
        """단어가 사전에 존재하는지 확인"""
        search_result = self.search_words(word, display=1)
        
        if not search_result:
            return False
        
        items = search_result.get('items', [])
        if not items:
            return False
        
        # 첫 번째 검색 결과의 제목이 검색어와 유사한지 확인
        first_item = items[0]
        title = first_item.get('title', '').replace('<b>', '').replace('</b>', '')
        
        return word in title or title in word
    
    def batch_validate_words(self, words: List[str]) -> Dict[str, bool]:
        """단어 목록 일괄 검증"""
        results = {}
        
        for word in words:
            try:
                results[word] = self.validate_word_exists(word)
                # API 호출 제한을 위한 지연
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"단어 검증 실패 '{word}': {e}")
                results[word] = False
        
        return results