# ai/db/connection.py
import os
import logging
import time
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)

# Docker Compose에서 사용하는 환경변수에 맞춤
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'memory_forest'),
    'user': os.getenv('DB_USER', 'kcc'),
    'password': os.getenv('DB_PASSWORD', 'kcc'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': False,
    'raise_on_warnings': True,
    'connection_timeout': 10,
    'buffered': True
}

def get_db_connection(retry_count=3, retry_delay=2):
    """데이터베이스 연결을 시도하고 재시도 로직 포함"""
    
    logger.info(f"🔌 DB 연결 시도: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    logger.info(f"📋 연결 정보: user={DB_CONFIG['user']}, host={DB_CONFIG['host']}")
    
    for attempt in range(retry_count):
        try:
            logger.debug(f"🔄 연결 시도 {attempt + 1}/{retry_count}")
            
            connection = mysql.connector.connect(**DB_CONFIG)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                logger.info(f"✅ MySQL 연결 성공! 서버 버전: {db_info}")
                logger.info(f"📊 연결된 데이터베이스: {connection.database}")
                return connection
                
        except Error as e:
            error_code = e.errno if hasattr(e, 'errno') else 'Unknown'
            logger.warning(f"⚠️ DB 연결 실패 (시도 {attempt + 1}/{retry_count}): [{error_code}] {e}")
            
            # 특정 에러에 대한 상세 정보
            if error_code == 2003:  # Can't connect to MySQL server
                logger.error("🚨 MySQL 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            elif error_code == 1045:  # Access denied
                logger.error("🚨 접근이 거부되었습니다. 사용자명과 비밀번호를 확인하세요.")
            elif error_code == 1049:  # Unknown database
                logger.error("🚨 알 수 없는 데이터베이스입니다. 데이터베이스 이름을 확인하세요.")
            
            if attempt < retry_count - 1:
                logger.info(f"⏳ {retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ 모든 연결 시도 실패")
                
        except Exception as e:
            logger.error(f"❌ 예상치 못한 DB 연결 오류: {e}")
            if attempt < retry_count - 1:
                logger.info(f"⏳ {retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
    
    logger.error("💥 데이터베이스 연결 완전 실패")
    return None

def test_connection():
    """연결 테스트 함수 - 상세한 정보 포함"""
    logger.info("🧪 DB 연결 테스트 시작...")
    logger.info(f"🎯 대상: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # 기본 연결 테스트
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            logger.info(f"✅ 기본 쿼리 테스트 성공: {result}")
            
            # 서버 정보 확인
            cursor.execute("SELECT VERSION(), DATABASE(), USER(), CONNECTION_ID()")
            server_info = cursor.fetchone()
            if server_info:
                logger.info(f"📋 서버 정보:")
                logger.info(f"  - MySQL 버전: {server_info[0]}")
                logger.info(f"  - 현재 DB: {server_info[1]}")
                logger.info(f"  - 사용자: {server_info[2]}")
                logger.info(f"  - 연결 ID: {server_info[3]}")
            
            # 테이블 목록 확인
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logger.info(f"📊 사용 가능한 테이블 수: {len(tables)}")
            if tables:
                table_names = [table[0] for table in tables[:5]]  # 처음 5개만 표시
                logger.info(f"📋 테이블 목록 (일부): {', '.join(table_names)}")
            
            # 권한 확인
            cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
            grants = cursor.fetchall()
            logger.info(f"🔐 사용자 권한 수: {len(grants)}")
            
            cursor.close()
            logger.info("✅ DB 연결 테스트 완료: 모든 검사 통과")
            return True
            
        except Error as e:
            logger.error(f"❌ DB 테스트 쿼리 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ DB 테스트 중 예상치 못한 오류: {e}")
            return False
        finally:
            if connection.is_connected():
                connection.close()
                logger.debug("🔌 DB 연결 종료")
    else:
        logger.error("💥 DB 연결 테스트 실패: 연결을 생성할 수 없음")
        return False

def get_connection_info():
    """현재 DB 설정 정보 반환 (비밀번호 제외)"""
    return {
        "host": DB_CONFIG['host'],
        "port": DB_CONFIG['port'],
        "database": DB_CONFIG['database'],
        "user": DB_CONFIG['user'],
        "charset": DB_CONFIG['charset'],
        "collation": DB_CONFIG['collation']
    }

# 모듈 로드 시 환경변수 정보 로깅
logger.info("🔧 DB 설정 로드 완료:")
logger.info(f"  - Host: {DB_CONFIG['host']}")
logger.info(f"  - Port: {DB_CONFIG['port']}")
logger.info(f"  - Database: {DB_CONFIG['database']}")
logger.info(f"  - User: {DB_CONFIG['user']}")
logger.info(f"  - Password: {'*' * len(DB_CONFIG['password'])}")