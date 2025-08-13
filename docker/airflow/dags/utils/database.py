"""
데이터베이스 관리 유틸리티
game_detail 테이블의 ai_status_code 기반 처리에 집중
"""

import logging
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, AI_STATUS_CODES, MODEL_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 연결 및 게임 데이터 관리"""
    
    def __init__(self):
        self.config = DB_CONFIG
        
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            logger.error(f"데이터베이스 연결 오류: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result is not None
        except Exception as e:
            logger.error(f"데이터베이스 연결 테스트 실패: {e}")
            return False
    
    def get_failed_games(self, limit: int = 20) -> List[Dict]:
        """실패한 게임들 조회 (재처리 대상)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = """
                SELECT 
                    gd.game_id,
                    gd.game_seq,
                    gd.answer_text,
                    gd.ai_status_code,
                    gd.description,
                    gd.ai_processed_at,
                    fi.s3_url,
                    fi.original_name
                FROM game_detail gd
                LEFT JOIN file_info fi ON gd.file_id = fi.file_id
                WHERE gd.ai_status_code IN ('B20005', 'B20008')  -- 대기, 실패
                AND gd.answer_text IS NOT NULL 
                AND gd.answer_text != ''
                ORDER BY gd.ai_processed_at ASC
                LIMIT %s
                """
                
                cursor.execute(query, (limit,))
                results = cursor.fetchall()
                cursor.close()
                
                logger.info(f"재처리 대상 게임 {len(results)}개 조회 완료")
                return results
                
        except Exception as e:
            logger.error(f"실패 게임 조회 오류: {e}")
            return []
    
    def get_missing_word_games(self, limit: int = 50) -> List[Dict]:
        """모델에 없는 단어가 포함된 게임들 조회"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # description에 '%모델%' 마커가 있는 게임들
                query = """
                SELECT 
                    gd.game_id,
                    gd.game_seq,
                    gd.answer_text,
                    gd.description,
                    gd.ai_status_code
                FROM game_detail gd
                WHERE gd.description LIKE %s
                AND gd.answer_text IS NOT NULL
                AND gd.answer_text != ''
                ORDER BY gd.ai_processed_at DESC
                LIMIT %s
                """
                
                cursor.execute(query, (f'%{MODEL_CONFIG["missing_words_marker"]}%', limit))
                results = cursor.fetchall()
                cursor.close()
                
                logger.info(f"모델 학습 대상 게임 {len(results)}개 조회 완료")
                return results
                
        except Exception as e:
            logger.error(f"모델 학습 대상 조회 오류: {e}")
            return []
    
    def update_game_status(self, game_id: str, game_seq: int, 
                          status_code: str, description: str = None) -> bool:
        """게임 AI 상태 업데이트"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                UPDATE game_detail 
                SET ai_status_code = %s,
                    description = %s,
                    ai_processed_at = %s
                WHERE game_id = %s AND game_seq = %s
                """
                
                params = (
                    status_code,
                    description,
                    datetime.now(),
                    game_id,
                    game_seq
                )
                
                cursor.execute(query, params)
                conn.commit()
                cursor.close()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"게임 상태 업데이트 실패 {game_id}/{game_seq}: {e}")
            return False
    
    def update_game_ai_result(self, game_id: str, game_seq: int, 
                             ai_result: Dict) -> bool:
        """AI 분석 결과 업데이트"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                UPDATE game_detail 
                SET ai_status_code = %s,
                    wrong_option_1 = %s,
                    wrong_option_2 = %s,
                    wrong_option_3 = %s,
                    wrong_score_1 = %s,
                    wrong_score_2 = %s,
                    wrong_score_3 = %s,
                    description = %s,
                    ai_processed_at = %s
                WHERE game_id = %s AND game_seq = %s
                """
                
                params = (
                    AI_STATUS_CODES['COMPLETED'],
                    ai_result.get('wrong_option_1'),
                    ai_result.get('wrong_option_2'),
                    ai_result.get('wrong_option_3'),
                    ai_result.get('wrong_score_1'),
                    ai_result.get('wrong_score_2'),
                    ai_result.get('wrong_score_3'),
                    ai_result.get('description', 'AI 분석 완료'),
                    datetime.now(),
                    game_id,
                    game_seq
                )
                
                cursor.execute(query, params)
                conn.commit()
                cursor.close()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"AI 결과 업데이트 실패 {game_id}/{game_seq}: {e}")
            return False
    
    def mark_as_processing(self, game_id: str, game_seq: int) -> bool:
        """게임을 처리 중 상태로 표시"""
        return self.update_game_status(
            game_id, game_seq, 
            AI_STATUS_CODES['PROCESSING'], 
            'AI 분석 진행 중...'
        )
    
    def mark_as_failed(self, game_id: str, game_seq: int, error_msg: str) -> bool:
        """게임을 실패 상태로 표시"""
        return self.update_game_status(
            game_id, game_seq,
            AI_STATUS_CODES['FAILED'],
            f'AI 분석 실패: {error_msg}'
        )
    
    def extract_training_words(self, limit: int = 100) -> List[str]:
        """모델 학습용 단어 추출"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 간단한 방식: ORDER BY 제거하고 DISTINCT만 사용
                query = """
                SELECT DISTINCT answer_text
                FROM game_detail
                WHERE description LIKE %s
                AND answer_text IS NOT NULL
                AND answer_text != ''
                AND LENGTH(answer_text) >= 2
                LIMIT %s
                """
                
                cursor.execute(query, (f'%{MODEL_CONFIG["missing_words_marker"]}%', limit))
                results = cursor.fetchall()
                cursor.close()
                
                words = [row[0] for row in results if row[0]]
                logger.info(f"모델 학습용 단어 {len(words)}개 추출 완료: {words[:5]}...")
                return words
                
        except Exception as e:
            logger.error(f"학습 단어 추출 오류: {e}")
            return []
    
    def get_processing_statistics(self) -> Dict:
        """처리 상태 통계 조회"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # 전체 상태별 통계
                query = """
                SELECT 
                    ai_status_code,
                    COUNT(*) as count
                FROM game_detail
                WHERE answer_text IS NOT NULL
                GROUP BY ai_status_code
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                
                stats = {
                    'status_breakdown': results,
                    'total_games': sum(row['count'] for row in results)
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"통계 조회 오류: {e}")
            return {'status_breakdown': [], 'total_games': 0}