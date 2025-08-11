"""
AI 서비스 호출 유틸리티 - 기존 AI 서비스 코드에 완전 호환
"""

import logging
import requests
import time
from typing import Dict, Optional, List
from config import AI_SERVICE_CONFIG, DIFFICULTY_CODES

logger = logging.getLogger(__name__)

class AIServiceClient:
    """AI 서비스 클라이언트 - 기존 AI 서비스 형식에 맞춤"""
    
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
            
            if response.status_code == 200:
                logger.info("✅ AI 서비스 상태 정상")
                return True
            else:
                logger.warning(f"⚠️ AI 서비스 상태 이상: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI 서비스 상태 확인 실패: {e}")
            return False
    
    def analyze_game(self, game_data: Dict) -> Dict:
        """게임 AI 분석 요청 - 기존 AI 서비스 응답 형식 그대로 사용"""
        
        # 입력 데이터 검증
        game_id = game_data.get('game_id', 'UNKNOWN')
        game_seq = game_data.get('game_seq', 0)
        answer_text = game_data.get('answer_text', '').strip()
        
        if not answer_text:
            return {
                "status": "error",
                "error": "빈 답변 텍스트"
            }
        
        # 난이도 매핑
        difficulty_code = game_data.get('difficulty_level_code', 'B20002')
        difficulty_level = DIFFICULTY_CODES.get(difficulty_code, 'NORMAL')
        
        logger.info(f"🔄 AI 분석 요청: {game_id}/{game_seq} - '{answer_text}' ({difficulty_level})")
        
        # 재시도 로직
        last_error = None
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # 기존 AI 서비스가 내부적으로 generate_wrong_options_with_difficulty 함수를 호출
                # /analyze 엔드포인트는 answer_text와 difficulty를 받아서 처리
                response = requests.post(
                    f"{self.base_url}/analyze",
                    json={
                        "answer_text": answer_text,
                        "difficulty": difficulty_level
                    },
                    headers={
                        'Content-Type': 'application/json'
                    },
                    timeout=self.timeout
                )
                
                response_time = round(time.time() - start_time, 2)
                
                if response.status_code == 200:
                    try:
                        ai_result = response.json()
                        
                        # 기존 AI 서비스 응답 형식:
                        # {
                        #   "status": "COMPLETED" or "FAILED",
                        #   "wrong_options": [word1, word2, word3],
                        #   "wrong_scores": [score1, score2, score3],
                        #   "difficulty_used": "NORMAL",
                        #   "error": "error message" (실패시만)
                        # }
                        
                        if ai_result.get("status") == "COMPLETED":
                            # DB repository 형식으로 변환
                            wrong_options = ai_result.get("wrong_options", ["", "", ""])
                            wrong_scores = ai_result.get("wrong_scores", [0.0, 0.0, 0.0])
                            
                            # 3개 미만이면 빈 값으로 채우기
                            while len(wrong_options) < 3:
                                wrong_options.append("")
                            while len(wrong_scores) < 3:
                                wrong_scores.append(0.0)
                            
                            result_data = {
                                "wrong_option_1": wrong_options[0],
                                "wrong_option_2": wrong_options[1], 
                                "wrong_option_3": wrong_options[2],
                                "wrong_score_1": wrong_scores[0],
                                "wrong_score_2": wrong_scores[1],
                                "wrong_score_3": wrong_scores[2],
                                "ai_status": "COMPLETED",
                                "description": f"AI 분석 완료 - 난이도: {ai_result.get('difficulty_used', difficulty_level)}"
                            }
                            
                            logger.info(f"✅ AI 분석 성공: {game_id}/{game_seq} "
                                      f"- 옵션: {wrong_options[:3]} ({response_time}초)")
                            
                            return {
                                "status": "success",
                                "result": result_data
                            }
                        
                        elif ai_result.get("status") == "FAILED":
                            error_msg = ai_result.get("error", "AI 분석 실패")
                            logger.error(f"❌ AI 분석 실패: {game_id}/{game_seq} - {error_msg}")
                            
                            return {
                                "status": "error",
                                "error": error_msg
                            }
                        
                        else:
                            error_msg = f"알 수 없는 AI 응답 상태: {ai_result.get('status')}"
                            logger.error(f"❌ {error_msg}")
                            return {
                                "status": "error", 
                                "error": error_msg
                            }
                            
                    except Exception as e:
                        logger.error(f"❌ AI 응답 파싱 실패: {e}")
                        return {
                            "status": "error",
                            "error": f"응답 파싱 실패: {str(e)}"
                        }
                
                else:
                    # HTTP 오류
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    last_error = error_msg
                    logger.warning(f"⚠️ {error_msg} (시도 {attempt + 1}/{self.max_retries})")
                    
                    # 4xx 오류는 재시도하지 않음
                    if 400 <= response.status_code < 500:
                        return {
                            "status": "error",
                            "error": error_msg
                        }
            
            except requests.exceptions.Timeout:
                last_error = f"요청 타임아웃 ({self.timeout}초)"
                logger.warning(f"⚠️ {last_error} (시도 {attempt + 1}/{self.max_retries})")
            
            except requests.exceptions.ConnectionError:
                last_error = "AI 서비스 연결 실패"
                logger.warning(f"⚠️ {last_error} (시도 {attempt + 1}/{self.max_retries})")
            
            except Exception as e:
                last_error = f"예상치 못한 오류: {str(e)}"
                logger.error(f"❌ {last_error}")
                return {
                    "status": "error",
                    "error": last_error
                }
            
            # 마지막 시도가 아니면 재시도 대기
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        # 모든 재시도 실패
        final_error = last_error or "알 수 없는 오류"
        logger.error(f"❌ AI 분석 최종 실패: {game_id}/{game_seq} - {final_error}")
        return {
            "status": "error",
            "error": f"최대 재시도 후 실패: {final_error}"
        }
    
    def reload_model(self) -> bool:
        """AI 서비스 모델 리로드 요청"""
        try:
            logger.info("🔄 AI 서비스 모델 리로드 요청...")
            
            response = requests.post(
                f"{self.base_url}/reload-model",
                timeout=60  # 모델 로딩은 시간이 걸릴 수 있음
            )
            
            if response.status_code == 200:
                logger.info("✅ AI 서비스 모델 리로드 성공")
                return True
            else:
                logger.warning(f"⚠️ 모델 리로드 실패: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ 모델 리로드 요청 실패: {e}")
            return False
    
    def get_model_info(self) -> Optional[Dict]:
        """AI 서비스 모델 정보 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/model/info",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"모델 정보 조회 실패: HTTP {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"모델 정보 조회 실패: {e}")
            return None

# 전역 AI 서비스 클라이언트 인스턴스
ai_client = AIServiceClient()

# 편의 함수들
def check_ai_service_health() -> bool:
    """AI 서비스 상태 확인"""
    return ai_client.check_health()

def analyze_game_with_ai(game_data: Dict) -> Dict:
    """게임 AI 분석"""
    return ai_client.analyze_game(game_data)

def reload_ai_model() -> bool:
    """AI 모델 리로드"""
    return ai_client.reload_model()

def get_ai_service_info() -> Optional[Dict]:
    """AI 서비스 정보 조회"""
    return ai_client.get_model_info()