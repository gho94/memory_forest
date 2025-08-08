# ai/api/analyze.py 수정 - 점수 변환 및 DB 저장 개선
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import asyncio
import logging
import numpy as np

from dto.ai_request import AIAnalysisRequest
from dto.ai_response import AIAnalysisResponse
from dto.batch_request import BatchProcessRequest
from services import ai_service
from db import repository

logger = logging.getLogger(__name__)
router = APIRouter()

def safe_score_convert(score):
    """안전한 점수 변환 함수 (numpy array 지원)"""
    try:
        if score is None:
            return 0
        
        logger.info(f"점수 변환: 원본={score}, 타입={type(score)}")
        
        # numpy array인 경우 첫 번째 원소 추출
        if hasattr(score, 'shape') and len(score.shape) > 0:
            logger.info(f"numpy array 감지: shape={score.shape}")
            if len(score) > 0:
                score = score[0]
            else:
                return 0
        
        # numpy scalar 타입을 Python 타입으로 변환
        if hasattr(score, 'item'):
            score = score.item()
            logger.info(f"numpy scalar -> Python: {score}")
        
        # list/tuple인 경우 첫 번째 원소
        if isinstance(score, (list, tuple)) and len(score) > 0:
            score = score[0]
        
        # float를 int로 변환 (0-1 범위를 0-100으로)
        if isinstance(score, (float, int)):
            if 0 <= score <= 1:
                result = max(0, min(100, round(float(score) * 100)))
            else:
                result = max(0, min(100, round(float(score))))
            logger.info(f"최종 변환: {score} -> {result}")
            return result
        else:
            logger.warning(f"예상하지 못한 점수 타입: {type(score)}")
            return 0
    except Exception as e:
        logger.error(f"점수 변환 오류: {e}", exc_info=True)
        return 0

def check_models_loaded():
    """모델 로드 상태를 안전하게 확인하는 함수"""
    try:
        # ai_service에 models 속성이 있는지 확인
        if hasattr(ai_service, 'models') and ai_service.models:
            return any(ai_service.models.values())
        # 기본 model 속성이 있는지 확인  
        elif hasattr(ai_service, 'model') and ai_service.model:
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"모델 상태 확인 중 오류: {e}")
        return False

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_answer(request: AIAnalysisRequest):
    """답변 분석 (난이도별 지원) - DB 저장 순서 수정"""
    
    # 요청 정보 상세 로깅
    logger.info("=== AI 분석 요청 수신 ===")
    logger.info(f"Request 객체: {request}")
    logger.info(f"game_id: {request.game_id}")
    logger.info(f"game_seq: {request.game_seq}") 
    logger.info(f"answer_text: '{request.answer_text}'")
    logger.info(f"difficulty_level: {request.difficulty_level}")
    
    # 모델 로드 확인
    if not check_models_loaded():
        logger.error("모델이 로드되지 않았습니다.")
        response = AIAnalysisResponse(
            game_id=request.game_id,
            game_seq=request.game_seq,
            wrong_option_1="",
            wrong_option_2="",
            wrong_option_3="",
            wrong_score_1=0,
            wrong_score_2=0,
            wrong_score_3=0,
            ai_status="FAILED",
            description="Model not loaded"
        )
        return response.model_dump(by_alias=True)

    difficulty = getattr(request, 'difficulty_level', 'NORMAL')
    
    logger.info(f"AI 분석 시작: game_id={request.game_id}, game_seq={request.game_seq}, "
                f"answer_text='{request.answer_text}', difficulty={difficulty}")

    try:
        # 난이도별 분석 시도
        result = ai_service.generate_wrong_options_with_difficulty(request.answer_text, difficulty)
        
        logger.info(f"AI 서비스 결과: {result}")

        if result["status"] == "FAILED":
            logger.error(f"AI 분석 실패: {result.get('error', 'Unknown error')}")
            response = AIAnalysisResponse(
                game_id=request.game_id,
                game_seq=request.game_seq,
                wrong_option_1="",
                wrong_option_2="",
                wrong_option_3="",
                wrong_score_1=0,
                wrong_score_2=0,
                wrong_score_3=0,
                ai_status="FAILED",
                description=result.get('error', 'AI 분석 실패')
            )
            
            # ✅ 실패한 경우도 DB에 저장 (API 응답 전에!)
            try:
                db_data = response.to_db_format()
                logger.info(f"💾 실패 결과 DB 저장 시도: {db_data}")
                
                if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                    logger.info(f"✅ 실패 결과 DB 저장 성공: {request.game_id}-{request.game_seq}")
                else:
                    logger.error(f"❌ 실패 결과 DB 저장 실패: {request.game_id}-{request.game_seq}")
            except Exception as db_error:
                logger.error(f"❌ 실패 결과 DB 저장 중 예외: {db_error}", exc_info=True)
            
            return response.model_dump(by_alias=True)

        wrong_options = result["wrong_options"]
        wrong_scores = result["wrong_scores"]
        difficulty_used = result.get("difficulty_used", difficulty)

        logger.info(f"AI 분석 완료 (난이도: {difficulty_used})")
        logger.info(f"wrong_options: {wrong_options}")
        logger.info(f"wrong_scores 원본: {wrong_scores} (타입: {[type(s) for s in wrong_scores]})")

        # 점수를 0-100 정수로 변환
        converted_scores = [safe_score_convert(score) for score in wrong_scores]
        logger.info(f"wrong_scores 변환됨: {converted_scores}")

        # 안전한 인덱스 접근으로 응답 생성
        response = AIAnalysisResponse(
            game_id=request.game_id,
            game_seq=request.game_seq,
            wrong_option_1=wrong_options[0] if len(wrong_options) > 0 else "",
            wrong_option_2=wrong_options[1] if len(wrong_options) > 1 else "",
            wrong_option_3=wrong_options[2] if len(wrong_options) > 2 else "",
            wrong_score_1=converted_scores[0] if len(converted_scores) > 0 else 0,
            wrong_score_2=converted_scores[1] if len(converted_scores) > 1 else 0,
            wrong_score_3=converted_scores[2] if len(converted_scores) > 2 else 0,
            ai_status="COMPLETED",
            description=f"AI 분석 완료 (난이도: {difficulty_used})"
        )
        
        logger.info("=== AI 분석 응답 생성 완료 ===")
        logger.info(f"최종 응답: {response}")
        
        # ✅ 중요: DB에 결과 저장 (API 응답 전에!)
        db_save_success = False
        try:
            db_data = response.to_db_format()
            logger.info(f"💾 DB 저장 시도 (응답 전): {db_data}")
            
            if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                logger.info(f"✅ DB 저장 성공: {request.game_id}-{request.game_seq}")
                db_save_success = True
            else:
                logger.error(f"❌ DB 저장 실패: {request.game_id}-{request.game_seq}")
                
        except Exception as db_error:
            logger.error(f"❌ DB 저장 중 예외: {db_error}", exc_info=True)
        
        # DB 저장 결과를 응답에 반영
        if not db_save_success:
            logger.warning("⚠️ DB 저장 실패로 인해 상태를 FAILED로 변경")
            response.ai_status = "FAILED"
            response.description = f"{response.description} (단, DB 저장 실패)"
        
        # 응답을 dict로 변환하여 Java가 기대하는 camelCase로 반환
        response_dict = response.model_dump(by_alias=True)
        logger.info(f"📤 최종 응답 JSON: {response_dict}")
        
        return response_dict
        
    except Exception as e:
        logger.error(f"AI 분석 중 예외 발생: {e}", exc_info=True)
        error_response = AIAnalysisResponse(
            game_id=request.game_id,
            game_seq=request.game_seq,
            wrong_option_1="",
            wrong_option_2="",
            wrong_option_3="",
            wrong_score_1=0,
            wrong_score_2=0,
            wrong_score_3=0,
            ai_status="FAILED",
            description=f"AI 분석 중 예외 발생: {str(e)}"
        )
        
        # ✅ 예외 발생한 경우도 DB에 저장 (API 응답 전에!)
        try:
            db_data = error_response.to_db_format()
            logger.info(f"💾 예외 결과 DB 저장 시도: {db_data}")
            
            if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                logger.info(f"✅ 예외 결과 DB 저장 성공: {request.game_id}-{request.game_seq}")
            else:
                logger.error(f"❌ 예외 결과 DB 저장 실패: {request.game_id}-{request.game_seq}")
        except Exception as db_error:
            logger.error(f"❌ 예외 결과 DB 저장 중 예외: {db_error}", exc_info=True)
        
        return error_response.model_dump(by_alias=True)
    

@router.post("/batch/process")
async def batch_process(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    """배치 처리 - DB 저장 형식 개선"""
    if not check_models_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")

    games = repository.get_games_needing_analysis(request.limit)

    if not games:
        return {"message": "처리할 게임이 없습니다.", "processed_count": 0}

    background_tasks.add_task(process_games_batch, games)

    return {
        "message": f"{len(games)}개 게임의 AI 분석을 시작합니다.",
        "games_to_process": len(games)
    }

async def process_games_batch(games: List[dict]):
    """기존 배치 처리 - DB 저장 형식 개선"""
    processed_count = 0
    failed_count = 0

    for game in games:
        try:
            # 게임의 난이도 정보 가져오기
            difficulty = game.get('difficulty_level', 'NORMAL')
            
            # 난이도별 분석
            result = ai_service.generate_wrong_options_with_difficulty(game['answer_text'], difficulty)

            if result['status'] == 'COMPLETED':
                # 오답 선택지 검증 및 정리
                wrong_options = validate_and_clean_options(result['wrong_options'])
                
                # 점수를 0-100 정수로 변환
                converted_scores = [safe_score_convert(score) for score in result['wrong_scores']]
                
                ai_result = {
                    'wrong_option_1': wrong_options[0] if len(wrong_options) > 0 else '',
                    'wrong_option_2': wrong_options[1] if len(wrong_options) > 1 else '',
                    'wrong_option_3': wrong_options[2] if len(wrong_options) > 2 else '',
                    'wrong_score_1': converted_scores[0] if len(converted_scores) > 0 else 0,
                    'wrong_score_2': converted_scores[1] if len(converted_scores) > 1 else 0,
                    'wrong_score_3': converted_scores[2] if len(converted_scores) > 2 else 0,
                    'ai_status': 'COMPLETED',
                    'description': f"AI 분석 완료 (난이도: {result.get('difficulty_used', difficulty)})"
                }
            else:
                ai_result = {
                    'wrong_option_1': '',
                    'wrong_option_2': '',
                    'wrong_option_3': '',
                    'wrong_score_1': 0,
                    'wrong_score_2': 0,
                    'wrong_score_3': 0,
                    'ai_status': 'FAILED',
                    'description': result.get('error', 'AI 분석 실패')
                }

            if repository.update_game_ai_result(game['game_id'], game['game_seq'], ai_result):
                processed_count += 1
                logger.info(f"게임 처리 성공: {game['game_id']}-{game['game_seq']} (난이도: {difficulty})")
                logger.info(f"저장된 점수: {[ai_result['wrong_score_1'], ai_result['wrong_score_2'], ai_result['wrong_score_3']]}")
            else:
                logger.error(f"게임 DB 업데이트 실패: {game['game_id']}-{game['game_seq']}")
                failed_count += 1

            await asyncio.sleep(1)

        except Exception as e:
            failed_count += 1
            logger.error(f"게임 처리 중 예외 발생: game_id={game['game_id']}, game_seq={game['game_seq']}, 에러={e}", exc_info=True)

    logger.info(f"배치 처리 완료: 성공={processed_count}, 실패={failed_count}")

async def process_games_batch_with_difficulty(games: List[dict], difficulty: str):
    """난이도별 배치 처리 - DB 저장 형식 개선"""
    processed_count = 0
    failed_count = 0

    logger.info(f"난이도 '{difficulty}' 배치 처리 시작: {len(games)}개 게임")

    for game in games:
        try:
            result = ai_service.generate_wrong_options_with_difficulty(game['answer_text'], difficulty)

            if result['status'] == 'COMPLETED':
                # 점수를 0-100 정수로 변환
                converted_scores = [safe_score_convert(score) for score in result['wrong_scores']]
                
                ai_result = {
                    'wrong_option_1': result['wrong_options'][0] if len(result['wrong_options']) > 0 else '',
                    'wrong_option_2': result['wrong_options'][1] if len(result['wrong_options']) > 1 else '',
                    'wrong_option_3': result['wrong_options'][2] if len(result['wrong_options']) > 2 else '',
                    'wrong_score_1': converted_scores[0] if len(converted_scores) > 0 else 0,
                    'wrong_score_2': converted_scores[1] if len(converted_scores) > 1 else 0,
                    'wrong_score_3': converted_scores[2] if len(converted_scores) > 2 else 0,
                    'ai_status': 'COMPLETED',
                    'description': f"난이도별 AI 분석 완료 (난이도: {difficulty})"
                }
            else:
                ai_result = {
                    'wrong_option_1': '',
                    'wrong_option_2': '',
                    'wrong_option_3': '',
                    'wrong_score_1': 0,
                    'wrong_score_2': 0,
                    'wrong_score_3': 0,
                    'ai_status': 'FAILED',
                    'description': f"난이도 '{difficulty}' AI 분석 실패: {result.get('error', '알 수 없는 오류')}"
                }

            if repository.update_game_ai_result(game['game_id'], game['game_seq'], ai_result):
                processed_count += 1
                logger.info(f"난이도별 게임 처리 성공: {game['game_id']}-{game['game_seq']} (난이도: {difficulty})")
                logger.info(f"저장된 점수: {[ai_result['wrong_score_1'], ai_result['wrong_score_2'], ai_result['wrong_score_3']]}")
            else:
                logger.error(f"난이도별 게임 DB 업데이트 실패: {game['game_id']}-{game['game_seq']}")
                failed_count += 1

            await asyncio.sleep(1)

        except Exception as e:
            failed_count += 1
            logger.error(f"난이도별 게임 처리 중 예외 발생: game_id={game['game_id']}, game_seq={game['game_seq']}, "
                        f"difficulty={difficulty}, 에러={e}", exc_info=True)

    logger.info(f"난이도 '{difficulty}' 배치 처리 완료: 성공={processed_count}, 실패={failed_count}")

# 나머지 엔드포인트들은 동일하게 유지...
@router.post("/batch/process-by-difficulty")
async def batch_process_by_difficulty(
    difficulty: str,
    limit: int = 50,
    background_tasks: BackgroundTasks = None
):
    """난이도별 배치 처리"""
    if not check_models_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")

    # 특정 난이도의 게임들만 조회
    games = repository.get_games_needing_analysis_by_difficulty(difficulty, limit)

    if not games:
        return {"message": f"처리할 {difficulty} 난이도 게임이 없습니다.", "processed_count": 0}

    background_tasks.add_task(process_games_batch_with_difficulty, games, difficulty)

    return {
        "message": f"{len(games)}개 {difficulty} 난이도 게임의 AI 분석을 시작합니다.",
        "games_to_process": len(games),
        "difficulty": difficulty
    }

@router.get("/models/status")
async def get_models_status():
    """모든 난이도 모델의 상태 조회"""
    status = {}
    
    for difficulty in ['EASY', 'NORMAL', 'HARD', 'EXPERT']:
        try:
            if hasattr(ai_service, 'get_model_for_difficulty'):
                model_info = ai_service.get_model_for_difficulty(difficulty)
                if model_info:
                    vocab_size = len(model_info['model'].wv)
                    vector_size = model_info['model'].vector_size
                    status[difficulty] = {
                        "loaded": True,
                        "vocab_size": vocab_size,
                        "vector_size": vector_size,
                        "vocab_limit": model_info['vocab_limit'],
                        "similarity_threshold": model_info['similarity_threshold']
                    }
                else:
                    status[difficulty] = {
                        "loaded": False,
                        "error": "Model not found"
                    }
            else:
                status[difficulty] = {
                    "loaded": False,
                    "error": "get_model_for_difficulty method not available"
                }
        except Exception as e:
            status[difficulty] = {
                "loaded": False,
                "error": str(e)
            }
    
    return {
        "models_status": status,
        "default_model_loaded": hasattr(ai_service, 'model') and ai_service.model is not None,
        "models_available": check_models_loaded()
    }

@router.post("/models/reload/{difficulty}")
async def reload_difficulty_model(difficulty: str):
    """특정 난이도 모델 리로드"""
    if difficulty not in ['EASY', 'NORMAL', 'HARD', 'EXPERT']:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")
    
    try:
        # 기존 모델 해제
        if hasattr(ai_service, 'models') and difficulty in ai_service.models:
            ai_service.models[difficulty] = None
        
        # 새 모델 로드
        if hasattr(ai_service, 'load_models') and ai_service.load_models():
            if hasattr(ai_service, 'get_model_for_difficulty'):
                model_info = ai_service.get_model_for_difficulty(difficulty)
                if model_info:
                    vocab_size = len(model_info['model'].wv)
                    logger.info(f"{difficulty} 모델 리로드 성공: 어휘 크기 {vocab_size}")
                    return {
                        "status": "success",
                        "message": f"{difficulty} 모델이 성공적으로 리로드되었습니다.",
                        "vocab_size": vocab_size,
                        "difficulty": difficulty
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"{difficulty} 모델 리로드 실패")
            else:
                raise HTTPException(status_code=500, detail="get_model_for_difficulty method not available")
        else:
            raise HTTPException(status_code=500, detail="모델 리로드 실패")
                  
    except Exception as e:
        logger.error(f"{difficulty} 모델 리로드 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"{difficulty} 모델 리로드 오류: {str(e)}")

@router.get("/difficulties")
async def get_supported_difficulties():
    """지원하는 난이도 목록 조회"""
    return {
        "supported_difficulties": ['EASY', 'NORMAL', 'HARD', 'EXPERT'],
        "difficulty_descriptions": {
            "EASY": "초급 - 유사도가 낮은 단어들로 구성하여 구분하기 쉬움",
            "NORMAL": "중급 - 적절한 난이도의 유사 단어들로 구성",
            "HARD": "고급 - 유사도가 높은 단어들로 구성하여 구분하기 어려움", 
            "EXPERT": "전문가 - 매우 높은 유사도의 단어들로 구성하여 가장 어려움"
        }
    }

    
@router.post("/debug/test-ai-service/{answer_text}")
async def debug_test_ai_service(answer_text: str, difficulty: str = "NORMAL"):
    """디버깅용: AI 서비스 직접 테스트"""
    logger.info(f"🧪 AI 서비스 직접 테스트: '{answer_text}' (난이도: {difficulty})")
    
    try:
        result = ai_service.generate_wrong_options_with_difficulty(answer_text, difficulty)
        
        logger.info(f"🧪 AI 서비스 테스트 결과: {result}")
        
        # 결과 상세 분석
        analysis = {
            "raw_result": result,
            "result_type": type(result),
            "status": result.get("status"),
            "wrong_options": result.get("wrong_options", []),
            "wrong_options_types": [type(opt) for opt in result.get("wrong_options", [])],
            "wrong_scores": result.get("wrong_scores", []),
            "wrong_scores_types": [type(score) for score in result.get("wrong_scores", [])],
            "cleaned_options": validate_and_clean_options(result.get("wrong_options", [])) if result.get("status") == "COMPLETED" else [],
            "converted_scores": [safe_score_convert(score) for score in result.get("wrong_scores", [])] if result.get("status") == "COMPLETED" else []
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"🧪 AI 서비스 테스트 실패: {e}", exc_info=True)
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.post("/debug/test-update/{game_id}/{game_seq}")
async def debug_test_update(game_id: str, game_seq: int):
    """디버깅용: 직접 DB 업데이트 테스트"""
    logger.info(f"🧪 디버그 업데이트 테스트: {game_id}-{game_seq}")
    
    # 1. 직접 업데이트 테스트
    result = repository.test_direct_update(game_id, game_seq)
    
    return {
        "message": f"직접 업데이트 테스트 {'성공' if result else '실패'}",
        "game_id": game_id,
        "game_seq": game_seq,
        "success": result
    }



@router.get("/debug/game-info/{game_id}/{game_seq}")
async def debug_game_info(game_id: str, game_seq: int):
    """디버깅용: 게임 정보 상세 조회"""
    from db.connection import get_db_connection
    
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="DB connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 게임 상세 정보 조회
        query = """
        SELECT gd.*, gm.difficulty_level_code, gm.game_name
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.game_id = %s AND gd.game_seq = %s
        """
        cursor.execute(query, (game_id, game_seq))
        game_info = cursor.fetchone()
        
        if not game_info:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # 테이블 구조 정보
        cursor.execute("DESCRIBE game_detail")
        table_structure = cursor.fetchall()
        
        return {
            "game_info": game_info,
            "table_structure": table_structure
        }
        
    except Exception as e:
        logger.error(f"게임 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.post("/debug/manual-update/{game_id}/{game_seq}")
async def debug_manual_update(game_id: str, game_seq: int):
    """디버깅용: 수동으로 특정 값 업데이트"""
    from db.connection import get_db_connection
    
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="DB connection failed")
    
    try:
        cursor = connection.cursor()
        
        # 수동 업데이트
        query = """
        UPDATE game_detail 
        SET wrong_option_1 = 'TEST1',
            wrong_option_2 = 'TEST2',
            wrong_option_3 = 'TEST3',
            wrong_score_1 = 10,
            wrong_score_2 = 20,
            wrong_score_3 = 30,
            ai_status_code = 'A10002',
            description = 'Manual test update',
            ai_processed_at = NOW()
        WHERE game_id = %s AND game_seq = %s
        """
        
        logger.info(f"🔧 수동 업데이트: {game_id}-{game_seq}")
        cursor.execute(query, (game_id, game_seq))
        rowcount = cursor.rowcount
        
        logger.info(f"🔧 수동 업데이트 rowcount: {rowcount}")
        connection.commit()
        logger.info("🔧 수동 업데이트 커밋 완료")
        
        # 결과 확인
        cursor.execute("SELECT * FROM game_detail WHERE game_id = %s AND game_seq = %s", (game_id, game_seq))
        updated_data = cursor.fetchone()
        
        return {
            "message": f"수동 업데이트 {'성공' if rowcount > 0 else '실패'}",
            "rowcount": rowcount,
            "updated_data": updated_data
        }
        
    except Exception as e:
        logger.error(f"수동 업데이트 실패: {e}")
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/debug/check-columns")
async def debug_check_columns():
    """디버깅용: game_detail 테이블 컬럼 확인"""
    from db.connection import get_db_connection
    
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="DB connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 테이블 구조 확인
        cursor.execute("DESCRIBE game_detail")
        columns = cursor.fetchall()
        
        # 인덱스 확인
        cursor.execute("SHOW INDEX FROM game_detail")
        indexes = cursor.fetchall()
        
        # 샘플 데이터 확인
        cursor.execute("SELECT * FROM game_detail LIMIT 5")
        sample_data = cursor.fetchall()
        
        return {
            "columns": columns,
            "indexes": indexes,
            "sample_data": sample_data
        }
        
    except Exception as e:
        logger.error(f"컬럼 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# 기존 analyze 함수에 추가 디버깅
@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_answer(request: AIAnalysisRequest):
    """답변 분석 (난이도별 지원) - 디버깅 강화"""
    
    # 요청 정보 상세 로깅
    logger.info("=== AI 분석 요청 수신 ===")
    logger.info(f"Request 객체: {request}")
    logger.info(f"game_id: {request.game_id}")
    logger.info(f"game_seq: {request.game_seq}") 
    logger.info(f"answer_text: '{request.answer_text}'")
    logger.info(f"difficulty_level: {request.difficulty_level}")
    
    # 모델 로드 확인
    if not check_models_loaded():
        logger.error("모델이 로드되지 않았습니다.")
        response = AIAnalysisResponse(
            game_id=request.game_id,
            game_seq=request.game_seq,
            wrong_option_1="MODEL_NOT_LOADED",
            wrong_option_2="MODEL_NOT_LOADED", 
            wrong_option_3="MODEL_NOT_LOADED",
            wrong_score_1=0,
            wrong_score_2=0,
            wrong_score_3=0,
            ai_status="FAILED",
            description="Model not loaded"
        )
        
        # 실패한 경우도 DB에 저장
        try:
            db_data = response.to_db_format()
            logger.info(f"💾 모델 미로드 결과 DB 저장: {db_data}")
            
            if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                logger.info(f"✅ 모델 미로드 결과 DB 저장 성공")
            else:
                logger.error(f"❌ 모델 미로드 결과 DB 저장 실패")
        except Exception as db_error:
            logger.error(f"❌ 모델 미로드 결과 DB 저장 중 예외: {db_error}")
        
        return response.model_dump(by_alias=True)

    difficulty = getattr(request, 'difficulty_level', 'NORMAL')
    
    logger.info(f"AI 분석 시작: game_id={request.game_id}, game_seq={request.game_seq}, "
                f"answer_text='{request.answer_text}', difficulty={difficulty}")

    try:
        # 난이도별 분석 시도
        result = ai_service.generate_wrong_options_with_difficulty(request.answer_text, difficulty)
        
        logger.info(f"🔍 AI 서비스 원본 결과: {result}")
        logger.info(f"🔍 AI 서비스 결과 타입: {type(result)}")

        if result["status"] == "FAILED":
            logger.error(f"AI 분석 실패: {result.get('error', 'Unknown error')}")
            
            # 실패 시에도 의미있는 더미 데이터 제공 (디버깅용)
            response = AIAnalysisResponse(
                game_id=request.game_id,
                game_seq=request.game_seq,
                wrong_option_1=f"FAILED_OPTION_1_{request.answer_text[:10]}",
                wrong_option_2=f"FAILED_OPTION_2_{request.answer_text[:10]}",
                wrong_option_3=f"FAILED_OPTION_3_{request.answer_text[:10]}",
                wrong_score_1=10,
                wrong_score_2=20,
                wrong_score_3=30,
                ai_status="FAILED",
                description=result.get('error', 'AI 분석 실패')
            )
            
            # ✅ 실패한 경우도 DB에 저장 (API 응답 전에!)
            try:
                db_data = response.to_db_format()
                logger.info(f"💾 실패 결과 DB 저장 시도: {db_data}")
                
                if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                    logger.info(f"✅ 실패 결과 DB 저장 성공: {request.game_id}-{request.game_seq}")
                else:
                    logger.error(f"❌ 실패 결과 DB 저장 실패: {request.game_id}-{request.game_seq}")
            except Exception as db_error:
                logger.error(f"❌ 실패 결과 DB 저장 중 예외: {db_error}", exc_info=True)
            
            return response.model_dump(by_alias=True)

        # 성공한 경우 데이터 추출 및 검증
        wrong_options_raw = result.get("wrong_options", [])
        wrong_scores_raw = result.get("wrong_scores", [])
        difficulty_used = result.get("difficulty_used", difficulty)

        logger.info(f"🔍 AI 분석 완료 (난이도: {difficulty_used})")
        logger.info(f"🔍 wrong_options 원본: {wrong_options_raw} (타입: {type(wrong_options_raw)})")
        logger.info(f"🔍 wrong_scores 원본: {wrong_scores_raw} (타입: {[type(s) for s in wrong_scores_raw] if isinstance(wrong_scores_raw, list) else type(wrong_scores_raw)})")

        # 오답 선택지 검증 및 정리
        wrong_options = validate_and_clean_options(wrong_options_raw)
        logger.info(f"🔍 wrong_options 정리됨: {wrong_options}")

        # 점수를 0-100 정수로 변환
        converted_scores = [safe_score_convert(score) for score in wrong_scores_raw]
        logger.info(f"🔍 wrong_scores 변환됨: {converted_scores}")

        # 응답 생성 - 더 안전한 방식
        response = AIAnalysisResponse(
            game_id=request.game_id,
            game_seq=request.game_seq,
            wrong_option_1=wrong_options[0] if len(wrong_options) > 0 else "EMPTY_OPTION_1",
            wrong_option_2=wrong_options[1] if len(wrong_options) > 1 else "EMPTY_OPTION_2",
            wrong_option_3=wrong_options[2] if len(wrong_options) > 2 else "EMPTY_OPTION_3",
            wrong_score_1=converted_scores[0] if len(converted_scores) > 0 else 0,
            wrong_score_2=converted_scores[1] if len(converted_scores) > 1 else 0,
            wrong_score_3=converted_scores[2] if len(converted_scores) > 2 else 0,
            ai_status="COMPLETED",
            description=f"AI 분석 완료 (난이도: {difficulty_used})"
        )
        
        logger.info("=== AI 분석 응답 생성 완료 ===")
        logger.info(f"🔍 최종 응답 객체: {response}")
        
        # ✅ 중요: DB에 결과 저장 (API 응답 전에!)
        db_save_success = False
        try:
            db_data = response.to_db_format()
            logger.info(f"💾 DB 저장 시도 (응답 전): {db_data}")
            logger.info(f"💾 DB 저장 데이터 타입 확인:")
            for key, value in db_data.items():
                logger.info(f"  - {key}: '{value}' (타입: {type(value)})")
            
            if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                logger.info(f"✅ DB 저장 성공: {request.game_id}-{request.game_seq}")
                db_save_success = True
            else:
                logger.error(f"❌ DB 저장 실패: {request.game_id}-{request.game_seq}")
                
        except Exception as db_error:
            logger.error(f"❌ DB 저장 중 예외: {db_error}", exc_info=True)
        
        # DB 저장 결과를 응답에 반영
        if not db_save_success:
            logger.warning("⚠️ DB 저장 실패로 인해 상태를 FAILED로 변경")
            response.ai_status = "FAILED"
            response.description = f"{response.description} (단, DB 저장 실패)"
        
        # 응답을 dict로 변환하여 Java가 기대하는 camelCase로 반환
        response_dict = response.model_dump(by_alias=True)
        logger.info(f"📤 최종 응답 JSON: {response_dict}")
        
        return response_dict
        
    except Exception as e:
        logger.error(f"AI 분석 중 예외 발생: {e}", exc_info=True)
        error_response = AIAnalysisResponse(
            game_id=request.game_id,
            game_seq=request.game_seq,
            wrong_option_1=f"ERROR_OPTION_1_{str(e)[:20]}",
            wrong_option_2=f"ERROR_OPTION_2_{str(e)[:20]}",
            wrong_option_3=f"ERROR_OPTION_3_{str(e)[:20]}",
            wrong_score_1=0,
            wrong_score_2=0,
            wrong_score_3=0,
            ai_status="FAILED",
            description=f"AI 분석 중 예외 발생: {str(e)}"
        )
        
        # ✅ 예외 발생한 경우도 DB에 저장 (API 응답 전에!)
        try:
            db_data = error_response.to_db_format()
            logger.info(f"💾 예외 결과 DB 저장 시도: {db_data}")
            
            if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                logger.info(f"✅ 예외 결과 DB 저장 성공: {request.game_id}-{request.game_seq}")
            else:
                logger.error(f"❌ 예외 결과 DB 저장 실패: {request.game_id}-{request.game_seq}")
        except Exception as db_error:
            logger.error(f"❌ 예외 결과 DB 저장 중 예외: {db_error}", exc_info=True)
        
        return error_response.model_dump(by_alias=True)
    


def check_models_loaded():
    """모델 로드 상태를 안전하게 확인하는 함수"""
    try:
        # ai_service에 models 속성이 있는지 확인
        if hasattr(ai_service, 'models') and ai_service.models:
            return any(ai_service.models.values())
        # 기본 model 속성이 있는지 확인  
        elif hasattr(ai_service, 'model') and ai_service.model:
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"모델 상태 확인 중 오류: {e}")
        return False

def safe_score_convert(score):
    """안전한 점수 변환 함수 (numpy array 지원)"""
    try:
        if score is None:
            return 0
        
        logger.info(f"점수 변환: 원본={score}, 타입={type(score)}")
        
        # numpy array인 경우 첫 번째 원소 추출
        if hasattr(score, 'shape') and len(score.shape) > 0:
            logger.info(f"numpy array 감지: shape={score.shape}")
            if len(score) > 0:
                score = score[0]
            else:
                return 0
        
        # numpy scalar 타입을 Python 타입으로 변환
        if hasattr(score, 'item'):
            score = score.item()
            logger.info(f"numpy scalar -> Python: {score}")
        
        # list/tuple인 경우 첫 번째 원소
        if isinstance(score, (list, tuple)) and len(score) > 0:
            score = score[0]
        
        # float를 int로 변환 (0-1 범위를 0-100으로)
        if isinstance(score, (float, int)):
            if 0 <= score <= 1:
                result = max(0, min(100, round(float(score) * 100)))
            else:
                result = max(0, min(100, round(float(score))))
            logger.info(f"최종 변환: {score} -> {result}")
            return result
        else:
            logger.warning(f"예상하지 못한 점수 타입: {type(score)}")
            return 0
    except Exception as e:
        logger.error(f"점수 변환 오류: {e}", exc_info=True)
        return 0
    

def validate_and_clean_options(options):
    """오답 선택지 검증 및 정리"""
    cleaned_options = []
    
    for i, option in enumerate(options):
        try:
            # None이나 빈 값 처리
            if option is None:
                cleaned_option = ""
            elif isinstance(option, str):
                # 문자열 정리 (앞뒤 공백 제거, 특수문자 처리)
                cleaned_option = str(option).strip()
                # 너무 긴 문자열 자르기 (DB 필드 크기 고려)
                if len(cleaned_option) > 100:  # 예시: 100자 제한
                    cleaned_option = cleaned_option[:100]
            else:
                # 다른 타입은 문자열로 변환
                cleaned_option = str(option).strip()
            
            cleaned_options.append(cleaned_option)
            logger.info(f"선택지 {i+1} 정리: '{option}' -> '{cleaned_option}'")
            
        except Exception as e:
            logger.error(f"선택지 {i+1} 처리 중 오류: {e}")
            cleaned_options.append("")
    
    # 3개까지만 보장
    while len(cleaned_options) < 3:
        cleaned_options.append("")
    
    return cleaned_options[:3]