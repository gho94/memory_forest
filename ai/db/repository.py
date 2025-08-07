# ai/db/repository.py 수정
import logging
from typing import List, Dict, Optional
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

def get_games_needing_analysis(limit: int = 10) -> List[Dict]:
    """AI 분석이 필요한 게임들을 조회 (난이도 정보 포함) - 올바른 컬럼명 사용"""
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
            gd.ai_status_code,
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
        AND (gd.ai_status_code = 'PENDING' OR gd.ai_status_code = 'FAILED' OR gd.ai_status_code = 'A10001' OR gd.ai_status_code = 'A10003')
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
    """특정 난이도의 AI 분석이 필요한 게임들을 조회 - 올바른 컬럼명 사용"""
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
            gd.ai_status_code,
            gm.difficulty_level_code,
            %s as difficulty_level
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.answer_text IS NOT NULL 
        AND gd.answer_text != '' 
        AND (gd.ai_status_code = 'PENDING' OR gd.ai_status_code = 'FAILED' OR gd.ai_status_code = 'A10001' OR gd.ai_status_code = 'A10003')
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
    """게임의 AI 분석 결과를 업데이트 - 올바른 컬럼명 사용"""
    logger.info(f"🔄 DB 업데이트 시작: game_id={game_id}, game_seq={game_seq}")
    logger.info(f"📊 업데이트 데이터: {ai_result}")
    
    connection = get_db_connection()
    if not connection:
        logger.error("❌ DB 연결 실패")
        return False
    
    try:
        cursor = connection.cursor()
        
        # 먼저 해당 행이 존재하는지 확인 (올바른 컬럼명 사용)
        check_query = """
        SELECT game_id, game_seq, answer_text, ai_status_code, 
               wrong_option_1, wrong_option_2, wrong_option_3,
               wrong_score_1, wrong_score_2, wrong_score_3 
        FROM game_detail 
        WHERE game_id = %s AND game_seq = %s
        """
        cursor.execute(check_query, (game_id, game_seq))
        existing_row = cursor.fetchone()
        
        if not existing_row:
            logger.error(f"❌ 해당 게임이 존재하지 않음: {game_id}-{game_seq}")
            return False
            
        logger.info(f"📋 업데이트 전 데이터:")
        logger.info(f"  - game_id: {existing_row[0]}")
        logger.info(f"  - game_seq: {existing_row[1]}")
        logger.info(f"  - answer_text: '{existing_row[2]}'")
        logger.info(f"  - ai_status_code: '{existing_row[3]}'")  # 컬럼명 수정
        logger.info(f"  - wrong_option_1: '{existing_row[4]}'")
        logger.info(f"  - wrong_option_2: '{existing_row[5]}'")
        logger.info(f"  - wrong_option_3: '{existing_row[6]}'")
        logger.info(f"  - wrong_score_1: {existing_row[7]}")
        logger.info(f"  - wrong_score_2: {existing_row[8]}")
        logger.info(f"  - wrong_score_3: {existing_row[9]}")
        
        # 업데이트할 값들 추출 및 검증
        wrong_option_1 = ai_result.get('wrong_option_1', '')
        wrong_option_2 = ai_result.get('wrong_option_2', '')
        wrong_option_3 = ai_result.get('wrong_option_3', '')
        wrong_score_1 = ai_result.get('wrong_score_1', 0)
        wrong_score_2 = ai_result.get('wrong_score_2', 0)
        wrong_score_3 = ai_result.get('wrong_score_3', 0)
        ai_status = ai_result.get('ai_status', 'FAILED')
        description = ai_result.get('description', '')
        
        # AI 상태를 상태 코드로 매핑 (필요시)
        status_code_map = {
            'PENDING': 'A10001',  # 예시 - 실제 코드에 맞게 수정 필요
            'COMPLETED': 'A10002',
            'FAILED': 'A10003'
        }
        ai_status_code = status_code_map.get(ai_status, ai_status)  # 매핑되지 않으면 원본 값 사용
        
        logger.info(f"📝 업데이트할 값들:")
        logger.info(f"  - wrong_option_1: '{wrong_option_1}' (길이: {len(wrong_option_1)})")
        logger.info(f"  - wrong_option_2: '{wrong_option_2}' (길이: {len(wrong_option_2)})")
        logger.info(f"  - wrong_option_3: '{wrong_option_3}' (길이: {len(wrong_option_3)})")
        logger.info(f"  - wrong_score_1: {wrong_score_1} (타입: {type(wrong_score_1)})")
        logger.info(f"  - wrong_score_2: {wrong_score_2} (타입: {type(wrong_score_2)})")
        logger.info(f"  - wrong_score_3: {wrong_score_3} (타입: {type(wrong_score_3)})")
        logger.info(f"  - ai_status: '{ai_status}' -> ai_status_code: '{ai_status_code}'")
        logger.info(f"  - description: '{description}'")
        
        # 타입 검증 및 변환
        try:
            wrong_score_1 = int(wrong_score_1) if wrong_score_1 is not None else 0
            wrong_score_2 = int(wrong_score_2) if wrong_score_2 is not None else 0
            wrong_score_3 = int(wrong_score_3) if wrong_score_3 is not None else 0
            logger.info(f"✅ 점수 타입 변환 완료: {wrong_score_1}, {wrong_score_2}, {wrong_score_3}")
        except (ValueError, TypeError) as e:
            logger.error(f"❌ 점수 타입 변환 실패: {e}")
            return False
        
        # VARCHAR(20) 길이 제한 체크
        if len(wrong_option_1) > 20:
            wrong_option_1 = wrong_option_1[:20]
            logger.warning(f"⚠️ wrong_option_1 길이 초과로 자름: '{wrong_option_1}'")
        if len(wrong_option_2) > 20:
            wrong_option_2 = wrong_option_2[:20]
            logger.warning(f"⚠️ wrong_option_2 길이 초과로 자름: '{wrong_option_2}'")
        if len(wrong_option_3) > 20:
            wrong_option_3 = wrong_option_3[:20]
            logger.warning(f"⚠️ wrong_option_3 길이 초과로 자름: '{wrong_option_3}'")
        if len(description) > 200:
            description = description[:200]
            logger.warning(f"⚠️ description 길이 초과로 자름: '{description}'")
        
        # 업데이트 쿼리 실행 (올바른 컬럼명 사용)
        query = """
        UPDATE game_detail 
        SET wrong_option_1 = %s,
            wrong_option_2 = %s, 
            wrong_option_3 = %s,
            wrong_score_1 = %s,
            wrong_score_2 = %s,
            wrong_score_3 = %s,
            ai_status_code = %s,
            description = %s,
            ai_processed_at = NOW()
        WHERE game_id = %s AND game_seq = %s
        """
        
        values = (
            wrong_option_1,
            wrong_option_2,
            wrong_option_3,
            wrong_score_1,
            wrong_score_2,
            wrong_score_3,
            ai_status_code,  # ai_status -> ai_status_code 수정
            description,
            game_id,
            game_seq
        )
        
        logger.info(f"🗃️ SQL 실행: {query}")
        logger.info(f"📝 최종 파라미터: {values}")
        
        cursor.execute(query, values)
        connection.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"✅ AI 결과 업데이트 성공: {game_id}-{game_seq}, 영향받은 행: {cursor.rowcount}")
            
            # 업데이트 결과 확인
            cursor.execute(check_query, (game_id, game_seq))
            updated_row = cursor.fetchone()
            
            if updated_row:
                logger.info(f"🔍 업데이트 후 데이터:")
                logger.info(f"  - ai_status_code: '{updated_row[3]}'")
                logger.info(f"  - wrong_option_1: '{updated_row[4]}'")
                logger.info(f"  - wrong_option_2: '{updated_row[5]}'") 
                logger.info(f"  - wrong_option_3: '{updated_row[6]}'")
                logger.info(f"  - wrong_score_1: {updated_row[7]}")
                logger.info(f"  - wrong_score_2: {updated_row[8]}")
                logger.info(f"  - wrong_score_3: {updated_row[9]}")
                
                # 값이 제대로 저장되었는지 검증
                if not updated_row[4] or not updated_row[5] or not updated_row[6]:
                    logger.error(f"❌ 오답 선택지가 제대로 저장되지 않음!")
                    return False
                if updated_row[7] is None or updated_row[8] is None or updated_row[9] is None:
                    logger.error(f"❌ 오답 점수가 제대로 저장되지 않음!")
                    return False
                    
            return True
        else:
            logger.warning(f"⚠️ 업데이트할 행이 없음: {game_id}-{game_seq}, rowcount: {cursor.rowcount}")
            return False
            
    except Exception as e:
        logger.error(f"❌ AI 결과 업데이트 실패: {game_id}-{game_seq}, 에러: {e}", exc_info=True)
        if connection:
            connection.rollback()
            logger.info("🔄 트랜잭션 롤백됨")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("🔌 DB 연결 종료")

def get_analysis_statistics_by_difficulty() -> Dict:
    """난이도별 AI 분석 통계 조회 - 올바른 컬럼명 사용"""
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
            gd.ai_status_code,
            COUNT(*) as count
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.answer_text IS NOT NULL 
        AND gd.answer_text != ''
        GROUP BY difficulty_level, gd.ai_status_code
        ORDER BY difficulty_level, gd.ai_status_code
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 난이도별 통계 구성
        stats_by_difficulty = {}
        for row in results:
            difficulty = row['difficulty_level']
            status = row['ai_status_code']
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