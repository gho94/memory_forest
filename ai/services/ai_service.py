import os
import re
import random
import logging
import numpy as np
from typing import List, Dict
from konlpy.tag import Okt
from gensim.models import Word2Vec

logger = logging.getLogger(__name__)
okt = Okt()
model = None

def load_model() -> bool:
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

def generate_wrong_options(answer_text: str, model: Word2Vec, max_vocab: int = 50000) -> Dict:
    try:
        if not answer_text or not isinstance(answer_text, str):
            logger.warning("빈 문자열 또는 유효하지 않은 타입의 answer_text가 입력됨")
            return {
                "status": "FAILED",
                "error": "정답 텍스트가 유효하지 않습니다."
            }

        if answer_text not in model.wv.key_to_index:
            logger.warning(f"모델에 없는 단어: '{answer_text}'")
            return {
                "status": "FAILED",
                "error": f"'{answer_text}'는 모델에 존재하지 않습니다."
            }

        query_vec = model.wv[answer_text]
        vocab_words = list(model.wv.key_to_index)[:max_vocab]
        candidate_words = [w for w in vocab_words if w != answer_text]
        nouns = filter_nouns(candidate_words)

        if len(nouns) < 3:
            logger.warning(f"후보 명사 부족: 총 {len(nouns)}개")
            return {
                "status": "FAILED",
                "error": "후보 명사가 부족합니다."
            }

        vecs = model.wv[nouns]
        sims = np.dot(vecs, query_vec) / (np.linalg.norm(vecs, axis=1) * np.linalg.norm(query_vec) + 1e-10)
        sims = np.nan_to_num(sims, nan=0.0, posinf=0.0, neginf=0.0)

        bins = {
            'high': [],
            'medium': [],
            'low': []
        }

        for w, s in zip(nouns, sims):
            if 0.6 <= s <= 1.0:
                bins['high'].append((w, s))
            elif 0.4 <= s < 0.6:
                bins['medium'].append((w, s))
            elif 0.1 <= s < 0.4:
                bins['low'].append((w, s))

        selected = []
        for group_name in ['high', 'medium', 'low']:
            group = bins[group_name]
            if group:
                sorted_group = sorted(group, key=lambda x: -x[1])
                top_candidates = sorted_group[:min(5, len(sorted_group))]
                selected.append(random.choice(top_candidates))

        if len(selected) < 3:
            all_candidates = [(w, s) for w, s in zip(nouns, sims) if w not in [item[0] for item in selected]]
            if len(all_candidates) >= (3 - len(selected)):
                additional = random.sample(all_candidates, 3 - len(selected))
                selected.extend(additional)
            else:
                logger.warning("추가 후보 단어가 부족하여 3개 미만 선택됨")

        selected = selected[:3]

        # 수정된 유사도 점수 처리 부분
        similarity_scores = []
        for word, score in selected:
            try:
                # numpy 타입도 포함하여 숫자 타입 확인
                if isinstance(score, (int, float, np.integer, np.floating)):
                    if np.isnan(score) or np.isinf(score):
                        logger.warning(f"유효하지 않은 유사도 값 (NaN/Inf): {score}, 기본값 0.0으로 대체")
                        similarity_scores.append(0.0)
                    else:
                        # numpy 타입을 Python float로 변환
                        float_score = float(score)
                        similarity_scores.append(round(float_score, 4))
                        logger.info(f"유사도 점수 정상 처리: {word} -> {round(float_score, 4)}")
                else:
                    logger.warning(f"유효하지 않은 유사도 타입: {type(score)}, 값: {score}, 기본값 0.0으로 대체")
                    similarity_scores.append(0.0)
            except Exception as e:
                logger.error(f"유사도 점수 처리 중 예외 발생: {e}")
                similarity_scores.append(0.0)

        return {
            "status": "COMPLETED",
            "wrong_options": [item[0] for item in selected],
            "similarity_scores": similarity_scores
        }

    except Exception as e:
        logger.error(f"generate_wrong_options 함수에서 예외 발생: {e}", exc_info=True)
        return {
            "status": "FAILED",
            "error": f"알 수 없는 오류: {e}"
        }