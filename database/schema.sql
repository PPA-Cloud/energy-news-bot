-- Energy News Bot Database Schema

-- Articles discovered from news sources
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    image_url TEXT,
    source TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',  -- pending|approved|filtered_out|posted|failed
    us_energy_relevant BOOLEAN,
    filter_reason TEXT
);

-- Generated tweets ready to post
CREATE TABLE IF NOT EXISTS tweets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id),
    tweet_text TEXT NOT NULL,
    hashtags TEXT,
    image_url TEXT,
    article_link TEXT,
    tweet_id TEXT,  -- X tweet ID after posting
    posted_at TIMESTAMP,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    status TEXT DEFAULT 'draft',  -- draft|posted|failed
    error TEXT,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- Crawl execution log
CREATE TABLE IF NOT EXISTS crawl_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    articles_found INTEGER DEFAULT 0,
    articles_new INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success',  -- success|failed
    error TEXT
);

-- News sources configuration
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    rss_url TEXT NOT NULL,
    website_url TEXT,
    priority INTEGER DEFAULT 2,  -- 1=high, 2=medium, 3=low
    enabled BOOLEAN DEFAULT 1,
    last_crawled TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_tweets_status ON tweets(status);
CREATE INDEX IF NOT EXISTS idx_tweets_posted ON tweets(posted_at);
