"""
Airflow DAG용 데이터베이스 유틸리티 - 기존 repository 코드 호환
"""

import logging
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
from config import DB_CONFIG

logger = logging.getLogger(__name__)

class AirflowDatabaseManager:
    """Airflow DAG용 데이터베이스 관리 클래스 - 기존 repository와 호환"""
    
    def __init__(self):
        self.config = {
            **DB_CONFIG,
            'buffered': True,
            'consume_results': True,
            'use_pure': True,
            'sql_mode': 'TRADITIONAL',
        }
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                connection.ping(reconnect=True, attempts=3, delay=1)
                yield connection
            else:
                raise Exception("데이터베이스 연결 실패")
        except Error as e:
            logger.error(f"데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"예상치 못한 데이터베이스 오류: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                try:
                    connection.cmd_reset_connection()
                except:
                    pass
                connection.close()
                logger.debug("데이터베이스 연결 종료")
    
    def test_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(buffered=True, dictionary=True)
                
                try:
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchone()
                    
                    if result and result['test'] == 1:
                        logger.info("✅ 데이터베이스 연결 테스트 성공")
                        return True
                    else:
                        logger.error("❌ 데이터베이스 테스트 쿼리 결과 이상")
                        return False
                        
                except Exception as e:
                    logger.error(f"❌ 데이터베이스 테스트 쿼리 실패: {e}")
                    return False
                finally:
                    try:
                        while cursor.nextset():
                            pass
                    except:
                        pass
                    cursor.close()
                    
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 테스트 실패: {e}")
            return False
    
    def get_games_by_status(self, ai_status: str, limit: int = 50) -> List[Dict]:
        """AI 상태별 게임 조회 - 기존 repository 호환"""
        with self.get_connection() as conn:
            cursor = conn.cursor(buffered=True, dictionary=True)
            
            try:
                # AI 상태를 DB 값으로 변환
                if ai_status == 'PENDING':
                    ai_status_value = 'B20005'  # 대기중
                elif ai_status == 'COMPLETED':
                    ai_status_value = 'B20007'  # 완료  
                elif ai_status == 'FAILED':
                    ai_status_value = 'B20008'  # 실패
                else:
                    ai_status_value = ai_status  # 직접 값 사용
                
                query = """
                SELECT 
                    gd.game_id,
                    gd.game_seq,
                    gd.game_order,
                    gd.answer_text,
                    gd.ai_status_code,
                    gd.ai_processed_at,
                    gd.description,
                    gd.wrong_option_1,
                    gd.wrong_option_2,
                    gd.wrong_option_3,
                    gd.wrong_score_1,
                    gd.wrong_score_2,
                    gd.wrong_score_3,
                    gm.game_name,
                    gm.difficulty_level_code,
                    gm.created_by,
                    fi.original_name as file_name,
                    CASE 
                        WHEN gm.difficulty_level_code = 'B20001' THEN 'EASY'
                        WHEN gm.difficulty_level_code = 'B20002' THEN 'NORMAL'
                        WHEN gm.difficulty_level_code = 'B20003' THEN 'HARD'
                        WHEN gm.difficulty_level_code = 'B20004' THEN 'EXPERT'
                        ELSE 'NORMAL'
                    END as difficulty_name
                FROM game_detail gd
                JOIN game_master gm ON gd.game_id = gm.game_id
                LEFT JOIN file_info fi ON gd.file_id = fi.file_id
                WHERE gd.ai_status_code = %s
                AND gd.answer_text IS NOT NULL 
                AND gd.answer_text != ''
                ORDER BY gd.game_id, gd.game_seq
                LIMIT %s
                """
                
                cursor.execute(query, (ai_status_value, limit))
                results = cursor.fetchall()
                
                logger.info(f"{ai_status} 상태 게임 {len(results)}개 조회")
                return results
                
            except Exception as e:
                logger.error(f"게임 조회 실패: {e}")
                return []
            finally:
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass
                cursor.close()
    
    def update_game_ai_result(self, game_id: str, game_seq: int, 
                             status: str, description: str = '',
                             ai_result: Optional[Dict] = None) -> bool:
        """게임 AI 분석 결과 업데이트 - 기존 repository save_ai_analysis_result 호환"""
        with self.get_connection() as conn:
            cursor = conn.cursor(buffered=True)
            
            try:
                # 상태를 DB 값으로 변환
                if status == 'PENDING':
                    status_code = 'B20005'  # 대기중
                elif status == 'PROCESSING':
                    status_code = 'B20006'  # 처리중 
                elif status == 'COMPLETED':
                    status_code = 'B20007'  # 완료
                elif status == 'ERROR' or status == 'FAILED':
                    status_code = 'B20008'  # 실패
                else:
                    status_code = status  # 직접 값 사용
                
                # 점수 변환 함수 (기존 repository와 동일)
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
                
                if ai_result and status == 'COMPLETED':
                    # AI 분석 완료 시 모든 결과 저장 (기존 repository와 동일한 형식)
                    score1 = convert_score_to_integer(ai_result.get('wrong_score_1'))
                    score2 = convert_score_to_integer(ai_result.get('wrong_score_2'))
                    score3 = convert_score_to_integer(ai_result.get('wrong_score_3'))
                    
                    query = """
                    UPDATE game_detail 
                    SET ai_status_code = %s,
                        ai_processed_at = NOW(),
                        description = %s,
                        wrong_option_1 = %s,
                        wrong_option_2 = %s,
                        wrong_option_3 = %s,
                        wrong_score_1 = %s,
                        wrong_score_2 = %s,
                        wrong_score_3 = %s
                    WHERE game_id = %s AND game_seq = %s
                    """
                    values = (
                        status_code, 
                        description[:500],  # VARCHAR(500) 제한
                        ai_result.get('wrong_option_1', '')[:20],  # VARCHAR(20) 제한
                        ai_result.get('wrong_option_2', '')[:20],
                        ai_result.get('wrong_option_3', '')[:20],
                        score1,  # DOUBLE 타입에 정수값 저장
                        score2,
                        score3,
                        game_id, game_seq
                    )
                else:
                    # 상태만 업데이트
                    query = """
                    UPDATE game_detail 
                    SET ai_status_code = %s,
                        ai_processed_at = NOW(),
                        description = %s
                    WHERE game_id = %s AND game_seq = %s
                    """
                    values = (status_code, description[:500], game_id, game_seq)
                
                cursor.execute(query, values)
                conn.commit()
                
                affected_rows = cursor.rowcount
                logger.info(f"게임 업데이트: {game_id}/{game_seq} -> {status} ({status_code})")
                return affected_rows > 0
                
            except Exception as e:
                conn.rollback()
                logger.error(f"게임 업데이트 실패: {game_id}/{game_seq} - {e}")
                return False
            finally:
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass
                cursor.close()
    
    def get_processing_statistics(self) -> Dict:
        """처리 통계 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor(buffered=True, dictionary=True)
            
            try:
                # 전체 상태별 통계
                query1 = """
                SELECT 
                    ai_status_code,
                    COUNT(*) as total_count,
                    COUNT(CASE WHEN DATE(ai_processed_at) = CURDATE() THEN 1 END) as today_count
                FROM game_detail 
                WHERE answer_text IS NOT NULL AND answer_text != ''
                GROUP BY ai_status_code
                """
                cursor.execute(query1)
                status_stats = cursor.fetchall()
                
                # 난이도별 통계
                query2 = """
                SELECT 
                    gm.difficulty_level_code,
                    gd.ai_status_code,
                    COUNT(*) as count
                FROM game_detail gd
                JOIN game_master gm ON gd.game_id = gm.game_id
                WHERE gd.answer_text IS NOT NULL AND gd.answer_text != ''
                GROUP BY gm.difficulty_level_code, gd.ai_status_code
                """
                cursor.execute(query2)
                difficulty_stats = cursor.fetchall()
                
                # 오늘의 처리 현황
                query3 = """
                SELECT 
                    COUNT(*) as total_processed_today,
                    COUNT(CASE WHEN ai_status_code = 'B20007' THEN 1 END) as completed_today,
                    COUNT(CASE WHEN ai_status_code = 'B20008' THEN 1 END) as failed_today
                FROM game_detail 
                WHERE DATE(ai_processed_at) = CURDATE()
                """
                cursor.execute(query3)
                today_stats = cursor.fetchone()
                
                return {
                    'status_breakdown': status_stats,
                    'difficulty_breakdown': difficulty_stats,
                    'today_summary': today_stats
                }
                
            except Exception as e:
                logger.error(f"통계 조회 실패: {e}")
                return {
                    'status_breakdown': [],
                    'difficulty_breakdown': [],
                    'today_summary': {
                        'total_processed_today': 0,
                        'completed_today': 0,
                        'failed_today': 0
                    }
                }
            finally:
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass
                cursor.close()
    
    def mark_games_for_retry(self, error_keywords: List[str], max_count: int = 50) -> int:
        """특정 오류 키워드를 가진 게임들을 재시도 대기로 변경"""
        with self.get_connection() as conn:
            cursor = conn.cursor(buffered=True)
            
            try:
                # 조건 구성
                conditions = ' OR '.join(['description LIKE %s' for _ in error_keywords])
                keywords_params = [f'%{keyword}%' for keyword in error_keywords]
                
                query = f"""
                UPDATE game_detail 
                SET ai_status_code = 'B20005',
                    description = CONCAT('재시도: ', description),
                    ai_processed_at = NOW()
                WHERE ai_status_code = 'B20008' 
                AND ({conditions})
                LIMIT %s
                """
                
                params = keywords_params + [max_count]
                cursor.execute(query, params)
                conn.commit()
                
                affected_rows = cursor.rowcount
                logger.info(f"재시도 설정: {affected_rows}개 게임")
                return affected_rows
                
            except Exception as e:
                conn.rollback()
                logger.error(f"재시도 설정 실패: {e}")
                return 0
            finally:
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass
                cursor.close()

# 전역 데이터베이스 매니저 인스턴스
db_manager = AirflowDatabaseManager()