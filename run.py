"""
Energy News Bot - Main Orchestrator
Runs the complete pipeline: crawl → filter → generate → post
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Python 3.13 compatibility - must be imported before tweepy
import imghdr_compat

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from crawler.rss_crawler import RSSCrawler
from processor.llm_processor import LLMProcessor
from poster.x_poster import XPoster

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('energy_news_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline(hours_back: int = 12, max_tweets: int = 10):
    """
    Run the complete news bot pipeline.
    
    Args:
        hours_back: Crawl articles from last N hours
        max_tweets: Maximum tweets to post in this run
    """
    
    # Load environment variables
    load_dotenv()
    
    db_path = os.getenv('DATABASE_PATH', './database/energy_news.db')
    
    logger.info("="*80)
    logger.info("ENERGY NEWS BOT - PIPELINE START")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # Step 1: Crawl RSS feeds
    logger.info("\n📡 STEP 1: Crawling RSS feeds...")
    crawler = RSSCrawler(db_path)
    crawl_stats = crawler.crawl_all_sources(hours_back=hours_back)
    logger.info(f"✓ Crawled {crawl_stats['sources_crawled']} sources")
    logger.info(f"✓ Found {crawl_stats['articles_found']} articles ({crawl_stats['articles_new']} new)")
    
    # Step 2: Filter articles with LLM
    logger.info("\n🤖 STEP 2: Filtering articles with LLM...")
    processor = LLMProcessor(db_path, os.getenv('OPENAI_API_KEY'))
    filter_stats = processor.filter_articles()
    logger.info(f"✓ Filtered {filter_stats['total']} articles")
    logger.info(f"✓ Approved: {filter_stats['approved']}, Filtered out: {filter_stats['filtered_out']}")
    
    # Step 3: Generate tweets
    logger.info("\n✍️  STEP 3: Generating tweets...")
    tweet_stats = processor.generate_tweets()
    logger.info(f"✓ Generated {tweet_stats['generated']} tweets")
    
    # Step 4: Post to X
    logger.info("\n🐦 STEP 4: Posting to X...")
    poster = XPoster(
        db_path,
        os.getenv('X_API_KEY'),
        os.getenv('X_API_SECRET'),
        os.getenv('X_ACCESS_TOKEN'),
        os.getenv('X_ACCESS_TOKEN_SECRET')
    )
    post_stats = poster.post_tweets(max_tweets=max_tweets, delay_seconds=60)
    logger.info(f"✓ Posted {post_stats['posted']} tweets (failed: {post_stats['failed']})")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("PIPELINE COMPLETE - SUMMARY")
    logger.info("="*80)
    logger.info(f"Articles crawled: {crawl_stats['articles_new']}")
    logger.info(f"Articles approved: {filter_stats['approved']}")
    logger.info(f"Tweets generated: {tweet_stats['generated']}")
    logger.info(f"Tweets posted: {post_stats['posted']}")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Energy News Bot")
    parser.add_argument('--hours', type=int, default=12, help='Crawl articles from last N hours')
    parser.add_argument('--max-tweets', type=int, default=10, help='Maximum tweets to post')
    
    args = parser.parse_args()
    
    try:
        run_pipeline(hours_back=args.hours, max_tweets=args.max_tweets)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)
