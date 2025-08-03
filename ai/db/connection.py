import os
import logging
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql-db'),
    'database': os.getenv('DB_NAME', 'myapp'),
    'user': os.getenv('DB_USER', 'app_user'),
    'password': os.getenv('DB_PASSWORD', 'mysql'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return None
