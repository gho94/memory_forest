"""
AI 서비스 클라이언트
기존 ai/services/ai_service.py와 호환되는 API 호출
"""

import logging
import requests
import time
from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AI_SERVICE_CONFIG, MODEL_CONFIG

logger = logging.getLogger(__name__)

class AIServiceClient:
    """AI 서비스와의 통신 담당"""
    
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
    
    def analyze_game(self, answer_text: str, difficulty: str = "NORMAL", game_id: str = None, game_seq: int = None) -> Optional[Dict]:
        """게임 분석 요청 - 기존 AI 서비스 API 완전 호환"""
        for attempt in range(self.max_retries):
            try:
                # AI 서비스가 요구하는 모든 필수 필드 포함 (camelCase)
                request_data = {
                    "gameId": game_id or "TEMP_GAME",
                    "gameSeq": game_seq or 999,
                    "answerText": answer_text,
                    "difficultyLevel": difficulty
                }
                
                response = requests.post(
                    f"{self.base_url}/analyze",
                    json=request_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"AI 분석 성공: {answer_text[:20]}...")
                    
                    # camelCase 응답을 snake_case로 변환
                    return {
                        'wrong_option_1': result.get('wrongOption1', ''),
                        'wrong_option_2': result.get('wrongOption2', ''),
                        'wrong_option_3': result.get('wrongOption3', ''),
                        'wrong_score_1': result.get('wrongScore1', 0),
                        'wrong_score_2': result.get('wrongScore2', 0),
                        'wrong_score_3': result.get('wrongScore3', 0),
                        'description': result.get('description', 'AI 분석 완료')
                    }
                elif response.status_code == 422:
                    # 검증 오류 - 상세 분석
                    try:
                        error_response = response.json()
                        error_detail = str(error_response.get('detail', ''))
                        
                        logger.warning(f"422 검증 오류: {error_detail}")
                        
                        # 모델에 없는 단어인지 확인
                        missing_word_keywords = [
                            '모델에 존재하지 않',
                            '모델에 없는',
                            'not in vocabulary',
                            'vocabulary',
                            '찾을 수 없습니다'
                        ]
                        
                        is_missing_word = any(keyword in error_detail.lower() for keyword in missing_word_keywords)
                        
                        if is_missing_word:
                            logger.warning(f"모델에 없는 단어 확인됨: {answer_text}")
                            return {
                                'status': 'missing_word',
                                'message': f'{answer_text}는 {MODEL_CONFIG["missing_words_marker"]}에 존재하지 않는 단어입니다',
                                'needs_training': True,
                                'answer_text': answer_text,
                                'original_error': error_detail
                            }
                        else:
                            # 다른 검증 오류 (필드 누락, 타입 오류 등)
                            logger.error(f"검증 오류 (모델 단어 외): {error_detail}")
                            return {
                                'status': 'validation_error',
                                'error': f'요청 검증 실패: {error_detail}',
                                'answer_text': answer_text
                            }
                            
                    except Exception as parse_error:
                        logger.error(f"422 응답 파싱 실패: {parse_error}")
                        logger.error(f"원본 응답: {response.text}")
                        
                        # 파싱 실패시 기본적으로 모델 누락으로 처리
                        return {
                            'status': 'missing_word',
                            'message': f'{answer_text}는 {MODEL_CONFIG["missing_words_marker"]}에 존재하지 않는 단어입니다 (응답 파싱 실패)',
                            'needs_training': True,
                            'answer_text': answer_text,
                            'original_error': 'JSON 파싱 실패'
                        }
                else:
                    logger.error(f"AI 분석 실패 (HTTP {response.status_code}): {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"AI 서비스 타임아웃 (시도 {attempt + 1}/{self.max_retries})")
            except Exception as e:
                logger.error(f"AI 분석 요청 오류 (시도 {attempt + 1}/{self.max_retries}): {e}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        logger.error(f"AI 분석 최종 실패: {answer_text}")
        return None
    
    def reload_model(self) -> bool:
        """AI 서비스 모델 리로드"""
        try:
            response = requests.post(
                f"{self.base_url}/model/reload",
                timeout=60  # 모델 로드는 시간이 걸림
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"모델 리로드 성공: {result}")
                return True
            else:
                logger.error(f"모델 리로드 실패: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"모델 리로드 요청 오류: {e}")
            return False
    
    def get_model_info(self) -> Optional[Dict]:
        """현재 모델 정보 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/model/info",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"모델 정보 조회 실패: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"모델 정보 조회 오류: {e}")
            return None
    
    def train_missing_words(self, words: List[str]) -> bool:
        """누락된 단어들을 모델에 학습"""
        try:
            request_data = {
                "words": words,
                "training_type": "incremental"  # 증분 학습
            }
            
            response = requests.post(
                f"{self.base_url}/model/train",
                json=request_data,
                timeout=300  # 모델 학습은 시간이 오래 걸림
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"단어 학습 성공: {result}")
                return True
            else:
                logger.error(f"단어 학습 실패: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"단어 학습 요청 오류: {e}")
            return False
    
    def batch_analyze_games(self, games: List[Dict]) -> List[Dict]:
        """게임들 일괄 분석"""
        results = []
        
        for game in games:
            try:
                game_id = game['game_id']
                game_seq = game['game_seq']
                answer_text = game['answer_text']
                
                logger.info(f"AI 분석 시작: {game_id}/{game_seq} - {answer_text}")
                
                # 개별 게임 분석 (실제 game_id, game_seq 전달)
                ai_result = self.analyze_game(answer_text, "NORMAL", game_id, game_seq)
                
                if ai_result:
                    if ai_result.get('status') == 'missing_word':
                        # 모델에 없는 단어
                        results.append({
                            'game_id': game_id,
                            'game_seq': game_seq,
                            'status': 'missing_word',
                            'description': ai_result['message'],
                            'needs_training': True,
                            'answer_text': answer_text,
                            'original_error': ai_result.get('original_error', '')
                        })
                    elif ai_result.get('status') == 'validation_error':
                        # 검증 오류
                        results.append({
                            'game_id': game_id,
                            'game_seq': game_seq,
                            'status': 'error',
                            'error': ai_result.get('error', '검증 실패'),
                            'answer_text': answer_text
                        })
                    elif 'wrong_option_1' in ai_result:
                        # 정상 분석 완료
                        results.append({
                            'game_id': game_id,
                            'game_seq': game_seq,
                            'status': 'success',
                            'ai_result': ai_result
                        })
                    else:
                        # 예상치 못한 응답 형식
                        results.append({
                            'game_id': game_id,
                            'game_seq': game_seq,
                            'status': 'error',
                            'error': '예상치 못한 응답 형식',
                            'ai_result': ai_result,
                            'answer_text': answer_text
                        })
                else:
                    # 분석 실패
                    results.append({
                        'game_id': game_id,
                        'game_seq': game_seq,
                        'status': 'error',
                        'error': 'AI 분석 실패'
                    })
                    
            except Exception as e:
                logger.error(f"게임 분석 처리 오류 {game.get('game_id')}/{game.get('game_seq')}: {e}")
                results.append({
                    'game_id': game.get('game_id'),
                    'game_seq': game.get('game_seq'),
                    'status': 'error',
                    'error': str(e)
                })
        
        return results