# ai/db/repository.py 수정
import logging
from typing import List, Dict, Optional
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

def get_games_needing_analysis(limit: int = 10) -> List[Dict]:
    """AI 분석이 필요한 게임들을 조회 (난이도 정보 포함)"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            gd.game_id, 
            gd.game_seq, 
            gd.answer_text, 
            gd.ai_status,
            gm.difficulty_level_code,
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
        
        logger.info(f"AI 분석 대기 중인 게임 {len(results)}개 조회 (난이도 정보 포함)")
        return results
        
    except Exception as e:
        logger.error(f"게임 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_games_needing_analysis_by_difficulty(difficulty: str, limit: int = 10) -> List[Dict]:
    """특정 난이도의 AI 분석이 필요한 게임들을 조회"""
    connection = get_db_connection()
    if not connection:
        return []
    
    # 난이도 코드 매핑
    difficulty_code_map = {
        'EASY': 'D10001',
        'NORMAL': 'D10002', 
        'HARD': 'D10003',
        'EXPERT': 'D10004'
    }
    
    difficulty_code = difficulty_code_map.get(difficulty)
    if not difficulty_code:
        logger.error(f"지원하지 않는 난이도: {difficulty}")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            gd.game_id, 
            gd.game_seq, 
            gd.answer_text, 
            gd.ai_status,
            gm.difficulty_level_code,
            %s as difficulty_level
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.answer_text IS NOT NULL 
        AND gd.answer_text != '' 
        AND (gd.ai_status = 'PENDING' OR gd.ai_status = 'FAILED')
        AND gm.difficulty_level_code = %s
        ORDER BY gd.game_id, gd.game_seq
        LIMIT %s
        """
        cursor.execute(query, (difficulty, difficulty_code, limit))
        results = cursor.fetchall()
        
        logger.info(f"난이도 '{difficulty}' AI 분석 대기 중인 게임 {len(results)}개 조회")
        return results
        
    except Exception as e:
        logger.error(f"난이도별 게임 조회 실패: {e}")
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
        score1 = ai_result.get('wrong_score_1', 0)
        score2 = ai_result.get('wrong_score_2', 0)
        score3 = ai_result.get('wrong_score_3', 0)

        # float이면 정수로 변환, 아니면 그대로 사용
        if isinstance(score1, float):
            score1 = int(score1)
        if isinstance(score2, float):
            score2 = int(score2)
        if isinstance(score3, float):
            score3 = int(score3)

        values = (
            ai_result.get('wrong_option_1', ''),
            ai_result.get('wrong_option_2', ''),
            ai_result.get('wrong_option_3', ''),
            score1,  # 정수로 변환된 점수
            score2,  # 정수로 변환된 점수
            score3,
            ai_result.get('ai_status', 'FAILED'),
            ai_result.get('description', ''),
            game_id,
            game_seq
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        affected_rows = cursor.rowcount
        logger.info(f"게임 AI 결과 업데이트 완료: {game_id}/{game_seq} (영향받은 행: {affected_rows})")
        return affected_rows > 0
            
    except Exception as e:
        logger.error(f"AI 결과 업데이트 실패: {game_id}-{game_seq}, 에러: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_failed_analysis_games_by_difficulty() -> Dict[str, List[Dict]]:
    """난이도별 분석 실패한 게임들의 answer_text를 조회"""
    connection = get_db_connection()
    if not connection:
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            CASE 
                WHEN gm.difficulty_level_code = 'D10001' THEN 'EASY'
                WHEN gm.difficulty_level_code = 'D10002' THEN 'NORMAL'
                WHEN gm.difficulty_level_code = 'D10003' THEN 'HARD'
                WHEN gm.difficulty_level_code = 'D10004' THEN 'EXPERT'
                ELSE 'NORMAL'
            END as difficulty_level,
            gd.answer_text, 
            COUNT(*) as fail_count
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.ai_status = 'FAILED' 
        AND gd.answer_text IS NOT NULL 
        AND gd.answer_text != ''
        AND gd.description LIKE '%모델에 존재하지 않습니다%'
        GROUP BY difficulty_level, gd.answer_text
        ORDER BY difficulty_level, fail_count DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 난이도별로 그룹화
        failed_by_difficulty = {}
        for row in results:
            difficulty = row['difficulty_level']
            if difficulty not in failed_by_difficulty:
                failed_by_difficulty[difficulty] = []
            failed_by_difficulty[difficulty].append({
                'answer_text': row['answer_text'],
                'fail_count': row['fail_count']
            })
        
        logger.info(f"난이도별 분석 실패 단어 조회 완료: {[(k, len(v)) for k, v in failed_by_difficulty.items()]}")
        return failed_by_difficulty
        
    except Exception as e:
        logger.error(f"난이도별 실패 게임 조회 실패: {e}")
        return {}
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_analysis_statistics_by_difficulty() -> Dict:
    """난이도별 AI 분석 통계 조회"""
    connection = get_db_connection()
    if not connection:
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            CASE 
                WHEN gm.difficulty_level_code = 'D10001' THEN 'EASY'
                WHEN gm.difficulty_level_code = 'D10002' THEN 'NORMAL'
                WHEN gm.difficulty_level_code = 'D10003' THEN 'HARD'
                WHEN gm.difficulty_level_code = 'D10004' THEN 'EXPERT'
                ELSE 'NORMAL'
            END as difficulty_level,
            gd.ai_status,
            COUNT(*) as count
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.answer_text IS NOT NULL 
        AND gd.answer_text != ''
        GROUP BY difficulty_level, gd.ai_status
        ORDER BY difficulty_level, gd.ai_status
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 난이도별 통계 구성
        stats_by_difficulty = {}
        for row in results:
            difficulty = row['difficulty_level']
            status = row['ai_status']
            count = row['count']
            
            if difficulty not in stats_by_difficulty:
                stats_by_difficulty[difficulty] = {}
            stats_by_difficulty[difficulty][status] = count
        
        logger.info(f"난이도별 AI 분석 통계: {stats_by_difficulty}")
        return stats_by_difficulty
        
    except Exception as e:
        logger.error(f"난이도별 통계 조회 실패: {e}")
        return {}
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def mark_games_for_reanalysis_by_difficulty(difficulty: str, answer_texts: List[str]) -> int:
    """특정 난이도의 특정 단어들의 게임을 재분석 대상으로 표시"""
    if not answer_texts:
        return 0
    
    # 난이도 코드 매핑
    difficulty_code_map = {
        'EASY': 'D10001',
        'NORMAL': 'D10002', 
        'HARD': 'D10003',
        'EXPERT': 'D10004'
    }
    
    difficulty_code = difficulty_code_map.get(difficulty)
    if not difficulty_code:
        logger.error(f"지원하지 않는 난이도: {difficulty}")
        return 0
        
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        cursor = connection.cursor()
        
        # IN 절을 위한 플레이스홀더 생성
        placeholders = ','.join(['%s'] * len(answer_texts))
        query = f"""
        UPDATE game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        SET gd.ai_status = 'PENDING',
            gd.description = '난이도별 모델 업데이트 후 재분석 대상',
            gd.ai_processed_at = NULL
        WHERE gd.answer_text IN ({placeholders})
        AND gd.ai_status = 'FAILED'
        AND gm.difficulty_level_code = %s
        """
        
        values = answer_texts + [difficulty_code]
        cursor.execute(query, values)
        connection.commit()
        
        updated_count = cursor.rowcount
        logger.info(f"난이도 '{difficulty}' 재분석 대상으로 표시된 게임: {updated_count}개")
        return updated_count
        
    except Exception as e:
        logger.error(f"난이도별 재분석 표시 실패: {e}")
        if connection:
            connection.rollback()
        return 0
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# 기존 함수들 (호환성 유지)
def get_failed_analysis_games() -> List[Dict]:
    """분석 실패한 게임들의 answer_text를 조회 (기존 호환성)"""
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
    """특정 단어들의 게임을 재분석 대상으로 표시 (기존 호환성)"""
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
    """AI 분석 통계 조회 (기존 호환성)"""
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