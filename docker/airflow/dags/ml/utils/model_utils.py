# ml/utils/model_utils.py
import os
import logging
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from gensim.models import Word2Vec
import sys

sys.path.append('/opt/airflow/dags')
from common.config import DATA_BASE_PATH, MODEL_SAVE_PATH, BACKUP_MODEL_PATH
from common.database import DatabaseManager, execute_query

class ModelManager:
    """Word2Vec 모델 관리 클래스"""
    
    def __init__(self):
        self.model_path = MODEL_SAVE_PATH
        self.backup_path = BACKUP_MODEL_PATH
        
    def check_available_training_data(self) -> Dict:
        """학습 가능한 데이터 확인"""
        
        data_info = {
            'has_data': False,
            'total_sentences': 0,
            'total_files': 0,
            'date_folders': [],
            'latest_folder': None
        }
        
        try:
            if not os.path.exists(DATA_BASE_PATH):
                return data_info
            
            # 날짜 폴더들 확인
            date_folders = []
            for folder_name in os.listdir(DATA_BASE_PATH):
                folder_path = os.path.join(DATA_BASE_PATH, folder_name)
                if os.path.isdir(folder_path):
                    processed_file = os.path.join(folder_path, 'processed_sentences.txt')
                    if os.path.exists(processed_file):
                        date_folders.append(folder_name)
            
            if not date_folders:
                return data_info
            
            # 최신 폴더 찾기
            date_folders.sort(reverse=True)
            latest_folder = date_folders[0]
            
            # 총 문장 수 계산
            total_sentences = 0
            for folder_name in date_folders[:5]:  # 최근 5개 폴더만 사용
                file_path = os.path.join(DATA_BASE_PATH, folder_name, 'processed_sentences.txt')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        sentences = sum(1 for line in f if line.strip())
                        total_sentences += sentences
                except Exception as e:
                    logging.warning(f"파일 읽기 실패 {file_path}: {e}")
            
            data_info.update({
                'has_data': total_sentences > 0,
                'total_sentences': total_sentences,
                'total_files': len(date_folders),
                'date_folders': date_folders[:5],
                'latest_folder': latest_folder
            })
            
        except Exception as e:
            logging.error(f"데이터 확인 중 오류: {e}")
        
        return data_info
    
    def calculate_data_quality_score(self, data_info: Dict) -> float:
        """데이터 품질 점수 계산"""
        
        score = 0.0
        
        # 문장 수에 따른 점수 (최대 50점)
        sentence_count = data_info.get('total_sentences', 0)
        if sentence_count >= 10000:
            score += 50
        elif sentence_count >= 5000:
            score += 40
        elif sentence_count >= 2000:
            score += 30
        elif sentence_count >= 1000:
            score += 20
        elif sentence_count >= 500:
            score += 10
        
        # 파일 수에 따른 점수 (최대 30점)
        file_count = data_info.get('total_files', 0)
        if file_count >= 7:
            score += 30
        elif file_count >= 5:
            score += 25
        elif file_count >= 3:
            score += 20
        elif file_count >= 1:
            score += 10
        
        # 최신성 점수 (최대 20점)
        latest_folder = data_info.get('latest_folder')
        if latest_folder:
            try:
                latest_date = datetime.strptime(latest_folder, '%Y%m%d')
                days_old = (datetime.now() - latest_date).days
                
                if days_old <= 1:
                    score += 20
                elif days_old <= 3:
                    score += 15
                elif days_old <= 7:
                    score += 10
                elif days_old <= 14:
                    score += 5
            except:
                pass
        
        return min(score, 100.0)
    
    def backup_current_model(self) -> bool:
        """현재 모델을 백업"""
        
        try:
            if os.path.exists(self.model_path):
                # 백업 디렉토리 생성
                backup_dir = os.path.dirname(self.backup_path)
                os.makedirs(backup_dir, exist_ok=True)
                
                # 모델 파일 복사
                shutil.copy2(self.model_path, self.backup_path)
                
                logging.info(f"모델 백업 완료: {self.backup_path}")
                return True
            else:
                logging.warning("백업할 모델이 존재하지 않습니다.")
                return True  # 첫 번째 학습인 경우
                
        except Exception as e:
            logging.error(f"모델 백업 실패: {e}")
            return False
    
    def train_word2vec_model(self, params: Dict) -> Dict:
        """Word2Vec 모델 학습"""
        
        start_time = datetime.now()
        
        try:
            # 학습 데이터 로드
            sentences = self._load_training_sentences()
            
            if not sentences:
                return {'success': False, 'error': 'No training sentences found'}
            
            logging.info(f"학습 데이터 로드 완료: {len(sentences)}개 문장")
            
            # Word2Vec 모델 생성 및 학습
            model = Word2Vec(
                sentences=sentences,
                vector_size=params.get('vector_size', 100),
                window=params.get('window', 5),
                min_count=params.get('min_count', 2),
                workers=params.get('workers', 4),
                epochs=params.get('epochs', 10),
                sg=params.get('sg', 1)
            )
            
            # 모델 저장
            model_dir = os.path.dirname(self.model_path)
            os.makedirs(model_dir, exist_ok=True)
            
            model.save(self.model_path)
            
            end_time = datetime.now()
            training_time = (end_time - start_time).total_seconds()
            
            result = {
                'success': True,
                'model_path': self.model_path,
                'training_time': training_time,
                'vocabulary_size': len(model.wv.key_to_index),
                'total_sentences': len(sentences),
                'parameters': params,
                'trained_at': end_time.isoformat()
            }
            
            logging.info(f"모델 학습 완료: 어휘 크기 {result['vocabulary_size']}")
            
            return result
            
        except Exception as e:
            logging.error(f"모델 학습 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_training_sentences(self) -> List[List[str]]:
        """학습용 문장들 로드"""
        
        data_info = self.check_available_training_data()
        
        if not data_info['has_data']:
            return []
        
        sentences = []
        
        # 최근 5개 폴더의 데이터 사용
        for folder_name in data_info['date_folders']:
            file_path = os.path.join(DATA_BASE_PATH, folder_name, 'processed_sentences.txt')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            words = line.split()
                            if len(words) >= 2:  # 최소 2개 단어
                                sentences.append(words)
                                
            except Exception as e:
                logging.warning(f"파일 로드 실패 {file_path}: {e}")
                continue
        
        return sentences
    
    def deploy_new_model(self) -> Dict:
        """새 모델 배포"""
        
        try:
            if not os.path.exists(self.model_path):
                return {'success': False, 'error': 'Trained model not found'}
            
            # 모델 로드 테스트
            try:
                model = Word2Vec.load(self.model_path)
                vocab_size = len(model.wv.key_to_index)
            except Exception as e:
                return {'success': False, 'error': f'Model load failed: {str(e)}'}
            
            # AI 서비스에 모델 업데이트 알림 (있다면)
            # self._notify_ai_service_model_update()
            
            result = {
                'success': True,
                'model_path': self.model_path,
                'vocabulary_size': vocab_size,
                'deployed_at': datetime.now().isoformat()
            }
            
            logging.info(f"모델 배포 완료: 어휘 크기 {vocab_size}")
            
            return result
            
        except Exception as e:
            logging.error(f"모델 배포 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def rollback_to_backup(self) -> Dict:
        """백업 모델로 롤백"""
        
        try:
            if not os.path.exists(self.backup_path):
                return {'success': False, 'error': 'Backup model not found'}
            
            # 백업 모델을 현재 모델로 복사
            shutil.copy2(self.backup_path, self.model_path)
            
            # 롤백된 모델 정보
            model = Word2Vec.load(self.model_path)
            vocab_size = len(model.wv.key_to_index)
            
            result = {
                'success': True,
                'model_path': self.model_path,
                'vocabulary_size': vocab_size,
                'rolled_back_at': datetime.now().isoformat()
            }
            
            logging.info(f"모델 롤백 완료: 어휘 크기 {vocab_size}")
            
            return result
            
        except Exception as e:
            logging.error(f"모델 롤백 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_vocabulary_coverage(self) -> Dict:
        """현재 모델의 어휘 커버리지 확인"""
        
        try:
            if not os.path.exists(self.model_path):
                return {'vocabulary': set(), 'size': 0}
            
            model = Word2Vec.load(self.model_path)
            vocabulary = set(model.wv.key_to_index.keys())
            
            return {
                'vocabulary': vocabulary,
                'size': len(vocabulary)
            }
            
        except Exception as e:
            logging.error(f"어휘 확인 실패: {e}")
            return {'vocabulary': set(), 'size': 0}
    
    def save_training_report(self, report: Dict):
        """학습 리포트 저장"""
        
        try:
            # 리포트 저장 디렉토리
            report_dir = os.path.join(os.path.dirname(self.model_path), 'reports')
            os.makedirs(report_dir, exist_ok=True)
            
            # 파일명에 날짜 포함
            report_filename = f"training_report_{report['execution_date'].replace('-', '')}.json"
            report_path = os.path.join(report_dir, report_filename)
            
            # JSON으로 저장
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logging.info(f"학습 리포트 저장: {report_path}")
            
        except Exception as e:
            logging.error(f"리포트 저장 실패: {e}")
    
    def get_model_info(self) -> Optional[Dict]:
        """현재 모델 정보 조회"""
        
        try:
            if not os.path.exists(self.model_path):
                return None
            
            model = Word2Vec.load(self.model_path)
            
            return {
                'vocabulary_size': len(model.wv.key_to_index),
                'vector_size': model.wv.vector_size,
                'model_path': self.model_path,
                'file_size': os.path.getsize(self.model_path),
                'last_modified': datetime.fromtimestamp(
                    os.path.getmtime(self.model_path)
                ).isoformat()
            }
            
        except Exception as e:
            logging.error(f"모델 정보 조회 실패: {e}")
            return None