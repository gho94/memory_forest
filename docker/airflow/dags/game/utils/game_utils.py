# game/utils/game_utils.py
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import sys

sys.path.append('/opt/airflow/dags')
from common.database import DatabaseManager, execute_query
from common.constants import STATUS_CODES

class GameProcessor:
    """게임 처리 관련 클래스"""
    
    def __init__(self):
        pass
    
    def get_games_by_status(self, status: str, limit: int = 100) -> List[Dict]:
        """상태별 게임 조회"""
        
        status_code = STATUS_CODES.get(status, status)
        
        query = """
        SELECT gd.game_id, gd.game_seq, gd.file_id, gd.answer_text,
               gd.ai_status_code, gd.description, fi.s3_url, fi.original_name
        FROM game_detail gd
        LEFT JOIN file_info fi ON gd.file_id = fi.file_id
        WHERE gd.ai_status_code = %s
        ORDER BY gd.game_id DESC, gd.game_seq ASC
        LIMIT %s
        """
        
        results = execute_query(query, (status_code, limit), fetch=True)
        return results or []
    
    def update_game_status(self, game_id: str, game_seq: int, 
                          status: str, description: str = None) -> bool:
        """게임 상태 업데이트"""
        
        status_code = STATUS_CODES.get(status, status)
        
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
        
        result = execute_query(query, params, fetch=False)
        return result is not None and result > 0
    
    def update_game_ai_result(self, game_id: str, game_seq: int, ai_result: Dict) -> bool:
        """AI 분석 결과 업데이트"""
        
        query = """
        UPDATE game_detail 
        SET ai_status_code = %s,
            answer_text = %s,
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
            STATUS_CODES['COMPLETED'],
            ai_result.get('answer_text'),
            ai_result.get('wrong_option_1'),
            ai_result.get('wrong_option_2'),
            ai_result.get('wrong_option_3'),
            ai_result.get('wrong_score_1', 0),
            ai_result.get('wrong_score_2', 0),
            ai_result.get('wrong_score_3', 0),
            'AI 분석 완료',
            datetime.now(),
            game_id,
            game_seq
        )
        
        result = execute_query(query, params, fetch=False)
        return result is not None and result > 0
    
    def get_retry_count(self, game_id: str, game_seq: int) -> int:
        """게임의 재시도 횟수 조회"""
        
        query = """
        SELECT description
        FROM game_detail
        WHERE game_id = %s AND game_seq = %s
        """
        
        result = execute_query(query, (game_id, game_seq), fetch=True)
        
        if not result:
            return 0
        
        description = result[0].get('description', '')
        
        # 재시도 횟수 파싱 (예: "네트워크 오류 재시도 (2/3)")
        import re
        match = re.search(r'\((\d+)/\d+\)', description)
        if match:
            return int(match.group(1))
        
        return 0
    
    def reactivate_model_failed_games(self) -> int:
        """모델 부족으로 실패한 게임들을 재활성화"""
        
        query = """
        UPDATE game_detail 
        SET ai_status_code = %s,
            description = '새 모델 업데이트 후 재처리'
        WHERE ai_status_code = %s 
        AND (description LIKE '%모델에 존재하지 않습니다%' 
             OR description LIKE '%vocabulary%'
             OR description LIKE '%model%')
        """
        
        result = execute_query(
            query, 
            (STATUS_CODES['PENDING'], STATUS_CODES['ERROR']), 
            fetch=False
        )
        
        return result or 0
    
    def archive_game(self, game: Dict) -> bool:
        """게임을 아카이브 테이블로 이동"""
        
        try:
            with DatabaseManager() as db:
                # 아카이브 테이블에 삽입
                archive_query = """
                INSERT INTO game_detail_archive 
                (game_id, game_seq, file_id, answer_text, wrong_option_1, 
                 wrong_option_2, wrong_option_3, wrong_score_1, wrong_score_2, 
                 wrong_score_3, ai_status_code, ai_processed_at, description, 
                 archived_at, archive_reason)
                SELECT game_id, game_seq, file_id, answer_text, wrong_option_1,
                       wrong_option_2, wrong_option_3, wrong_score_1, wrong_score_2,
                       wrong_score_3, ai_status_code, ai_processed_at, description,
                       %s, %s
                FROM game_detail 
                WHERE game_id = %s AND game_seq = %s
                """
                
                archive_result = db.execute(
                    archive_query, 
                    (datetime.now(), '오래된 실패 게임', game['game_id'], game['game_seq']),
                    fetch=False
                )
                
                return archive_result is not None and archive_result > 0
                
        except Exception as e:
            logging.error(f"게임 아카이브 실패: {e}")
            return False
    
    def delete_game(self, game_id: str, game_seq: int) -> bool:
        """게임 삭제"""
        
        query = """
        DELETE FROM game_detail 
        WHERE game_id = %s AND game_seq = %s
        """
        
        result = execute_query(query, (game_id, game_seq), fetch=False)
        return result is not None and result > 0
    
    def get_old_failed_games(self, cutoff_date: datetime) -> List[Dict]:
        """오래된 실패 게임들 조회"""
        
        query = """
        SELECT game_id, game_seq, ai_status_code, description, ai_processed_at
        FROM game_detail 
        WHERE ai_status_code = %s 
        AND ai_processed_at < %s
        ORDER BY ai_processed_at ASC
        """
        
        results = execute_query(
            query, 
            (STATUS_CODES['ERROR'], cutoff_date), 
            fetch=True
        )
        
        return results or []
    
    def analyze_failure_type(self, game: Dict) -> str:
        """실패 유형 분석"""
        
        description = game.get('description', '').lower()
        
        if any(keyword in description for keyword in ['모델에 존재하지', 'vocabulary', 'not found']):
            return 'model_limitation'
        elif any(keyword in description for keyword in ['연결', 'timeout', 'connection', 'network']):
            return 'temporary_error'
        elif any(keyword in description for keyword in ['corruption', '손상', 'invalid']):
            return 'data_corruption'
        elif any(keyword in description for keyword in ['처리 중', 'processing', 'exception']):
            return 'permanent_error'
        else:
            return 'unknown_error'


class GameAnalyzer:
    """게임 분석 관련 클래스"""
    
    def __init__(self):
        pass
    
    def count_games_by_status(self, status: str) -> int:
        """상태별 게임 개수 조회"""
        
        status_code = STATUS_CODES.get(status, status)
        
        query = """
        SELECT COUNT(*) as count
        FROM game_detail 
        WHERE ai_status_code = %s
        """
        
        result = execute_query(query, (status_code,), fetch=True)
        
        if result and len(result) > 0:
            return result[0]['count']
        
        return 0
    
    def get_failed_words(self, limit: int = 100) -> List[str]:
        """분석 실패한 단어들 조회"""
        
        query = """
        SELECT DISTINCT answer_text
        FROM game_detail 
        WHERE ai_status_code = %s 
        AND answer_text IS NOT NULL
        AND (description LIKE '%모델에 존재하지 않습니다%' 
             OR description LIKE '%vocabulary%')
        ORDER BY ai_processed_at DESC
        LIMIT %s
        """
        
        results = execute_query(query, (STATUS_CODES['ERROR'], limit), fetch=True)
        
        if results:
            return [row['answer_text'] for row in results if row['answer_text']]
        
        return []
    
    def analyze_failure_patterns(self) -> Dict[str, int]:
        """실패 패턴 분석"""
        
        query = """
        SELECT ai_status_code, description, COUNT(*) as count
        FROM game_detail 
        WHERE ai_status_code = %s
        GROUP BY ai_status_code, description
        ORDER BY count DESC
        """
        
        results = execute_query(query, (STATUS_CODES['ERROR'],), fetch=True)
        
        patterns = {}
        
        if results:
            for row in results:
                description = row['description'] or 'Unknown error'
                count = row['count']
                
                # 오류 유형 분류
                if '모델에 존재하지' in description:
                    patterns['model_missing_word'] = patterns.get('model_missing_word', 0) + count
                elif any(keyword in description.lower() for keyword in ['연결', 'timeout', 'connection']):
                    patterns['network_error'] = patterns.get('network_error', 0) + count
                elif '처리 중 예외' in description:
                    patterns['processing_error'] = patterns.get('processing_error', 0) + count
                else:
                    patterns['other_error'] = patterns.get('other_error', 0) + count
        
        return patterns
    
    def get_failed_words_frequency(self) -> Dict[str, int]:
        """실패한 단어 빈도 분석"""
        
        query = """
        SELECT answer_text, COUNT(*) as count
        FROM game_detail 
        WHERE ai_status_code = %s 
        AND answer_text IS NOT NULL
        AND description LIKE '%모델에 존재하지 않습니다%'
        GROUP BY answer_text
        ORDER BY count DESC
        LIMIT 50
        """
        
        results = execute_query(query, (STATUS_CODES['ERROR'],), fetch=True)
        
        frequency = {}
        if results:
            for row in results:
                frequency[row['answer_text']] = row['count']
        
        return frequency
    
    def get_recent_failure_trends(self, days: int = 7) -> Dict:
        """최근 실패 트렌드 분석"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT DATE(ai_processed_at) as failure_date, 
               COUNT(*) as failure_count
        FROM game_detail 
        WHERE ai_status_code = %s 
        AND ai_processed_at >= %s
        GROUP BY DATE(ai_processed_at)
        ORDER BY failure_date DESC
        """
        
        results = execute_query(query, (STATUS_CODES['ERROR'], cutoff_date), fetch=True)
        
        trends = {
            'daily_failures': {},
            'total_failures': 0,
            'average_daily': 0
        }
        
        if results:
            for row in results:
                date_str = row['failure_date'].strftime('%Y-%m-%d')
                count = row['failure_count']
                trends['daily_failures'][date_str] = count
                trends['total_failures'] += count
            
            trends['average_daily'] = trends['total_failures'] / len(results)
        
        return trends
    
    def get_games_by_failed_word(self, word: str) -> List[Dict]:
        """특정 실패 단어로 실패한 게임들 조회"""
        
        query = """
        SELECT game_id, game_seq, answer_text, description, ai_processed_at
        FROM game_detail 
        WHERE ai_status_code = %s 
        AND answer_text = %s
        AND description LIKE '%모델에 존재하지 않습니다%'
        ORDER BY ai_processed_at DESC
        """
        
        results = execute_query(query, (STATUS_CODES['ERROR'], word), fetch=True)
        return results or []
    
    def get_retryable_games(self, error_type: str, max_retry_count: int = 3) -> List[Dict]:
        """재시도 가능한 게임들 조회"""
        
        # 오류 유형별 검색 조건
        conditions = {
            'network_error': "description LIKE '%연결%' OR description LIKE '%timeout%' OR description LIKE '%connection%'",
            'timeout_error': "description LIKE '%timeout%' OR description LIKE '%시간초과%'",
            'processing_error': "description LIKE '%처리 중 예외%' OR description LIKE '%processing%'"
        }
        
        condition = conditions.get(error_type, "1=0")  # 기본값은 매칭되지 않는 조건
        
        query = f"""
        SELECT game_id, game_seq, description, ai_processed_at
        FROM game_detail 
        WHERE ai_status_code = %s 
        AND ({condition})
        AND (description NOT LIKE '%(%/%' OR 
             CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(description, '(', -1), '/', 1) AS UNSIGNED) < %s)
        ORDER BY ai_processed_at ASC
        LIMIT 50
        """
        
        results = execute_query(query, (STATUS_CODES['ERROR'], max_retry_count), fetch=True)
        return results or []
    
    def get_error_games_by_type(self, error_type: str) -> List[Dict]:
        """오류 유형별 게임 조회"""
        
        conditions = {
            'network': "description LIKE '%연결%' OR description LIKE '%timeout%' OR description LIKE '%connection%'",
            'model': "description LIKE '%모델에 존재하지%' OR description LIKE '%vocabulary%'",
            'processing': "description LIKE '%처리 중 예외%' OR description LIKE '%processing%'"
        }
        
        condition = conditions.get(error_type, "1=0")
        
        query = f"""
        SELECT game_id, game_seq, answer_text, description, ai_processed_at
        FROM game_detail 
        WHERE ai_status_code = %s 
        AND ({condition})
        ORDER BY ai_processed_at DESC
        LIMIT 100
        """
        
        results = execute_query(query, (STATUS_CODES['ERROR'],), fetch=True)
        return results or []
    
    def save_processing_stats(self, stats: Dict):
        """처리 통계 저장 (파일 또는 DB)"""
        
        try:
            # 간단한 로그 기록
            logging.info(f"게임 처리 통계 저장: {stats}")
            
            # 필요시 별도 통계 테이블에 저장하는 로직 추가 가능
            
        except Exception as e:
            logging.error(f"통계 저장 실패: {e}")
    
    def save_reprocessing_statistics(self, stats: Dict):
        """재처리 통계 저장"""
        
        try:
            logging.info(f"재처리 통계 저장: {stats}")
            
            # 필요시 별도 테이블이나 파일에 저장
            
        except Exception as e:
            logging.error(f"재처리 통계 저장 실패: {e}")