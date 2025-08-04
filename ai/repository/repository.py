import logging
from typing import List, Dict, Optional
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

def get_games_needing_analysis(limit: int = 10) -> List[Dict]:
    """AI 분석이 필요한 게임들을 조회"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT game_id, game_seq, answer_text, ai_status
        FROM game_detail 
        WHERE answer_text IS NOT NULL 
        AND answer_text != '' 
        AND (ai_status = 'PENDING' OR ai_status = 'FAILED')
        ORDER BY created_at ASC
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        logger.info(f"AI 분석 대기 중인 게임 {len(results)}개 조회")
        return results
        
    except Exception as e:
        logger.error(f"게임 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_game_ai_result(game_id: str, game_seq: int, ai_result: Dict) -> bool:
    """게임의 AI 분석 결과를 업데이트"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        UPDATE game_detail 
        SET wrong_option_1 = %s,
            wrong_option_2 = %s, 
            wrong_option_3 = %s,
            wrong_score_1 = %s,
            wrong_score_2 = %s,
            wrong_score_3 = %s,
            ai_status = %s,
            description = %s,
            ai_processed_at = NOW()
        WHERE game_id = %s AND game_seq = %s
        """
        
        values = (
            ai_result.get('wrong_option_1', ''),
            ai_result.get('wrong_option_2', ''),
            ai_result.get('wrong_option_3', ''),
            ai_result.get('wrong_score_1', 0.0),
            ai_result.get('wrong_score_2', 0.0), 
            ai_result.get('wrong_score_3', 0.0),
            ai_result.get('ai_status', 'FAILED'),
            ai_result.get('description', ''),
            game_id,
            game_seq
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"AI 결과 업데이트 성공: {game_id}-{game_seq}")
            return True
        else:
            logger.warning(f"업데이트할 행이 없음: {game_id}-{game_seq}")
            return False
            
    except Exception as e:
        logger.error(f"AI 결과 업데이트 실패: {game_id}-{game_seq}, 에러: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_failed_analysis_games() -> List[Dict]:
    """분석 실패한 게임들의 answer_text를 조회 (모델 학습용)"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT DISTINCT answer_text, COUNT(*) as fail_count
        FROM game_detail 
        WHERE ai_status = 'FAILED' 
        AND answer_text IS NOT NULL 
        AND answer_text != ''
        AND description LIKE '%모델에 존재하지 않습니다%'
        GROUP BY answer_text
        ORDER BY fail_count DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        logger.info(f"분석 실패한 단어 {len(results)}개 조회")
        return results
        
    except Exception as e:
        logger.error(f"실패 게임 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def mark_games_for_reanalysis(answer_texts: List[str]) -> int:
    """특정 단어들의 게임을 재분석 대상으로 표시"""
    if not answer_texts:
        return 0
        
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        cursor = connection.cursor()
        
        # IN 절을 위한 플레이스홀더 생성
        placeholders = ','.join(['%s'] * len(answer_texts))
        query = f"""
        UPDATE game_detail 
        SET ai_status = 'PENDING',
            description = '모델 업데이트 후 재분석 대상',
            ai_processed_at = NULL
        WHERE answer_text IN ({placeholders})
        AND ai_status = 'FAILED'
        """
        
        cursor.execute(query, answer_texts)
        connection.commit()
        
        updated_count = cursor.rowcount
        logger.info(f"재분석 대상으로 표시된 게임: {updated_count}개")
        return updated_count
        
    except Exception as e:
        logger.error(f"재분석 표시 실패: {e}")
        if connection:
            connection.rollback()
        return 0
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_analysis_statistics() -> Dict:
    """AI 분석 통계 조회"""
    connection = get_db_connection()
    if not connection:
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            ai_status,
            COUNT(*) as count
        FROM game_detail 
        WHERE answer_text IS NOT NULL 
        AND answer_text != ''
        GROUP BY ai_status
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        stats = {row['ai_status']: row['count'] for row in results}
        logger.info(f"AI 분석 통계: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        return {}
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()