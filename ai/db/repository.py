from .connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

def get_games_needing_analysis(limit: int = 10):
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
    except Exception as e:
        logger.error(f"게임 조회 실패: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_game_ai_result(game_id: str, game_seq: int, ai_result: dict):
    connection = get_db_connection()
    if not connection:
        logger.error(f"DB 연결 실패로 인해 game_id={game_id}, game_seq={game_seq} 업데이트 불가")
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
            float(ai_result.get('similarity_score_1', 0.0)),
            float(ai_result.get('similarity_score_2', 0.0)),
            float(ai_result.get('similarity_score_3', 0.0)),
            ai_result.get('ai_status', 'FAILED'),
            ai_result.get('description', ''),
            game_id,
            game_seq
        )
        cursor.execute(query, values)
        connection.commit()
        return True
    except Exception as e:
        logger.error(f"DB 업데이트 실패: game_id={game_id}, game_seq={game_seq}, 에러={e}", exc_info=True)
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
