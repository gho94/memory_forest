def train_word2vec_with_failed_words(folder_date=None):
    """실패한 단어들을 고려한 Word2Vec 학습"""
    # 기존 word_train.py의 train_word2vec 함수 내용 + 개선사항
    import time
    import shutil
    import csv
    import optuna
    from gensim.models import Word2Vec
    from konlpy.tag import Okt
    from numpy import dot
    from numpy.linalg import norm
    import numpy as np
    import os
    import logging
    import requests
    from datetime import datetime
    import pandas as pd
    from ai.db.connection import get_db_connection
    from ai.services.ai_service import get_failed_words, evaluate_failed_words_coverage


    start_time = time.time()

    if folder_date is None:
        folder_date = datetime.now().strftime("%Y%m%d")

    csv_path = f"/opt/airflow/data/{folder_date}/sentence_level_cleaned.csv"
    model_save_path = "/opt/airflow/models/word2vec_custom.model"
    backup_model_path = "/opt/airflow/models/word2vec_custom_backup.model"
    train_stats_path = "/opt/airflow/data/word2vec_train_stats.csv"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

    df = pd.read_csv(csv_path)
    texts = df['text'].dropna().drop_duplicates()

    okt = Okt()

    def tokenize_text(text):
        allowed_pos = ['Noun', 'Verb', 'Adjective']
        return [word for word, pos in okt.pos(text, stem=True) if pos in allowed_pos]

    tokenized_sentences = [tokenize_text(line.strip()) for line in texts if line.strip()]
    all_tokens = [token for sentence in tokenized_sentences for token in sentence]
    total_token_count = len(all_tokens)

    # 실패한 단어들 조회
    failed_words = get_failed_words()
    
    def evaluate_failed_words_coverage(model):
        """실패한 단어들이 모델에 포함되었는지 확인"""
        if not failed_words:
            return 1.0
        
        covered_count = sum(1 for word in failed_words if word in model.wv.key_to_index)
        coverage_rate = covered_count / len(failed_words)
        logging.info(f"실패 단어 커버리지: {covered_count}/{len(failed_words)} ({coverage_rate:.2%})")
        return coverage_rate

    def average_cosine_similarity(model, words):
        vectors = [model.wv[word] for word in words if word in model.wv]
        if len(vectors) < 2:
            return 0.0
        similarities = []
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                sim = dot(vectors[i], vectors[j]) / (norm(vectors[i]) * norm(vectors[j]))
                similarities.append(sim)
        return round(np.mean(similarities), 4) if similarities else 0.0

    common_words = [
        "부모", "유럽", "기쁨", "고양이", "김치찌개", "출근", "축구", "칫솔",
        "냉장고", "선인장", "호랑이", "불교", "병원", "청바지", "졸업식", "독서",
        "봄비", "교과서", "간호사", "부산", "지하철", "박물관", "연극", "생일", "유치원"
    ]

    baseline_similarity = 0.0
    baseline_coverage = 0.0
    restored = False

    if os.path.exists(model_save_path):
        baseline_model = Word2Vec.load(model_save_path)
        baseline_similarity = average_cosine_similarity(baseline_model, common_words)
        baseline_coverage = evaluate_failed_words_coverage(baseline_model)
        logging.info(f"[기준 모델] 평균 유사도: {baseline_similarity}, 실패 단어 커버리지: {baseline_coverage:.2%}")
    else:
        logging.info("[기존 모델 없음 - 초기 학습]")

    def objective(trial):
        vector_size = trial.suggest_categorical("vector_size", [50, 100, 150, 200])
        window = trial.suggest_int("window", 3, 10)
        min_count = trial.suggest_int("min_count", 2, 8)  # 실패 단어 포함을 위해 min_count 낮춤
        epochs = trial.suggest_int("epochs", 10, 20)

        model = Word2Vec(
            sentences=tokenized_sentences,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=4,
            sg=1,
            epochs=epochs
        )
        
        # 평가 점수 = 유사도 점수 * 0.7 + 실패 단어 커버리지 * 0.3
        similarity_score = average_cosine_similarity(model, common_words)
        coverage_score = evaluate_failed_words_coverage(model)
        combined_score = similarity_score * 0.7 + coverage_score * 0.3
        
        return combined_score

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=15)  # 더 많은 시도

    best_params = study.best_params
    logging.info(f"[최적 파라미터]: {best_params}")

    model = Word2Vec(
        sentences=tokenized_sentences,
        vector_size=best_params["vector_size"],
        window=best_params["window"],
        min_count=best_params["min_count"],
        workers=4,
        sg=1,
        epochs=best_params["epochs"]
    )
    model.save(model_save_path)
    logging.info(f"Word2Vec 모델 저장 완료: {model_save_path}")

    new_similarity = average_cosine_similarity(model, common_words)
    new_coverage = evaluate_failed_words_coverage(model)
    new_combined_score = new_similarity * 0.7 + new_coverage * 0.3
    baseline_combined_score = baseline_similarity * 0.7 + baseline_coverage * 0.3

    logging.info(f"[새 모델] 유사도: {new_similarity}, 커버리지: {new_coverage:.2%}, 종합점수: {new_combined_score:.4f}")
    logging.info(f"[기준 모델] 종합점수: {baseline_combined_score:.4f}")

    if new_combined_score < baseline_combined_score:
        logging.info("[성능 저하] 백업 모델로 복원")
        if os.path.exists(backup_model_path):
            if os.path.exists(model_save_path):
                if os.path.isdir(model_save_path):
                    shutil.rmtree(model_save_path)
                else:
                    os.remove(model_save_path)
            shutil.copy2(backup_model_path, model_save_path)
            restored = True
    else:
        logging.info("[성능 향상 또는 유지] 백업 모델 갱신")
        if os.path.exists(backup_model_path):
            if os.path.isdir(backup_model_path):
                shutil.rmtree(backup_model_path)
            else:
                os.remove(backup_model_path)
        shutil.copy2(model_save_path, backup_model_path)

    # 통계 저장
    train_time_sec = round(time.time() - start_time, 2)
    train_date = datetime.now().strftime("%Y-%m-%d")
    train_time = datetime.now().strftime("%H:%M:%S")
    vocab_size = len(model.wv)
    vector_size = model.vector_size
    raw_word_count = model.corpus_total_words
    effective_word_count = model.corpus_count
    words_per_sec = int(effective_word_count / train_time_sec)
    alpha = model.alpha

    file_exists = os.path.exists(train_stats_path)
    with open(train_stats_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                'date', 'time', 'vocab_size', 'vector_size',
                'total_raw_words', 'effective_words', 'total_token_count',
                'avg_similarity', 'failed_words_coverage', 'combined_score',
                'train_time_sec', 'words_per_sec', 'alpha', 'model_path', 'restored'
            ])
        writer.writerow([
            train_date, train_time, vocab_size, vector_size,
            raw_word_count, effective_word_count, total_token_count,
            new_similarity if not restored else baseline_similarity,
            new_coverage if not restored else baseline_coverage,
            new_combined_score if not restored else baseline_combined_score,
            train_time_sec, words_per_sec, alpha, model_save_path,
            'yes' if restored else 'no'
        ])

def trigger_reanalysis():
    """모델 업데이트 후 실패한 게임들 재분석 트리거"""
    try:
        # 1. 실패한 단어들을 재분석 대상으로 표시
        failed_words = get_failed_words()
        if not failed_words:
            logging.info("재분석할 실패 단어가 없습니다.")
            return
            
        connection = get_db_connection()
        if not connection:
            logging.error("DB 연결 실패")
            return
            
        try:
            cursor = connection.cursor()
            placeholders = ','.join(['%s'] * len(failed_words))
            query = f"""
            UPDATE game_detail 
            SET ai_status = 'PENDING',
                description = '모델 업데이트 후 재분석 대상',
                ai_processed_at = NULL
            WHERE answer_text IN ({placeholders})
            AND ai_status = 'FAILED'
            """
            
            cursor.execute(query, failed_words)
            connection.commit()
            updated_count = cursor.rowcount
            logging.info(f"재분석 대상으로 표시된 게임: {updated_count}개")
            
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
        
        # 2. AI 서비스에 배치 분석 요청
        try:
            response = requests.post(
                f"{AI_SERVICE_URL}/batch/process",
                json={"limit": 100},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"배치 재분석 요청 성공: {result}")
            else:
                logging.error(f"배치 재분석 요청 실패: {response.status_code}, {response.text}")
                
        except requests.RequestException as e:
            logging.error(f"AI 서비스 요청 실패: {e}")
            
    except Exception as e:
        logging.error(f"재분석 트리거 실패: {e}")

def reload_ai_model():
    """AI 서비스 모델 리로드"""
    try:
        response = requests.post(f"{AI_SERVICE_URL}/reload-model", timeout=30)
        if response.status_code == 200:
            logging.info("AI 모델 리로드 성공")
        else:
            logging.error(f"AI 모델 리로드 실패: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"AI 모델 리로드 요청 실패: {e}")

# DAG 정의
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 6, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': False,
}

with DAG(
    dag_id='memory_forest_ml_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # 매일 오전 2시 실행
    start_date=pendulum.datetime(2025, 6, 17, tz=local_tz),
    catchup=False,
    max_active_runs=1,
    tags=['memory_forest', 'ml', 'word2vec', 'reanalysis'],
    description='Memory Forest ML Pipeline: 실패 단어 학습 및 재분석'
) as dag:

    # Task 1: 향상된 데이터 수집 (실패 단어 포함)
    crawl_task = PythonOperator(
        task_id='enhanced_crawl_and_preprocess',
        python_callable=enhanced_crawl_and_preprocess,
        op_kwargs={'folder_date': datetime.now().strftime("%Y%m%d")},
        execution_timeout=timedelta(hours=2)
    )

    # Task 2: 실패 단어를 고려한 모델 학습
    train_task = PythonOperator(
        task_id='train_word2vec_with_failed_words',
        python_callable=train_word2vec_with_failed_words,
        op_kwargs={'folder_date': datetime.now().strftime("%Y%m%d")},
        execution_timeout=timedelta(hours=1)
    )

    # Task 3: AI 서비스 모델 리로드
    reload_task = PythonOperator(
        task_id='reload_ai_model',
        python_callable=reload_ai_model,
        execution_timeout=timedelta(minutes=5)
    )

    # Task 4: 실패한 게임들 재분석 트리거
    reanalysis_task = PythonOperator(
        task_id='trigger_reanalysis',
        python_callable=trigger_reanalysis,
        execution_timeout=timedelta(minutes=10)
    )

    # Task 의존성 설정
    crawl_task >> train_task >> reload_task >> reanalysis_task
        