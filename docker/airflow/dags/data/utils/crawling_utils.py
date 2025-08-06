# data/utils/crawling_utils.py
import logging
from common.constants import BASE_EMOTION_CATEGORIES
from data.utils.crawling_utils import NaverBlogCrawler
from game.utils.game_utils import GameAnalyzer

def collect_failed_words(**context):
    logging.info("=== 분석 실패 단어 수집 시작 ===")
    
    game_analyzer = GameAnalyzer()
    failed_words = game_analyzer.get_failed_words(limit=100)
    
    if not failed_words:
        logging.info("분석 실패한 단어가 없습니다.")
        return []
    
    logging.info(f"분석 실패 단어 {len(failed_words)}개 수집: {failed_words[:10]}...")
    context['task_instance'].xcom_push(key='failed_words', value=failed_words)
    return failed_words

def crawl_naver_blogs(**context):
    logging.info("=== 네이버 블로그 크롤링 시작 ===")
    
    failed_words = context['task_instance'].xcom_pull(
        task_ids='collect_failed_words', key='failed_words'
    ) or []

    search_keywords = BASE_EMOTION_CATEGORIES + failed_words
    folder_date = context['ds_nodash']

    crawler = NaverBlogCrawler()
    results = crawler.crawl_blogs(
        keywords=search_keywords,
        folder_date=folder_date,
        failed_words=failed_words
    )

    logging.info(f"크롤링 완료: 총 {len(results)}개 문장 수집")

    context['task_instance'].xcom_push(key='crawl_results', value={
        'total_sentences': len(results),
        'folder_date': folder_date,
        'keywords_count': len(search_keywords),
        'failed_words_count': len(failed_words)
    })
    
    return results
