# data/utils/crawling_utils.py
import requests
import logging
import time
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote
import sys

sys.path.append('/opt/airflow/dags')
from common.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, DATA_BASE_PATH

class NaverBlogCrawler:
    """네이버 블로그 크롤링 클래스"""
    
    def __init__(self):
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET
        self.base_url = "https://openapi.naver.com/v1/search/blog.json"
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
    def crawl_blogs(self, keywords: List[str], folder_date: str, 
                   failed_words: List[str] = None) -> List[str]:
        """키워드 리스트로 블로그 크롤링 실행"""
        
        all_sentences = []
        failed_words = failed_words or []
        
        logging.info(f"크롤링 시작: {len(keywords)}개 키워드")
        
        for keyword in keywords:
            try:
                # 실패한 단어는 더 많이 수집
                display_count = 50 if keyword in failed_words else 20
                sentences = self._crawl_by_keyword(keyword, display_count)
                all_sentences.extend(sentences)
                
                logging.info(f"키워드 '{keyword}': {len(sentences)}개 문장 수집")
                
                # API 호출 제한을 위한 딜레이
                time.sleep(0.1)
                
            except Exception as e:
                logging.error(f"키워드 '{keyword}' 크롤링 실패: {e}")
                continue
        
        # 수집된 데이터를 파일로 저장
        self._save_crawled_data(all_sentences, folder_date)
        
        logging.info(f"총 {len(all_sentences)}개 문장 수집 완료")
        return all_sentences
    
    def _crawl_by_keyword(self, keyword: str, display: int = 20) -> List[str]:
        """단일 키워드로 블로그 검색"""
        
        params = {
            'query': keyword,
            'display': display,
            'start': 1,
            'sort': 'date'
        }
        
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logging.warning(f"API 호출 실패: {response.status_code}")
                return []
            
            data = response.json()
            items = data.get('items', [])
            
            sentences = []
            for item in items:
                # 제목과 내용에서 텍스트 추출
                title = self._clean_text(item.get('title', ''))
                description = self._clean_text(item.get('description', ''))
                
                if title:
                    sentences.append(title)
                if description:
                    sentences.extend(self._split_sentences(description))
            
            return sentences
            
        except requests.exceptions.RequestException as e:
            logging.error(f"네트워크 오류: {e}")
            return []
        except Exception as e:
            logging.error(f"크롤링 오류: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """HTML 태그 및 특수 문자 제거"""
        import re
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # HTML 엔티티 디코딩
        html_entities = {
            '&lt;': '<', '&gt;': '>', '&amp;': '&',
            '&quot;': '"', '&#39;': "'", '&nbsp;': ' '
        }
        
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _split_sentences(self, text: str) -> List[str]:
        """텍스트를 문장 단위로 분할"""
        import re
        
        # 문장 끝 표시로 분할
        sentences = re.split(r'[.!?]+', text)
        
        # 빈 문장 제거 및 길이 필터링
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= 10 and len(sentence) <= 200:  # 적절한 길이의 문장만
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _save_crawled_data(self, sentences: List[str], folder_date: str):
        """크롤링된 데이터를 파일로 저장"""
        
        folder_path = os.path.join(DATA_BASE_PATH, folder_date)
        os.makedirs(folder_path, exist_ok=True)
        
        # 원본 데이터 저장
        raw_file_path = os.path.join(folder_path, 'crawled_sentences.txt')
        with open(raw_file_path, 'w', encoding='utf-8') as f:
            for sentence in sentences:
                f.write(sentence + '\n')
        
        # 메타데이터 저장
        metadata = {
            'crawl_date': datetime.now().isoformat(),
            'total_sentences': len(sentences),
            'file_path': raw_file_path
        }
        
        metadata_file_path = os.path.join(folder_path, 'crawl_metadata.json')
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"크롤링 데이터 저장 완료: {raw_file_path}")