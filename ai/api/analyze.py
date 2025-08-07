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
    """안전한 점수 변환 함수"""
    try:
        if score is None:
            return 0
        
        # numpy 타입을 Python 타입으로 변환
        if hasattr(score, 'item'):
            score = score.item()
        
        # float를 int로 변환 (0-1 범위를 0-100으로)
        if isinstance(score, (float, int)):
            if 0 <= score <= 1:
                return max(0, min(100, round(float(score) * 100)))
            else:
                return max(0, min(100, round(float(score))))
        else:
            logger.warning(f"예상하지 못한 점수 타입: {type(score)}")
            return 0
    except Exception as e:
        logger.error(f"점수 변환 오류: {e}")
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
    """답변 분석 (난이도별 지원) - MySQL 호환성 개선"""
    
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
        
        # 응답을 dict로 변환하여 Java가 기대하는 camelCase로 반환
        response_dict = response.model_dump(by_alias=True)
        logger.info(f"응답 JSON: {response_dict}")
        
        # ✅ 중요: DB에 결과 저장
        try:
            db_data = response.to_db_format()
            logger.info(f"DB 저장 시도: {db_data}")
            
            if repository.update_game_ai_result(request.game_id, request.game_seq, db_data):
                logger.info(f"✅ DB 저장 성공: {request.game_id}-{request.game_seq}")
            else:
                logger.error(f"❌ DB 저장 실패: {request.game_id}-{request.game_seq}")
        except Exception as db_error:
            logger.error(f"❌ DB 저장 중 예외: {db_error}", exc_info=True)
        
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