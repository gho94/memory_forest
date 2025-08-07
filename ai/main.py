# ai/main.py
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
    logger.info("🚀 AI Service 시작 중...")
    
    # 모델 로드
    logger.info("📦 Word2Vec 모델 로드 시도...")
    if not ai_service.load_model():
        logger.error("❌ 모델 로드 실패 - 서버를 종료합니다.")
        raise Exception("모델 로드 실패")
    logger.info("✅ Word2Vec 모델 로드 완료")
    
    # DB 연결 테스트
    logger.info("🔌 데이터베이스 연결 테스트 시도...")
    if connection.test_connection():
        logger.info("✅ 데이터베이스 연결 성공")
    else:
        logger.warning("⚠️ 데이터베이스 연결 실패 - 서비스는 계속 실행됩니다")
    
    logger.info("🎉 AI Service 시작 완료!")

@app.get("/")
async def root():
    return {"message": "Memory Forest AI Service"}

@app.get("/health")
async def health_check():
    try:
        # DB 연결 테스트
        db_conn = connection.get_db_connection()
        db_connected = False
        
        if db_conn:
            try:
                if db_conn.is_connected():
                    db_connected = True
                    logger.debug("🔌 Health check: DB 연결 OK")
                db_conn.close()
            except Exception as e:
                logger.warning(f"🔌 Health check: DB 연결 확인 중 오류: {e}")
        else:
            logger.warning("🔌 Health check: DB 연결 실패")
        
        # 모델 상태 확인
        model_loaded = ai_service.model is not None
        vocab_size = len(ai_service.model.wv) if model_loaded else 0
        
        health_status = {
            "status": "healthy" if (model_loaded and db_connected) else "degraded",
            "model_loaded": model_loaded,
            "database_connected": db_connected,
            "model_vocab_size": vocab_size,
            "timestamp": str(logging.Formatter().formatTime(logging.LogRecord(
                "", 0, "", 0, "", (), None)))
        }
        
        logger.info(f"💚 Health check: {health_status['status']} (모델: {model_loaded}, DB: {db_connected})")
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Health check 실패: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "model_loaded": False,
            "database_connected": False,
            "model_vocab_size": 0
        }

@app.get("/db/test")
async def test_db_connection():
    """데이터베이스 연결 테스트 전용 엔드포인트"""
    try:
        logger.info("🔍 DB 연결 테스트 시작...")
        
        # 기본 연결 테스트
        conn = connection.get_db_connection()
        if not conn:
            return {
                "status": "failed",
                "message": "데이터베이스 연결 실패",
                "config": {
                    "host": connection.DB_CONFIG['host'],
                    "port": connection.DB_CONFIG['port'],
                    "database": connection.DB_CONFIG['database'],
                    "user": connection.DB_CONFIG['user']
                }
            }
        
        # 연결 상태 확인
        if not conn.is_connected():
            conn.close()
            return {
                "status": "failed",
                "message": "데이터베이스가 연결되지 않음"
            }
        
        # 쿼리 테스트
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION(), DATABASE(), USER()")
        result = cursor.fetchone()
        
        # 테이블 존재 확인
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        logger.info("✅ DB 연결 테스트 성공")
        return {
            "status": "success",
            "message": "데이터베이스 연결 성공",
            "server_info": {
                "version": result[0] if result else "Unknown",
                "database": result[1] if result else "Unknown", 
                "user": result[2] if result else "Unknown"
            },
            "tables_count": len(tables),
            "config": {
                "host": connection.DB_CONFIG['host'],
                "port": connection.DB_CONFIG['port'],
                "database": connection.DB_CONFIG['database'],
                "user": connection.DB_CONFIG['user']
            }
        }
        
    except Exception as e:
        logger.error(f"❌ DB 연결 테스트 실패: {e}")
        return {
            "status": "error",
            "message": str(e),
            "config": {
                "host": connection.DB_CONFIG.get('host', 'Unknown'),
                "port": connection.DB_CONFIG.get('port', 'Unknown'),
                "database": connection.DB_CONFIG.get('database', 'Unknown'),
                "user": connection.DB_CONFIG.get('user', 'Unknown')
            }
        }

@app.post("/reload-model")
async def reload_model():
    """모델을 다시 로드하는 엔드포인트"""
    try:
        logger.info("🔄 모델 리로드 요청 받음")
        
        # 기존 모델 참조 해제
        ai_service.model = None
        
        # 새 모델 로드
        if ai_service.load_model():
            vocab_size = len(ai_service.model.wv) if ai_service.model else 0
            logger.info(f"✅ 모델 리로드 성공: 어휘 크기 {vocab_size}")
            return {
                "status": "success",
                "message": "모델이 성공적으로 리로드되었습니다.",
                "vocab_size": vocab_size
            }
        else:
            logger.error("❌ 모델 리로드 실패")
            raise HTTPException(status_code=500, detail="모델 리로드 실패")
            
    except Exception as e:
        logger.error(f"❌ 모델 리로드 중 오류: {e}")
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
    # 시작 전 DB 연결 테스트
    logger.info("🔍 서버 시작 전 DB 연결 테스트...")
    connection.test_connection()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)