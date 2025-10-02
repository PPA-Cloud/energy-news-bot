#!/usr/bin/env python3
"""
Generate and post tweets from already-approved articles in the database
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Python 3.13 compatibility - must be imported before tweepy
import imghdr_compat

from processor.llm_processor import LLMProcessor
from poster.x_poster import XPoster

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    db_path = Path(__file__).parent / 'database' / 'energy_news.db'
    
    logger.info("=" * 80)
    logger.info("GENERATING TWEETS FROM APPROVED ARTICLES")
    logger.info("=" * 80)
    
    # Initialize processor
    processor = LLMProcessor(db_path, os.getenv('OPENAI_API_KEY'))
    
    # Generate tweets for approved articles
    logger.info("\n✍️  Generating tweets from approved articles...")
    tweet_stats = processor.generate_tweets()
    logger.info(f"✓ Generated {tweet_stats['generated']} tweets")
    
    # Post to X
    logger.info("\n🐦 Posting to X...")
    poster = XPoster(
        db_path,
        os.getenv('X_API_KEY'),
        os.getenv('X_API_SECRET'),
        os.getenv('X_ACCESS_TOKEN'),
        os.getenv('X_ACCESS_TOKEN_SECRET')
    )
    
    post_stats = poster.post_tweets(max_tweets=3)
    logger.info(f"✓ Posted {post_stats['posted']} tweets (failed: {post_stats['failed']})")
    
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Tweets generated: {tweet_stats['generated']}")
    logger.info(f"Tweets posted: {post_stats['posted']}")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
