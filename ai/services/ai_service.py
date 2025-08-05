# ai/services/ai_service.py 수정
import os
import re
import random
import logging
import numpy as np
from typing import List, Dict, Optional
from konlpy.tag import Okt
from gensim.models import Word2Vec

logger = logging.getLogger(__name__)
okt = Okt()

# 난이도별 모델 저장
models = {
    'EASY': None,
    'NORMAL': None,
    'HARD': None,
    'EXPERT': None
}

def load_models() -> bool:
    """난이도별 모델 로드"""
    global models
    
    model_configs = {
        'EASY': {
            'path': os.getenv("EASY_MODEL_PATH", "../../docker/airflow/models/word2vec_easy.model"),
            'vocab_limit': 30000,
            'similarity_threshold': 0.3
        },
        'NORMAL': {
            'path': os.getenv("NORMAL_MODEL_PATH", "../../docker/airflow/models/word2vec_normal.model"),
            'vocab_limit': 50000,
            'similarity_threshold': 0.4
        },
        'HARD': {
            'path': os.getenv("HARD_MODEL_PATH", "../../docker/airflow/models/word2vec_hard.model"),
            'vocab_limit': 70000,
            'similarity_threshold': 0.5
        },
        'EXPERT': {
            'path': os.getenv("EXPERT_MODEL_PATH", "../../docker/airflow/models/word2vec_expert.model"),
            'vocab_limit': 100000,
            'similarity_threshold': 0.6
        }
    }
    
    loaded_count = 0
    
    for difficulty, config in model_configs.items():
        try:
            model_path = config['path']
            
            # 모델 파일이 없으면 기본 모델 사용
            if not os.path.exists(model_path):
                default_model_path = os.getenv("MODEL_PATH", "../../docker/airflow/models/word2vec_custom.model")
                if os.path.exists(default_model_path):
                    model_path = default_model_path
                    logger.warning(f"{difficulty} 전용 모델이 없어 기본 모델 사용: {model_path}")
                else:
                    logger.error(f"{difficulty} 모델 파일을 찾을 수 없습니다: {model_path}")
                    continue
            
            models[difficulty] = {
                'model': Word2Vec.load(model_path),
                'vocab_limit': config['vocab_limit'],
                'similarity_threshold': config['similarity_threshold']
            }
            
            logger.info(f"{difficulty} 모델 로드 완료: {model_path}")
            loaded_count += 1
            
        except Exception as e:
            logger.error(f"{difficulty} 모델 로드 실패: {str(e)}")
    
    # 최소 하나의 모델이라도 로드되면 성공
    if loaded_count > 0:
        logger.info(f"총 {loaded_count}개 난이도 모델 로드 완료")
        return True
    else:
        logger.error("모든 모델 로드 실패")
        return False

def get_model_for_difficulty(difficulty: str = 'NORMAL') -> Optional[Dict]:
    """난이도에 맞는 모델 반환"""
    if difficulty in models and models[difficulty]:
        return models[difficulty]
    
    # 요청한 난이도 모델이 없으면 사용 가능한 모델 중 하나 반환
    for diff, model_info in models.items():
        if model_info:
            logger.warning(f"요청 난이도 '{difficulty}' 모델이 없어 '{diff}' 모델 사용")
            return model_info
    
    return None

def filter_nouns(words: List[str]) -> List[str]:
    """명사 필터링"""
    valid_nouns = set()
    for word in words:
        if re.fullmatch(r'[가-힣]{2,}', word):
            try:
                pos = okt.pos(word, stem=True, norm=True)
                if len(pos) == 1 and pos[0][1] == 'Noun':
                    valid_nouns.add(word)
            except Exception:
                continue
    return list(valid_nouns)

def get_difficulty_specific_candidates(difficulty: str, all_candidates: List[tuple], answer_text: str) -> List[tuple]:
    """난이도별 후보 선택 전략"""
    
    if difficulty == 'EASY':
        # 초급: 유사도가 낮은 것들 위주 (더 쉬운 구분)
        filtered = [item for item in all_candidates if 0.1 <= item[1] <= 0.4]
        return sorted(filtered, key=lambda x: x[1])  # 유사도 낮은 순
        
    elif difficulty == 'NORMAL':
        # 중급: 적절한 유사도 범위
        filtered = [item for item in all_candidates if 0.2 <= item[1] <= 0.6]
        return filtered
        
    elif difficulty == 'HARD':
        # 고급: 유사도가 높은 것들 포함 (더 어려운 구분)
        filtered = [item for item in all_candidates if 0.3 <= item[1] <= 0.8]
        return sorted(filtered, key=lambda x: -x[1])  # 유사도 높은 순
        
    elif difficulty == 'EXPERT':
        # 전문가: 매우 높은 유사도 (가장 어려운 구분)
        filtered = [item for item in all_candidates if 0.5 <= item[1] <= 1.0]
        return sorted(filtered, key=lambda x: -x[1])  # 유사도 높은 순
        
    else:
        return all_candidates

def generate_wrong_options_with_difficulty(answer_text: str, difficulty: str = 'NORMAL') -> Dict:
    """난이도별 오답 옵션 생성"""
    try:
        if not answer_text or not isinstance(answer_text, str):
            logger.warning("빈 문자열 또는 유효하지 않은 타입의 answer_text가 입력됨")
            return {
                "status": "FAILED",
                "error": "정답 텍스트가 유효하지 않습니다."
            }

        # 난이도별 모델 가져오기
        model_info = get_model_for_difficulty(difficulty)
        if not model_info:
            return {
                "status": "FAILED",
                "error": f"'{difficulty}' 난이도 모델을 찾을 수 없습니다."
            }
        
        model = model_info['model']
        vocab_limit = model_info['vocab_limit']
        similarity_threshold = model_info['similarity_threshold']

        if answer_text not in model.wv.key_to_index:
            logger.warning(f"모델에 없는 단어: '{answer_text}' (난이도: {difficulty})")
            return {
                "status": "FAILED",
                "error": f"'{answer_text}'는 {difficulty} 모델에 존재하지 않습니다."
            }

        query_vec = model.wv[answer_text]
        vocab_words = list(model.wv.key_to_index)[:vocab_limit]
        candidate_words = [w for w in vocab_words if w != answer_text]
        nouns = filter_nouns(candidate_words)

        if len(nouns) < 3:
            logger.warning(f"후보 명사 부족: 총 {len(nouns)}개 (난이도: {difficulty})")
            return {
                "status": "FAILED",
                "error": f"후보 명사가 부족합니다. (난이도: {difficulty})"
            }

        # 유사도 계산
        vecs = model.wv[nouns]
        sims = np.dot(vecs, query_vec) / (np.linalg.norm(vecs, axis=1) * np.linalg.norm(query_vec) + 1e-10)
        sims = np.nan_to_num(sims, nan=0.0, posinf=0.0, neginf=0.0)

        # 난이도별 후보 필터링
        all_candidates = [(w, s) for w, s in zip(nouns, sims) if s >= similarity_threshold]
        difficulty_candidates = get_difficulty_specific_candidates(difficulty, all_candidates, answer_text)

        if len(difficulty_candidates) < 3:
            # 후보가 부족하면 전체 후보에서 선택
            logger.warning(f"난이도별 후보 부족, 전체 후보에서 선택 (난이도: {difficulty})")
            difficulty_candidates = all_candidates

        if len(difficulty_candidates) < 3:
            return {
                "status": "FAILED",
                "error": f"충분한 후보를 찾을 수 없습니다. (난이도: {difficulty})"
            }

        # 최종 3개 선택
        if difficulty == 'EASY':
            # 초급: 다양한 유사도 범위에서 선택
            selected = random.sample(difficulty_candidates[:min(10, len(difficulty_candidates))], 3)
        elif difficulty == 'EXPERT':
            # 전문가: 가장 유사도가 높은 것들 중에서 선택
            selected = difficulty_candidates[:3]
        else:
            # 중급, 고급: 적절히 섞어서 선택
            top_candidates = difficulty_candidates[:min(15, len(difficulty_candidates))]
            selected = random.sample(top_candidates, 3)

        # 점수 처리
        wrong_scores = []
        for word, score in selected:
            try:
                if isinstance(score, (int, float, np.integer, np.floating)):
                    if np.isnan(score) or np.isinf(score):
                        wrong_scores.append(0.0)
                    else:
                        float_score = float(score)
                        wrong_scores.append(round(float_score, 4))
                else:
                    wrong_scores.append(0.0)
            except Exception:
                wrong_scores.append(0.0)

        logger.info(f"난이도 '{difficulty}' AI 분석 완료: {[item[0] for item in selected]}")

        return {
            "status": "COMPLETED",
            "wrong_options": [item[0] for item in selected],
            "wrong_scores": wrong_scores,
            "difficulty_used": difficulty
        }

    except Exception as e:
        logger.error(f"generate_wrong_options_with_difficulty 함수에서 예외 발생 (난이도: {difficulty}): {e}", exc_info=True)
        return {
            "status": "FAILED",
            "error": f"알 수 없는 오류 (난이도: {difficulty}): {e}"
        }

# 기존 함수는 호환성을 위해 유지
def generate_wrong_options(answer_text: str, model: Word2Vec) -> Dict:
    """기존 호환성을 위한 함수"""
    return generate_wrong_options_with_difficulty(answer_text, 'NORMAL')

# 모듈 레벨에서 사용할 수 있도록 기본 모델 변수 유지
model = None

def load_model() -> bool:
    """기존 호환성을 위한 함수"""
    global model
    
    # 새로운 난이도별 모델 로드
    if load_models():
        # 기본 모델을 NORMAL 난이도 모델로 설정
        normal_model_info = get_model_for_difficulty('NORMAL')
        if normal_model_info:
            model = normal_model_info['model']
            return True
    
    # 기존 방식으로 폴백
    try:
        model_path = os.getenv("MODEL_PATH", "../../docker/airflow/models/word2vec_custom.model")
        if not os.path.exists(model_path):
            logger.error(f"모델 파일을 찾을 수 없습니다: {model_path}")
            return False
        
        model = Word2Vec.load(model_path)
        logger.info(f"기본 Word2Vec 모델 로드 완료: {model_path}")
        return True
    except Exception as e:
        logger.error(f"모델 로드 실패: {str(e)}")
        return False