from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

# 공통 모듈 import 경로 추가
sys.path.append('/opt/airflow/dags')

from common.config import DEFAULT_ARGS, LOCAL_TZ, TIMEOUTS, SCHEDULES
from data.utils.crawling_utils import collect_failed_words, crawl_naver_blogs
from data.utils.preprocessing_utils import (
    preprocess_texts, 
    validate_processed_data, 
    cleanup_old_data, 
    send_collection_summary
)

dag = DAG(
    'data_collection_pipeline',
    default_args=DEFAULT_ARGS,
    description='데이터 수집 및 전처리 파이프라인',
    schedule_interval=SCHEDULES['data_collection'],
    start_date=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    catchup=False,
    max_active_runs=1,
    tags=['data', 'collection', 'preprocessing', 'crawling']
)

collect_failed_words_task = PythonOperator(
    task_id='collect_failed_words',
    python_callable=collect_failed_words,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

crawl_blogs_task = PythonOperator(
    task_id='crawl_naver_blogs',
    python_callable=crawl_naver_blogs,
    execution_timeout=TIMEOUTS['data_collection'],
    dag=dag
)

preprocess_task = PythonOperator(
    task_id='preprocess_texts',
    python_callable=preprocess_texts,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_processed_data',
    python_callable=validate_processed_data,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_data',
    python_callable=cleanup_old_data,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

summary_task = PythonOperator(
    task_id='send_collection_summary',
    python_callable=send_collection_summary,
    execution_timeout=TIMEOUTS['system_management'],
    dag=dag
)

collect_failed_words_task >> crawl_blogs_task >> preprocess_task
preprocess_task >> validate_task >> cleanup_task >> summary_task
