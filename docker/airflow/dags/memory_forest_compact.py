"""
Memory Forest 컴팩트 DAG - 하이퍼파라미터 최적화 포함
두 가지 핵심 기능에 집중:
1. 실패/대기 상태 게임들의 AI 재분석
2. 모델에 없는 단어들의 학습 (Optuna 최적화 포함)
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pendulum
import logging
import csv
import time
import os
import shutil
import pandas as pd
import optuna
from gensim.models import Word2Vec
from numpy import dot
from numpy.linalg import norm
import numpy as np
import requests
import json
import re
import urllib.request
import urllib.parse
from typing import Dict, List, Tuple, Optional

# 로컬 모듈 import
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_ARGS, AI_STATUS_CODES, SCHEDULES, BATCH_CONFIG, MODEL_CONFIG, NAVER_API_CONFIG
from utils import db_manager, ai_client, text_processor

logger = logging.getLogger(__name__)

# DAG 기본 설정
dag_default_args = {
    **DEFAULT_ARGS,
    'start_date': pendulum.datetime(2024, 1, 1, tz=pendulum.timezone("Asia/Seoul")),
}

class OptimizedWord2VecTrainer:
    """Word2Vec 모델 하이퍼파라미터 최적화 트레이너"""
    
    def __init__(self):
        # utils/__init__.py에서 이미 생성된 인스턴스 사용
        self.text_processor = text_processor
        self.model_path = MODEL_CONFIG['model_path']
        self.backup_path = MODEL_CONFIG['backup_path']
        self.train_stats_path = "/opt/airflow/data/word2vec_train_stats.csv"
        
        # 평가용 표준 단어 세트 (치메 혹은 노인들이 자주 쓸법한 단어들)
        self.evaluation_words = [
            "부모", "유럽", "기쁨", "고양이", "김치찌개", "출근", "축구", "칫솔",
            "냉장고", "선인장", "호랑이", "불교", "병원", "청바지", "졸업식", "독서",
            "봄비", "교과서", "간호사", "부산", "지하철", "박물관", "연극", "생일", "유치원"
        ]
    
    def preprocess_sentences(self, sentences: List[str], progress_callback=None) -> List[List[str]]:
        """문장들을 전처리하여 토큰화된 문장 리스트 반환 - 완전 빠른 방식"""
        logger.info(f"📝 빠른 문장 전처리 시작: {len(sentences)}개 문장")
        
        tokenized_sentences = []
        processed_count = 0
        batch_size = 30  # 빠른 처리를 위한 배치 크기
        
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i+batch_size]
            
            for j, sentence in enumerate(batch):
                if not sentence or len(sentence.strip()) < 5:
                    continue
                
                # 빠른 토큰화 (KoNLPy 없이)
                tokens = self.fast_tokenize(sentence)
                if len(tokens) >= 2:  # 최소 2개 토큰 이상
                    tokenized_sentences.append(tokens)
                    processed_count += 1
                
                # 진행률 보고 (배치마다)
                if progress_callback and (i + j + 1) % batch_size == 0:
                    progress = (i + j + 1) / len(sentences) * 100
                    progress_callback(f"빠른 전처리 진행률: {progress:.1f}% ({processed_count}개 유효 문장)")
        
        logger.info(f"✅ 빠른 전처리 완료: {len(sentences)}개 → {len(tokenized_sentences)}개 유효 문장")
        return tokenized_sentences
    
    def fast_tokenize(self, text: str) -> List[str]:
        """빠른 토큰화 (TextProcessor 실패 시 대체용)"""
        # HTML 태그 제거
        clean_text = re.sub(r'<.*?>', '', text)
        # 특수문자 제거
        clean_text = re.sub(r'[^\w\s가-힣]', ' ', clean_text)
        # 연속 공백 정리
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # 한글 단어만 추출 (2글자 이상)
        tokens = re.findall(r'[가-힣]{2,8}', clean_text)
        
        # 중복 제거
        unique_tokens = []
        seen = set()
        for token in tokens:
            if token not in seen:
                unique_tokens.append(token)
                seen.add(token)
        
        return unique_tokens
    
    def calculate_similarity_score(self, model: Word2Vec, words: List[str]) -> float:
        """모델의 품질을 평가하는 유사도 점수 계산"""
        try:
            vectors = [model.wv[word] for word in words if word in model.wv]
            if len(vectors) < 2:
                return 0.0
                
            similarities = []
            for i in range(len(vectors)):
                for j in range(i + 1, len(vectors)):
                    sim = dot(vectors[i], vectors[j]) / (norm(vectors[i]) * norm(vectors[j]))
                    similarities.append(sim)
            
            return round(np.mean(similarities), 4) if similarities else 0.0
        except Exception as e:
            logger.warning(f"유사도 계산 실패: {e}")
            return 0.0
    
    def get_baseline_score(self) -> float:
        """기존 모델의 베이스라인 점수 가져오기"""
        if os.path.exists(self.model_path):
            try:
                baseline_model = Word2Vec.load(self.model_path)
                baseline_score = self.calculate_similarity_score(baseline_model, self.evaluation_words)
                logger.info(f"📊 기준 모델 평균 유사도: {baseline_score}")
                return baseline_score
            except Exception as e:
                logger.warning(f"기준 모델 로드 실패: {e}")
        else:
            logger.info("🆕 기존 모델 없음 - 초기 학습")
        return 0.0
    
    def optimize_hyperparameters(self, tokenized_sentences: List[List[str]], 
                                n_trials: int = 15, progress_callback=None) -> Dict:
        """Optuna를 사용한 하이퍼파라미터 최적화"""
        logger.info(f"🔬 하이퍼파라미터 최적화 시작 ({n_trials}회 시도)")
        
        trial_count = 0
        best_score = 0.0
        
        def objective(trial):
            nonlocal trial_count, best_score
            trial_count += 1
            
            # 하이퍼파라미터 범위 정의
            vector_size = trial.suggest_categorical("vector_size", [50, 100, 150, 200])
            window = trial.suggest_int("window", 3, 10)
            min_count = trial.suggest_int("min_count", 2, 8)
            epochs = trial.suggest_int("epochs", 5, 20)
            sg = trial.suggest_categorical("sg", [0, 1])  # CBOW vs Skip-gram
            alpha = trial.suggest_float("alpha", 0.01, 0.05)
            
            try:
                # 모델 학습
                model = Word2Vec(
                    sentences=tokenized_sentences,
                    vector_size=vector_size,
                    window=window,
                    min_count=min_count,
                    workers=4,
                    sg=sg,
                    epochs=epochs,
                    alpha=alpha
                )
                
                # 성능 평가
                score = self.calculate_similarity_score(model, self.evaluation_words)
                
                if score > best_score:
                    best_score = score
                
                # 진행률 보고
                if progress_callback:
                    progress = trial_count / n_trials * 100
                    progress_callback(f"최적화 진행률: {progress:.1f}% (시도 {trial_count}/{n_trials}, 현재 점수: {score:.4f}, 최고 점수: {best_score:.4f})")
                
                logger.info(f"🧪 시도 {trial_count}/{n_trials}: 점수 {score:.4f} (파라미터: vec={vector_size}, win={window}, cnt={min_count}, ep={epochs}, sg={sg})")
                
                return score
                
            except Exception as e:
                logger.warning(f"❌ 시도 {trial_count} 실패: {e}")
                return 0.0
        
        # Optuna 스터디 실행
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)
        
        best_params = study.best_params
        best_value = study.best_value
        
        logger.info(f"🏆 최적화 완료!")
        logger.info(f"   최고 점수: {best_value:.4f}")
        logger.info(f"   최적 파라미터: {best_params}")
        
        return best_params, best_value
    
    def train_optimized_model(self, tokenized_sentences: List[List[str]], 
                            best_params: Dict, baseline_score: float,
                            progress_callback=None) -> Tuple[bool, Dict]:
        """최적화된 파라미터로 기존 모델에 추가 학습"""
        logger.info(f"🎯 기존 모델에 새 데이터 추가 학습 시작")
        
        start_time = time.time()
        
        try:
            if progress_callback:
                progress_callback("기존 모델 로드 및 학습 전 성능 측정 중...")
            
            # 기존 모델 로드
            if os.path.exists(self.model_path):
                logger.info(f"📚 기존 모델 로드: {self.model_path}")
                model = Word2Vec.load(self.model_path)
                
                # 학습 전 성능 측정 (현재 시점의 실제 기준점)
                pre_training_score = self.calculate_similarity_score(model, self.evaluation_words)
                logger.info(f"📊 학습 전 현재 모델 성능: {pre_training_score:.4f}")
                
                # 새 데이터로 vocabulary 업데이트
                logger.info(f"📖 새 단어들을 기존 모델에 추가...")
                original_vocab_size = len(model.wv)
                model.build_vocab(tokenized_sentences, update=True)
                new_vocab_size = len(model.wv)
                added_words = new_vocab_size - original_vocab_size
                logger.info(f"📈 어휘 크기: {original_vocab_size} → {new_vocab_size} ({added_words}개 단어 추가)")
                
                # 추가 학습 (기존 지식 유지하면서 새 데이터 학습)
                logger.info(f"🔄 기존 모델에 새 데이터 추가 학습...")
                model.train(tokenized_sentences, total_examples=len(tokenized_sentences), epochs=best_params["epochs"])
                
            else:
                # 기존 모델이 없으면 새로 생성
                logger.info(f"🆕 새 모델 생성...")
                pre_training_score = 0.0  # 기존 모델이 없으므로 0
                model = Word2Vec(
                    sentences=tokenized_sentences,
                    vector_size=best_params["vector_size"],
                    window=best_params["window"],
                    min_count=best_params["min_count"],
                    workers=4,
                    sg=best_params.get("sg", 1),
                    epochs=best_params["epochs"],
                    alpha=best_params.get("alpha", 0.025)
                )
            
            # 학습 후 성능 평가
            post_training_score = self.calculate_similarity_score(model, self.evaluation_words)
            train_time = time.time() - start_time
            
            logger.info(f"📊 학습 후 모델 성능: {post_training_score:.4f}")
            logger.info(f"📊 학습 전 기준 성능: {pre_training_score:.4f}")
            logger.info(f"📊 성능 변화: {post_training_score - pre_training_score:+.4f}")
            logger.info(f"⏱️ 학습 시간: {train_time:.2f}초")
            
            # 성능 변화 허용 임계값 (학습 전 성능 기준)
            performance_threshold_ratio = 0.05  # 5% 성능 저하까지 허용
            min_acceptable_score = pre_training_score * (1 - performance_threshold_ratio)
            
            logger.info(f"🎯 최소 허용 성능: {min_acceptable_score:.4f} (기준의 {(1-performance_threshold_ratio)*100}%)")
            
            if post_training_score >= min_acceptable_score:
                # 성능이 허용 범위 내에서 유지됨
                performance_change = ((post_training_score - pre_training_score) / pre_training_score * 100) if pre_training_score > 0 else 0
                logger.info(f"✅ 성능 허용 범위 내 ({performance_change:+.2f}%) - 모델 저장")
                
                # 기존 모델 백업
                if os.path.exists(self.backup_path):
                    if os.path.isdir(self.backup_path):
                        shutil.rmtree(self.backup_path)
                    else:
                        os.remove(self.backup_path)
                shutil.copy2(self.model_path, self.backup_path)
                logger.info(f"💾 기존 모델 백업 완료")
                
                # 새 모델 저장
                model.save(self.model_path)
                logger.info(f"💾 추가 학습된 모델 저장 완료: {self.model_path}")
                
                # 학습 통계 저장
                self.save_training_stats(model, post_training_score, train_time, best_params, False)
                
                return True, {
                    'success': True,
                    'pre_training_score': pre_training_score,
                    'post_training_score': post_training_score,
                    'performance_change': post_training_score - pre_training_score,
                    'train_time': train_time,
                    'vocab_size': len(model.wv),
                    'restored': False,
                    'training_mode': 'incremental'
                }
            else:
                # 성능이 허용 범위를 벗어남
                performance_drop = ((pre_training_score - post_training_score) / pre_training_score * 100) if pre_training_score > 0 else 0
                logger.warning(f"⚠️ 성능 저하 임계값 초과 ({performance_drop:.2f}% 저하) - 기존 모델 유지")
                
                # 기존 모델 그대로 유지 (이미 로드된 상태이므로 다시 로드)
                if os.path.exists(self.model_path):
                    baseline_model = Word2Vec.load(self.model_path)
                else:
                    baseline_model = model  # 새 모델이었다면 그대로 사용
                
                self.save_training_stats(baseline_model, pre_training_score, train_time, best_params, True)
                
                return False, {
                    'success': False,
                    'pre_training_score': pre_training_score,
                    'post_training_score': post_training_score,
                    'performance_change': post_training_score - pre_training_score,
                    'train_time': train_time,
                    'vocab_size': len(baseline_model.wv),
                    'restored': True,
                    'reason': f'성능 저하 임계값 초과 ({performance_drop:.2f}% 저하)',
                    'training_mode': 'incremental'
                }
                    
        except Exception as e:
            logger.error(f"❌ 추가 학습 실패: {e}")
            return False, {
                'success': False,
                'error': str(e)
            }
    
    def save_training_stats(self, model: Word2Vec, score: float, train_time: float, 
                          params: Dict, restored: bool):
        """학습 통계를 CSV 파일에 저장"""
        try:
            train_date = datetime.now().strftime("%Y-%m-%d")
            train_time_str = datetime.now().strftime("%H:%M:%S")
            
            stats = {
                'date': train_date,
                'time': train_time_str,
                'vocab_size': len(model.wv),
                'vector_size': params.get('vector_size', model.vector_size),
                'window': params.get('window', model.window),
                'min_count': params.get('min_count', model.min_count),
                'epochs': params.get('epochs', model.epochs),
                'sg': params.get('sg', model.sg),
                'alpha': params.get('alpha', model.alpha),
                'avg_similarity': score,
                'train_time_sec': round(train_time, 2),
                'corpus_count': model.corpus_count,
                'corpus_total_words': model.corpus_total_words,
                'restored': 'yes' if restored else 'no'
            }
            
            # CSV 파일 존재 여부 확인
            file_exists = os.path.exists(self.train_stats_path)
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(self.train_stats_path), exist_ok=True)
            
            with open(self.train_stats_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # 헤더 쓰기 (파일이 새로 생성된 경우)
                if not file_exists:
                    writer.writerow(stats.keys())
                
                # 데이터 쓰기
                writer.writerow(stats.values())
            
            logger.info(f"📊 학습 통계 저장 완료: {self.train_stats_path}")
            
        except Exception as e:
            logger.error(f"❌ 학습 통계 저장 실패: {e}")

def train_missing_words(**context):
    """수집된 단어들로 하이퍼파라미터 최적화된 모델 학습"""
    logger.info("=== 🚀 빠른 모델 학습 시작 ===")
    
    try:
        # 이전 태스크에서 단어 목록 가져오기
        missing_words = context['task_instance'].xcom_pull(
            task_ids='collect_missing_words',
            key='missing_words'
        )
        
        if not missing_words:
            logger.info("❌ 학습할 단어가 없습니다")
            return {
                'training_executed': False,
                'words_trained': 0,
                'model_reloaded': False
            }
        
        logger.info(f"🎯 대상 단어: {missing_words}")
        logger.info(f"📊 총 {len(missing_words)}개 단어 학습 예정")
        
        # 진행률 콜백 함수
        def progress_callback(message):
            logger.info(f"📈 {message}")
        
        # 1단계: 네이버 블로그에서 관련 텍스트 수집
        logger.info(f"\n" + "="*60)
        logger.info(f"📝 1단계: 블로그 텍스트 수집 시작")
        logger.info(f"="*60)
        
        all_collected_texts = []
        
        # 각 단어별로 텍스트 수집 (최대 5개 단어)
        max_words_to_process = min(5, len(missing_words))
        for i, word in enumerate(missing_words[:max_words_to_process]):
            progress_callback(f"텍스트 수집 진행률: {(i+1)/max_words_to_process*100:.1f}% (단어: '{word}')")
            
            try:
                word_texts = collect_blog_texts_for_word(word, max_texts=150)
                if word_texts:
                    all_collected_texts.extend(word_texts)
                    logger.info(f"✅ '{word}' 완료: {len(word_texts)}개 문장 수집")
                else:
                    logger.warning(f"⚠️ '{word}' 수집 결과 없음")
                    
            except Exception as word_error:
                logger.error(f"❌ '{word}' 텍스트 수집 중 오류: {word_error}")
                continue
        
        logger.info(f"📊 총 수집된 문장: {len(all_collected_texts)}개")
        
        # 수집된 텍스트가 충분하지 않으면 학습 건너뛰기
        if len(all_collected_texts) < 50:
            logger.warning(f"⚠️ 수집된 텍스트가 부족합니다 ({len(all_collected_texts)}개 < 50개)")
            logger.info(f"🔄 AI 서비스 모델 리로드만 수행")
            
            reload_success = ai_client.reload_model()
            return {
                'training_executed': False,
                'words_trained': 0,
                'model_reloaded': reload_success,
                'reason': 'insufficient_text'
            }
        
        # 2단계: 하이퍼파라미터 최적화된 모델 학습
        logger.info(f"\n🧠 2단계: 하이퍼파라미터 최적화 모델 학습")
        logger.info(f"=" * 50)
        
        trainer = OptimizedWord2VecTrainer()
        
        # 문장 전처리
        progress_callback("문장 전처리 시작...")
        tokenized_sentences = trainer.preprocess_sentences(all_collected_texts, progress_callback)
        
        if len(tokenized_sentences) < 30:
            logger.warning(f"⚠️ 유효한 문장이 부족합니다 ({len(tokenized_sentences)}개 < 30개)")
            reload_success = ai_client.reload_model()
            return {
                'training_executed': False,
                'words_trained': 0,
                'model_reloaded': reload_success,
                'reason': 'insufficient_valid_sentences'
            }
        
        # 기준 성능 확인
        baseline_score = trainer.get_baseline_score()
        
        # 하이퍼파라미터 최적화
        progress_callback("하이퍼파라미터 최적화 시작...")
        best_params, best_score = trainer.optimize_hyperparameters(
            tokenized_sentences, 
            n_trials=12,  # 적당한 시도 횟수
            progress_callback=progress_callback
        )
        
        # 최종 모델 학습
        progress_callback("최종 모델 학습 시작...")
        training_success, training_result = trainer.train_optimized_model(
            tokenized_sentences,
            best_params,
            baseline_score,
            progress_callback
        )
        
        # 3단계: 모델 리로드
        logger.info(f"\n🔄 3단계: 모델 리로드")
        logger.info(f"=" * 50)
        
        if training_success:
            logger.info(f"⏳ AI 서비스 모델 리로드 중...")
            reload_success = ai_client.reload_model()
            
            if reload_success:
                logger.info(f"✅ 모델 리로드 성공!")
                
                # 4단계: 게임 상태 업데이트
                logger.info(f"\n📊 4단계: 게임 상태 업데이트")
                logger.info(f"=" * 50)
                
                updated_count = update_trained_word_games(missing_words)
                
                # 최종 결과
                logger.info(f"\n🎉 학습 완료!")
                logger.info(f"=" * 50)
                logger.info(f"✅ 학습된 단어: {len(missing_words)}개")
                logger.info(f"📚 사용된 문장: {len(tokenized_sentences)}개")
                logger.info(f"🎮 업데이트된 게임: {updated_count}개")
                logger.info(f"📈 성능 개선: {training_result.get('improvement', 0):.4f}")
                logger.info(f"🏆 최종 점수: {training_result.get('new_score', 0):.4f}")
                
                return {
                    'training_executed': True,
                    'words_trained': len(missing_words),
                    'model_reloaded': True,
                    'games_updated': updated_count,
                    'texts_collected': len(all_collected_texts),
                    'valid_sentences': len(tokenized_sentences),
                    'trained_words': missing_words,
                    'performance_score': training_result.get('new_score', 0),
                    'improvement': training_result.get('improvement', 0),
                    'best_params': best_params
                }
            else:
                logger.error("❌ 모델 리로드 실패")
                return {
                    'training_executed': True,
                    'words_trained': len(missing_words),
                    'model_reloaded': False
                }
        else:
            logger.warning(f"⚠️ 모델 학습 실패 또는 성능 저하로 인한 복원")
            
            # 복원된 경우에도 리로드 시도
            reload_success = ai_client.reload_model()
            
            return {
                'training_executed': False,
                'words_trained': 0,
                'model_reloaded': reload_success,
                'reason': training_result.get('reason', 'training_failed'),
                'performance_degradation': True
            }
            
    except Exception as e:
        logger.error(f"❌ 모델 학습 중 치명적 오류: {e}")
        import traceback
        logger.error(f"상세 오류:\n{traceback.format_exc()}")
        return {
            'training_executed': False,
            'words_trained': 0,
            'model_reloaded': False,
            'error': str(e)
        }

def collect_blog_texts_for_word(word: str, max_texts: int = 100) -> List[str]:
    """특정 단어에 대한 네이버 블로그 텍스트 수집 - 문장 단위로 분리"""
    
    logger.info(f"🌐 네이버 API 설정 확인...")
    logger.info(f"  Client ID: {NAVER_API_CONFIG['client_id'][:10] if NAVER_API_CONFIG['client_id'] else 'None'}...")
    logger.info(f"  Client Secret: {'설정됨' if NAVER_API_CONFIG['client_secret'] else '없음'}")
    
    if not NAVER_API_CONFIG['client_id'] or not NAVER_API_CONFIG['client_secret']:
        logger.error(f"❌ 네이버 API 인증 정보가 없습니다!")
        return []
    
    def get_request_url(url):
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", NAVER_API_CONFIG['client_id'])
        req.add_header("X-Naver-Client-Secret", NAVER_API_CONFIG['client_secret'])
        try:
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                return response.read().decode('utf-8')
            else:
                logger.error(f"❌ API 응답 실패 (상태: {response.getcode()})")
                return None
        except Exception as e:
            logger.error(f"❌ 네이버 API 요청 실패: {e}")
            return None
    
    def get_naver_search(query, start=1, display=50):
        base = "https://openapi.naver.com/v1/search"
        node = "/blog.json"
        parameters = f"?query={urllib.parse.quote(query)}&start={start}&display={display}"
        url = base + node + parameters
        
        response = get_request_url(url)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON 파싱 실패: {e}")
                return None
        return None
    
    def split_into_sentences(text: str) -> List[str]:
        """텍스트를 문장 단위로 분리 - 빠른 방식"""
        # 빠른 문장 분리 규칙
        sentences = []
        
        # 마침표, 느낌표, 물음표로 분리
        raw_sentences = re.split(r'[.!?。]', text)
        
        for sentence in raw_sentences:
            sentence = sentence.strip()
            
            # 길이 검증 (너무 짧거나 긴 문장 제외)
            if 8 <= len(sentence) <= 80:  # 길이 기준 완화
                # 검색어가 포함된 문장만 수집
                if word in sentence:
                    sentences.append(sentence)
        
        return sentences
    
    logger.info(f"📝 '{word}' 관련 블로그 텍스트 수집 시작...")
    logger.info(f"🎯 목표: 최대 {max_texts}개 문장 수집")
    
    collected_sentences = []
    
    try:
        # 네이버 블로그 검색 (여러 페이지)
        max_blogs_per_page = 50
        max_pages = 2  # 최대 2페이지까지 수집
        
        for page in range(max_pages):
            start_idx = page * max_blogs_per_page + 1
            logger.info(f"🔍 페이지 {page + 1} 검색 중... (시작 인덱스: {start_idx})")
            
            search_result = get_naver_search(word, start=start_idx, display=max_blogs_per_page)
            
            if not search_result or 'items' not in search_result:
                logger.warning(f"⚠️ 페이지 {page + 1} 검색 결과 없음")
                continue
            
            items = search_result['items']
            logger.info(f"📊 페이지 {page + 1}: {len(items)}개 블로그 글 발견")
            
            for i, item in enumerate(items):
                # description에서 HTML 태그 제거
                description = item.get('description', '')
                clean_text = re.sub(r'<[^>]+>', '', description)
                clean_text = re.sub(r'&[a-zA-Z0-9#]+;', '', clean_text)
                
                if len(clean_text) < 20:
                    continue
                
                # 문장 단위로 분리
                sentences = split_into_sentences(clean_text)
                
                for sentence in sentences:
                    if len(collected_sentences) >= max_texts:
                        logger.info(f"🎯 목표 달성: {max_texts}개 문장 수집 완료")
                        return collected_sentences
                    
                    collected_sentences.append(sentence)
                    
                    # 진행률 로그 (10개마다)
                    if len(collected_sentences) % 10 == 0:
                        logger.info(f"📈 수집 진행률: {len(collected_sentences)}/{max_texts}개 문장")
                
                if len(collected_sentences) >= max_texts:
                    break
            
            if len(collected_sentences) >= max_texts:
                break
            
            # API 호출 제한을 위한 짧은 지연
            time.sleep(0.1)
    
    except Exception as e:
        logger.error(f"❌ 블로그 텍스트 수집 실패: {e}")
        import traceback
        logger.error(f"상세 오류:\n{traceback.format_exc()}")
    
    logger.info(f"✅ 수집 완료: '{word}' 관련 {len(collected_sentences)}개 문장")
    return collected_sentences

def collect_missing_words(**context):
    """모델에 없는 단어들 수집"""
    logger.info("=== 모델 누락 단어 수집 시작 ===")
    
    try:
        # 먼저 디버깅: %모델% 마커가 있는 레코드 확인
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # %모델% 마커가 있는 레코드 개수 확인
                debug_query = """
                SELECT COUNT(*) as count
                FROM game_detail
                WHERE description LIKE %s
                """
                cursor.execute(debug_query, (f'%{MODEL_CONFIG["missing_words_marker"]}%',))
                marker_count = cursor.fetchone()['count']
                logger.info(f"🔍 {MODEL_CONFIG['missing_words_marker']} 마커가 있는 레코드: {marker_count}개")
                
                # 샘플 확인
                if marker_count > 0:
                    sample_query = """
                    SELECT game_id, game_seq, answer_text, description
                    FROM game_detail
                    WHERE description LIKE %s
                    LIMIT 5
                    """
                    cursor.execute(sample_query, (f'%{MODEL_CONFIG["missing_words_marker"]}%',))
                    samples = cursor.fetchall()
                    logger.info(f"📋 샘플 레코드들:")
                    for sample in samples:
                        logger.info(f"  - {sample['game_id']}/{sample['game_seq']}: '{sample['answer_text']}' -> {sample['description']}")
                
                cursor.close()
                
        except Exception as debug_error:
            logger.error(f"디버깅 쿼리 실패: {debug_error}")
        
        # %모델% 마커가 있는 게임들에서 단어 추출
        missing_words = db_manager.extract_training_words(BATCH_CONFIG['model_training_batch_size'])
        
        if not missing_words:
            logger.info("학습할 새로운 단어가 없습니다")
            return {
                'collected_words': 0,
                'cleaned_words': 0,
                'words': []
            }
        
        # 텍스트 처리기로 단어 정제 - 기존 TextProcessor 활용
        logger.info(f"📝 단어 정제 시작 (TextProcessor 사용)...")
        
        # 빠른 단어 정제 (KoNLPy 없이)
        logger.info(f"📝 빠른 단어 정제 시작...")
        
        cleaned_words = []
        seen = set()
        
        for word in missing_words:
            if not word:
                continue
                
            word = word.strip()
            
            # 빠른 검증: 한글만, 2-10글자, 중복 제거
            if (len(word) >= 2 and 
                len(word) <= 10 and 
                re.fullmatch(r'[가-힣]+', word) and
                word not in seen):
                
                cleaned_words.append(word)
                seen.add(word)
        
        logger.info(f"✅ 빠른 단어 정제 완료: {len(missing_words)}개 → {len(cleaned_words)}개")
        
        # XCom으로 다음 태스크에 전달
        context['task_instance'].xcom_push(key='missing_words', value=cleaned_words)
        
        return {
            'collected_words': len(missing_words),
            'cleaned_words': len(cleaned_words),
            'words': cleaned_words[:10]  # 로그용으로 처음 10개만
        }
        
    except Exception as e:
        logger.error(f"단어 수집 중 오류: {e}")
        return {
            'collected_words': 0,
            'cleaned_words': 0,
            'words': [],
            'error': str(e)
        }

def retry_failed_games(**context):
    """실패/대기 상태의 게임들을 재분석"""
    logger.info("=== 실패 게임 재처리 시작 ===")
    
    try:
        # 실패/대기 상태 게임들 조회
        failed_games = db_manager.get_failed_games(BATCH_CONFIG['retry_games_batch_size'])
        
        if not failed_games:
            logger.info("재처리할 게임이 없습니다")
            return {
                'total_games': 0,
                'processed': 0,
                'failed': 0,
                'missing_words': 0
            }
        
        logger.info(f"재처리 대상 게임 {len(failed_games)}개 발견")
        
        # 게임들을 처리 중 상태로 표시
        for game in failed_games:
            db_manager.mark_as_processing(game['game_id'], game['game_seq'])
        
        # AI 서비스로 일괄 분석
        analysis_results = ai_client.batch_analyze_games(failed_games)
        
        # 결과 처리
        stats = {
            'total_games': len(failed_games),
            'processed': 0,
            'failed': 0,
            'missing_words': 0
        }
        
        for result in analysis_results:
            game_id = result['game_id']
            game_seq = result['game_seq']
            
            if result['status'] == 'success':
                # AI 분석 성공 - 결과 저장
                if db_manager.update_game_ai_result(game_id, game_seq, result['ai_result']):
                    stats['processed'] += 1
                    logger.info(f"게임 재처리 성공: {game_id}/{game_seq}")
                else:
                    stats['failed'] += 1
                    logger.error(f"게임 결과 저장 실패: {game_id}/{game_seq}")
                    
            elif result['status'] == 'missing_word':
                # 모델에 없는 단어
                missing_word_desc = f"{result['answer_text']}는 {MODEL_CONFIG['missing_words_marker']}에 존재하지 않는 단어입니다"
                if db_manager.update_game_status(
                    game_id, game_seq, 
                    AI_STATUS_CODES['COMPLETED'],  # 완료로 표시하되 설명에 마커 포함
                    missing_word_desc
                ):
                    stats['missing_words'] += 1
                    logger.info(f"모델 누락 단어 표시: {game_id}/{game_seq} - {result['answer_text']}")
                else:
                    stats['failed'] += 1
                    
            else:
                # 분석 실패
                error_msg = result.get('error', 'AI 분석 실패')
                if db_manager.mark_as_failed(game_id, game_seq, error_msg):
                    stats['failed'] += 1
                    logger.error(f"게임 재처리 실패: {game_id}/{game_seq} - {error_msg}")
        
        logger.info(f"재처리 완료: 성공 {stats['processed']}, 실패 {stats['failed']}, 누락단어 {stats['missing_words']}")
        return stats
        
    except Exception as e:
        logger.error(f"재처리 작업 중 오류: {e}")
        return {
            'total_games': 0,
            'processed': 0,
            'failed': 0,
            'missing_words': 0,
            'error': str(e)
        }

def update_trained_word_games(words: List[str]) -> int:
    """학습된 단어들의 게임을 재분석 대기 상태로 변경"""
    updated_count = 0
    
    try:
        for word in words:
            # 해당 단어가 포함된 게임들 찾기
            with db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # %모델% 마커가 있고 해당 단어가 포함된 게임들
                query = """
                SELECT game_id, game_seq
                FROM game_detail
                WHERE description LIKE %s
                AND answer_text = %s
                """
                
                cursor.execute(query, (f'%{MODEL_CONFIG["missing_words_marker"]}%', word))
                games = cursor.fetchall()
                
                # 대기 상태로 변경
                for game in games:
                    if db_manager.update_game_status(
                        game['game_id'], 
                        game['game_seq'],
                        AI_STATUS_CODES['WAITING'],
                        f'"{word}" 단어 학습 완료 - 재분석 대기 중'
                    ):
                        updated_count += 1
                        logger.info(f"재분석 대기로 변경: {game['game_id']}/{game['game_seq']} - {word}")
                
                cursor.close()
                
    except Exception as e:
        logger.error(f"게임 상태 업데이트 실패: {e}")
    
    logger.info(f"총 {updated_count}개 게임을 재분석 대기 상태로 변경")
    return updated_count

def check_system_status(**context):
    """시스템 상태 확인"""
    logger.info("=== 시스템 상태 확인 ===")
    
    try:
        # 데이터베이스 연결 확인
        db_healthy = db_manager.test_connection()
        
        # AI 서비스 상태 확인
        ai_healthy = ai_client.check_health()
        
        # 처리 통계 조회
        stats = db_manager.get_processing_statistics()
        
        # 모델 정보 조회
        model_info = ai_client.get_model_info()
        
        status = {
            'database_healthy': db_healthy,
            'ai_service_healthy': ai_healthy,
            'processing_stats': stats,
            'model_info': model_info,
            'overall_healthy': db_healthy and ai_healthy
        }
        
        if status['overall_healthy']:
            logger.info("✅ 시스템 상태 정상")
        else:
            logger.warning("⚠️ 시스템 일부 구성요소에 문제 있음")
        
        return status
        
    except Exception as e:
        logger.error(f"시스템 상태 확인 중 오류: {e}")
        return {
            'database_healthy': False,
            'ai_service_healthy': False,
            'overall_healthy': False,
            'error': str(e)
        }

# DAG 정의
memory_forest_compact_dag = DAG(
    'memory_forest_compact',
    default_args=dag_default_args,
    description='Memory Forest 컴팩트 버전 - 핵심 기능만 포함',
    schedule_interval=None,  # 수동 실행 또는 외부 트리거
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'compact', 'ai-processing']
)

# 실패 게임 재처리 DAG
retry_dag = DAG(
    'memory_forest_retry_failed',
    default_args=dag_default_args,
    description='실패/대기 게임 재처리',
    schedule_interval=SCHEDULES['retry_failed_games'],  # 10분마다
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'retry', 'ai-processing']
)

# 모델 학습 DAG - 하이퍼파라미터 최적화 포함
training_dag = DAG(
    'memory_forest_train_words',
    default_args=dag_default_args,
    description='모델에 없는 단어 학습 - 하이퍼파라미터 최적화 포함',
    schedule_interval=SCHEDULES['train_missing_words'],  # 매일 오전 3시
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'training', 'model', 'optuna']
)

# 태스크 정의 - 재처리 DAG
start_retry = DummyOperator(task_id='start_retry', dag=retry_dag)

check_status_task = PythonOperator(
    task_id='check_system_status',
    python_callable=check_system_status,
    dag=retry_dag
)

retry_games_task = PythonOperator(
    task_id='retry_failed_games',
    python_callable=retry_failed_games,
    dag=retry_dag
)

end_retry = DummyOperator(task_id='end_retry', dag=retry_dag)

# 태스크 정의 - 학습 DAG (하이퍼파라미터 최적화 포함)
start_training = DummyOperator(task_id='start_training', dag=training_dag)

collect_words_task = PythonOperator(
    task_id='collect_missing_words',
    python_callable=collect_missing_words,
    dag=training_dag
)

train_words_task = PythonOperator(
    task_id='train_missing_words',
    python_callable=train_missing_words,
    dag=training_dag,
    priority_weight=10  # 높은 우선순위
)

end_training = DummyOperator(task_id='end_training', dag=training_dag)

# 의존성 설정
start_retry >> check_status_task >> retry_games_task >> end_retry
start_training >> collect_words_task >> train_words_task >> end_training