import os
import logging
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)

# Docker Compose에서 사용하는 환경변수에 맞춤
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'database': os.getenv('DB_NAME', 'memory_forest'),  # Docker Compose의 MYSQL_DATABASE
    'user': os.getenv('DB_USER', 'kcc'),  # Docker Compose의 MYSQL_USER
    'password': os.getenv('DB_PASSWORD', 'kcc'),  # Docker Compose의 MYSQL_PASSWORD
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': False,
    'raise_on_warnings': True
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.debug(f"MySQL 연결 성공: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
            return connection
    except Error as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        logger.error(f"연결 시도 정보: host={DB_CONFIG['host']}, database={DB_CONFIG['database']}, user={DB_CONFIG['user']}")
        return None

def test_connection():
    """연결 테스트 함수"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            logger.info(f"DB 연결 테스트 성공: {result}")
            return True
        except Error as e:
            logger.error(f"DB 연결 테스트 실패: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False