# ml/ml_training_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import logging

# 공통 모듈 import를 위한 경로 설정
sys.path.append('/opt/airflow/dags')

from common.config import DEFAULT_ARGS, LOCAL_TZ, TIMEOUTS, SCHEDULES, MODEL_SAVE_PATH, BACKUP_MODEL_PATH
from common.constants import COMMON_EVALUATION_WORDS
from ml.utils.model_utils import ModelManager
from ml.utils.evaluation_utils import ModelEvaluator

def check_training_data(**context):
    """학습 데이터 존재 및 품질 확인"""
    logging.info("=== 학습 데이터 확인 시작 ===")
    
    model_manager = ModelManager()
    data_info = model_manager.check_available_training_data()
    
    if not data_info['has_data']:
        logging.warning("학습 가능한 데이터가 없습니다.")
        return {'skip_training': True, 'reason': 'no_data'}
    
    # 데이터 품질 체크
    quality_score = model_manager.calculate_data_quality_score(data_info)
    
    if quality_score < 70:
        logging.warning(f"데이터 품질이 낮습니다: {quality_score}")
        return {'skip_training': True, 'reason': 'low_quality', 'score': quality_score}
    
    logging.info(f"학습 데이터 확인 완료: {data_info}")
    
    # XCom에 저장
    context['task_instance'].xcom_push(key='data_check_result', value={
        'skip_training': False,
        'data_info': data_info,
        'quality_score': quality_score
    })
    
    return data_info

def backup_current_model(**context):
    """현재 모델 백업"""
    logging.info("=== 현재 모델 백업 시작 ===")
    
    model_manager = ModelManager()
    backup_success = model_manager.backup_current_model()
    
    if not backup_success:
        logging.warning("모델 백업 실패, 하지만 학습은 계속 진행")
    
    context['task_instance'].xcom_push(key='backup_success', value=backup_success)
    
    return backup_success

def train_word2vec_model(**context):
    """Word2Vec 모델 학습"""
    logging.info("=== Word2Vec 모델 학습 시작 ===")
    
    # 데이터 체크 결과 확인
    data_check = context['task_instance'].xcom_pull(
        task_ids='check_training_data',
        key='data_check_result'
    )
    
    if data_check and data_check.get('skip_training'):
        logging.info(f"학습 스킵: {data_check.get('reason')}")
        return {'status': 'skipped', 'reason': data_check.get('reason')}
    
    model_manager = ModelManager()
    
    # 학습 파라미터 설정
    training_params = {
        'vector_size': 100,
        'window': 5,
        'min_count': 2,
        'workers': 4,
        'epochs': 10,
        'sg': 1  # Skip-gram
    }
    
    try:
        # 모델 학습 실행
        training_result = model_manager.train_word2vec_model(training_params)
        
        if training_result['success']:
            logging.info(f"모델 학습 완료: {training_result}")
            
            context['task_instance'].xcom_push(key='training_result', value=training_result)
            return training_result
        else:
            raise Exception(f"모델 학습 실패: {training_result.get('error')}")
            
    except Exception as e:
        logging.error(f"모델 학습 중 예외 발생: {e}")
        return {'success': False, 'error': str(e)}

def evaluate_new_model(**context):
    """새 모델 성능 평가"""
    logging.info("=== 새 모델 성능 평가 시작 ===")
    
    # 학습 결과 확인
    training_result = context['task_instance'].xcom_pull(
        task_ids='train_word2vec_model',
        key='training_result'
    )
    
    if not training_result or not training_result.get('success'):
        logging.error("학습된 모델이 없어 평가를 건너뜁니다.")
        return {'evaluation_passed': False, 'reason': 'no_trained_model'}
    
    model_evaluator = ModelEvaluator()
    
    try:
        # 모델 평가 실행
        evaluation_result = model_evaluator.evaluate_model(
            model_path=training_result.get('model_path', MODEL_SAVE_PATH),
            test_words=COMMON_EVALUATION_WORDS
        )
        
        # 평가 기준 확인
        passed = model_evaluator.check_evaluation_criteria(evaluation_result)
        
        evaluation_summary = {
            'evaluation_passed': passed,
            'vocabulary_size': evaluation_result.get('vocabulary_size', 0),
            'similarity_score': evaluation_result.get('avg_similarity_score', 0),
            'coverage_rate': evaluation_result.get('word_coverage_rate', 0),
            'evaluation_details': evaluation_result
        }
        
        logging.info(f"모델 평가 완료: 통과={passed}")
        
        context['task_instance'].xcom_push(key='evaluation_result', value=evaluation_summary)
        return evaluation_summary
        
    except Exception as e:
        logging.error(f"모델 평가 중 예외 발생: {e}")
        return {'evaluation_passed': False, 'error': str(e)}

def deploy_or_rollback_model(**context):
    """모델 배포 또는 롤백"""
    logging.info("=== 모델 배포/롤백 결정 ===")
    
    evaluation_result = context['task_instance'].xcom_pull(
        task_ids='evaluate_new_model',
        key='evaluation_result'
    )
    
    model_manager = ModelManager()
    
    if evaluation_result and evaluation_result.get('evaluation_passed'):
        # 평가 통과: 새 모델 배포
        logging.info("평가 통과 - 새 모델 배포")
        
        deploy_result = model_manager.deploy_new_model()
        
        if deploy_result['success']:
            logging.info("새 모델 배포 완료")
            result = {
                'action': 'deployed',
                'success': True,
                'model_info': deploy_result
            }
        else:
            logging.error("모델 배포 실패 - 백업으로 롤백")
            rollback_result = model_manager.rollback_to_backup()
            result = {
                'action': 'rollback_after_deploy_fail',
                'success': rollback_result['success'],
                'error': deploy_result.get('error')
            }
    else:
        # 평가 실패: 백업 모델로 롤백
        logging.warning("평가 실패 - 백업 모델로 롤백")
        
        rollback_result = model_manager.rollback_to_backup()
        result = {
            'action': 'rollback_after_eval_fail',
            'success': rollback_result['success'],
            'reason': evaluation_result.get('error', 'evaluation_failed')
        }
    
    context['task_instance'].xcom_push(key='deployment_result', value=result)
    
    return result

def update_failed_games_status(**context):
    """실패했던 게임들의 상태 업데이트"""
    logging.info("=== 실패 게임 상태 업데이트 시작 ===")
    
    deployment_result = context['task_instance'].xcom_pull(
        task_ids='deploy_or_rollback_model',
        key='deployment_result'
    )
    
    # 새 모델이 배포된 경우에만 실행
    if not (deployment_result and deployment_result.get('action') == 'deployed'):
        logging.info("새 모델이 배포되지 않아 상태 업데이트 스킵")
        return {'updated_count': 0, 'reason': 'no_new_model'}
    
    from game.utils.game_utils import GameProcessor
    game_processor = GameProcessor()
    
    try:
        # 모델 부족으로 실패한 게임들을 PENDING 상태로 변경
        updated_count = game_processor.reactivate_model_failed_games()
        
        logging.info(f"실패 게임 상태 업데이트 완료: {updated_count}개")
        
        result = {
            'updated_count': updated_count,
            'action': 'reactivated_failed_games'
        }
        
        context['task_instance'].xcom_push(key='game_update_result', value=result)
        return result
        
    except Exception as e:
        logging.error(f"게임 상태 업데이트 실패: {e}")
        return {'updated_count': 0, 'error': str(e)}

def generate_training_report(**context):
    """학습 리포트 생성"""
    logging.info("=== 학습 리포트 생성 ===")
    
    # 모든 task 결과 수집
    data_check = context['task_instance'].xcom_pull(
        task_ids='check_training_data', key='data_check_result'
    ) or {}
    
    training_result = context['task_instance'].xcom_pull(
        task_ids='train_word2vec_model', key='training_result'
    ) or {}
    
    evaluation_result = context['task_instance'].xcom_pull(
        task_ids='evaluate_new_model', key='evaluation_result'
    ) or {}
    
    deployment_result = context['task_instance'].xcom_pull(
        task_ids='deploy_or_rollback_model', key='deployment_result'
    ) or {}
    
    game_update_result = context['task_instance'].xcom_pull(
        task_ids='update_failed_games_status', key='game_update_result'
    ) or {}
    
    # 리포트 구성
    report = {
        'execution_date': context['ds'],
        'dag_run_id': context['dag_run'].run_id,
        'data_quality': {
            'skip_training': data_check.get('skip_training', False),
            'quality_score': data_check.get('quality_score', 0),
            'data_info': data_check.get('data_info', {})
        },
        'training_results': {
            'success': training_result.get('success', False),
            'training_time': training_result.get('training_time', 0),
            'vocabulary_size': training_result.get('vocabulary_size', 0)
        },
        'evaluation_results': {
            'passed': evaluation_result.get('evaluation_passed', False),
            'similarity_score': evaluation_result.get('similarity_score', 0),
            'coverage_rate': evaluation_result.get('coverage_rate', 0)
        },
        'deployment_results': {
            'action': deployment_result.get('action', 'unknown'),
            'success': deployment_result.get('success', False)
        },
        'game_updates': {
            'reactivated_count': game_update_result.get('updated_count', 0)
        },
        'overall_success': _calculate_overall_success(
            training_result, evaluation_result, deployment_result
        )
    }
    
    # 리포트 저장
    model_manager = ModelManager()
    model_manager.save_training_report(report)
    
    logging.info(f"학습 리포트 생성 완료: {report['overall_success']}")
    
    return report

def _calculate_overall_success(training_result, evaluation_result, deployment_result):
    """전체 성공 여부 계산"""
    return (
        training_result.get('success', False) and
        evaluation_result.get('evaluation_passed', False) and
        deployment_result.get('success', False)
    )

# DAG 정의
dag = DAG(
    'ml_training_pipeline',
    default_args=DEFAULT_ARGS,
    description='Word2Vec 모델 학습 파이프라인',
    schedule_interval=SCHEDULES['model_training'],
    start_date=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    catchup=False,
    max_active_runs=1,
    tags=['ml', 'training', 'word2vec', 'model']
)

# Task 정의
check_data_task = PythonOperator(
    task_id='check_training_data',
    python_callable=check_training_data,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

backup_model_task = PythonOperator(
    task_id='backup_current_model',
    python_callable=backup_current_model,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

train_model_task = PythonOperator(
    task_id='train_word2vec_model',
    python_callable=train_word2vec_model,
    execution_timeout=TIMEOUTS['model_training'],
    dag=dag
)

evaluate_model_task = PythonOperator(
    task_id='evaluate_new_model',
    python_callable=evaluate_new_model,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

deploy_model_task = PythonOperator(
    task_id='deploy_or_rollback_model',
    python_callable=deploy_or_rollback_model,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

update_games_task = PythonOperator(
    task_id='update_failed_games_status',
    python_callable=update_failed_games_status,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

generate_report_task = PythonOperator(
    task_id='generate_training_report',
    python_callable=generate_training_report,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

# Task 의존성 설정
check_data_task >> backup_model_task >> train_model_task
train_model_task >> evaluate_model_task >> deploy_model_task
deploy_model_task >> update_games_task >> generate_report_task