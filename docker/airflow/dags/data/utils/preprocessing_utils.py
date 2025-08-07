# data/utils/preprocessing_utils.py
import os
import json
import logging
import re
from typing import List, Dict, Optional
from collections import Counter
import sys

sys.path.append('/opt/airflow/dags')
from common.config import DATA_BASE_PATH

class TextPreprocessor:
    """텍스트 전처리 클래스"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
        
    def process_crawled_data(self, folder_date: str) -> Optional[Dict]:
        """크롤링된 데이터 전처리"""
        
        folder_path = os.path.join(DATA_BASE_PATH, folder_date)
        raw_file_path = os.path.join(folder_path, 'crawled_sentences.txt')
        
        if not os.path.exists(raw_file_path):
            logging.error(f"크롤링 파일을 찾을 수 없습니다: {raw_file_path}")
            return None
        
        # 원본 데이터 로드
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            sentences = [line.strip() for line in f if line.strip()]
        
        logging.info(f"원본 문장 수: {len(sentences)}")
        
        # 전처리 실행
        processed_sentences = []
        unique_words = set()
        
        for sentence in sentences:
            processed = self._preprocess_sentence(sentence)
            if processed:
                processed_sentences.append(processed)
                # 단어 추출
                words = processed.split()
                unique_words.update(words)
        
        # 전처리된 데이터 저장
        processed_file_path = os.path.join(folder_path, 'processed_sentences.txt')
        with open(processed_file_path, 'w', encoding='utf-8') as f:
            for sentence in processed_sentences:
                f.write(sentence + '\n')
        
        # 통계 정보 계산
        total_length = sum(len(s) for s in processed_sentences)
        avg_length = total_length / len(processed_sentences) if processed_sentences else 0
        
        # 처리 결과 저장
        result = {
            'processed_count': len(processed_sentences),
            'unique_words': len(unique_words),
            'avg_length': round(avg_length, 2),
            'processed_file_path': processed_file_path
        }
        
        # 메타데이터 저장
        self._save_processing_metadata(folder_path, result, unique_words)
        
        logging.info(f"전처리 완료: {result}")
        return result
    
    def _preprocess_sentence(self, sentence: str) -> Optional[str]:
        """개별 문장 전처리"""
        
        # 1. 기본 정제
        sentence = sentence.strip()
        if len(sentence) < 5:
            return None
        
        # 2. 불필요한 문자 제거
        sentence = re.sub(r'[^\w\s가-힣]', ' ', sentence)
        sentence = re.sub(r'\s+', ' ', sentence)
        
        # 3. 영어/숫자만 있는 문장 제외
        korean_chars = re.findall(r'[가-힣]', sentence)
        if len(korean_chars) < 3:
            return None
        
        # 4. 불용어 제거
        words = sentence.split()
        filtered_words = [word for word in words if word not in self.stopwords]
        
        if len(filtered_words) < 2:
            return None
        
        return ' '.join(filtered_words)
    
    def _load_stopwords(self) -> set:
        """불용어 목록 로드"""
        # 기본 불용어 (실제 서비스에서는 파일에서 로드)
        stopwords = {
            '그리고', '그런데', '하지만', '그러나', '또한', '따라서',
            '이제', '이미', '아직', '벌써', '이번', '다음', '지난',
            '정말', '너무', '매우', '아주', '완전', '진짜', '좀',
            '것', '수', '때', '곳', '더', '덜', '좀', '뭔가', '뭔',
            '어떤', '어떻게', '왜', '언제', '어디서', '무엇',
            '있다', '없다', '이다', '아니다', '되다', '하다'
        }
        return stopwords
    
    def _save_processing_metadata(self, folder_path: str, result: Dict, unique_words: set):
        """전처리 메타데이터 저장"""
        
        # 단어 빈도 계산 (상위 100개)
        word_frequency = Counter()
        
        processed_file_path = result['processed_file_path']
        with open(processed_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                words = line.strip().split()
                word_frequency.update(words)
        
        top_words = dict(word_frequency.most_common(100))
        
        metadata = {
            'processing_date': os.path.basename(folder_path),
            'statistics': result,
            'top_words': top_words,
            'unique_word_count': len(unique_words),
            'sample_sentences': self._get_sample_sentences(processed_file_path, 10)
        }
        
        metadata_file_path = os.path.join(folder_path, 'processing_metadata.json')
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _get_sample_sentences(self, file_path: str, count: int) -> List[str]:
        """샘플 문장 추출"""
        with open(file_path, 'r', encoding='utf-8') as f:
            sentences = f.readlines()
        
        # 적절한 길이의 문장들을 샘플로 선택
        sample_sentences = []
        for sentence in sentences[:count*3]:  # 여유롭게 읽어서
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 100:  # 적절한 길이
                sample_sentences.append(sentence)
                if len(sample_sentences) >= count:
                    break
        
        return sample_sentences
    
    def validate_processed_data(self, folder_date: str) -> Dict:
        """전처리된 데이터 검증"""
        
        folder_path = os.path.join(DATA_BASE_PATH, folder_date)
        processed_file_path = os.path.join(folder_path, 'processed_sentences.txt')
        
        if not os.path.exists(processed_file_path):
            return {'valid': False, 'reason': 'processed file not found'}
        
        # 파일 읽기
        with open(processed_file_path, 'r', encoding='utf-8') as f:
            sentences = [line.strip() for line in f if line.strip()]
        
        # 검증 기준
        validation_result = {
            'valid': True,
            'sentence_count': len(sentences),
            'avg_length': sum(len(s) for s in sentences) / len(sentences) if sentences else 0,
            'issues': []
        }
        
        # 최소 문장 수 체크
        if len(sentences) < 1000:
            validation_result['issues'].append(f'문장 수 부족: {len(sentences)} < 1000')
        
        # 평균 길이 체크
        if validation_result['avg_length'] < 10:
            validation_result['issues'].append(f'평균 문장 길이 부족: {validation_result["avg_length"]:.1f} < 10')
        
        # 중복 문장 비율 체크
        unique_sentences = set(sentences)
        duplicate_ratio = (len(sentences) - len(unique_sentences)) / len(sentences) * 100
        if duplicate_ratio > 30:
            validation_result['issues'].append(f'중복 문장 비율 높음: {duplicate_ratio:.1f}% > 30%')
        
        validation_result['valid'] = len(validation_result['issues']) == 0
        
        return validation_result