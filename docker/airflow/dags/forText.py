
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum
import os
import json
import pandas as pd
import re
import logging
import urllib.request
import urllib.parse
import requests
import mysql.connector
from mysql.connector import Error

# Airflow 설정
local_tz = pendulum.timezone("Asia/Seoul")
DATA_BASE_PATH = "/opt/airflow/data"

# DB 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'database': os.getenv('DB_NAME', 'memory_forest'),
    'user': os.getenv('DB_USER', 'kcc'),
    'password': os.getenv('DB_PASSWORD', 'kcc'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

# AI 서비스 URL
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://ai-service:8000')

# 네이버 API 설정
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logging.error(f"데이터베이스 연결 실패: {e}")
        return None

def get_failed_words():
    """분석 실패한 단어들을 DB에서 조회"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT DISTINCT answer_text, COUNT(*) as fail_count
        FROM game_detail 
        WHERE ai_status = 'FAILED' 
        AND answer_text IS NOT NULL 
        AND answer_text != ''
        AND description LIKE '%모델에 존재하지 않습니다%'
        GROUP BY answer_text
        ORDER BY fail_count DESC
        LIMIT 50
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        failed_words = [row['answer_text'] for row in results]
        logging.info(f"분석 실패한 단어 {len(failed_words)}개 조회: {failed_words}")
        return failed_words
        
    except Exception as e:
        logging.error(f"실패 단어 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def clean_html(text):
    return re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', text)).strip()

def split_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def enhanced_crawl_and_preprocess(folder_date=None):
    """실패한 단어들을 포함한 향상된 크롤링"""
    if folder_date is None:
        folder_date = datetime.now().strftime("%Y%m%d")
    
    # 1. 기존 실패한 단어들 조회
    failed_words = get_failed_words()
    
    # 2. 기본 감정 카테고리
    base_categories = [
        '기쁨', '웃음', '눈물', '외로움', '뿌듯함', '안도감', '걱정', '슬픔',
        '사랑', '설렘', '감동', '그리움', '허탈감', '추억', '희망', '정',
        '위로', '고마움', '반가움', '미소', '두려움', '따뜻함', '편안함',
        '불안', '긴장', '놀람', '공허함', '그윽함', '포근함', '친숙함'
    ]
    
    # 3. 실패한 단어들을 검색 키워드에 추가
    search_keywords = base_categories + failed_words
    
    results = []
    
    def getRequestUrl(url):
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", client_id)
        req.add_header("X-Naver-Client-Secret", client_secret)
        try:
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                return response.read().decode('utf-8')
        except Exception as e:
            logging.error(f"Error for URL: {url}\n{e}")
            return None

    def getNaverSearch(node, srcText, start, display):
        base = "https://openapi.naver.com/v1/search"
        node = f"/{node}.json"
        parameters = f"?query={urllib.parse.quote(srcText)}&start={start}&display={display}"
        url = base + node + parameters
        response = getRequestUrl(url)
        return json.loads(response) if response else None

    # 4. 향상된 크롤링 (실패한 단어들 우선 처리)
    for keyword in search_keywords:
        cnt = 0
        max_per_keyword = 200 if keyword in failed_words else 100  # 실패한 단어는 더 많이 수집
        
        jsonResponse = getNaverSearch('blog', keyword, 1, 100)
        if not jsonResponse:
            continue

        while jsonResponse and jsonResponse['display'] != 0 and cnt < max_per_keyword:
            for post in jsonResponse['items']:
                title = clean_html(post.get('title', ''))
                description = clean_html(post.get('description', ''))
                combined = f"{title} {description}".strip()
                
                # 실패한 단어가 포함된 문장 우선 수집
                for sent in split_sentences(combined):
                    if keyword in failed_words and keyword in sent:
                        results.append({'text': sent, 'keyword': keyword, 'priority': 'high'})
                    else:
                        results.append({'text': sent, 'keyword': keyword, 'priority': 'normal'})
                cnt += 1
            
            start = jsonResponse['start'] + jsonResponse['display']
            jsonResponse = getNaverSearch('blog', keyword, start, 100)

    # 5. 저장
    output_dir = os.path.join(DATA_BASE_PATH, folder_date)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sentence_level_cleaned.csv")

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"[향상된 전처리 완료] 저장 경로: {output_path}, 총 {len(results)}개 문장")
