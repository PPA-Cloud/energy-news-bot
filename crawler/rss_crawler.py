"""
RSS Feed Crawler for Energy News Bot
"""
import feedparser
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RSSCrawler:
    """Crawls RSS feeds and saves new articles to database."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def crawl_all_sources(self, hours_back: int = 12) -> Dict:
        """
        Crawl all enabled RSS sources.
        
        Args:
            hours_back: Only fetch articles from last N hours
            
        Returns:
            Summary dict with stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all enabled sources
        cursor.execute("""
            SELECT id, name, rss_url, priority 
            FROM sources 
            WHERE enabled = 1 
            ORDER BY priority ASC
        """)
        sources = cursor.fetchall()
        
        total_found = 0
        total_new = 0
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        logger.info(f"Starting crawl of {len(sources)} sources...")
        
        for source_id, name, rss_url, priority in sources:
            try:
                found, new = self._crawl_source(
                    cursor, 
                    source_id, 
                    name, 
                    rss_url, 
                    cutoff_time
                )
                total_found += found
                total_new += new
                
                # Log crawl
                cursor.execute("""
                    INSERT INTO crawl_log (source, articles_found, articles_new, status)
                    VALUES (?, ?, ?, 'success')
                """, (name, found, new))
                
                logger.info(f"✓ {name}: {found} articles, {new} new")
                
            except Exception as e:
                logger.error(f"✗ {name}: {e}")
                cursor.execute("""
                    INSERT INTO crawl_log (source, articles_found, articles_new, status, error)
                    VALUES (?, 0, 0, 'failed', ?)
                """, (name, str(e)))
        
        conn.commit()
        conn.close()
        
        return {
            'sources_crawled': len(sources),
            'articles_found': total_found,
            'articles_new': total_new
        }
    
    def _crawl_source(self, cursor, source_id: int, name: str, rss_url: str, cutoff_time: datetime) -> tuple:
        """Crawl a single RSS source."""
        
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:  # Feed has errors
            raise Exception(f"Feed parse error: {feed.bozo_exception}")
        
        found = 0
        new = 0
        
        for entry in feed.entries:
            found += 1
            
            # Extract article data
            url = entry.get('link', '')
            title = entry.get('title', 'No title')
            summary = entry.get('summary', entry.get('description', ''))
            
            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6])
            else:
                published_at = datetime.now()
            
            # Skip if too old
            if published_at < cutoff_time:
                continue
            
            # Image extraction disabled - images were low quality
            image_url = None
            
            # Insert article (ignore if duplicate URL)
            try:
                cursor.execute("""
                    INSERT INTO articles (url, title, summary, image_url, source, published_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """, (url, title, summary, image_url, name, published_at))
                new += 1
            except sqlite3.IntegrityError:
                # Article already exists
                pass
        
        # Update source last_crawled
        cursor.execute("""
            UPDATE sources SET last_crawled = CURRENT_TIMESTAMP WHERE id = ?
        """, (source_id,))
        
        return found, new


if __name__ == "__main__":
    # Test crawler
    import sys
    sys.path.append('..')
    
    logging.basicConfig(level=logging.INFO)
    
    crawler = RSSCrawler("./database/energy_news.db")
    stats = crawler.crawl_all_sources(hours_back=24)
    
    print(f"\n✅ Crawl complete!")
    print(f"   Sources: {stats['sources_crawled']}")
    print(f"   Articles found: {stats['articles_found']}")
    print(f"   New articles: {stats['articles_new']}")
