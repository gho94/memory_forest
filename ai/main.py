# main.py - 실제 DB 스키마에 맞춘 버전
import numpy as np
import re
import random
import os
import asyncio
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from konlpy.tag import Okt
from gensim.models import Word2Vec
import logging
import mysql.connector
from mysql.connector import Error

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Memory Forest AI Service", version="1.0.0")

# 전역 변수
model = None
okt = Okt()

class AIAnalysisRequest(BaseModel):
    answer_text: str
    game_id: str
    game_seq: int

class AIAnalysisResponse(BaseModel):
    game_id: str
    game_seq: int
    wrong_option_1: str
    wrong_option_2: str
    wrong_option_3: str
    similarity_score_1: float
    similarity_score_2: float
    similarity_score_3: float
    ai_status: str
    description: Optional[str] = None

class BatchProcessRequest(BaseModel):
    limit: Optional[int] = 10

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),     
    'database': os.getenv('DB_NAME', 'myapp'),       
    'user': os.getenv('DB_USER', 'app_user'),           
    'password': os.getenv('DB_PASSWORD', 'mysql'),   
    'port': int(os.getenv('DB_PORT', '3306'))       
}

def get_db_connection():
    """데이터베이스 연결"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return None

def get_games_needing_analysis(limit: int = 10):
    """AI 분석이 필요한 게임들 조회"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT game_id, game_seq, answer_text, original_name, category_code
        FROM game_master 
        WHERE answer_text IS NOT NULL 
        AND answer_text != ''
        AND (ai_status = 'PENDING' OR ai_status = 'FAILED')
        ORDER BY game_id, game_seq
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        games = cursor.fetchall()
        return games
    except Error as e:
        logger.error(f"게임 조회 실패: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_game_ai_result(game_id: str, game_seq: int, ai_result: dict):
    """게임의 AI 분석 결과 업데이트"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        UPDATE game_master 
        SET wrong_option_1 = %s, wrong_option_2 = %s, wrong_option_3 = %s,
            similarity_score_1 = %s, similarity_score_2 = %s, similarity_score_3 = %s,
            ai_status = %s, description = %s, ai_processed_at = NOW()
        WHERE game_id = %s AND game_seq = %s
        """
        
        values = (
            ai_result.get('wrong_option_1', ''),
            ai_result.get('wrong_option_2', ''),
            ai_result.get('wrong_option_3', ''),
            str(ai_result.get('similarity_score_1', 0.0)),
            str(ai_result.get('similarity_score_2', 0.0)),
            str(ai_result.get('similarity_score_3', 0.0)),
            ai_result.get('ai_status', 'FAILED'),
            ai_result.get('description', ''),
            game_id,
            game_seq
        )
        
        cursor.execute(query, values)
        connection.commit()
        return True
        
    except Error as e:
        logger.error(f"게임 업데이트 실패: game_id={game_id}, game_seq={game_seq}, error={e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def load_model():
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
    """명사만 필터링"""
    valid_nouns = set()
    for word in words:
        if re.fullmatch(r'[가-힣]{2,}', word):
            try:
                pos = okt.pos(word, stem=True, norm=True)
                if len(pos) == 1 and pos[0][1] == 'Noun':
                    valid_nouns.add(word)
            except:
                continue
    return list(valid_nouns)

def generate_wrong_options(answer_text: str, model: Word2Vec, max_vocab: int = 50000) -> Dict:
    """정답에 대한 오답 3개와 유사도 점수 생성"""
    try:
        # 모델에서 정답 단어 확인
        if answer_text not in model.wv.key_to_index:
            return {
                "status": "FAILED",
                "error": f"'{answer_text}'는 모델에 존재하지 않습니다."
            }
        
        query_vec = model.wv[answer_text]
        
        # 후보 단어 선정
        vocab_words = list(model.wv.key_to_index)[:max_vocab]
        candidate_words = [w for w in vocab_words if w != answer_text]
        nouns = filter_nouns(candidate_words)
        
        if len(nouns) < 3:
            return {
                "status": "FAILED",
                "error": "후보 명사가 부족합니다."
            }
        
        # 유사도 계산
        vecs = model.wv[nouns]
        sims = np.dot(vecs, query_vec) / (np.linalg.norm(vecs, axis=1) * np.linalg.norm(query_vec) + 1e-10)
        
        # 유사도별 그룹화
        bins = {
            'high': [],    # 0.6~1.0
            'medium': [],  # 0.4~0.6
            'low': []      # 0.1~0.4
        }
        
        for w, s in zip(nouns, sims):
            if 0.6 <= s <= 1.0:
                bins['high'].append((w, s))
            elif 0.4 <= s < 0.6:
                bins['medium'].append((w, s))
            elif 0.1 <= s < 0.4:
                bins['low'].append((w, s))
        
        # 각 그룹에서 1개씩 선택
        selected = []
        for group_name in ['high', 'medium', 'low']:
            group = bins[group_name]
            if group:
                # 유사도 순으로 정렬 후 상위 후보 중 랜덤 선택
                sorted_group = sorted(group, key=lambda x: -x[1])
                top_candidates = sorted_group[:min(5, len(sorted_group))]  # 상위 5개 중 랜덤
                selected.append(random.choice(top_candidates))
        
        # 3개가 안 되면 전체에서 랜덤 선택
        if len(selected) < 3:
            all_candidates = [(w, s) for w, s in zip(nouns, sims) if w not in [item[0] for item in selected]]
            additional = random.sample(all_candidates, min(3 - len(selected), len(all_candidates)))
            selected.extend(additional)
        
        # 정확히 3개 선택
        selected = selected[:3]
        
        return {
            "status": "COMPLETED",
            "wrong_options": [item[0] for item in selected],
            "similarity_scores": [round(float(item[1]), 4) for item in selected]
        }
        
    except Exception as e:
        logger.error(f"오답 생성 중 오류: {str(e)}")
        return {
            "status": "FAILED",
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    if not load_model():
        logger.error("모델 로드 실패 - 서버를 종료합니다.")
        raise Exception("모델 로드 실패")

@app.get("/")
async def root():
    return {"message": "Memory Forest AI Service"}

@app.get("/health")
async def health_check():
    """헬스 체크"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # 데이터베이스 연결 확인
    connection = get_db_connection()
    db_connected = connection is not None
    if connection and connection.is_connected():
        connection.close()
    
    return {
        "status": "healthy", 
        "model_loaded": True,
        "database_connected": db_connected
    }

@app.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_answer(request: AIAnalysisRequest):
    """정답 텍스트 분석 및 오답 생성"""
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    logger.info(f"AI 분석 요청: game_id={request.game_id}, game_seq={request.game_seq}, answer_text={request.answer_text}")
    
    # 오답 생성
    result = generate_wrong_options(request.answer_text, model)
    
    if result["status"] == "FAILED":
        logger.error(f"AI 분석 실패: {result.get('error', 'Unknown error')}")
        return AIAnalysisResponse(
            game_id=request.game_id,
            game_seq=request.game_seq,
            wrong_option_1="",
            wrong_option_2="",
            wrong_option_3="",
            similarity_score_1=0.0,
            similarity_score_2=0.0,
            similarity_score_3=0.0,
            ai_status="FAILED",
            description=result.get('error', 'AI 분석 실패')
        )
    
    wrong_options = result["wrong_options"]
    similarity_scores = result["similarity_scores"]
    
    logger.info(f"AI 분석 완료: game_id={request.game_id}, game_seq={request.game_seq}, options={wrong_options}")
    
    return AIAnalysisResponse(
        game_id=request.game_id,
        game_seq=request.game_seq,
        wrong_option_1=wrong_options[0] if len(wrong_options) > 0 else "",
        wrong_option_2=wrong_options[1] if len(wrong_options) > 1 else "",
        wrong_option_3=wrong_options[2] if len(wrong_options) > 2 else "",
        similarity_score_1=similarity_scores[0] if len(similarity_scores) > 0 else 0.0,
        similarity_score_2=similarity_scores[1] if len(similarity_scores) > 1 else 0.0,
        similarity_score_3=similarity_scores[2] if len(similarity_scores) > 2 else 0.0,
        ai_status="COMPLETED",
        description="AI 분석 완료"
    )

@app.post("/batch/process")
async def batch_process(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    """배치로 AI 분석이 필요한 게임들 처리"""
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    games = get_games_needing_analysis(request.limit)
    
    if not games:
        return {"message": "처리할 게임이 없습니다.", "processed_count": 0}
    
    # 백그라운드에서 처리
    background_tasks.add_task(process_games_batch, games)
    
    return {
        "message": f"{len(games)}개 게임의 AI 분석을 시작합니다.",
        "games_to_process": len(games)
    }

async def process_games_batch(games: List[dict]):
    """게임들을 배치로 처리"""
    processed_count = 0
    failed_count = 0
    
    for game in games:
        try:
            result = generate_wrong_options(game['answer_text'], model)
            
            ai_result = {
                'wrong_option_1': result['wrong_options'][0] if result['status'] == 'COMPLETED' and len(result['wrong_options']) > 0 else '',
                'wrong_option_2': result['wrong_options'][1] if result['status'] == 'COMPLETED' and len(result['wrong_options']) > 1 else '',
                'wrong_option_3': result['wrong_options'][2] if result['status'] == 'COMPLETED' and len(result['wrong_options']) > 2 else '',
                'similarity_score_1': result['similarity_scores'][0] if result['status'] == 'COMPLETED' and len(result['similarity_scores']) > 0 else 0.0,
                'similarity_score_2': result['similarity_scores'][1] if result['status'] == 'COMPLETED' and len(result['similarity_scores']) > 1 else 0.0,
                'similarity_score_3': result['similarity_scores'][2] if result['status'] == 'COMPLETED' and len(result['similarity_scores']) > 2 else 0.0,
                'ai_status': result['status'],
                'description': result.get('error', 'AI 분석 완료') if result['status'] == 'FAILED' else 'AI 분석 완료'
            }
            
            if update_game_ai_result(game['game_id'], game['game_seq'], ai_result):
                processed_count += 1
                logger.info(f"게임 처리 완료: {game['game_id']}-{game['game_seq']}")
            else:
                failed_count += 1
                logger.error(f"게임 업데이트 실패: {game['game_id']}-{game['game_seq']}")
                
            # API 과부하 방지를 위한 딜레이
            await asyncio.sleep(1)
            
        except Exception as e:
            failed_count += 1
            logger.error(f"게임 처리 중 오류: game_id={game['game_id']}, game_seq={game['game_seq']}, error={e}")
    
    logger.info(f"배치 처리 완료: 성공={processed_count}, 실패={failed_count}")

@app.get("/batch/status")
async def batch_status():
    """배치 처리 상태 확인"""
    games_needing_analysis = get_games_needing_analysis(1000)  # 최대 1000개까지 조회
    
    return {
        "games_needing_analysis": len(games_needing_analysis),
        "model_loaded": model is not None,
        "database_connected": get_db_connection() is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)