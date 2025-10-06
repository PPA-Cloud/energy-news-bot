"""
LLM Processor for Energy News Bot
Filters articles and generates tweets using OpenAI
"""
import sqlite3
import yaml
from pathlib import Path
from typing import Dict
from openai import OpenAI
import logging
import os

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Processes articles with LLM for filtering and tweet generation."""
    
    def __init__(self, db_path: str, openai_api_key: str):
        self.db_path = db_path
        self.client = OpenAI(api_key=openai_api_key)
        
        # Load prompts
        prompts_path = Path(__file__).parent.parent / "config" / "prompts.yaml"
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)
    
    def filter_articles(self) -> Dict:
        """Filter pending articles for US energy relevance."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get pending articles
        cursor.execute("""
            SELECT id, title, summary 
            FROM articles 
            WHERE status = 'pending'
            ORDER BY published_at DESC
            LIMIT 50
        """)
        articles = cursor.fetchall()
        
        approved = 0
        filtered_out = 0
        
        logger.info(f"Filtering {len(articles)} articles...")
        
        for article_id, title, summary in articles:
            try:
                # Build filter prompt
                prompt = self.prompts['filter_prompt'].format(
                    title=title,
                    summary=summary or "No summary available"
                )
                
                # Call LLM
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a news filter that identifies US energy and data center news."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=100
                )
                
                result = response.choices[0].message.content.strip()
                
                # Parse response
                if result.lower().startswith('yes'):
                    cursor.execute("""
                        UPDATE articles 
                        SET status = 'approved', us_energy_relevant = 1, filter_reason = ?
                        WHERE id = ?
                    """, (result, article_id))
                    approved += 1
                    logger.info(f"✓ Approved: {title[:50]}...")
                else:
                    cursor.execute("""
                        UPDATE articles 
                        SET status = 'filtered_out', us_energy_relevant = 0, filter_reason = ?
                        WHERE id = ?
                    """, (result, article_id))
                    filtered_out += 1
                    logger.info(f"✗ Filtered: {title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error filtering article {article_id}: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            'total': len(articles),
            'approved': approved,
            'filtered_out': filtered_out
        }
    
    def generate_tweets(self) -> Dict:
        """Generate tweets for approved articles."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get approved articles without tweets
        cursor.execute("""
            SELECT a.id, a.title, a.summary, a.url, a.image_url
            FROM articles a
            LEFT JOIN tweets t ON a.id = t.article_id
            WHERE a.status = 'approved' AND t.id IS NULL
            ORDER BY a.published_at DESC
        """)
        articles = cursor.fetchall()
        
        generated = 0
        
        logger.info(f"Generating tweets for {len(articles)} articles...")
        
        for article_id, title, summary, url, image_url in articles:
            try:
                # Generate tweet text
                tweet_prompt = self.prompts['tweet_prompt'].format(
                    title=title,
                    summary=summary or "No summary available",
                    url=url
                )
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional energy news writer creating concise, engaging tweets."},
                        {"role": "user", "content": tweet_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                
                tweet_text = response.choices[0].message.content.strip()
                
                # Hard enforce 280 character limit (including newlines)
                if len(tweet_text) > 280:
                    # Truncate to 277 chars and add ellipsis
                    tweet_text = tweet_text[:277] + "..."
                
                full_tweet = tweet_text
                
                # Save tweet draft (no hashtags, no images)
                cursor.execute("""
                    INSERT INTO tweets (article_id, tweet_text, hashtags, image_url, article_link, status)
                    VALUES (?, ?, ?, ?, ?, 'draft')
                """, (article_id, full_tweet, "", None, url))
                
                generated += 1
                logger.info(f"✓ Generated tweet for: {title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error generating tweet for article {article_id}: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            'total': len(articles),
            'generated': generated
        }


if __name__ == "__main__":
    # Test processor
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    processor = LLMProcessor(
        "./database/energy_news.db",
        os.getenv("OPENAI_API_KEY")
    )
    
    # Filter articles
    filter_stats = processor.filter_articles()
    print(f"\n✅ Filtering complete!")
    print(f"   Total: {filter_stats['total']}")
    print(f"   Approved: {filter_stats['approved']}")
    print(f"   Filtered out: {filter_stats['filtered_out']}")
    
    # Generate tweets
    tweet_stats = processor.generate_tweets()
    print(f"\n✅ Tweet generation complete!")
    print(f"   Total: {tweet_stats['total']}")
    print(f"   Generated: {tweet_stats['generated']}")
