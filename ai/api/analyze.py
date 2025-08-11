# ai/api/analyze.py 수정 - ai_status_code 대응
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

def convert_numpy_scores_to_float(scores):
    """1단계: numpy 타입을 안전하게 Python float으로 변환"""
    safe_scores = []
    for score in scores:
        try:
            if isinstance(score, (np.floating, np.integer)):
                # numpy 타입인 경우
                converted = float(score)
                if np.isnan(converted) or np.isinf(converted):
                    safe_scores.append(0.0)
                else:
                    safe_scores.append(converted)
            elif isinstance(score, (int, float)):
                # 일반 Python 타입인 경우
                if isinstance(score, float) and (np.isnan(score) or np.isinf(score)):
                    safe_scores.append(0.0)
                else:
                    safe_scores.append(float(score))
            else:
                # 기타 타입은 0.0으로 처리
                safe_scores.append(0.0)
        except (ValueError, TypeError, OverflowError):
            safe_scores.append(0.0)
    
    return safe_scores

def convert_float_scores_to_integer(float_scores):
    """2단계: Python float을 0-100 정수로 변환 (반올림 적용)"""
    integer_scores = []
    
    for score in float_scores:
        try:
            # 0-1 범위를 벗어나면 0으로 처리
            if score < 0 or score > 1:
                integer_scores.append(0)
                continue
            
            # 소수점을 100배 하고 반올림하여 정수로 변환
            integer_score = round(score * 100)
            
            # 0-100 범위 보장
            integer_scores.append(max(0, min(100, integer_score)))
            
        except (ValueError, TypeError, OverflowError):
            integer_scores.append(0)
    
    return integer_scores

def convert_numpy_scores_to_integers_complete(scores):
    """완전한 변환: numpy float → Python float → 정수"""
    # 1단계: numpy → Python float
    float_scores = convert_numpy_scores_to_float(scores)
    
    # 2단계: Python float → 정수 (반올림)
    integer_scores = convert_float_scores_to_integer(float_scores)
    
    return integer_scores

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_answer(request: AIAnalysisRequest):
    """답변 분석 후 MySQL에 즉시 저장 - ai_status_code 사용"""
    
    # 모델 로드 확인
    if ai_service.model is None:
        logger.error("모델이 로드되지 않았습니다.")
        raise HTTPException(status_code=503, detail="Model not loaded")

    difficulty = getattr(request, 'difficulty_level', 'NORMAL')
    
    logger.info(f"AI 분석 요청: game_id={request.game_id}, game_seq={request.game_seq}, "
                f"answer_text={request.answer_text}, difficulty={difficulty}")

    # AI 분석 수행
    result = ai_service.generate_wrong_options_with_difficulty(request.answer_text, difficulty)

    if result["status"] == "FAILED":
        logger.error(f"AI 분석 실패: {result.get('error', 'Unknown error')}")
        
        # 실패 결과도 DB에 저장 - ai_status 대신 ai_status_code 매핑
        failed_result = {
            'wrong_option_1': '',
            'wrong_option_2': '',
            'wrong_option_3': '',
            'wrong_score_1': 0,  # 정수
            'wrong_score_2': 0,  # 정수
            'wrong_score_3': 0,  # 정수
            'ai_status': 'FAILED',  # 내부적으로는 문자열 사용하고 repository에서 코드로 변환
            'description': result.get('error', 'AI 분석 실패')
        }
        
        # MySQL에 실패 결과 저장
        save_success = repository.save_ai_analysis_result(
            request.game_id, 
            request.game_seq, 
            failed_result
        )
        
        if save_success:
            logger.info(f"AI 분석 실패 결과 DB 저장 완료: {request.game_id}/{request.game_seq}")
        else:
            logger.error(f"AI 분석 실패 결과 DB 저장 실패: {request.game_id}/{request.game_seq}")
        
        return AIAnalysisResponse(
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

    # 성공한 경우 데이터 처리
    wrong_options = result["wrong_options"]
    wrong_scores = result["wrong_scores"]  # 이것은 numpy float 배열
    difficulty_used = result.get("difficulty_used", difficulty)

    logger.info(f"원본 numpy 점수: {wrong_scores} (타입: {[type(s).__name__ for s in wrong_scores]})")

    # 1단계: numpy float → Python float 변환
    float_scores = convert_numpy_scores_to_float(wrong_scores)
    logger.info(f"Python float 변환: {float_scores}")
    
    # 2단계: Python float → 정수 변환 (반올림)
    integer_scores = convert_float_scores_to_integer(float_scores)
    logger.info(f"정수 변환 (반올림): {integer_scores}")
    
    # 3개 미만인 경우 0으로 채우기
    while len(integer_scores) < 3:
        integer_scores.append(0)
    while len(wrong_options) < 3:
        wrong_options.append("")

    # MySQL 저장용 데이터 준비 - ai_status 사용 (repository에서 코드로 변환)
    mysql_result = {
        'wrong_option_1': wrong_options[0],
        'wrong_option_2': wrong_options[1], 
        'wrong_option_3': wrong_options[2],
        'wrong_score_1': integer_scores[0],
        'wrong_score_2': integer_scores[1],
        'wrong_score_3': integer_scores[2],
        'ai_status': 'COMPLETED',  # 문자열로 전달, repository에서 B20007로 변환
        'description': f"AI 분석 완료 (난이도: {difficulty_used})"
    }

    # MySQL에 결과 저장
    save_success = repository.save_ai_analysis_result(
        request.game_id, 
        request.game_seq, 
        mysql_result
    )
    
    if save_success:
        logger.info(f"AI 분석 성공 결과 DB 저장 완료: {request.game_id}/{request.game_seq} - 점수: {integer_scores}")
    else:
        logger.error(f"AI 분석 성공 결과 DB 저장 실패: {request.game_id}/{request.game_seq}")

    logger.info(f"AI 분석 완료 (난이도: {difficulty_used}): options={wrong_options}, scores={integer_scores}")

    return AIAnalysisResponse(
        game_id=request.game_id,
        game_seq=request.game_seq,
        wrong_option_1=wrong_options[0],
        wrong_option_2=wrong_options[1],
        wrong_option_3=wrong_options[2],
        wrong_score_1=integer_scores[0],
        wrong_score_2=integer_scores[1],
        wrong_score_3=integer_scores[2],
        ai_status="COMPLETED",
        description=f"AI 분석 완료 (난이도: {difficulty_used})"
    )

@router.post("/batch/process")
async def batch_process(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    """배치 처리 - 백그라운드에서 MySQL 저장"""
    if ai_service.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    games = repository.get_games_needing_analysis(request.limit)

    if not games:
        return {"message": "처리할 게임이 없습니다.", "processed_count": 0}

    # 백그라운드에서 배치 처리 실행
    background_tasks.add_task(process_games_batch_with_mysql, games)

    return {
        "message": f"{len(games)}개 게임의 AI 분석을 시작합니다.",
        "games_to_process": len(games)
    }

async def process_games_batch_with_mysql(games: List[dict]):
    """배치 처리 함수 - ai_status_code 대응"""
    processed_count = 0
    failed_count = 0

    logger.info(f"배치 처리 시작: {len(games)}개 게임")

    for game in games:
        try:
            game_id = game['game_id']
            game_seq = game['game_seq']
            answer_text = game['answer_text']
            difficulty = game.get('difficulty_level', 'NORMAL')
            
            logger.info(f"배치 처리 중: {game_id}/{game_seq} - {answer_text} (난이도: {difficulty})")

            # AI 분석 수행
            result = ai_service.generate_wrong_options_with_difficulty(answer_text, difficulty)

            # 결과 처리 및 MySQL 저장
            if result['status'] == 'COMPLETED':
                # 성공한 경우
                wrong_options = result['wrong_options']
                wrong_scores = result['wrong_scores']  # numpy float 배열
                
                # 올바른 순서로 점수 변환
                integer_scores = convert_numpy_scores_to_integers_complete(wrong_scores)
                
                # 3개 미만인 경우 채우기
                while len(integer_scores) < 3:
                    integer_scores.append(0)
                while len(wrong_options) < 3:
                    wrong_options.append("")

                mysql_result = {
                    'wrong_option_1': wrong_options[0],
                    'wrong_option_2': wrong_options[1],
                    'wrong_option_3': wrong_options[2],
                    'wrong_score_1': integer_scores[0],
                    'wrong_score_2': integer_scores[1],
                    'wrong_score_3': integer_scores[2],
                    'ai_status': 'COMPLETED',  # repository에서 B20007로 변환
                    'description': f"배치 AI 분석 완료 (난이도: {result.get('difficulty_used', difficulty)})"
                }
            else:
                # 실패한 경우
                mysql_result = {
                    'wrong_option_1': '',
                    'wrong_option_2': '',
                    'wrong_option_3': '',
                    'wrong_score_1': 0,
                    'wrong_score_2': 0,
                    'wrong_score_3': 0,
                    'ai_status': 'FAILED',  # repository에서 B20008로 변환
                    'description': f"배치 AI 분석 실패: {result.get('error', '알 수 없는 오류')}"
                }

            # MySQL에 저장
            if repository.save_ai_analysis_result(game_id, game_seq, mysql_result):
                processed_count += 1
                logger.info(f"배치 처리 성공: {game_id}/{game_seq} (난이도: {difficulty})")
            else:
                logger.error(f"배치 처리 DB 저장 실패: {game_id}/{game_seq}")
                failed_count += 1

            # 과부하 방지를 위한 지연
            await asyncio.sleep(0.5)

        except Exception as e:
            failed_count += 1
            logger.error(f"배치 처리 중 예외 발생: game_id={game.get('game_id')}, "
                        f"game_seq={game.get('game_seq')}, 에러={e}", exc_info=True)

    logger.info(f"배치 처리 완료: 성공={processed_count}, 실패={failed_count}")

# 나머지 엔드포인트들도 ai_status_code 대응
@router.get("/analysis/stats")
async def get_analysis_statistics():
    """AI 분석 통계 조회"""
    try:
        stats = repository.get_analysis_statistics()
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="통계 조회 실패")

@router.post("/reprocess/failed")
async def reprocess_failed_games(background_tasks: BackgroundTasks, limit: int = 100):
    """실패한 게임들 재처리"""
    try:
        failed_games = repository.get_failed_games_for_reprocess(limit)
        
        if not failed_games:
            return {"message": "재처리할 실패 게임이 없습니다.", "count": 0}
        
        # 백그라운드에서 재처리
        background_tasks.add_task(process_games_batch_with_mysql, failed_games)
        
        return {
            "message": f"{len(failed_games)}개 실패 게임의 재처리를 시작합니다.",
            "games_to_reprocess": len(failed_games)
        }
        
    except Exception as e:
        logger.error(f"실패 게임 재처리 요청 실패: {e}")
        raise HTTPException(status_code=500, detail="재처리 요청 실패")

@router.post("/test/save-result")
async def test_save_result(game_id: str, game_seq: int):
    """테스트: 더미 AI 결과를 MySQL에 저장"""
    try:
        # 더미 AI 분석 결과 생성
        dummy_result = {
            'wrong_option_1': '테스트1',
            'wrong_option_2': '테스트2', 
            'wrong_option_3': '테스트3',
            'wrong_score_1': 12,
            'wrong_score_2': 57,
            'wrong_score_3': 90,
            'ai_status': 'COMPLETED',  # repository에서 B20007로 변환
            'description': 'FastAPI 테스트 저장'
        }
        
        # MySQL에 저장
        success = repository.save_ai_analysis_result(game_id, game_seq, dummy_result)
        
        if success:
            return {
                "status": "success",
                "message": f"테스트 결과 저장 완료: {game_id}/{game_seq}",
                "saved_data": dummy_result
            }
        else:
            return {
                "status": "failed", 
                "message": f"테스트 결과 저장 실패: {game_id}/{game_seq}"
            }
            
    except Exception as e:
        logger.error(f"테스트 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=f"테스트 저장 실패: {str(e)}")

@router.get("/test/game-status/{game_id}/{game_seq}")
async def test_get_game_status(game_id: str, game_seq: int):
    """테스트: 게임의 현재 AI 분석 상태 조회"""
    try:
        status = repository.get_game_current_status(game_id, game_seq)
        
        if status:
            return {
                "status": "success",
                "game_data": status
            }
        else:
            return {
                "status": "not_found",
                "message": f"게임 데이터를 찾을 수 없음: {game_id}/{game_seq}"
            }
            
    except Exception as e:
        logger.error(f"게임 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@router.post("/test/analyze-and-save")
async def test_analyze_and_save():
    """테스트: 실제 AI 분석 후 MySQL 저장 전체 플로우"""
    try:
        # 테스트용 답변들
        test_cases = [
            {"game_id": "TEST001", "game_seq": 1, "answer_text": "사과", "difficulty": "EASY"},
            {"game_id": "TEST001", "game_seq": 2, "answer_text": "강아지", "difficulty": "NORMAL"},
            {"game_id": "TEST001", "game_seq": 3, "answer_text": "행복", "difficulty": "HARD"}
        ]
        
        results = []
        
        for test_case in test_cases:
            # AI 분석 수행
            ai_result = ai_service.generate_wrong_options_with_difficulty(
                test_case["answer_text"], 
                test_case["difficulty"]
            )
            
            if ai_result["status"] == "COMPLETED":
                # 성공한 경우 MySQL에 저장
                wrong_options = ai_result["wrong_options"]
                wrong_scores = ai_result["wrong_scores"]
                
                # numpy float 안전 변환 - 올바른 순서로
                integer_scores = convert_numpy_scores_to_integers_complete(wrong_scores)
                
                # 3개 미만인 경우 채우기
                while len(integer_scores) < 3:
                    integer_scores.append(0)
                while len(wrong_options) < 3:
                    wrong_options.append("")

                mysql_result = {
                    'wrong_option_1': wrong_options[0],
                    'wrong_option_2': wrong_options[1],
                    'wrong_option_3': wrong_options[2],
                    'wrong_score_1': integer_scores[0], 
                    'wrong_score_2': integer_scores[1], 
                    'wrong_score_3': integer_scores[2], 
                    'ai_status': 'COMPLETED',  # repository에서 B20007로 변환
                    'description': f"테스트 AI 분석 완료 (난이도: {test_case['difficulty']})"
                }
                
                # MySQL 저장 시도 (게임 데이터가 실제로 있는 경우만 성공)
                save_success = repository.save_ai_analysis_result(
                    test_case["game_id"], 
                    test_case["game_seq"], 
                    mysql_result
                )
                
                results.append({
                    "test_case": test_case,
                    "ai_analysis": "SUCCESS", 
                    "mysql_save": "SUCCESS" if save_success else "FAILED (게임 데이터 없음)",
                    "ai_result": mysql_result
                })
                
            else:
                # AI 분석 실패
                results.append({
                    "test_case": test_case,
                    "ai_analysis": "FAILED",
                    "mysql_save": "SKIPPED",
                    "error": ai_result.get("error", "알 수 없는 오류")
                })
        
        return {
            "status": "completed",
            "message": "전체 플로우 테스트 완료",
            "test_results": results
        }
        
    except Exception as e:
        logger.error(f"전체 플로우 테스트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"테스트 실패: {str(e)}")

@router.get("/test/db-check")
async def test_database_connection():
    """테스트: 데이터베이스 연결 및 테이블 구조 확인"""
    try:
        connection = repository.get_db_connection()
        if not connection:
            return {"status": "failed", "message": "DB 연결 실패"}
        
        cursor = connection.cursor(dictionary=True)
        
        # GAME_DETAIL 테이블 구조 확인
        cursor.execute("DESCRIBE game_detail")
        table_structure = cursor.fetchall()
        
        # 샘플 데이터 개수 확인
        cursor.execute("SELECT COUNT(*) as total FROM game_detail")
        total_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM game_detail WHERE ai_status_code = 'B20005'")
        pending_count = cursor.fetchone()['pending']
        
        cursor.execute("SELECT COUNT(*) as completed FROM game_detail WHERE ai_status_code = 'B20007'")
        completed_count = cursor.fetchone()['completed']
        
        cursor.execute("SELECT COUNT(*) as failed FROM game_detail WHERE ai_status_code = 'B20008'")
        failed_count = cursor.fetchone()['failed']
        
        cursor.close()
        connection.close()
        
        return {
            "status": "success",
            "table_structure": table_structure,
            "data_counts": {
                "total": total_count,
                "pending": pending_count,
                "completed": completed_count,
                "failed": failed_count
            }
        }
        
    except Exception as e:
        logger.error(f"DB 테스트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"DB 테스트 실패: {str(e)}")

@router.get("/test/sample-games")
async def test_get_sample_games(limit: int = 5):
    """테스트: 분석 가능한 샘플 게임 조회"""
    try:
        games = repository.get_games_needing_analysis(limit)
        
        return {
            "status": "success",
            "sample_games_count": len(games),
            "sample_games": games
        }
        
    except Exception as e:
        logger.error(f"샘플 게임 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"샘플 게임 조회 실패: {str(e)}")

@router.post("/test/process-one-game")
async def test_process_one_game():
    """테스트: 실제 게임 데이터 1개를 AI 분석 후 MySQL 저장"""
    try:
        # 분석할 게임 1개 조회
        games = repository.get_games_needing_analysis(1)
        
        if not games:
            return {
                "status": "no_games",
                "message": "분석할 게임이 없습니다."
            }
        
        game = games[0]
        game_id = game['game_id']
        game_seq = game['game_seq']
        answer_text = game['answer_text']
        difficulty = game.get('difficulty_level', 'NORMAL')
        
        logger.info(f"테스트 게임 처리: {game_id}/{game_seq} - {answer_text} (난이도: {difficulty})")
        
        # 처리 중 상태로 표시
        repository.mark_game_as_processing(game_id, game_seq)
        
        # AI 분석 수행
        ai_result = ai_service.generate_wrong_options_with_difficulty(answer_text, difficulty)
        
        if ai_result["status"] == "COMPLETED":
            # 성공한 경우
            wrong_options = ai_result["wrong_options"]
            wrong_scores = ai_result["wrong_scores"]
            
            # numpy float 안전 변환 - 올바른 순서로
            integer_scores = convert_numpy_scores_to_integers_complete(wrong_scores)
            
            # 3개 미만인 경우 채우기
            while len(integer_scores) < 3:
                integer_scores.append(0)
            while len(wrong_options) < 3:
                wrong_options.append("")

            mysql_result = {
                'wrong_option_1': wrong_options[0],
                'wrong_option_2': wrong_options[1],
                'wrong_option_3': wrong_options[2],
                'wrong_score_1': integer_scores[0],
                'wrong_score_2': integer_scores[1],
                'wrong_score_3': integer_scores[2],
                'ai_status': 'COMPLETED',  # repository에서 B20007로 변환
                'description': f"테스트 처리 완료 (난이도: {ai_result.get('difficulty_used', difficulty)})"
            }
            
            # MySQL에 저장
            save_success = repository.save_ai_analysis_result(game_id, game_seq, mysql_result)
            
            return {
                "status": "success",
                "message": f"게임 처리 완료: {game_id}/{game_seq}",
                "original_game": game,
                "ai_analysis_result": mysql_result,
                "mysql_save_success": save_success
            }
            
        else:
            # AI 분석 실패
            failed_result = {
                'wrong_option_1': '',
                'wrong_option_2': '',
                'wrong_option_3': '',
                'wrong_score_1': 0,
                'wrong_score_2': 0,
                'wrong_score_3': 0,
                'ai_status': 'FAILED',  # repository에서 B20008로 변환
                'description': f"테스트 처리 실패: {ai_result.get('error', '알 수 없는 오류')}"
            }
            
            save_success = repository.save_ai_analysis_result(game_id, game_seq, failed_result)
            
            return {
                "status": "ai_failed",
                "message": f"AI 분석 실패: {game_id}/{game_seq}",
                "original_game": game,
                "error": ai_result.get('error', '알 수 없는 오류'),
                "mysql_save_success": save_success
            }
        
    except Exception as e:
        logger.error(f"게임 처리 테스트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"게임 처리 테스트 실패: {str(e)}")