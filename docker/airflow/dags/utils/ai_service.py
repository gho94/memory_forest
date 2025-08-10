"""
AI 서비스 호출 유틸리티
"""

import logging
import requests
import time
from typing import Dict, Optional, List
from config import AI_SERVICE_CONFIG, DIFFICULTY_CODES

logger = logging.getLogger(__name__)

class AIServiceClient:
    """AI 서비스 클라이언트"""
    
    def __init__(self):
        self.base_url = AI_SERVICE_CONFIG['base_url']
        self.timeout = AI_SERVICE_CONFIG['timeout']
        self.max_retries = AI_SERVICE_CONFIG['max_retries']
        self.retry_delay = AI_SERVICE_CONFIG['retry_delay']
    
    def check_health(self) -> bool:
        """AI 서비스 상태 확인"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"AI 서비스 상태 확인 실패: {e}")
            return False
    
    def analyze_game(self, game_data: Dict) -> Dict:
        """게임 AI 분석 요청"""
        difficulty_code = game_data.get('difficulty_level_code', 'D10002')
        difficulty_level = DIFFICULTY_CODES.get(difficulty_code, 'NORMAL')
        
        request_data = {
            "gameId": game_data['game_id'],
            "gameSeq": game_data['game_seq'],
            "answerText": game_data['answer_text'],
            "difficultyLevel": difficulty_level
        }
        
        logger.info(f"AI 분석 요청: {game_data['game_id']}/{game_data['game_seq']} - {game_data['answer_text']}")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/analyze",
                    json=request_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"AI 분석 성공: {game_data['game_id']}/{game_data['game_seq']}")
                    return {
                        "status": "success",
                        "result": result
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(f"AI 분석 HTTP 오류 (시도 {attempt + 1}): {error_msg}")
                    
                    if attempt == self.max_retries - 1:
                        return {
                            "status": "error",
                            "error": f"HTTP 오류: {error_msg}"
                        }
                    
            except requests.exceptions.Timeout:
                error_msg = f"타임아웃 (시도 {attempt + 1})"
                logger.warning(error_msg)
                if attempt == self.max_retries - 1:
                    return {"status": "error", "error": "AI 서비스 타임아웃"}
                    
            except requests.exceptions.ConnectionError:
                error_msg = f"연결 실패 (시도 {attempt + 1})"
                logger.warning(error_msg)
                if attempt == self.max_retries - 1:
                    return {"status": "error", "error": "AI 서비스 연결 실패"}
                    
            except Exception as e:
                error_msg = f"예외 발생: {str(e)}"
                logger.error(error_msg)
                return {"status": "error", "error": error_msg}
            
            # 재시도 전 대기
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return {"status": "error", "error": "최대 재시도 횟수 초과"}

# 전역 AI 서비스 클라이언트 인스턴스
ai_client = AIServiceClient()