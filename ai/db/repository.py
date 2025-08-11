# ai/db/repository.py (MySQL 저장 함수 추가)
import logging
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

def save_ai_analysis_result(game_id: str, game_seq: int, result_data: Dict) -> bool:
    """AI 분석 결과를 MySQL GAME_DETAIL 테이블에 저장 - DOUBLE 타입에 정수값 저장"""
    
    connection = get_db_connection()
    if not connection:
        logger.error("데이터베이스 연결 실패")
        return False
    
    try:
        cursor = connection.cursor()
        
        # 소문자 테이블명/컬럼명 사용 (실제 DB 구조에 맞춤)
        update_query = """
        UPDATE game_detail 
        SET 
            wrong_option_1 = %s,
            wrong_option_2 = %s, 
            wrong_option_3 = %s,
            wrong_score_1 = %s,
            wrong_score_2 = %s,
            wrong_score_3 = %s,
            ai_status = %s,
            ai_processed_at = NOW(),
            description = %s
        WHERE game_id = %s AND game_seq = %s
        """
        
        # 0.5763 → 57.63 → 58 (반올림) 변환
        def convert_score_to_integer(score):
            """소수점 점수를 0-100 범위의 정수로 변환하여 DOUBLE로 저장"""
            try:
                if score is None:
                    return 0.0
                
                # 이미 정수면 그대로 float로 변환
                if isinstance(score, int):
                    return float(score)
                
                # float이면 100배 후 반올림
                if isinstance(score, float):
                    # 0-1 범위를 벗어나면 0으로 처리
                    if score < 0 or score > 1:
                        return 0.0
                    
                    # 100배 하고 반올림하여 정수로 변환한 후 다시 float로
                    integer_score = round(score * 100)
                    return float(max(0, min(100, integer_score)))
                
                # 문자열이면 float로 변환 후 처리
                score_float = float(score)
                if score_float < 0 or score_float > 1:
                    return 0.0
                integer_score = round(score_float * 100)
                return float(max(0, min(100, integer_score)))
                
            except (ValueError, TypeError, OverflowError):
                return 0.0
        
        score1 = convert_score_to_integer(result_data.get('wrong_score_1'))
        score2 = convert_score_to_integer(result_data.get('wrong_score_2'))
        score3 = convert_score_to_integer(result_data.get('wrong_score_3'))
            
        values = (
            result_data.get('wrong_option_1', '')[:20],  # VARCHAR(20) 제한
            result_data.get('wrong_option_2', '')[:20], 
            result_data.get('wrong_option_3', '')[:20],
            score1,  # DOUBLE 타입에 정수값 저장 (예: 58.0)
            score2,  # DOUBLE 타입에 정수값 저장 (예: 72.0)
            score3,  # DOUBLE 타입에 정수값 저장 (예: 85.0)
            result_data.get('ai_status', 'FAILED')[:10],  # VARCHAR(10) 제한
            result_data.get('description', '')[:500],     # VARCHAR(500) 제한
            game_id,
            game_seq
        )
        
        cursor.execute(update_query, values)
        connection.commit()
        
        affected_rows = cursor.rowcount
        logger.info(f"AI 분석 결과 MySQL 저장 완료: {game_id}/{game_seq} - 점수: {score1}, {score2}, {score3} (영향받은 행: {affected_rows})")
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"AI 분석 결과 MySQL 저장 실패: {game_id}/{game_seq}, 에러: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_games_needing_analysis(limit: int = 50) -> List[Dict]:
    """AI 분석이 필요한 게임들을 조회 (소문자 테이블명 사용)"""
    
    connection = get_db_connection()
    if not connection:
        logger.error("데이터베이스 연결 실패")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 소문자 테이블명으로 수정
        query = """
        SELECT 
            gd.game_id as game_id,
            gd.game_seq as game_seq, 
            gd.answer_text as answer_text,
            gm.difficulty_level_code as difficulty_level_code,
            gd.ai_status as ai_status,
            CASE 
                WHEN gm.difficulty_level_code = 'D10001' THEN 'EASY'
                WHEN gm.difficulty_level_code = 'D10002' THEN 'NORMAL'
                WHEN gm.difficulty_level_code = 'D10003' THEN 'HARD'
                WHEN gm.difficulty_level_code = 'D10004' THEN 'EXPERT'
                ELSE 'NORMAL'
            END as difficulty_level
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.answer_text IS NOT NULL 
        AND gd.answer_text != ''
        AND (gd.ai_status = 'PENDING' OR gd.ai_status = 'FAILED')
        ORDER BY gd.game_id, gd.game_seq
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        logger.info(f"AI 분석 대기 중인 게임 {len(results)}개 조회 완료")
        return results
        
    except Error as e:
        logger.error(f"게임 조회 중 DB 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"게임 조회 중 예상치 못한 오류: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_failed_games_for_reprocess(limit: int = 100) -> List[Dict]:
    """재처리가 필요한 실패 게임들 조회 (소문자 테이블명 사용)"""
    
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 소문자 테이블명으로 수정
        query = """
        SELECT 
            gd.game_id as game_id,
            gd.game_seq as game_seq, 
            gd.answer_text as answer_text,
            gm.difficulty_level_code as difficulty_level_code,
            gd.ai_status as ai_status,
            CASE 
                WHEN gm.difficulty_level_code = 'D10001' THEN 'EASY'
                WHEN gm.difficulty_level_code = 'D10002' THEN 'NORMAL'
                WHEN gm.difficulty_level_code = 'D10003' THEN 'HARD'
                WHEN gm.difficulty_level_code = 'D10004' THEN 'EXPERT'
                ELSE 'NORMAL'
            END as difficulty_level
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.answer_text IS NOT NULL 
        AND gd.answer_text != ''
        AND gd.ai_status = 'FAILED'
        ORDER BY gd.ai_processed_at DESC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        logger.info(f"재처리 대상 실패 게임 {len(results)}개 조회")
        return results
        
    except Exception as e:
        logger.error(f"실패 게임 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_analysis_statistics() -> Dict:
    """AI 분석 통계 조회 (소문자 테이블명 사용)"""
    
    connection = get_db_connection()
    if not connection:
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 전체 통계 (소문자 테이블명)
        overall_query = """
        SELECT 
            ai_status as status,
            COUNT(*) as count
        FROM game_detail 
        WHERE answer_text IS NOT NULL 
        AND answer_text != ''
        GROUP BY ai_status
        """
        cursor.execute(overall_query)
        overall_results = cursor.fetchall()
        
        # 난이도별 통계 (소문자 테이블명)
        difficulty_query = """
        SELECT 
            CASE 
                WHEN gm.difficulty_level_code = 'D10001' THEN 'EASY'
                WHEN gm.difficulty_level_code = 'D10002' THEN 'NORMAL'
                WHEN gm.difficulty_level_code = 'D10003' THEN 'HARD'
                WHEN gm.difficulty_level_code = 'D10004' THEN 'EXPERT'
                ELSE 'NORMAL'
            END as difficulty_level,
            gd.ai_status as status,
            COUNT(*) as count
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.answer_text IS NOT NULL 
        AND gd.answer_text != ''
        GROUP BY difficulty_level, gd.ai_status_code
        ORDER BY difficulty_level, gd.ai_status_code
        """
        cursor.execute(difficulty_query)
        difficulty_results = cursor.fetchall()
        
        # 통계 구성
        overall_stats = {row['status']: row['count'] for row in overall_results}
        
        difficulty_stats = {}
        for row in difficulty_results:
            difficulty = row['difficulty_level']
            status = row['status']
            count = row['count']
            
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {}
            difficulty_stats[difficulty][status] = count
        
        return {
            "overall": overall_stats,
            "by_difficulty": difficulty_stats,
            "total_games": sum(overall_stats.values())
        }
        
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        return {}
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def check_game_exists(game_id: str, game_seq: int) -> bool:
    """게임 데이터 존재 여부 확인 (소문자 테이블명 사용)"""
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = "SELECT 1 FROM game_detail WHERE game_id = %s AND game_seq = %s"
        cursor.execute(query, (game_id, game_seq))
        result = cursor.fetchone()
        
        return result is not None
        
    except Exception as e:
        logger.error(f"게임 존재 확인 실패: {game_id}/{game_seq} - {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def get_game_current_status(game_id: str, game_seq: int) -> Optional[Dict]:
    """게임의 현재 AI 분석 상태 조회 (소문자 테이블명 사용)"""
    
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            game_id,
            game_seq,
            answer_text,
            ai_status,
            wrong_option_1,
            wrong_option_2,
            wrong_option_3,
            wrong_score_1,
            wrong_score_2,
            wrong_score_3,
            ai_processed_at,
            description
        FROM game_detail 
        WHERE game_id = %s AND game_seq = %s
        """
        cursor.execute(query, (game_id, game_seq))
        result = cursor.fetchone()
        
        return result
        
    except Exception as e:
        logger.error(f"게임 상태 조회 실패: {game_id}/{game_seq} - {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def mark_game_as_processing(game_id: str, game_seq: int) -> bool:
    """게임을 처리 중 상태로 표시 (소문자 테이블명 사용)"""
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        UPDATE game_detail 
        SET ai_status = 'PROCESSING',
            description = 'AI 분석 진행 중...'
        WHERE game_id = %s AND game_seq = %s
        """
        cursor.execute(query, (game_id, game_seq))
        connection.commit()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"게임 처리 중 표시 실패: {game_id}/{game_seq} - {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()