from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import asyncio
import logging

from dto.ai_request import AIAnalysisRequest
from dto.ai_response import AIAnalysisResponse
from dto.batch_request import BatchProcessRequest
from services import ai_service
from db import repository

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_answer(request: AIAnalysisRequest):
    if ai_service.model is None:
        logger.error("모델이 로드되지 않았습니다.")
        raise HTTPException(status_code=503, detail="Model not loaded")

    logger.info(f"AI 분석 요청: game_id={request.game_id}, game_seq={request.game_seq}, answer_text={request.answer_text}")

    result = ai_service.generate_wrong_options(request.answer_text, ai_service.model)

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

    logger.info(f"AI 분석 완료: options={wrong_options}, scores={similarity_scores}")

    # 응답 생성 시 필드명을 정확히 맞춰줍니다
    return AIAnalysisResponse(
        game_id=request.game_id,           # snake_case로 전달
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

@router.post("/batch/process")
async def batch_process(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    if ai_service.model is None:
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
    processed_count = 0
    failed_count = 0

    for game in games:
        try:
            result = ai_service.generate_wrong_options(game['answer_text'], ai_service.model)
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

            if repository.update_game_ai_result(game['game_id'], game['game_seq'], ai_result):
                processed_count += 1
                logger.info(f"게임 처리 성공: {game['game_id']}-{game['game_seq']}")
            else:
                logger.error(f"게임 DB 업데이트 실패: {game['game_id']}-{game['game_seq']}")
                # 실패 시 강제 실패 상태 업데이트 시도
                try:
                    repository.update_game_ai_result(game['game_id'], game['game_seq'], {
                        'wrong_option_1': '',
                        'wrong_option_2': '',
                        'wrong_option_3': '',
                        'similarity_score_1': 0.0,
                        'similarity_score_2': 0.0,
                        'similarity_score_3': 0.0,
                        'ai_status': 'FAILED',
                        'description': 'DB 업데이트 실패 후 강제 실패 처리'
                    })
                except Exception as ex:
                    logger.error(f"DB 업데이트 실패 후 강제 실패 처리도 실패: {ex}")
                failed_count += 1

            await asyncio.sleep(1)
        except Exception as e:
            failed_count += 1
            logger.error(f"게임 처리 중 예외 발생: game_id={game['game_id']}, game_seq={game['game_seq']}, 에러={e}", exc_info=True)

    logger.info(f"배치 처리 완료: 성공={processed_count}, 실패={failed_count}")
