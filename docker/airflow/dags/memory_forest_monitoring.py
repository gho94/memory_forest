"""
Memory Forest 모니터링 DAG
시스템 상태 모니터링, 알림, 긴급 상황 대응
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import pendulum
import logging

# 로컬 모듈 import
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DAG_DEFAULT_ARGS, MONITORING_CONFIG, STATUS_CODES
from utils.database import db_manager
from utils.ai_service import ai_client

local_tz = pendulum.timezone("Asia/Seoul")
logger = logging.getLogger(__name__)

def check_critical_metrics(**context):
    """핵심 지표 모니터링"""
    logger.info("=== 핵심 지표 체크 시작 ===")
    
    alerts = []
    metrics = {
        "ai_service_healthy": False,
        "database_healthy": False,
        "pending_games_count": 0,
        "error_rate_today": 0.0,
        "processing_queue_health": "unknown"
    }
    
    try:
        # AI 서비스 상태
        metrics["ai_service_healthy"] = ai_client.check_health()
        if not metrics["ai_service_healthy"]:
            alerts.append("AI 서비스 응답 없음")
        
        # 데이터베이스 상태 및 통계
        try:
            stats = db_manager.get_processing_statistics()
            metrics["database_healthy"] = True
            
            # 대기 중인 게임 수 체크
            pending_count = 0
            for stat in stats['status_breakdown']:
                if stat['ai_status_code'] == STATUS_CODES['PENDING']:
                    pending_count = stat['total_count']
                    break
            
            metrics["pending_games_count"] = pending_count
            
            # 임계치 체크
            if pending_count > MONITORING_CONFIG['pending_threshold_count']:
                alerts.append(f"대기 게임 수 임계치 초과: {pending_count}개")
            
            # 오늘의 오류율 계산
            today_stats = stats['today_summary']
            if today_stats['total_processed_today'] > 0:
                error_rate = (today_stats['failed_today'] / today_stats['total_processed_today']) * 100
                metrics["error_rate_today"] = round(error_rate, 2)
                
                if error_rate > MONITORING_CONFIG['error_threshold_percentage']:
                    alerts.append(f"오류율 임계치 초과: {error_rate:.1f}%")
            
            # 처리 대기열 상태 판단
            if pending_count == 0:
                metrics["processing_queue_health"] = "idle"
            elif pending_count < 50:
                metrics["processing_queue_health"] = "normal"
            elif pending_count < 100:
                metrics["processing_queue_health"] = "busy"
            else:
                metrics["processing_queue_health"] = "overloaded"
                
        except Exception as e:
            alerts.append(f"데이터베이스 체크 실패: {str(e)}")
            metrics["database_healthy"] = False
        
        # 전체 시스템 상태 로깅
        logger.info("=== 시스템 핵심 지표 ===")
        logger.info(f"AI 서비스: {'정상' if metrics['ai_service_healthy'] else '비정상'}")
        logger.info(f"데이터베이스: {'정상' if metrics['database_healthy'] else '비정상'}")
        logger.info(f"대기 게임 수: {metrics['pending_games_count']}개")
        logger.info(f"오늘 오류율: {metrics['error_rate_today']}%")
        logger.info(f"처리 대기열: {metrics['processing_queue_health']}")
        
        if alerts:
            logger.warning("=== 알림 발생 ===")
            for alert in alerts:
                logger.warning(f"  ⚠️  {alert}")
        else:
            logger.info("✅ 모든 지표 정상")
        
        return {
            "metrics": metrics,
            "alerts": alerts,
            "status": "critical" if alerts else "normal"
        }
        
    except Exception as e:
        logger.error(f"핵심 지표 체크 실패: {e}")
        return {
            "metrics": metrics,
            "alerts": [f"모니터링 시스템 오류: {str(e)}"],
            "status": "error"
        }

def check_disk_space(**context):
    """디스크 공간 체크"""
    logger.info("=== 디스크 공간 체크 ===")
    
    try:
        # df 명령어로 디스크 사용량 체크
        import subprocess
        result = subprocess.run(['df', '-h', '/opt/airflow'], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    usage_percent = parts[4].rstrip('%')
                    logger.info(f"디스크 사용량: {usage_percent}%")
                    
                    if int(usage_percent) > 85:
                        logger.warning(f"디스크 공간 부족: {usage_percent}% 사용중")
                        return {"disk_status": "warning", "usage": f"{usage_percent}%"}
                    else:
                        return {"disk_status": "normal", "usage": f"{usage_percent}%"}
        
        return {"disk_status": "unknown", "usage": "확인 불가"}
        
    except Exception as e:
        logger.error(f"디스크 공간 체크 실패: {e}")
        return {"disk_status": "error", "error": str(e)}

def check_memory_usage(**context):
    """메모리 사용량 체크"""
    logger.info("=== 메모리 사용량 체크 ===")
    
    try:
        import psutil
        
        # 시스템 메모리 정보
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        logger.info(f"메모리 사용량: {memory_percent:.1f}%")
        logger.info(f"사용 가능 메모리: {memory.available / (1024**3):.1f}GB")
        
        if memory_percent > 90:
            logger.warning(f"메모리 사용량 높음: {memory_percent:.1f}%")
            return {"memory_status": "critical", "usage": f"{memory_percent:.1f}%"}
        elif memory_percent > 80:
            logger.warning(f"메모리 사용량 주의: {memory_percent:.1f}%")
            return {"memory_status": "warning", "usage": f"{memory_percent:.1f}%"}
        else:
            return {"memory_status": "normal", "usage": f"{memory_percent:.1f}%"}
            
    except ImportError:
        logger.info("psutil 모듈 없음 - 메모리 체크 스킵")
        return {"memory_status": "skipped", "reason": "psutil not available"}
    except Exception as e:
        logger.error(f"메모리 체크 실패: {e}")
        return {"memory_status": "error", "error": str(e)}

def emergency_response(**context):
    """긴급 상황 대응"""
    logger.info("=== 긴급 상황 체크 ===")
    
    # 이전 태스크에서 메트릭스 가져오기
    metrics_result = context['task_instance'].xcom_pull(task_ids='check_critical_metrics')
    
    if not metrics_result:
        logger.error("메트릭스 정보를 가져올 수 없음")
        return {"emergency_actions": [], "status": "error"}
    
    emergency_actions = []
    
    try:
        alerts = metrics_result.get('alerts', [])
        metrics = metrics_result.get('metrics', {})
        
        # 긴급 상황 판단 및 대응
        if not metrics.get('ai_service_healthy'):
            emergency_actions.append("AI 서비스 재시작 필요")
            
        if not metrics.get('database_healthy'):
            emergency_actions.append("데이터베이스 연결 복구 필요")
            
        if metrics.get('pending_games_count', 0) > 500:
            emergency_actions.append("대기 게임 수 과다 - 처리 능력 증대 필요")
            
        if metrics.get('error_rate_today', 0) > 50:
            emergency_actions.append("높은 오류율 - 시스템 점검 필요")
        
        # 긴급 상황 시 자동 대응 (예시)
        if emergency_actions:
            logger.warning("=== 긴급 상황 감지 ===")
            for action in emergency_actions:
                logger.warning(f"🚨 {action}")
            
            # 실제 운영에서는 여기에 자동화된 복구 액션 추가
            # 예: 서비스 재시작, 알림 발송, 부하 분산 등
            
        else:
            logger.info("✅ 긴급 상황 없음")
        
        return {
            "emergency_actions": emergency_actions,
            "status": "emergency" if emergency_actions else "normal"
        }
        
    except Exception as e:
        logger.error(f"긴급 상황 체크 실패: {e}")
        return {"emergency_actions": [], "status": "error", "error": str(e)}

# 모니터링 DAG 정의
monitoring_default_args = {
    **DAG_DEFAULT_ARGS,
    'start_date': datetime(2024, 1, 1, tzinfo=local_tz),  # start_date 추가
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

monitoring_dag = DAG(
    'memory_forest_monitoring',
    default_args=monitoring_default_args,
    description='Memory Forest 시스템 모니터링 및 알림',
    schedule_interval='*/15 * * * *',  # 15분마다 실행
    catchup=False,
    max_active_runs=1,
    tags=['memory-forest', 'monitoring', 'alerts']
)

# 모니터링 Task 정의
metrics_check_task = PythonOperator(
    task_id='check_critical_metrics',
    python_callable=check_critical_metrics,
    dag=monitoring_dag
)

disk_check_task = PythonOperator(
    task_id='check_disk_space',
    python_callable=check_disk_space,
    dag=monitoring_dag
)

memory_check_task = PythonOperator(
    task_id='check_memory_usage',
    python_callable=check_memory_usage,
    dag=monitoring_dag
)

emergency_task = PythonOperator(
    task_id='emergency_response',
    python_callable=emergency_response,
    dag=monitoring_dag
)

# 모니터링 DAG 의존성
metrics_check_task >> [disk_check_task, memory_check_task] >> emergency_task