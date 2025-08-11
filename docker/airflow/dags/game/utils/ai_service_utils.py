# game/utils/ai_service_utils.py
import requests
import logging
import json
from typing import Dict, Optional
import sys

sys.path.append('/opt/airflow/dags')
from common.config import AI_SERVICE_URL, SPRING_BOOT_URL

class AIServiceClient:
    """AI 서비스 클라이언트"""
    
    def __init__(self):
        self.ai_service_url = AI_SERVICE_URL
        self.timeout = 30
    
    def analyze_game(self, game: Dict) -> Dict:
        """게임 AI 분석 요청"""
        
        try:
            # AI 서비스 호출을 위한 데이터 구성
            request_data = {
                'game_id': game['game_id'],
                'game_seq': game['game_seq'],
                'image_url': game.get('s3_url'),
                'answer_text': game.get('answer_text'),
                'file_name': game.get('original_name')
            }
            
            # AI 서비스 엔드포인트 호출
            response = requests.post(
                f"{self.ai_service_url}/api/analyze/game",
                json=request_data,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    return {
                        'status': 'success',
                        'data': {
                            'answer_text': result.get('answer_text'),
                            'wrong_option_1': result.get('wrong_options', [None, None, None])[0],
                            'wrong_option_2': result.get('wrong_options', [None, None, None])[1],
                            'wrong_option_3': result.get('wrong_options', [None, None, None])[2],
                            'wrong_score_1': result.get('wrong_scores', [0, 0, 0])[0],
                            'wrong_score_2': result.get('wrong_scores', [0, 0, 0])[1],
                            'wrong_score_3': result.get('wrong_scores', [0, 0, 0])[2]
                        }
                    }
                else:
                    return {
                        'status': 'error',
                        'error': result.get('error', 'AI 분석 실패')
                    }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'error',
                'error': 'AI 서비스 응답 시간 초과'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'error',
                'error': 'AI 서비스 연결 실패'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'AI 서비스 호출 예외: {str(e)}'
            }
    
    def check_service_health(self) -> Dict:
        """AI 서비스 상태 확인"""
        
        try:
            response = requests.get(
                f"{self.ai_service_url}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'http_status': response.status_code
                }
                
        except Exception as e:
            return {
                'status': 'unreachable',
                'error': str(e)
            }
    
    def get_model_info(self) -> Optional[Dict]:
        """현재 사용중인 모델 정보 조회"""
        
        try:
            response = requests.get(
                f"{self.ai_service_url}/api/model/info",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"모델 정보 조회 실패: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"모델 정보 조회 예외: {e}")
            return None
    
    def trigger_batch_processing(self, config: Dict) -> Dict:
        """배치 처리 트리거"""
        
        try:
            response = requests.post(
                f"{self.ai_service_url}/api/batch/trigger",
                json=config,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'batch_id': result.get('batch_id'),
                    'queued_count': result.get('queued_count', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def reload_model(self) -> Dict:
        """AI 서비스 모델 재로드 요청"""
        
        try:
            response = requests.post(
                f"{self.ai_service_url}/api/model/reload",
                timeout=60  # 모델 로딩은 시간이 걸릴 수 있음
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': '모델 재로드 완료'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class SpringBootClient:
    """Spring Boot 백엔드 클라이언트"""
    
    def __init__(self):
        self.backend_url = SPRING_BOOT_URL
        self.timeout = 30
    
    def check_service_health(self) -> Dict:
        """백엔드 서비스 상태 확인"""
        
        try:
            response = requests.get(
                f"{self.backend_url}/actuator/health",
                timeout=10
            )
            
            if response.status_code == 200:
                health_data = response.json()
                return {
                    'status': 'healthy',
                    'details': health_data
                }
            else:
                return {
                    'status': 'unhealthy',
                    'http_status': response.status_code
                }
                
        except Exception as e:
            return {
                'status': 'unreachable',
                'error': str(e)
            }
    
    def notify_game_completion(self, game_id: str) -> bool:
        """게임 완료 알림"""
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/game/completed",
                json={'game_id': game_id},
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"게임 완료 알림 실패: {e}")
            return False
    
    def get_pending_games_count(self) -> int:
        """대기중인 게임 수 조회"""
        
        try:
            response = requests.get(
                f"{self.backend_url}/api/game/pending/count",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('count', 0)
            else:
                return 0
                
        except Exception as e:
            logging.error(f"대기 게임 수 조회 실패: {e}")
            return 0
    
    def update_game_master_status(self, game_id: str, status: str) -> bool:
        """게임 마스터 상태 업데이트"""
        
        try:
            response = requests.put(
                f"{self.backend_url}/api/game/{game_id}/status",
                json={'status': status},
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"게임 마스터 상태 업데이트 실패: {e}")
            return False
    
    def get_system_metrics(self) -> Optional[Dict]:
        """시스템 메트릭 조회"""
        
        try:
            response = requests.get(
                f"{self.backend_url}/actuator/metrics",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logging.error(f"시스템 메트릭 조회 실패: {e}")
            return None