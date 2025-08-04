import logging
import uvicorn
from fastapi import FastAPI, Request, HTTPException

from api import analyze
from services import ai_service
from db import connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Memory Forest AI Service", version="1.0.0")

app.include_router(analyze.router)

@app.on_event("startup")
async def startup_event():
    if not ai_service.load_model():
        logger.error("모델 로드 실패 - 서버를 종료합니다.")
        raise Exception("모델 로드 실패")

@app.get("/")
async def root():
    return {"message": "Memory Forest AI Service"}

@app.get("/health")
async def health_check():
    db_conn = connection.get_db_connection()
    db_connected = db_conn is not None
    if db_conn and db_conn.is_connected():
        db_conn.close()

    return {
        "status": "healthy",
        "model_loaded": ai_service.model is not None,
        "database_connected": db_connected,
        "model_vocab_size": len(ai_service.model.wv) if ai_service.model else 0
    }

@app.post("/reload-model")
async def reload_model():
    """모델을 다시 로드하는 엔드포인트"""
    try:
        logger.info("모델 리로드 요청 받음")
        
        # 기존 모델 참조 해제
        ai_service.model = None
        
        # 새 모델 로드
        if ai_service.load_model():
            vocab_size = len(ai_service.model.wv) if ai_service.model else 0
            logger.info(f"모델 리로드 성공: 어휘 크기 {vocab_size}")
            return {
                "status": "success",
                "message": "모델이 성공적으로 리로드되었습니다.",
                "vocab_size": vocab_size
            }
        else:
            logger.error("모델 리로드 실패")
            raise HTTPException(status_code=500, detail="모델 리로드 실패")
            
    except Exception as e:
        logger.error(f"모델 리로드 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"모델 리로드 오류: {str(e)}")

@app.get("/model/info")
async def get_model_info():
    """현재 로드된 모델 정보 조회"""
    if ai_service.model is None:
        return {
            "status": "no_model",
            "message": "모델이 로드되지 않았습니다."
        }
    
    try:
        vocab_size = len(ai_service.model.wv)
        vector_size = ai_service.model.vector_size
        
        # 샘플 단어들 확인
        sample_words = ["기쁨", "사랑", "행복", "슬픔", "화", "두려움"]
        available_words = [word for word in sample_words if word in ai_service.model.wv.key_to_index]
        
        return {
            "status": "loaded",
            "vocab_size": vocab_size,
            "vector_size": vector_size,
            "sample_words_available": available_words,
            "sample_words_missing": [word for word in sample_words if word not in available_words]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"모델 정보 조회 실패: {str(e)}"
        }

@app.middleware("http")
async def log_request(request: Request, call_next):
    # POST 요청만 로깅 (GET 요청은 너무 많음)
    if request.method == "POST":
        try:
            body = await request.body()
            logger.info(f"📥 {request.method} {request.url.path}: {body.decode('utf-8')[:200]}...")
        except:
            logger.info(f"📥 {request.method} {request.url.path}: 본문 읽기 실패")
    
    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)