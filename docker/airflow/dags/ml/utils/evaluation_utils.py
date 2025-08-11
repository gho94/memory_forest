# ml/utils/evaluation_utils.py
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from gensim.models import Word2Vec
import sys

sys.path.append('/opt/airflow/dags')
from common.constants import COMMON_EVALUATION_WORDS

class ModelEvaluator:
    """모델 평가 클래스"""
    
    def __init__(self):
        self.evaluation_criteria = {
            'min_vocabulary_size': 1000,
            'min_word_coverage_rate': 60.0,  # %
            'min_avg_similarity_score': 0.3
        }
    
    def evaluate_model(self, model_path: str, test_words: List[str] = None) -> Dict:
        """모델 종합 평가"""
        
        if test_words is None:
            test_words = COMMON_EVALUATION_WORDS
        
        try:
            model = Word2Vec.load(model_path)
            
            # 기본 정보
            vocabulary_size = len(model.wv.key_to_index)
            vector_size = model.wv.vector_size
            
            # 단어 커버리지 평가
            coverage_result = self._evaluate_word_coverage(model, test_words)
            
            # 유사도 평가
            similarity_result = self._evaluate_similarity_quality(model, test_words)
            
            # 의미적 일관성 평가
            consistency_result = self._evaluate_semantic_consistency(model)
            
            evaluation_result = {
                'vocabulary_size': vocabulary_size,
                'vector_size': vector_size,
                'word_coverage_rate': coverage_result['coverage_rate'],
                'covered_words': coverage_result['covered_words'],
                'missing_words': coverage_result['missing_words'],
                'avg_similarity_score': similarity_result['avg_score'],
                'similarity_details': similarity_result['details'],
                'semantic_consistency_score': consistency_result['score'],
                'evaluation_timestamp': self._get_current_timestamp()
            }
            
            logging.info(f"모델 평가 완료: 어휘수={vocabulary_size}, 커버리지={coverage_result['coverage_rate']:.1f}%")
            
            return evaluation_result
            
        except Exception as e:
            logging.error(f"모델 평가 실패: {e}")
            return {'error': str(e)}
    
    def _evaluate_word_coverage(self, model: Word2Vec, test_words: List[str]) -> Dict:
        """단어 커버리지 평가"""
        
        covered_words = []
        missing_words = []
        
        for word in test_words:
            if word in model.wv.key_to_index:
                covered_words.append(word)
            else:
                missing_words.append(word)
        
        coverage_rate = (len(covered_words) / len(test_words)) * 100
        
        return {
            'coverage_rate': coverage_rate,
            'covered_words': covered_words,
            'missing_words': missing_words,
            'total_test_words': len(test_words)
        }
    
    def _evaluate_similarity_quality(self, model: Word2Vec, test_words: List[str]) -> Dict:
        """유사도 품질 평가"""
        
        similarity_scores = []
        similarity_details = {}
        
        # 모델에 있는 테스트 단어들만 사용
        available_words = [word for word in test_words if word in model.wv.key_to_index]
        
        if len(available_words) < 2:
            return {
                'avg_score': 0.0,
                'details': {},
                'error': 'Not enough words in vocabulary'
            }
        
        # 단어 쌍들 간의 유사도 계산
        for i, word1 in enumerate(available_words):
            word_similarities = []
            
            # 상위 5개 유사 단어 찾기
            try:
                similar_words = model.wv.most_similar(word1, topn=5)
                
                for similar_word, similarity in similar_words:
                    word_similarities.append(similarity)
                    similarity_scores.append(similarity)
                
                similarity_details[word1] = {
                    'similar_words': similar_words,
                    'avg_similarity': np.mean(word_similarities) if word_similarities else 0.0
                }
                
            except Exception as e:
                logging.warning(f"단어 '{word1}' 유사도 계산 실패: {e}")
                similarity_details[word1] = {'error': str(e)}
        
        avg_score = np.mean(similarity_scores) if similarity_scores else 0.0
        
        return {
            'avg_score': float(avg_score),
            'details': similarity_details,
            'total_comparisons': len(similarity_scores)
        }
    
    def _evaluate_semantic_consistency(self, model: Word2Vec) -> Dict:
        """의미적 일관성 평가"""
        
        # 의미적으로 관련된 단어 그룹들
        semantic_groups = [
            ['가족', '부모', '아들', '딸'],
            ['음식', '밥', '빵', '우유'],
            ['감정', '기쁨', '슬픔', '화'],
            ['동물', '고양이', '개', '새'],
            ['색깔', '빨강', '파랑', '노랑']
        ]
        
        group_consistency_scores = []
        
        for group in semantic_groups:
            # 그룹 내 단어들이 모델에 있는지 확인
            available_words = [word for word in group if word in model.wv.key_to_index]
            
            if len(available_words) < 2:
                continue
            
            # 그룹 내 단어들 간의 평균 유사도 계산
            group_similarities = []
            
            for i, word1 in enumerate(available_words):
                for j, word2 in enumerate(available_words):
                    if i < j:  # 중복 방지
                        try:
                            similarity = model.wv.similarity(word1, word2)
                            group_similarities.append(similarity)
                        except Exception:
                            continue
            
            if group_similarities:
                group_avg = np.mean(group_similarities)
                group_consistency_scores.append(group_avg)
        
        overall_consistency = np.mean(group_consistency_scores) if group_consistency_scores else 0.0
        
        return {
            'score': float(overall_consistency),
            'evaluated_groups': len(group_consistency_scores),
            'total_groups': len(semantic_groups)
        }
    
    def check_evaluation_criteria(self, evaluation_result: Dict) -> bool:
        """평가 기준 통과 여부 확인"""
        
        if 'error' in evaluation_result:
            return False
        
        # 어휘 크기 기준
        vocab_size = evaluation_result.get('vocabulary_size', 0)
        if vocab_size < self.evaluation_criteria['min_vocabulary_size']:
            logging.warning(f"어휘 크기 기준 미달: {vocab_size} < {self.evaluation_criteria['min_vocabulary_size']}")
            return False
        
        # 단어 커버리지 기준
        coverage_rate = evaluation_result.get('word_coverage_rate', 0)
        if coverage_rate < self.evaluation_criteria['min_word_coverage_rate']:
            logging.warning(f"커버리지 기준 미달: {coverage_rate:.1f}% < {self.evaluation_criteria['min_word_coverage_rate']}%")
            return False
        
        # 평균 유사도 점수 기준
        avg_similarity = evaluation_result.get('avg_similarity_score', 0)
        if avg_similarity < self.evaluation_criteria['min_avg_similarity_score']:
            logging.warning(f"유사도 기준 미달: {avg_similarity:.3f} < {self.evaluation_criteria['min_avg_similarity_score']}")
            return False
        
        logging.info("모든 평가 기준 통과")
        return True
    
    def compare_models(self, old_model_path: str, new_model_path: str, 
                      test_words: List[str] = None) -> Dict:
        """두 모델 비교"""
        
        if test_words is None:
            test_words = COMMON_EVALUATION_WORDS
        
        try:
            old_eval = self.evaluate_model(old_model_path, test_words)
            new_eval = self.evaluate_model(new_model_path, test_words)
            
            if 'error' in old_eval or 'error' in new_eval:
                return {'error': 'One or both models failed evaluation'}
            
            comparison = {
                'vocabulary_improvement': new_eval['vocabulary_size'] - old_eval['vocabulary_size'],
                'coverage_improvement': new_eval['word_coverage_rate'] - old_eval['word_coverage_rate'],
                'similarity_improvement': new_eval['avg_similarity_score'] - old_eval['avg_similarity_score'],
                'old_model_stats': {
                    'vocabulary_size': old_eval['vocabulary_size'],
                    'coverage_rate': old_eval['word_coverage_rate'],
                    'similarity_score': old_eval['avg_similarity_score']
                },
                'new_model_stats': {
                    'vocabulary_size': new_eval['vocabulary_size'],
                    'coverage_rate': new_eval['word_coverage_rate'],
                    'similarity_score': new_eval['avg_similarity_score']
                },
                'recommendation': self._generate_recommendation(old_eval, new_eval)
            }
            
            return comparison
            
        except Exception as e:
            logging.error(f"모델 비교 실패: {e}")
            return {'error': str(e)}
    
    def _generate_recommendation(self, old_eval: Dict, new_eval: Dict) -> str:
        """모델 선택 추천"""
        
        new_passes = self.check_evaluation_criteria(new_eval)
        old_passes = self.check_evaluation_criteria(old_eval)
        
        if new_passes and not old_passes:
            return "NEW_MODEL_RECOMMENDED"
        elif old_passes and not new_passes:
            return "OLD_MODEL_RECOMMENDED"
        elif new_passes and old_passes:
            # 둘 다 통과하면 성능 비교
            improvements = 0
            
            if new_eval['vocabulary_size'] > old_eval['vocabulary_size']:
                improvements += 1
            if new_eval['word_coverage_rate'] > old_eval['word_coverage_rate']:
                improvements += 1
            if new_eval['avg_similarity_score'] > old_eval['avg_similarity_score']:
                improvements += 1
            
            if improvements >= 2:
                return "NEW_MODEL_RECOMMENDED"
            else:
                return "OLD_MODEL_RECOMMENDED"
        else:
            return "BOTH_MODELS_FAILED"
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generate_evaluation_report(self, evaluation_result: Dict) -> str:
        """평가 리포트 텍스트 생성"""
        
        if 'error' in evaluation_result:
            return f"모델 평가 실패: {evaluation_result['error']}"
        
        report = f"""
모델 평가 리포트
================

기본 정보:
- 어휘 크기: {evaluation_result['vocabulary_size']:,}개
- 벡터 크기: {evaluation_result['vector_size']}
- 평가 시간: {evaluation_result['evaluation_timestamp']}

성능 지표:
- 단어 커버리지: {evaluation_result['word_coverage_rate']:.1f}%
- 평균 유사도 점수: {evaluation_result['avg_similarity_score']:.3f}
- 의미적 일관성: {evaluation_result['semantic_consistency_score']:.3f}

커버리지 세부사항:
- 인식된 단어: {len(evaluation_result['covered_words'])}개
- 누락된 단어: {len(evaluation_result['missing_words'])}개
- 누락된 단어 목록: {', '.join(evaluation_result['missing_words'][:10])}

평가 기준 통과 여부: {'✓ 통과' if self.check_evaluation_criteria(evaluation_result) else '✗ 실패'}
        """
        
        return report.strip()