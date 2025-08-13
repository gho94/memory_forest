"""
텍스트 처리 유틸리티
단어 정제, 검증 등의 기능
"""

import re
import logging
from typing import List, Set, Dict
from konlpy.tag import Okt

logger = logging.getLogger(__name__)

class TextProcessor:
    """텍스트 처리 및 단어 분석"""
    
    def __init__(self):
        try:
            self.okt = Okt()
            logger.info("형태소 분석기 초기화 완료")
        except Exception as e:
            logger.error(f"형태소 분석기 초기화 실패: {e}")
            self.okt = None
    
    def is_valid_korean_word(self, word: str) -> bool:
        """유효한 한국어 단어인지 확인"""
        if not word or len(word) < 2:
            return False
        
        # 한글만 포함하는지 확인
        if not re.fullmatch(r'[가-힣]+', word):
            return False
        
        # 형태소 분석으로 명사인지 확인
        if self.okt:
            try:
                pos_tags = self.okt.pos(word, stem=True, norm=True)
                # 단일 명사인지 확인
                if len(pos_tags) == 1 and pos_tags[0][1] == 'Noun':
                    return True
            except Exception as e:
                logger.warning(f"형태소 분석 실패 '{word}': {e}")
        
        return False
    
    def extract_nouns_from_text(self, text: str) -> List[str]:
        """텍스트에서 명사 추출"""
        if not text or not self.okt:
            return []
        
        try:
            nouns = self.okt.nouns(text)
            # 유효한 명사만 필터링
            valid_nouns = [
                noun for noun in nouns 
                if self.is_valid_korean_word(noun)
            ]
            return valid_nouns
        except Exception as e:
            logger.error(f"명사 추출 실패: {e}")
            return []
    
    def clean_word_list(self, words: List[str]) -> List[str]:
        """단어 목록 정제"""
        cleaned = []
        seen = set()
        
        for word in words:
            if not word:
                continue
                
            # 공백 제거
            word = word.strip()
            
            # 유효성 검사
            if self.is_valid_korean_word(word):
                # 중복 제거
                if word not in seen:
                    cleaned.append(word)
                    seen.add(word)
        
        return cleaned
    
    def prepare_training_sentences(self, words: List[str]) -> List[List[str]]:
        """단어들을 학습용 문장으로 변환"""
        sentences = []
        
        # 개별 단어를 단일 요소 문장으로
        for word in words:
            if self.is_valid_korean_word(word):
                sentences.append([word])
        
        # 유사한 의미의 단어들을 그룹화하여 문장 생성
        # (실제로는 더 복잡한 로직이 필요하지만 기본 구현)
        if len(words) >= 2:
            # 2-3개 단어로 구성된 문장들 생성
            for i in range(0, len(words), 2):
                if i + 1 < len(words):
                    sentence = [words[i], words[i + 1]]
                    if all(self.is_valid_korean_word(w) for w in sentence):
                        sentences.append(sentence)
        
        return sentences
    
    def validate_answer_text(self, answer_text: str) -> Dict:
        """정답 텍스트 유효성 검증"""
        result = {
            'is_valid': False,
            'word': answer_text.strip(),
            'issues': []
        }
        
        word = result['word']
        
        # 기본 검증
        if not word:
            result['issues'].append('빈 문자열')
            return result
        
        if len(word) < 2:
            result['issues'].append('너무 짧음 (2글자 이상 필요)')
            return result
        
        if len(word) > 10:
            result['issues'].append('너무 김 (10글자 이하 권장)')
        
        # 한글 검증
        if not re.fullmatch(r'[가-힣]+', word):
            result['issues'].append('한글이 아닌 문자 포함')
            return result
        
        # 형태소 분석
        if self.okt:
            try:
                pos_tags = self.okt.pos(word, stem=True, norm=True)
                if not any(tag[1] == 'Noun' for tag in pos_tags):
                    result['issues'].append('명사가 아님')
                elif len(pos_tags) > 1:
                    result['issues'].append('복합어 (단일 명사 권장)')
            except Exception as e:
                result['issues'].append(f'형태소 분석 실패: {e}')
        
        # 유효성 최종 판단
        result['is_valid'] = len(result['issues']) == 0
        
        return result