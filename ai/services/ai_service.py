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

# 단일 모델 저장
model = None

def load_model() -> bool:
    """Word2Vec 모델 로드"""
    global model
    
    try:
        model_path = os.getenv("MODEL_PATH", "/app/models/word2vec_custom.model")
        if not os.path.exists(model_path):
            logger.error(f"모델 파일을 찾을 수 없습니다: {model_path}")
            return False
        
        model = Word2Vec.load(model_path)
        logger.info(f"Word2Vec 모델 로드 완료: {model_path}")
        return True
        
    except Exception as e:
        logger.error(f"모델 로드 실패: {str(e)}")
        return False

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

def get_difficulty_candidates(difficulty: str, bins: Dict[str, List[tuple]]) -> List[tuple]:
    """난이도별 후보 선택 전략"""
    
    if difficulty == 'EASY':
        # 초급: 유사도가 낮은 것들 위주 (0.1~0.4 범위에서 3개)
        selected = []
        # 가장 낮은 유사도부터 선택
        for label in ['0.4~0.1', '0.6~0.4', '1.0~0.6']:
            if bins[label] and len(selected) < 3:
                # 유사도가 낮은 순으로 정렬해서 선택
                sorted_candidates = sorted(bins[label], key=lambda x: x[1])
                needed = min(3 - len(selected), len(sorted_candidates))
                selected.extend(sorted_candidates[:needed])
        return selected
        
    elif difficulty == 'NORMAL':
        # 중급: 각 구간에서 균등하게 1개씩 선택
        selected = []
        for label in ['0.4~0.1', '0.6~0.4', '1.0~0.6']:
            if bins[label]:
                # 각 구간에서 중간 정도 유사도 선택
                sorted_candidates = sorted(bins[label], key=lambda x: x[1])
                mid_idx = len(sorted_candidates) // 2
                selected.append(sorted_candidates[mid_idx])
        
        # 3개가 안 되면 나머지 구간에서 추가 선택
        if len(selected) < 3:
            all_remaining = []
            for label in ['0.4~0.1', '0.6~0.4', '1.0~0.6']:
                for candidate in bins[label]:
                    if candidate not in selected:
                        all_remaining.append(candidate)
            
            needed = 3 - len(selected)
            if all_remaining:
                selected.extend(random.sample(all_remaining, min(needed, len(all_remaining))))
        
        return selected
        
    elif difficulty == 'HARD':
        # 고급: 중간~높은 유사도 위주 (0.4~1.0 범위)
        selected = []
        for label in ['0.6~0.4', '1.0~0.6', '0.4~0.1']:
            if bins[label] and len(selected) < 3:
                # 유사도가 높은 순으로 정렬해서 선택
                sorted_candidates = sorted(bins[label], key=lambda x: -x[1])
                needed = min(3 - len(selected), len(sorted_candidates))
                selected.extend(sorted_candidates[:needed])
        return selected
        
    elif difficulty == 'EXPERT':
        # 전문가: 높은 유사도 위주 (0.6~1.0 범위)
        selected = []
        for label in ['1.0~0.6', '0.6~0.4', '0.4~0.1']:
            if bins[label] and len(selected) < 3:
                # 가장 높은 유사도부터 선택
                sorted_candidates = sorted(bins[label], key=lambda x: -x[1])
                needed = min(3 - len(selected), len(sorted_candidates))
                selected.extend(sorted_candidates[:needed])
        return selected
        
    else:
        # 기본값: NORMAL과 동일
        return get_difficulty_candidates('NORMAL', bins)

def generate_wrong_options_with_difficulty(answer_text: str, difficulty: str = 'NORMAL') -> Dict:
    """난이도별 오답 옵션 생성"""
    try:
        if not answer_text or not isinstance(answer_text, str):
            logger.warning("빈 문자열 또는 유효하지 않은 타입의 answer_text가 입력됨")
            return {
                "status": "FAILED",
                "error": "정답 텍스트가 유효하지 않습니다."
            }

        if not model:
            return {
                "status": "FAILED",
                "error": "모델이 로드되지 않았습니다."
            }

        if answer_text not in model.wv.key_to_index:
            logger.warning(f"모델에 없는 단어: '{answer_text}' (난이도: {difficulty})")
            return {
                "status": "FAILED",
                "error": f"'{answer_text}'는 모델에 존재하지 않습니다."
            }

        query_vec = model.wv[answer_text]
        vocab_words = list(model.wv.key_to_index)
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

        # 유사도 구간별로 분류
        bins = {'1.0~0.6': [], '0.6~0.4': [], '0.4~0.1': []}
        for w, s in zip(nouns, sims):
            if 0.6 <= s <= 1.0:
                bins['1.0~0.6'].append((w, s))
            elif 0.4 <= s < 0.6:
                bins['0.6~0.4'].append((w, s))
            elif 0.1 <= s < 0.4:
                bins['0.4~0.1'].append((w, s))

        # 난이도별 후보 선택
        selected = get_difficulty_candidates(difficulty, bins)

        # 후보가 부족한 경우 추가 선택
        if len(selected) < 3:
            all_candidates = []
            for bin_candidates in bins.values():
                all_candidates.extend(bin_candidates)
            
            # 이미 선택된 것 제외하고 추가 선택
            remaining = [c for c in all_candidates if c not in selected]
            if remaining:
                needed = 3 - len(selected)
                additional = random.sample(remaining, min(needed, len(remaining)))
                selected.extend(additional)

        if len(selected) < 3:
            return {
                "status": "FAILED",
                "error": f"충분한 후보를 찾을 수 없습니다. (난이도: {difficulty})"
            }

        # 최종 3개 선택 (혹시 3개보다 많으면 자르기)
        selected = selected[:3]

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

        logger.info(f"난이도 '{difficulty}' AI 분석 완료: {[item[0] for item in selected]} (유사도: {wrong_scores})")

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

# 기존 호환성을 위한 함수들 (더 이상 사용되지 않음)
def load_models() -> bool:
    """기존 호환성을 위한 함수 - 단일 모델 로드로 리다이렉트"""
    return load_model()

def get_model_for_difficulty(difficulty: str = 'NORMAL') -> Optional[Dict]:
    """기존 호환성을 위한 함수 - 전역 모델 반환"""
    global model
    if model:
        return {
            'model': model,
            'vocab_limit': 100000,  # 기본값
            'similarity_threshold': 0.1  # 기본값
        }
    return None