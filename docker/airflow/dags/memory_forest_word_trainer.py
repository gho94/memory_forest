"""
Memory Forest Word2Vec 모델 재학습 DAG
수집된 학습 데이터로 Word2Vec 모델을 재학습하고 성능 비교 후 교체
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import pendulum
import logging
import json
import os
import shutil
import time
import csv
import requests
from typing import Dict, List

# 로컬 모듈 import
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DAG_DEFAULT_ARGS, AI_SERVICE_CONFIG
from utils.database import db_manager

local_tz = pendulum.timezone("Asia/Seoul")
logger = logging.getLogger(__name__)

# AI 서비스 URL (.env 파일에서 가져옴)
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")

def check_training_data_available(**context):
    """학습 데이터가 준비되었는지 확인"""
    logger.info("=== 학습 데이터 가용성 확인 ===")
    
    today = datetime.now(local_tz).strftime("%Y%m%d")
    training_data_file = f"/opt/airflow/data/model_training/{today}/processed_sentences.json"
    
    if not os.path.exists(training_data_file):
        logger.warning(f"⚠️ 학습 데이터 파일이 없습니다: {training_data_file}")
        return {"training_ready": False, "reason": "학습 데이터 파일 없음"}
    
    try:
        with open(training_data_file, 'r', encoding='utf-8') as f:
            sentences = json.load(f)
        
        if len(sentences) < 100:  # 최소 100개 문장 필요
            logger.warning(f"⚠️ 학습 데이터 부족: {len(sentences)}개 문장")
            return {"training_ready": False, "reason": f"데이터 부족 ({len(sentences)}개)"}
        
        logger.info(f"✅ 학습 데이터 확인 완료: {len(sentences)}개 문장")
        
        # XCom으로 데이터 전달
        context['task_instance'].xcom_push(
            key='training_data_file', 
            value=training_data_file
        )
        context['task_instance'].xcom_push(
            key='sentences_count', 
            value=len(sentences)
        )
        
        return {
            "training_ready": True,
            "sentences_count": len(sentences),
            "data_file": training_data_file
        }
        
    except Exception as e:
        logger.error(f"❌ 학습 데이터 확인 실패: {e}")
        return {"training_ready": False, "reason": f"파일 읽기 오류: {e}"}

def train_enhanced_word2vec(**context):
    """기존 모델 + 새 데이터로 Word2Vec 모델 재학습"""
    logger.info("=== Word2Vec 모델 재학습 시작 ===")
    
    # 이전 태스크에서 학습 데이터 가져오기
    training_data_file = context['task_instance'].xcom_pull(
        task_ids='check_training_data',
        key='training_data_file'
    )
    sentences_count = context['task_instance'].xcom_pull(
        task_ids='check_training_data',
        key='sentences_count'
    )
    
    if not training_data_file:
        logger.error("❌ 학습 데이터를 가져올 수 없습니다.")
        return {"training_success": False, "reason": "학습 데이터 없음"}
    
    try:
        # 필요한 라이브러리 import
        import numpy as np
        import optuna
        from gensim.models import Word2Vec
        from numpy import dot
        from numpy.linalg import norm
        
        start_time = time.time()
        
        # 모델 경로 설정
        current_model_path = "/opt/airflow/models/word2vec_custom.model"
        backup_model_path = "/opt/airflow/models/word2vec_custom_backup.model"
        new_model_path = "/opt/airflow/models/word2vec_custom_new.model"
        
        # 기존 모델 백업
        if os.path.exists(current_model_path):
            if os.path.exists(backup_model_path):
                if os.path.isdir(backup_model_path):
                    shutil.rmtree(backup_model_path)
                else:
                    os.remove(backup_model_path)
            shutil.copy2(current_model_path, backup_model_path)
            logger.info("📦 기존 모델 백업 완료")
        
        # 새 학습 데이터 로드
        with open(training_data_file, 'r', encoding='utf-8') as f:
            new_sentences = json.load(f)
        
        logger.info(f"📚 새 학습 데이터 로드: {len(new_sentences)}개 문장")
        
        # 기존 모델이 있다면 기존 학습 데이터와 결합
        all_sentences = new_sentences.copy()
        
        if os.path.exists(current_model_path):
            try:
                existing_model = Word2Vec.load(current_model_path)
                logger.info(f"📖 기존 모델 어휘 크기: {len(existing_model.wv)}")
                
                # 기존 모델의 학습 데이터를 시뮬레이션하기 위해
                # 기존 어휘로 가상의 문장 생성 (선택적)
                existing_vocab = list(existing_model.wv.key_to_index.keys())
                
                # 기존 어휘를 포함한 문장들을 일부 추가 (다양성 확보)
                for i in range(min(100, len(existing_vocab) // 10)):
                    if i * 10 + 10 <= len(existing_vocab):
                        synthetic_sentence = existing_vocab[i*10:(i*10)+10]
                        all_sentences.append(synthetic_sentence)
                
                logger.info(f"📈 기존 어휘 통합 완료: 총 {len(all_sentences)}개 문장")
                
            except Exception as e:
                logger.warning(f"⚠️ 기존 모델 로드 실패, 새로 학습: {e}")
        
        # 성능 평가용 기준 단어들 (다양한 카테고리)
        test_words = [
            # 가족 관련
            "부모", "아버지", "어머니", "아들", "딸", "형제", "자매", "할머니", "할아버지",
            # 감정 관련  
            "기쁨", "슬픔", "사랑", "행복", "걱정", "두려움", "희망", "감동", "그리움",
            # 일상 관련
            "음식", "집", "학교", "병원", "회사", "친구", "선생님", "의사", "간호사",
            # 동물 관련
            "강아지", "고양이", "새", "물고기", "토끼", "햄스터", "거북이", "앵무새",
            # 계절/자연 관련
            "봄", "여름", "가을", "겨울", "바다", "산", "강", "하늘", "구름", "별"
        ]
        
        def calculate_avg_similarity(model, words):
            """평균 코사인 유사도 계산"""
            vectors = []
            for word in words:
                if word in model.wv:
                    vectors.append(model.wv[word])
            
            if len(vectors) < 2:
                return 0.0
            
            similarities = []
            for i in range(len(vectors)):
                for j in range(i + 1, len(vectors)):
                    sim = dot(vectors[i], vectors[j]) / (norm(vectors[i]) * norm(vectors[j]))
                    similarities.append(sim)
            
            return round(np.mean(similarities), 4) if similarities else 0.0
        
        # 기존 모델 성능 측정
        baseline_similarity = 0.0
        if os.path.exists(current_model_path):
            try:
                baseline_model = Word2Vec.load(current_model_path)
                baseline_similarity = calculate_avg_similarity(baseline_model, test_words)
                logger.info(f"📊 기존 모델 성능 (평균 유사도): {baseline_similarity}")
            except:
                logger.warning("⚠️ 기존 모델 성능 측정 실패")
        
        # Optuna를 이용한 하이퍼파라미터 최적화
        def objective(trial):
            vector_size = trial.suggest_categorical("vector_size", [100, 150, 200])
            window = trial.suggest_int("window", 5, 10)
            min_count = trial.suggest_int("min_count", 2, 5)
            epochs = trial.suggest_int("epochs", 10, 20)
            alpha = trial.suggest_float("alpha", 0.01, 0.05)
            
            try:
                model = Word2Vec(
                    sentences=all_sentences,
                    vector_size=vector_size,
                    window=window,
                    min_count=min_count,
                    workers=4,
                    sg=1,  # Skip-gram
                    epochs=epochs,
                    alpha=alpha,
                    seed=42
                )
                
                score = calculate_avg_similarity(model, test_words)
                return score
                
            except Exception as e:
                logger.warning(f"⚠️ 시도 실패: {e}")
                return 0.0
        
        # 최적화 실행
        logger.info("🔍 하이퍼파라미터 최적화 시작...")
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=15, timeout=300)  # 5분 제한
        
        best_params = study.best_params
        logger.info(f"🎯 최적 파라미터: {best_params}")
        
        # 최적 파라미터로 최종 모델 학습
        logger.info("🚀 최종 모델 학습 시작...")
        final_model = Word2Vec(
            sentences=all_sentences,
            vector_size=best_params["vector_size"],
            window=best_params["window"],
            min_count=best_params["min_count"],
            workers=4,
            sg=1,
            epochs=best_params["epochs"],
            alpha=best_params["alpha"],
            seed=42
        )
        
        # 새 모델 성능 측정
        new_similarity = calculate_avg_similarity(final_model, test_words)
        logger.info(f"📊 새 모델 성능 (평균 유사도): {new_similarity}")
        
        # 새 모델 임시 저장
        final_model.save(new_model_path)
        
        # 성능 비교 및 모델 교체 결정
        performance_improved = new_similarity > baseline_similarity
        vocab_size = len(final_model.wv)
        
        training_time = round(time.time() - start_time, 2)
        
        # 학습 기록 저장
        today = datetime.now(local_tz)
        stats_record = {
            "date": today.strftime("%Y-%m-%d"),
            "time": today.strftime("%H:%M:%S"),
            "baseline_similarity": baseline_similarity,
            "new_similarity": new_similarity,
            "performance_improved": performance_improved,
            "vocab_size": vocab_size,
            "vector_size": final_model.vector_size,
            "training_sentences": len(all_sentences),
            "new_sentences": len(new_sentences),
            "training_time_sec": training_time,
            "best_params": best_params
        }
        
        # 학습 기록 CSV 저장
        stats_file = "/opt/airflow/data/model_training_stats.csv"
        file_exists = os.path.exists(stats_file)
        
        with open(stats_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=stats_record.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(stats_record)
        
        # XCom으로 결과 전달
        context['task_instance'].xcom_push(key='new_model_path', value=new_model_path)
        context['task_instance'].xcom_push(key='performance_improved', value=performance_improved)
        context['task_instance'].xcom_push(key='baseline_similarity', value=baseline_similarity)
        context['task_instance'].xcom_push(key='new_similarity', value=new_similarity)
        context['task_instance'].xcom_push(key='vocab_size', value=vocab_size)
        
        logger.info(f"✅ 모델 학습 완료: {training_time}초 소요")
        
        return {
            "training_success": True,
            "performance_improved": performance_improved,
            "baseline_similarity": baseline_similarity,
            "new_similarity": new_similarity,
            "vocab_size": vocab_size,
            "training_time": training_time,
            "new_model_path": new_model_path
        }
        
    except ImportError as e:
        logger.error(f"❌ 필수 라이브러리 누락: {e}")
        return {"training_success": False, "reason": f"라이브러리 누락: {e}"}
    except Exception as e:
        logger.error(f"❌ 모델 학습 실패: {e}")
        return {"training_success": False, "reason": str(e)}

def deploy_new_model(**context):
    """성능이 향상된 경우 새 모델을 배포"""
    logger.info("=== 모델 배포 결정 ===")
    
    # 이전 태스크 결과 가져오기
    performance_improved = context['task_instance'].xcom_pull(
        task_ids='train_model',
        key='performance_improved'
    )
    new_model_path = context['task_instance'].xcom_pull(
        task_ids='train_model',
        key='new_model_path'
    )
    baseline_similarity = context['task_instance'].xcom_pull(
        task_ids='train_model',
        key='baseline_similarity'
    )
    new_similarity = context['task_instance'].xcom_pull(
        task_ids='train_model',
        key='new_similarity'
    )
    
    if not new_model_path or not os.path.exists(new_model_path):
        logger.error("❌ 새 모델 파일을 찾을 수 없습니다.")
        return {"deployed": False, "reason": "모델 파일 없음"}
    
    current_model_path = "/opt/airflow/models/word2vec_custom.model"
    backup_model_path = "/opt/airflow/models/word2vec_custom_backup.model"
    
    try:
        if performance_improved:
            logger.info(f"🚀 성능 향상 확인: {baseline_similarity} → {new_similarity}")
            
            # 기존 모델 삭제 후 새 모델 배포
            if os.path.exists(current_model_path):
                if os.path.isdir(current_model_path):
                    shutil.rmtree(current_model_path)
                else:
                    os.remove(current_model_path)
            
            # 새 모델을 메인 경로로 이동
            shutil.move(new_model_path, current_model_path)
            
            logger.info("✅ 새 모델 배포 완료")
            
            # AI 서비스에 모델 리로드 요청
            reload_success = request_ai_service_reload()
            
            return {
                "deployed": True,
                "performance_improved": True,
                "baseline_similarity": baseline_similarity,
                "new_similarity": new_similarity,
                "ai_reload_success": reload_success
            }
        
        else:
            logger.info(f"📉 성능 저하 또는 변화 없음: {baseline_similarity} vs {new_similarity}")
            logger.info("🔄 기존 모델 유지")
            
            # 새 모델 파일 삭제
            if os.path.exists(new_model_path):
                if os.path.isdir(new_model_path):
                    shutil.rmtree(new_model_path)
                else:
                    os.remove(new_model_path)
            
            return {
                "deployed": False,
                "performance_improved": False,
                "baseline_similarity": baseline_similarity,
                "new_similarity": new_similarity,
                "reason": "성능 향상 없음"
            }
    
    except Exception as e:
        logger.error(f"❌ 모델 배포 실패: {e}")
        return {"deployed": False, "reason": str(e)}

def request_ai_service_reload():
    """AI 서비스에 모델 리로드 요청"""
    try:
        reload_url = f"{AI_SERVICE_URL}/reload-model"
        response = requests.post(reload_url, timeout=60)
        
        if response.status_code == 200:
            logger.info("✅ AI 서비스 모델 리로드 성공")
            return True
        else:
            logger.warning(f"⚠️ AI 서비스 리로드 실패: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ AI 서비스 리로드 요청 실패: {e}")
        return False

def trigger_failed_games_retry(**context):
    """모델 업데이트 후 실패한 게임들 재시도 설정"""
    logger.info("=== 실패 게임 재시도 설정 ===")
    
    # 모델이 배포되었는지 확인
    deployed = context['task_instance'].xcom_pull(
        task_ids='deploy_model',
        key='deployed'
    )
    
    if not deployed:
        logger.info("ℹ️ 모델이 배포되지 않아 재시도 스킵")
        return {"retry_set": False, "reason": "모델 배포 안됨"}
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(buffered=True)
            
            # "모델에 존재하지 않습니다" 오류로 실패한 게임들을 다시 대기 상태로 변경
            query = """
            UPDATE game_detail 
            SET ai_status_code = 'B20005',
                description = '모델 업데이트 후 재시도 대기',
                ai_processed_at = NULL
            WHERE ai_status_code = 'B20008'
            AND description LIKE '%모델에 존재하지 않습니다%'
            AND ai_processed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """
            
            cursor.execute(query)
            conn.commit()
            
            retry_count = cursor.rowcount
            
            # 안전한 커서 닫기
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            cursor.close()
            
            logger.info(f"✅ {retry_count}개 실패 게임을 재시도 대기로 설정")
            
            return {
                "retry_set": True,
                "retry_count": retry_count
            }
    
    except Exception as e:
        logger.error(f"❌ 재시도 설정 실패: {e}")
        return {"retry_set": False, "reason": str(e)}

# DAG 정의
word_trainer_default_args = {
    **DAG_DEFAULT_ARGS,
    'start_date': datetime(2024, 1, 1, tzinfo=local_tz),
    'retries': 1,  # 학습은 시간이 오래 걸리므로 재시도 최소화
    'retry_delay': timedelta(minutes=10),
}

word_trainer_dag = DAG(
    'memory_forest_word_trainer',
    default_args=word_trainer_default_args,
    description='Memory Forest Word2Vec 모델 재학습 및 배포',
    schedule_interval='0 3 * * *',  # 매일 새벽 3시 실행 (수집 완료 후)
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'word2vec', 'model-training', 'ai-model']
)

# Task 정의
start_training = DummyOperator(
    task_id='start_training',
    dag=word_trainer_dag
)

check_data_task = PythonOperator(
    task_id='check_training_data',
    python_callable=check_training_data_available,
    dag=word_trainer_dag
)

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_enhanced_word2vec,
    dag=word_trainer_dag,
    pool='cpu_intensive',  # CPU 집약적 작업을 위한 풀 (Airflow 설정 필요)
)

deploy_model_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_new_model,
    dag=word_trainer_dag
)

retry_games_task = PythonOperator(
    task_id='retry_failed_games',
    python_callable=trigger_failed_games_retry,
    dag=word_trainer_dag
)

# 메인 DAG 트리거 (실패 게임 재처리를 위해)
trigger_main_dag = TriggerDagRunOperator(
    task_id='trigger_main_processing',
    trigger_dag_id='memory_forest_ai_main',
    dag=word_trainer_dag,
    wait_for_completion=False
)

end_training = DummyOperator(
    task_id='end_training',
    dag=word_trainer_dag
)

# Task 의존성
start_training >> check_data_task >> train_model_task >> deploy_model_task >> retry_games_task >> trigger_main_dag >> end_training