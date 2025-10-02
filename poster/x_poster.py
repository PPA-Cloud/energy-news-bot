"""
X (Twitter) Poster for Energy News Bot
Posts tweets with images using X API v2
"""
import sqlite3
import tweepy
import requests
from datetime import datetime
from typing import Dict
import logging
import time

logger = logging.getLogger(__name__)


class XPoster:
    """Posts tweets to X (Twitter) with media."""
    
    def __init__(self, db_path: str, api_key: str, api_secret: str, 
                 access_token: str, access_token_secret: str):
        self.db_path = db_path
        
        # Initialize Tweepy client (v2 API) with OAuth 1.0a
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Initialize API v1.1 for media upload
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret, access_token, access_token_secret
        )
        self.api = tweepy.API(auth)
    
    def post_tweets(self, max_tweets: int = 10, delay_seconds: int = 60) -> Dict:
        """
        Post draft tweets to X.
        
        Args:
            max_tweets: Maximum number of tweets to post in this run
            delay_seconds: Delay between posts to avoid rate limits
            
        Returns:
            Stats dict
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get draft tweets
        cursor.execute("""
            SELECT id, tweet_text, image_url, article_link
            FROM tweets
            WHERE status = 'draft'
            ORDER BY id ASC
            LIMIT ?
        """, (max_tweets,))
        tweets = cursor.fetchall()
        
        posted = 0
        failed = 0
        
        logger.info(f"Posting {len(tweets)} tweets...")
        
        for tweet_id, text, image_url, article_link in tweets:
            try:
                # Download and upload image if available
                media_id = None
                if image_url:
                    try:
                        media_id = self._upload_image(image_url)
                    except Exception as e:
                        logger.warning(f"Failed to upload image: {e}")
                
                # Post tweet
                if media_id:
                    response = self.client.create_tweet(
                        text=text,
                        media_ids=[media_id]
                    )
                else:
                    response = self.client.create_tweet(text=text)
                
                tweet_x_id = response.data['id']
                
                # Update database
                cursor.execute("""
                    UPDATE tweets
                    SET status = 'posted', tweet_id = ?, posted_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (tweet_x_id, tweet_id))
                
                # Update article status
                cursor.execute("""
                    UPDATE articles
                    SET status = 'posted'
                    WHERE id = (SELECT article_id FROM tweets WHERE id = ?)
                """, (tweet_id,))
                
                posted += 1
                logger.info(f"✓ Posted tweet {tweet_id}: {text[:50]}...")
                
                # Delay between posts
                if posted < len(tweets):
                    time.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"✗ Failed to post tweet {tweet_id}: {e}")
                
                # Mark as failed
                cursor.execute("""
                    UPDATE tweets
                    SET status = 'failed', error = ?
                    WHERE id = ?
                """, (str(e), tweet_id))
                
                failed += 1
        
        conn.commit()
        conn.close()
        
        return {
            'total': len(tweets),
            'posted': posted,
            'failed': failed
        }
    
    def _upload_image(self, image_url: str) -> str:
        """Download and upload image to X, return media_id."""
        
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Save temporarily
        temp_path = f"/tmp/news_image_{int(time.time())}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # Upload to X
        media = self.api.media_upload(temp_path)
        
        # Clean up
        import os
        os.remove(temp_path)
        
        return media.media_id_string
    
    def update_engagement_metrics(self) -> Dict:
        """Fetch and update engagement metrics for posted tweets."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get posted tweets from last 7 days
        cursor.execute("""
            SELECT id, tweet_id
            FROM tweets
            WHERE status = 'posted' 
            AND posted_at > datetime('now', '-7 days')
            AND tweet_id IS NOT NULL
        """)
        tweets = cursor.fetchall()
        
        updated = 0
        
        for tweet_id, x_tweet_id in tweets:
            try:
                # Fetch tweet metrics from X
                tweet_data = self.client.get_tweet(
                    x_tweet_id,
                    tweet_fields=['public_metrics']
                )
                
                metrics = tweet_data.data.public_metrics
                
                # Update database
                cursor.execute("""
                    UPDATE tweets
                    SET likes = ?, retweets = ?, replies = ?, impressions = ?
                    WHERE id = ?
                """, (
                    metrics.get('like_count', 0),
                    metrics.get('retweet_count', 0),
                    metrics.get('reply_count', 0),
                    metrics.get('impression_count', 0),
                    tweet_id
                ))
                
                updated += 1
                
            except Exception as e:
                logger.error(f"Failed to update metrics for tweet {tweet_id}: {e}")
        
        conn.commit()
        conn.close()
        
        return {'updated': updated}


if __name__ == "__main__":
    # Test poster
    import sys
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    poster = XPoster(
        "./database/energy_news.db",
        os.getenv("X_API_KEY"),
        os.getenv("X_API_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_TOKEN_SECRET")
    )
    
    # Post tweets
    stats = poster.post_tweets(max_tweets=5, delay_seconds=30)
    print(f"\n✅ Posting complete!")
    print(f"   Total: {stats['total']}")
    print(f"   Posted: {stats['posted']}")
    print(f"   Failed: {stats['failed']}")
