# common/database.py
import mysql.connector
from mysql.connector import Error
import logging
from typing import Optional, List, Dict
from .config import DB_CONFIG

def get_db_connection():
    """데이터베이스 연결을 생성하고 반환합니다."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logging.error(f"데이터베이스 연결 실패: {e}")
        return None

def execute_query(query: str, params: tuple = None, fetch: bool = False) -> Optional[List[Dict]]:
    """데이터베이스 쿼리를 실행합니다."""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            results = cursor.fetchall()
            return results
        else:
            connection.commit()
            return cursor.rowcount
            
    except Exception as e:
        logging.error(f"쿼리 실행 실패: {e}")
        if connection:
            connection.rollback()
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def execute_batch_update(query: str, data_list: List[tuple]) -> bool:
    """배치 업데이트를 실행합니다."""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.executemany(query, data_list)
        connection.commit()
        logging.info(f"배치 업데이트 성공: {cursor.rowcount}개 행 처리")
        return True
        
    except Exception as e:
        logging.error(f"배치 업데이트 실패: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.connection = None
    
    def __enter__(self):
        self.connection = get_db_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute(self, query: str, params: tuple = None, fetch: bool = False):
        """컨텍스트 매니저 내에서 쿼리 실행"""
        if not self.connection:
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            logging.error(f"쿼리 실행 실패: {e}")
            self.connection.rollback()
            return None