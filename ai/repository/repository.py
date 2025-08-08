# ai/db/repository.py 수정
import logging
from typing import List, Dict, Optional
from db.connection import get_db_connection

logger = logging.getLogger(__name__)

def get_games_needing_analysis(limit: int = 50) -> List[Dict]:
    """AI 분석이 필요한 게임 조회"""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ DB 연결 실패")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT gd.game_id, gd.game_seq, gd.answer_text, 
               gm.difficulty_level_code as difficulty_level
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE gd.ai_status_code = 'A10001' 
           OR gd.ai_status_code IS NULL
        ORDER BY gd.created_at ASC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        games = cursor.fetchall()
        
        logger.info(f"📋 분석 필요한 게임 조회: {len(games)}개")
        return games
        
    except Exception as e:
        logger.error(f"❌ 게임 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_games_needing_analysis_by_difficulty(difficulty: str, limit: int = 50) -> List[Dict]:
    """특정 난이도의 AI 분석이 필요한 게임 조회"""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ DB 연결 실패")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT gd.game_id, gd.game_seq, gd.answer_text, 
               gm.difficulty_level_code as difficulty_level
        FROM game_detail gd
        JOIN game_master gm ON gd.game_id = gm.game_id
        WHERE (gd.ai_status_code = 'A10001' OR gd.ai_status_code IS NULL)
          AND gm.difficulty_level_code = %s
        ORDER BY gd.created_at ASC
        LIMIT %s
        """
        
        cursor.execute(query, (difficulty, limit))
        games = cursor.fetchall()
        
        logger.info(f"📋 {difficulty} 난이도 분석 필요한 게임 조회: {len(games)}개")
        return games
        
    except Exception as e:
        logger.error(f"❌ 난이도별 게임 조회 실패: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def convert_ai_status_to_code(ai_status: str) -> str:
    """AI 상태를 DB 코드로 변환"""
    status_mapping = {
        'COMPLETED': 'A10002',  # AI 분석 완료
        'FAILED': 'A10003',     # AI 분석 실패
        'PROCESSING': 'A10001'   # AI 분석 중
    }
    
    code = status_mapping.get(ai_status, 'A10003')  # 기본값은 실패
    logger.info(f"상태 코드 매핑: '{ai_status}' -> '{code}'")
    return code



def update_game_ai_result(game_id: str, game_seq: int, ai_result: dict) -> bool:
    """게임 AI 분석 결과 업데이트 (디버깅 강화)"""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ DB 연결 실패")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. 먼저 현재 데이터 확인
        logger.info(f"🔍 업데이트 전 데이터 확인: {game_id}-{game_seq}")
        select_query = "SELECT * FROM game_detail WHERE game_id = %s AND game_seq = %s"
        cursor.execute(select_query, (game_id, game_seq))
        before_data = cursor.fetchone()
        
        if not before_data:
            logger.error(f"❌ 업데이트할 게임을 찾을 수 없음: {game_id}-{game_seq}")
            return False
        
        logger.info(f"🔍 업데이트 전 상태:")
        logger.info(f"  - ai_status_code: {before_data.get('ai_status_code')}")
        logger.info(f"  - wrong_option_1: '{before_data.get('wrong_option_1')}'")
        logger.info(f"  - wrong_option_2: '{before_data.get('wrong_option_2')}'")
        logger.info(f"  - wrong_option_3: '{before_data.get('wrong_option_3')}'")
        
        # 2. 입력 데이터 검증 및 로깅
        logger.info(f"📥 업데이트할 데이터 검증:")
        for key, value in ai_result.items():
            logger.info(f"  - {key}: '{value}' (타입: {type(value)}, 길이: {len(str(value)) if isinstance(value, str) else 'N/A'})")
        
        # 3. ai_status를 DB 코드로 변환
        ai_status_code = convert_ai_status_to_code(ai_result.get('ai_status', 'FAILED'))
        logger.info(f"🔄 상태 코드 변환: '{ai_result.get('ai_status')}' -> '{ai_status_code}'")
        
        # 4. 업데이트 쿼리 실행
        update_query = """
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
        
        params = (
            ai_result.get('wrong_option_1', ''),
            ai_result.get('wrong_option_2', ''),
            ai_result.get('wrong_option_3', ''),
            ai_result.get('wrong_score_1', 0),
            ai_result.get('wrong_score_2', 0),
            ai_result.get('wrong_score_3', 0),
            ai_status_code,
            ai_result.get('description', ''),
            game_id,
            game_seq
        )
        
        logger.info(f"📝 업데이트 쿼리:")
        logger.info(f"   {update_query}")
        logger.info(f"📝 업데이트 파라미터:")
        for i, param in enumerate(params):
            param_name = ['wrong_option_1', 'wrong_option_2', 'wrong_option_3', 
                         'wrong_score_1', 'wrong_score_2', 'wrong_score_3',
                         'ai_status_code', 'description', 'game_id', 'game_seq'][i]
            logger.info(f"   {param_name}: '{param}' (타입: {type(param)})")
        
        # 실제 업데이트 실행
        logger.info("🚀 업데이트 쿼리 실행 중...")
        cursor.execute(update_query, params)
        rowcount = cursor.rowcount
        logger.info(f"📊 영향받은 행 수: {rowcount}")
        
        # 트랜잭션 커밋
        connection.commit()
        logger.info("✅ 트랜잭션 커밋 완료")
        
        # 5. 업데이트 후 데이터 확인
        logger.info(f"🔍 업데이트 후 데이터 확인:")
        cursor.execute(select_query, (game_id, game_seq))
        after_data = cursor.fetchone()
        
        if after_data:
            logger.info(f"🔍 업데이트 후 상태:")
            logger.info(f"  - ai_status_code: '{after_data.get('ai_status_code')}'")
            logger.info(f"  - wrong_option_1: '{after_data.get('wrong_option_1')}' (길이: {len(str(after_data.get('wrong_option_1', '')))})")
            logger.info(f"  - wrong_option_2: '{after_data.get('wrong_option_2')}' (길이: {len(str(after_data.get('wrong_option_2', '')))})")
            logger.info(f"  - wrong_option_3: '{after_data.get('wrong_option_3')}' (길이: {len(str(after_data.get('wrong_option_3', '')))})")
            logger.info(f"  - wrong_score_1: {after_data.get('wrong_score_1')}")
            logger.info(f"  - wrong_score_2: {after_data.get('wrong_score_2')}")
            logger.info(f"  - wrong_score_3: {after_data.get('wrong_score_3')}")
            logger.info(f"  - description: '{after_data.get('description')}'")
            
            # 6. 데이터 변경 검증
            changes_detected = []
            
            if before_data.get('ai_status_code') != after_data.get('ai_status_code'):
                changes_detected.append(f"ai_status_code: '{before_data.get('ai_status_code')}' -> '{after_data.get('ai_status_code')}'")
            
            for i in range(1, 4):
                option_key = f'wrong_option_{i}'
                if before_data.get(option_key) != after_data.get(option_key):
                    changes_detected.append(f"{option_key}: '{before_data.get(option_key)}' -> '{after_data.get(option_key)}'")
            
            if changes_detected:
                logger.info(f"✅ 데이터 변경 감지: {len(changes_detected)}개 항목")
                for change in changes_detected:
                    logger.info(f"    {change}")
            else:
                logger.warning(f"⚠️ 업데이트 실행했으나 데이터 변경이 감지되지 않음")
            
            # 7. 빈 선택지 검사
            empty_options = []
            for i in range(1, 4):
                option_key = f'wrong_option_{i}'
                option_value = after_data.get(option_key, '')
                if not option_value or option_value.strip() == '':
                    empty_options.append(option_key)
            
            if empty_options and ai_result.get('ai_status') == 'COMPLETED':
                logger.error(f"❌ COMPLETED 상태인데 빈 선택지 발견: {empty_options}")
                return False
            elif empty_options:
                logger.warning(f"⚠️ 빈 선택지 발견 (상태: {ai_result.get('ai_status')}): {empty_options}")
        
        # 8. 최종 결과 판단
        success = rowcount > 0
        if success:
            logger.info(f"✅ AI 결과 업데이트 성공: {game_id}-{game_seq}")
        else:
            logger.error(f"❌ AI 결과 업데이트 실패: {game_id}-{game_seq} (rowcount: {rowcount})")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ AI 결과 업데이트 중 예외 발생: game_id={game_id}, game_seq={game_seq}, 오류={e}", exc_info=True)
        if connection:
            connection.rollback()
            logger.info("🔄 트랜잭션 롤백 완료")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("🔌 DB 연결 종료")


            
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

def test_direct_update(game_id: str, game_seq: int) -> bool:
    """디버깅용: 직접 업데이트 테스트"""
    logger.info(f"🧪 직접 업데이트 테스트 시작: {game_id}-{game_seq}")
    
    connection = get_db_connection()
    if not connection:
        logger.error("❌ DB 연결 실패")
        return False
    
    try:
        cursor = connection.cursor()
        
        # 간단한 테스트 업데이트
        test_query = """
        UPDATE game_detail 
        SET description = 'DIRECT_TEST_UPDATE',
            ai_processed_at = NOW()
        WHERE game_id = %s AND game_seq = %s
        """
        
        logger.info(f"🧪 테스트 쿼리 실행: {test_query}")
        logger.info(f"🧪 테스트 파라미터: {game_id}, {game_seq}")
        
        cursor.execute(test_query, (game_id, game_seq))
        rowcount = cursor.rowcount
        
        logger.info(f"🧪 테스트 결과: rowcount={rowcount}")
        
        connection.commit()
        logger.info("🧪 테스트 커밋 완료")
        
        # 결과 확인
        cursor.execute("SELECT description, ai_processed_at FROM game_detail WHERE game_id = %s AND game_seq = %s", 
                      (game_id, game_seq))
        result = cursor.fetchone()
        
        logger.info(f"🧪 테스트 후 데이터: {result}")
        
        return rowcount > 0
        
    except Exception as e:
        logger.error(f"🧪 직접 테스트 실패: {e}", exc_info=True)
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()