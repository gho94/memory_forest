"""
데이터베이스 유틸리티 함수들
init.sql 스키마에 맞춘 데이터베이스 작업
"""

import logging
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
from config import DB_CONFIG, STATUS_CODES, DIFFICULTY_CODES

logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.config = DB_CONFIG
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                yield connection
            else:
                raise Exception("데이터베이스 연결 실패")
        except Error as e:
            logger.error(f"데이터베이스 오류: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def get_games_by_status(self, status: str, limit: int = 50) -> List[Dict]:
        """상태별 게임 조회 - init.sql 스키마 기반"""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # 상태 코드 변환
            status_code = STATUS_CODES.get(status, status)
            
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
                    WHEN gm.difficulty_level_code = 'D10001' THEN 'EASY'
                    WHEN gm.difficulty_level_code = 'D10002' THEN 'NORMAL'
                    WHEN gm.difficulty_level_code = 'D10003' THEN 'HARD'
                    WHEN gm.difficulty_level_code = 'D10004' THEN 'EXPERT'
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
            
            cursor.execute(query, (status_code, limit))
            results = cursor.fetchall()
            
            logger.info(f"{status} 상태 게임 {len(results)}개 조회")
            return results
    
    def update_game_ai_result(self, game_id: str, game_seq: int, 
                             status: str, description: str = '',
                             ai_result: Optional[Dict] = None) -> bool:
        """게임 AI 분석 결과 업데이트"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                status_code = STATUS_CODES.get(status, status)
                
                if ai_result and status == 'COMPLETED':
                    # AI 분석 완료 시 모든 결과 저장
                    query = """
                    UPDATE game_detail 
                    SET ai_status_code = %s,
                        ai_processed_at = CURRENT_TIMESTAMP,
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
                        status_code, description,
                        ai_result.get('wrong_option_1', '')[:20],
                        ai_result.get('wrong_option_2', '')[:20],
                        ai_result.get('wrong_option_3', '')[:20],
                        int(ai_result.get('wrong_score_1', 0)),
                        int(ai_result.get('wrong_score_2', 0)),
                        int(ai_result.get('wrong_score_3', 0)),
                        game_id, game_seq
                    )
                else:
                    # 상태만 업데이트
                    query = """
                    UPDATE game_detail 
                    SET ai_status_code = %s,
                        ai_processed_at = CURRENT_TIMESTAMP,
                        description = %s
                    WHERE game_id = %s AND game_seq = %s
                    """
                    values = (status_code, description, game_id, game_seq)
                
                cursor.execute(query, values)
                conn.commit()
                
                affected_rows = cursor.rowcount
                logger.info(f"게임 업데이트: {game_id}/{game_seq} -> {status}")
                return affected_rows > 0
                
            except Exception as e:
                conn.rollback()
                logger.error(f"게임 업데이트 실패: {game_id}/{game_seq} - {e}")
                return False
    
    def get_processing_statistics(self) -> Dict:
        """처리 통계 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
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
                COUNT(CASE WHEN ai_status_code = %s THEN 1 END) as completed_today,
                COUNT(CASE WHEN ai_status_code = %s THEN 1 END) as failed_today
            FROM game_detail 
            WHERE DATE(ai_processed_at) = CURDATE()
            """
            cursor.execute(query3, (STATUS_CODES['COMPLETED'], STATUS_CODES['ERROR']))
            today_stats = cursor.fetchone()
            
            return {
                'status_breakdown': status_stats,
                'difficulty_breakdown': difficulty_stats,
                'today_summary': today_stats
            }
    
    def mark_games_for_retry(self, error_keywords: List[str], max_count: int = 50) -> int:
        """특정 오류 키워드를 가진 게임들을 재시도 대기로 변경"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # 조건 구성
                conditions = ' OR '.join(['description LIKE %s' for _ in error_keywords])
                keywords_params = [f'%{keyword}%' for keyword in error_keywords]
                
                query = f"""
                UPDATE game_detail 
                SET ai_status_code = %s,
                    description = CONCAT('재시도: ', description),
                    ai_processed_at = CURRENT_TIMESTAMP
                WHERE ai_status_code = %s 
                AND ({conditions})
                LIMIT %s
                """
                
                params = [STATUS_CODES['PENDING'], STATUS_CODES['ERROR']] + keywords_params + [max_count]
                cursor.execute(query, params)
                conn.commit()
                
                affected_rows = cursor.rowcount
                logger.info(f"재시도 설정: {affected_rows}개 게임")
                return affected_rows
                
            except Exception as e:
                conn.rollback()
                logger.error(f"재시도 설정 실패: {e}")
                return 0

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()