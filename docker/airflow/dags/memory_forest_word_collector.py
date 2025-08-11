"""
Memory Forest 실패 단어 수집 및 학습 데이터 생성 DAG - 기존 코드 호환
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pendulum
import logging
import urllib.request
import urllib.parse
import json
import os
import re
import time
from typing import List, Dict

# 로컬 모듈 import
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DAG_DEFAULT_ARGS, SCHEDULES, DEFAULT_ARGS, LOCAL_TZ, API_CONFIG
from utils.database import db_manager

logger = logging.getLogger(__name__)

# 환경변수에서 Naver API 정보 가져오기
NAVER_CLIENT_ID = API_CONFIG['naver_client_id']
NAVER_CLIENT_SECRET = API_CONFIG['naver_client_secret']

def collect_failed_words(**context):
    """모델에 없어서 실패한 단어들을 DB에서 수집"""
    logger.info("=== 실패 단어 수집 시작 ===")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(buffered=True, dictionary=True)
            
            # 최근 7일간 "모델에 존재하지 않습니다" 오류로 실패한 단어들 수집
            query = """
            SELECT 
                answer_text,
                COUNT(*) as fail_count,
                MAX(ai_processed_at) as last_failure,
                MIN(ai_processed_at) as first_failure
            FROM game_detail 
            WHERE ai_status_code = 'B20008'
            AND description LIKE '%모델에 존재하지 않습니다%'
            AND ai_processed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            AND answer_text IS NOT NULL 
            AND answer_text != ''
            AND LENGTH(answer_text) >= 2  -- 너무 짧은 단어 제외
            AND LENGTH(answer_text) <= 10 -- 너무 긴 단어 제외
            GROUP BY answer_text
            HAVING fail_count >= 1  
            ORDER BY fail_count DESC, last_failure DESC
            LIMIT 50  -- 최대 50개 단어만 처리
            """
            
            cursor.execute(query)
            failed_words = cursor.fetchall()
            
            # 안전한 커서 닫기
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            cursor.close()
            
            if not failed_words:
                logger.info("📭 수집할 실패 단어가 없습니다.")
                return {"collected_words": [], "total_count": 0}
            
            # 결과 저장
            today = datetime.now(LOCAL_TZ).strftime("%Y%m%d")
            failed_words_dir = f"/opt/airflow/data/failed_words/{today}"
            os.makedirs(failed_words_dir, exist_ok=True)
            
            failed_words_file = os.path.join(failed_words_dir, "failed_words.json")
            with open(failed_words_file, 'w', encoding='utf-8') as f:
                json.dump(failed_words, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📊 실패 단어 수집 완료: {len(failed_words)}개")
            for word in failed_words[:10]:  # 상위 10개만 로깅
                logger.info(f"  '{word['answer_text']}': {word['fail_count']}회 실패")
            
            # XCom으로 전달
            context['task_instance'].xcom_push(
                key='failed_words_file', 
                value=failed_words_file
            )
            context['task_instance'].xcom_push(
                key='failed_words_count', 
                value=len(failed_words)
            )
            
            return {
                "collected_words": [w['answer_text'] for w in failed_words],
                "total_count": len(failed_words),
                "file_path": failed_words_file
            }
            
    except Exception as e:
        logger.error(f"❌ 실패 단어 수집 실패: {e}")
        return {"collected_words": [], "total_count": 0, "error": str(e)}

def getRequestUrl(url: str) -> str:
    """Naver API 요청"""
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        logger.error("❌ Naver API 키가 환경변수에 설정되지 않았습니다.")
        return None
    
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    req.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            return response.read().decode('utf-8')
    except Exception as e:
        logger.error(f"❌ API 요청 실패: {url} - {e}")
        return None

def getNaverSearch(node: str, query: str, start: int = 1, display: int = 100) -> Dict:
    """Naver 검색 API"""
    base = "https://openapi.naver.com/v1/search"
    node_path = f"/{node}.json"
    parameters = f"?query={urllib.parse.quote(query)}&start={start}&display={display}"
    url = base + node_path + parameters
    
    response = getRequestUrl(url)
    return json.loads(response) if response else None

def clean_html(text: str) -> str:
    """HTML 태그 제거 및 텍스트 정제"""
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<.*?>', '', text)
    # HTML 엔티티 제거
    text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
    # 특수문자 및 기호 정리
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def collect_word_contexts(**context):
    """실패한 단어들의 맥락 텍스트를 Naver API로 수집"""
    logger.info("=== 단어 맥락 텍스트 수집 시작 ===")
    
    # 이전 태스크에서 실패 단어 파일 경로 가져오기
    failed_words_file = context['task_instance'].xcom_pull(
        task_ids='collect_failed_words',
        key='failed_words_file'
    )
    failed_words_count = context['task_instance'].xcom_pull(
        task_ids='collect_failed_words',
        key='failed_words_count'
    )
    
    if not failed_words_file or not os.path.exists(failed_words_file):
        logger.warning("⚠️ 실패 단어 파일을 찾을 수 없습니다.")
        return {"collected_texts": 0, "total_words": 0}
    
    if failed_words_count == 0:
        logger.info("📭 처리할 실패 단어가 없습니다.")
        return {"collected_texts": 0, "total_words": 0}
    
    # API 키 확인
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        logger.error("❌ Naver API 키가 설정되지 않았습니다.")
        return {"collected_texts": 0, "total_words": 0, "error": "API 키 없음"}
    
    # 실패 단어 로드
    with open(failed_words_file, 'r', encoding='utf-8') as f:
        failed_words = json.load(f)
    
    today = datetime.now(LOCAL_TZ).strftime("%Y%m%d")
    contexts_dir = f"/opt/airflow/data/collected_texts/{today}"
    os.makedirs(contexts_dir, exist_ok=True)
    
    total_texts = 0
    successful_words = 0
    
    for word_info in failed_words:
        word = word_info['answer_text']
        logger.info(f"🔍 '{word}' 관련 텍스트 수집 중...")
        
        try:
            # 블로그 검색으로 다양한 맥락의 텍스트 수집
            search_result = getNaverSearch('blog', word, 1, 50)  # 50개씩 수집
            
            if not search_result or 'items' not in search_result:
                logger.warning(f"⚠️ '{word}' 검색 결과 없음")
                continue
            
            word_texts = []
            for item in search_result['items']:
                title = clean_html(item.get('title', ''))
                description = clean_html(item.get('description', ''))
                
                # 제목과 본문을 합쳐서 저장
                full_text = f"{title} {description}".strip()
                
                # 품질 필터링
                if (full_text and 
                    len(full_text) > 20 and  # 최소 20자
                    len(full_text) < 1000 and  # 최대 1000자
                    word in full_text):  # 실제로 단어가 포함되어 있는지 확인
                    
                    word_texts.append({
                        'word': word,
                        'text': full_text,
                        'source': 'naver_blog',
                        'title': title,
                        'fail_count': word_info['fail_count'],
                        'collected_at': datetime.now(LOCAL_TZ).isoformat()
                    })
            
            # 단어별로 파일 저장
            if word_texts:
                word_file = os.path.join(contexts_dir, f"{word}_contexts.json")
                with open(word_file, 'w', encoding='utf-8') as f:
                    json.dump(word_texts, f, indent=2, ensure_ascii=False)
                
                total_texts += len(word_texts)
                successful_words += 1
                logger.info(f"✅ '{word}': {len(word_texts)}개 텍스트 수집 완료")
            else:
                logger.warning(f"⚠️ '{word}': 유효한 텍스트가 없음")
            
            # API 요청 제한 준수 (초당 10회 제한)
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ '{word}' 텍스트 수집 실패: {e}")
            continue
    
    # 통합 파일 생성 (모든 텍스트를 하나로)
    all_texts_file = os.path.join(contexts_dir, "all_collected_texts.txt")
    with open(all_texts_file, 'w', encoding='utf-8') as f:
        for filename in os.listdir(contexts_dir):
            if filename.endswith('_contexts.json'):
                filepath = os.path.join(contexts_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as json_file:
                    texts = json.load(json_file)
                    for text_data in texts:
                        f.write(text_data['text'] + '\n')
    
    logger.info(f"🎉 텍스트 수집 완료: {successful_words}/{len(failed_words)}개 단어, 총 {total_texts}개 텍스트")
    
    # XCom으로 결과 전달
    context['task_instance'].xcom_push(
        key='collected_texts_file', 
        value=all_texts_file
    )
    context['task_instance'].xcom_push(
        key='collected_texts_count', 
        value=total_texts
    )
    
    return {
        "collected_texts": total_texts,
        "successful_words": successful_words,
        "total_words": len(failed_words),
        "texts_file": all_texts_file
    }

def prepare_training_data(**context):
    """수집된 텍스트를 Word2Vec 학습용 데이터로 전처리"""
    logger.info("=== 학습 데이터 전처리 시작 ===")
    
    # 이전 태스크에서 수집된 텍스트 파일 가져오기
    texts_file = context['task_instance'].xcom_pull(
        task_ids='collect_word_contexts',
        key='collected_texts_file'
    )
    texts_count = context['task_instance'].xcom_pull(
        task_ids='collect_word_contexts',
        key='collected_texts_count'
    )
    
    if not texts_file or not os.path.exists(texts_file) or texts_count == 0:
        logger.warning("⚠️ 전처리할 텍스트가 없습니다.")
        return {"processed_sentences": 0, "training_ready": False}
    
    try:
        # KoNLPy 형태소 분석을 위한 import
        from konlpy.tag import Okt
        okt = Okt()
        
        # 텍스트 읽기
        with open(texts_file, 'r', encoding='utf-8') as f:
            texts = f.readlines()
        
        logger.info(f"📖 원본 텍스트 {len(texts)}줄 로드 완료")
        
        # 형태소 분석 및 전처리
        processed_sentences = []
        
        for i, text in enumerate(texts):
            text = text.strip()
            if len(text) < 10:  # 너무 짧은 텍스트 제외
                continue
                
            try:
                # 형태소 분석 (명사, 동사, 형용사만 추출)
                pos_tags = okt.pos(text, stem=True, norm=True)
                words = [word for word, pos in pos_tags 
                        if pos in ['Noun', 'Verb', 'Adjective'] 
                        and len(word) >= 2]  # 2글자 이상만
                
                if len(words) >= 3:  # 최소 3개 단어 이상
                    processed_sentences.append(words)
                    
            except Exception as e:
                logger.warning(f"⚠️ 텍스트 처리 실패 ({i+1}번째): {e}")
                continue
                
            # 진행상황 로깅
            if (i + 1) % 100 == 0:
                logger.info(f"📊 진행상황: {i+1}/{len(texts)} 처리 완료")
        
        if not processed_sentences:
            logger.error("❌ 전처리된 문장이 없습니다.")
            return {"processed_sentences": 0, "training_ready": False}
        
        # 전처리된 데이터 저장
        today = datetime.now(LOCAL_TZ).strftime("%Y%m%d")
        training_dir = f"/opt/airflow/data/model_training/{today}"
        os.makedirs(training_dir, exist_ok=True)
        
        training_data_file = os.path.join(training_dir, "processed_sentences.json")
        with open(training_data_file, 'w', encoding='utf-8') as f:
            json.dump(processed_sentences, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 전처리 완료: {len(processed_sentences)}개 문장")
        
        # XCom으로 결과 전달
        context['task_instance'].xcom_push(
            key='training_data_file', 
            value=training_data_file
        )
        context['task_instance'].xcom_push(
            key='processed_sentences_count', 
            value=len(processed_sentences)
        )
        
        return {
            "processed_sentences": len(processed_sentences),
            "training_ready": True,
            "training_data_file": training_data_file
        }
        
    except ImportError:
        logger.error("❌ KoNLPy가 설치되지 않았습니다. requirements.txt에 konlpy를 추가하세요.")
        return {"processed_sentences": 0, "training_ready": False, "error": "KoNLPy 없음"}
    except Exception as e:
        logger.error(f"❌ 전처리 실패: {e}")
        return {"processed_sentences": 0, "training_ready": False, "error": str(e)}

# DAG 정의
word_collector_default_args = {
    **DEFAULT_ARGS,
    'start_date': datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    'retries': 2,  # 네트워크 오류 대비 재시도
    'retry_delay': timedelta(minutes=5),
}

word_collector_dag = DAG(
    'memory_forest_word_collector',
    default_args=word_collector_default_args,
    description='Memory Forest 실패 단어 수집 및 학습 데이터 생성',
    schedule_interval=SCHEDULES['word_collection'],  # 매일 새벽 2시 실행
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'word2vec', 'data-collection', 'naver-api']
)

# Task 정의
start_collection = DummyOperator(
    task_id='start_collection',
    dag=word_collector_dag
)

collect_failed_words_task = PythonOperator(
    task_id='collect_failed_words',
    python_callable=collect_failed_words,
    dag=word_collector_dag
)

collect_contexts_task = PythonOperator(
    task_id='collect_word_contexts',
    python_callable=collect_word_contexts,
    dag=word_collector_dag
)

prepare_training_task = PythonOperator(
    task_id='prepare_training_data',
    python_callable=prepare_training_data,
    dag=word_collector_dag
)

end_collection = DummyOperator(
    task_id='end_collection',
    dag=word_collector_dag
)

# Task 의존성
start_collection >> collect_failed_words_task >> collect_contexts_task >> prepare_training_task >> end_collection