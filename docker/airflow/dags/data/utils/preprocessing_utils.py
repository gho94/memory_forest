# data/utils/preprocessing_utils.py
import logging
import os
import shutil
from datetime import datetime, timedelta
from data.utils.preprocessing_utils import TextPreprocessor

def preprocess_texts(**context):
    logging.info("=== 텍스트 전처리 시작 ===")
    
    crawl_info = context['task_instance'].xcom_pull(
        task_ids='crawl_naver_blogs', key='crawl_results'
    ) or {}

    folder_date = crawl_info.get('folder_date', context['ds_nodash'])

    preprocessor = TextPreprocessor()
    processed_data = preprocessor.process_crawled_data(folder_date)

    if processed_data is None:
        raise ValueError("전처리 실패: 크롤링 데이터를 찾을 수 없습니다.")

    logging.info(f"전처리 완료: {processed_data['processed_count']}개 문장 처리")
    context['task_instance'].xcom_push(key='preprocessing_results', value=processed_data)
    return processed_data

def validate_processed_data(**context):
    logging.info("=== 데이터 검증 시작 ===")

    preprocessing_info = context['task_instance'].xcom_pull(
        task_ids='preprocess_texts', key='preprocessing_results'
    ) or {}

    validation_results = {
        'total_sentences': preprocessing_info.get('processed_count', 0),
        'avg_sentence_length': preprocessing_info.get('avg_length', 0),
        'unique_words': preprocessing_info.get('unique_words', 0),
        'validation_passed': False
    }

    if (validation_results['total_sentences'] >= 1000 and
        validation_results['avg_sentence_length'] >= 10 and
        validation_results['unique_words'] >= 500):
        validation_results['validation_passed'] = True
        logging.info("데이터 검증 통과")
    else:
        logging.warning(f"데이터 품질 기준 미달: {validation_results}")

    context['task_instance'].xcom_push(key='validation_results', value=validation_results)
    return validation_results

def cleanup_old_data(**context):
    logging.info("=== 오래된 데이터 정리 시작 ===")
    
    data_base_path = "/opt/airflow/data"
    cutoff_date = datetime.now() - timedelta(days=7)
    deleted_folders = []

    for folder_name in os.listdir(data_base_path):
        folder_path = os.path.join(data_base_path, folder_name)

        if not os.path.isdir(folder_path):
            continue

        try:
            folder_date = datetime.strptime(folder_name, "%Y%m%d")
            if folder_date < cutoff_date:
                shutil.rmtree(folder_path)
                deleted_folders.append(folder_name)
                logging.info(f"삭제된 폴더: {folder_name}")
        except ValueError:
            continue

    logging.info(f"정리 완료: {len(deleted_folders)}개 폴더 삭제")
    return deleted_folders

def send_collection_summary(**context):
    logging.info("=== 데이터 수집 요약 생성 ===")

    failed_words = context['task_instance'].xcom_pull(
        task_ids='collect_failed_words', key='failed_words'
    ) or []

    crawl_info = context['task_instance'].xcom_pull(
        task_ids='crawl_naver_blogs', key='crawl_results'
    ) or {}

    preprocessing_info = context['task_instance'].xcom_pull(
        task_ids='preprocess_texts', key='preprocessing_results'
    ) or {}

    validation_info = context['task_instance'].xcom_pull(
        task_ids='validate_processed_data', key='validation_results'
    ) or {}

    summary = {
        'execution_date': context['ds'],
        'dag_run_id': context['dag_run'].run_id,
        'failed_words_count': len(failed_words),
        'total_sentences_crawled': crawl_info.get('total_sentences', 0),
        'keywords_used': crawl_info.get('keywords_count', 0),
        'sentences_processed': preprocessing_info.get('processed_count', 0),
        'unique_words_found': preprocessing_info.get('unique_words', 0),
        'validation_passed': validation_info.get('validation_passed', False),
        'data_quality_score': _calculate_quality_score(preprocessing_info, validation_info)
    }

    logging.info(f"데이터 수집 파이프라인 요약: {summary}")
    return summary

def _calculate_quality_score(preprocessing_info, validation_info):
    base_score = 0

    if validation_info.get('validation_passed', False):
        base_score += 50

    sentence_count = preprocessing_info.get('processed_count', 0)
    if sentence_count >= 5000:
        base_score += 30
    elif sentence_count >= 3000:
        base_score += 20
    elif sentence_count >= 1000:
        base_score += 10

    unique_words = preprocessing_info.get('unique_words', 0)
    if unique_words >= 2000:
        base_score += 20
    elif unique_words >= 1000:
        base_score += 10
    elif unique_words >= 500:
        base_score += 5

    return min(base_score, 100)
