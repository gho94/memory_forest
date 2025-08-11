"""
Memory Forest 유지보수 DAG - 기존 AI 서비스와 repository 호환
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pendulum
import logging

# 로컬 모듈 import
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    DAG_DEFAULT_ARGS, BATCH_SIZES, RETRY_RULES, MONITORING_CONFIG, 
    SCHEDULES, DEFAULT_ARGS, LOCAL_TZ
)
from utils.database import db_manager
from utils.ai_service import ai_client

logger = logging.getLogger(__name__)

def retry_failed_games(**context):
    """실패한 게임들 재시도 처리"""
    logger.info("=== 실패 게임 재시도 시작 ===")
    
    try:
        # 재시도 가능한 오류 키워드들
        retry_keywords = (
            RETRY_RULES['connection_errors'] + 
            RETRY_RULES['service_errors'] + 
            RETRY_RULES['temporary_errors']
        )
        
        # 재시도 설정
        retried_count = db_manager.mark_games_for_retry(
            retry_keywords, 
            BATCH_SIZES['error_games']
        )
        
        logger.info(f"재시도 설정 완료: {retried_count}개 게임")
        
        return {
            "retried_count": retried_count,
            "retry_keywords": retry_keywords
        }
        
    except Exception as e:
        logger.error(f"재시도 설정 실패: {e}")
        return {"retried_count": 0, "error": str(e)}

def analyze_error_patterns(**context):
    """오류 패턴 분석"""
    logger.info("=== 오류 패턴 분석 시작 ===")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(buffered=True, dictionary=True)
            
            # 최근 7일간 오류 패턴 분석 (B20008 = FAILED)
            query = """
            SELECT 
                SUBSTRING(description, 1, 50) as error_pattern,
                COUNT(*) as error_count,
                COUNT(DISTINCT answer_text) as unique_answers,
                GROUP_CONCAT(DISTINCT answer_text LIMIT 10) as sample_answers
            FROM game_detail 
            WHERE ai_status_code = 'B20008'
            AND ai_processed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            AND description IS NOT NULL
            GROUP BY SUBSTRING(description, 1, 50)
            ORDER BY error_count DESC
            LIMIT 20
            """
            
            cursor.execute(query)
            error_patterns = cursor.fetchall()
            
            logger.info("=== 오류 패턴 분석 결과 ===")
            for pattern in error_patterns:
                logger.info(f"  패턴: {pattern['error_pattern']}")
                logger.info(f"    발생 횟수: {pattern['error_count']}")
                logger.info(f"    고유 답변 수: {pattern['unique_answers']}")
                logger.info(f"    샘플: {pattern['sample_answers'][:100] if pattern['sample_answers'] else 'None'}...")
                logger.info("  ---")
            
            # 가장 문제가 되는 답변들 식별
            problem_answers_query = """
            SELECT 
                answer_text,
                COUNT(*) as failure_count,
                MAX(ai_processed_at) as last_failure,
                GROUP_CONCAT(DISTINCT SUBSTRING(description, 1, 30) LIMIT 3) as error_types
            FROM game_detail 
            WHERE ai_status_code = 'B20008'
            AND ai_processed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            AND answer_text IS NOT NULL
            GROUP BY answer_text
            HAVING failure_count >= 3
            ORDER BY failure_count DESC
            LIMIT 15
            """
            
            cursor.execute(problem_answers_query)
            problem_answers = cursor.fetchall()
            
            logger.info("=== 문제 답변 분석 ===")
            for answer in problem_answers:
                logger.info(f"  답변: '{answer['answer_text']}'")
                logger.info(f"    실패 횟수: {answer['failure_count']}")
                logger.info(f"    마지막 실패: {answer['last_failure']}")
                logger.info(f"    오류 유형: {answer['error_types']}")
                logger.info("  ---")
            
            # 커서 정리
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            cursor.close()
            
            return {
                "error_patterns": error_patterns,
                "problem_answers": problem_answers,
                "analysis_completed": True
            }
            
    except Exception as e:
        logger.error(f"오류 패턴 분석 실패: {e}")
        return {"analysis_completed": False, "error": str(e)}

def generate_daily_report(**context):
    """일일 처리 보고서 생성"""
    logger.info("=== 일일 보고서 생성 시작 ===")
    
    try:
        # 전체 통계 조회
        stats = db_manager.get_processing_statistics()
        
        # 보고서 생성
        report = {
            "report_date": datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {},
            "details": {}
        }
        
        # 오늘의 처리 요약
        today_stats = stats['today_summary']
        report["summary"] = {
            "total_processed_today": today_stats['total_processed_today'],
            "completed_today": today_stats['completed_today'],
            "failed_today": today_stats['failed_today'],
            "success_rate": (
                round((today_stats['completed_today'] / max(today_stats['total_processed_today'], 1)) * 100, 2)
            )
        }
        
        # 상태별 상세 현황
        status_details = {}
        status_mapping = {
            'B20005': 'PENDING',
            'B20007': 'COMPLETED', 
            'B20008': 'FAILED'
        }
        
        for stat in stats['status_breakdown']:
            status_code = stat['ai_status_code']
            status_name = status_mapping.get(status_code, status_code)
            status_details[status_name] = {
                "total": stat['total_count'],
                "today": stat['today_count']
            }
        
        report["details"]["status_breakdown"] = status_details
        
        # 난이도별 현황
        difficulty_details = {}
        difficulty_mapping = {
            'B20001': 'EASY',
            'B20002': 'NORMAL',
            'B20003': 'HARD', 
            'B20004': 'EXPERT'
        }
        
        for stat in stats['difficulty_breakdown']:
            difficulty_code = stat['difficulty_level_code']
            difficulty = difficulty_mapping.get(difficulty_code, difficulty_code)
            
            if difficulty not in difficulty_details:
                difficulty_details[difficulty] = {}
            
            status_code = stat['ai_status_code']
            status_name = status_mapping.get(status_code, status_code)
            difficulty_details[difficulty][status_name] = stat['count']
        
        report["details"]["difficulty_breakdown"] = difficulty_details
        
        # 보고서 로깅
        logger.info("=== 일일 처리 보고서 ===")
        logger.info(f"날짜: {report['report_date']}")
        logger.info(f"오늘 처리량: {report['summary']['total_processed_today']}개")
        logger.info(f"성공률: {report['summary']['success_rate']}%")
        logger.info(f"완료: {report['summary']['completed_today']}개")
        logger.info(f"실패: {report['summary']['failed_today']}개")
        
        logger.info("=== 상태별 현황 ===")
        for status, counts in status_details.items():
            logger.info(f"  {status}: 전체 {counts['total']}개, 오늘 {counts['today']}개")
        
        return report
        
    except Exception as e:
        logger.error(f"일일 보고서 생성 실패: {e}")
        return {"report_generated": False, "error": str(e)}

def cleanup_old_data(**context):
    """오래된 데이터 정리"""
    logger.info("=== 데이터 정리 시작 ===")
    
    cleanup_results = {
        "old_logs_cleaned": 0,
        "temp_data_cleaned": 0,
        "cleanup_completed": False
    }
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(buffered=True)
            
            # 90일 이상 된 완료 게임 카운트 (B20007 = COMPLETED)
            count_query = """
            SELECT COUNT(*) as old_count
            FROM game_detail 
            WHERE ai_status_code = 'B20007'
            AND ai_processed_at < DATE_SUB(NOW(), INTERVAL 90 DAY)
            """
            
            cursor.execute(count_query)
            result = cursor.fetchone()
            cleanup_results["old_logs_cleaned"] = result[0] if result else 0
            
            cleanup_results["cleanup_completed"] = True
            
            logger.info(f"정리 완료: 90일 이상 된 완료 게임 {cleanup_results['old_logs_cleaned']}개 확인")
            
            # 커서 정리
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            cursor.close()
            
    except Exception as e:
        logger.error(f"데이터 정리 실패: {e}")
        cleanup_results["error"] = str(e)
    
    return cleanup_results

def optimize_database_performance(**context):
    """데이터베이스 성능 최적화"""
    logger.info("=== 데이터베이스 최적화 시작 ===")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(buffered=True)
            
            # 테이블 분석 (통계 업데이트)
            tables_to_analyze = ['game_detail', 'game_master', 'file_info']
            
            for table in tables_to_analyze:
                try:
                    cursor.execute(f"ANALYZE TABLE {table}")
                    logger.info(f"테이블 분석 완료: {table}")
                except Exception as e:
                    logger.warning(f"테이블 분석 실패 ({table}): {e}")
            
            # 인덱스 사용량 체크
            index_query = """
            SELECT 
                TABLE_NAME,
                INDEX_NAME,
                CARDINALITY
            FROM information_schema.STATISTICS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME IN ('game_detail', 'game_master')
            ORDER BY TABLE_NAME, CARDINALITY DESC
            """
            
            cursor.execute(index_query, (db_manager.config['database'],))
            index_info = cursor.fetchall()
            
            logger.info("=== 인덱스 현황 ===")
            for info in index_info:
                logger.info(f"  {info[0]}.{info[1]}: {info[2]} cardinality")
            
            # 커서 정리
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            cursor.close()
            
            return {"optimization_completed": True, "tables_analyzed": len(tables_to_analyze)}
            
    except Exception as e:
        logger.error(f"데이터베이스 최적화 실패: {e}")
        return {"optimization_completed": False, "error": str(e)}

# 유지보수 DAG 정의
maintenance_default_args = {
    **DEFAULT_ARGS,
    'start_date': datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    'retries': 1,  # 유지보수 작업은 재시도 줄임
}

maintenance_dag = DAG(
    'memory_forest_ai_maintenance',
    default_args=maintenance_default_args,
    description='Memory Forest AI 시스템 유지보수 및 분석',
    schedule_interval=SCHEDULES['maintenance'],  # 매일 오전 9시 15분 실행
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'maintenance', 'analysis']
)

# 유지보수 Task 정의
start_maintenance = DummyOperator(
    task_id='start_maintenance',
    dag=maintenance_dag
)

retry_task = PythonOperator(
    task_id='retry_failed_games',
    python_callable=retry_failed_games,
    dag=maintenance_dag
)

error_analysis_task = PythonOperator(
    task_id='analyze_error_patterns',
    python_callable=analyze_error_patterns,
    dag=maintenance_dag
)

daily_report_task = PythonOperator(
    task_id='generate_daily_report',
    python_callable=generate_daily_report,
    dag=maintenance_dag
)

cleanup_data_task = PythonOperator(
    task_id='cleanup_old_data',
    python_callable=cleanup_old_data,
    dag=maintenance_dag
)

optimize_db_task = PythonOperator(
    task_id='optimize_database',
    python_callable=optimize_database_performance,
    dag=maintenance_dag
)

end_maintenance = DummyOperator(
    task_id='end_maintenance',
    dag=maintenance_dag
)

# 유지보수 DAG 의존성
start_maintenance >> [retry_task, error_analysis_task] >> daily_report_task >> [cleanup_data_task, optimize_db_task] >> end_maintenance