import logging
import uvicorn
from fastapi import FastAPI, Request

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
        "database_connected": db_connected
    }

@app.middleware("http")
async def log_request(request: Request, call_next):
    body = await request.body()
    logger.info(f"📥 요청 본문: {body.decode('utf-8')}")
    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
