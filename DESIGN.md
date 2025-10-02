# Energy News Bot - Detailed Design

## System Overview

**Purpose**: Automated X bot that posts US energy news 24/7

**Frequency**: Twice daily (9am & 6pm ET)

**Sources**: 50+ energy news sites

**Output**: Auto-posted tweets with images and links

---

## Data Flow

### 1. Crawling Phase (15 minutes)

```python
# Every 12 hours
for source in NEWS_SOURCES:
    articles = crawl_rss_feed(source)  # Fast RSS crawling
    
    for article in articles:
        if article.published > last_crawl_time:
            save_article(
                url=article.url,
                title=article.title,
                summary=article.summary,
                image_url=article.image,
                source=source.name,
                published_at=article.published
            )
```

### 2. Filtering Phase (5 minutes)

```python
# Filter for US energy news
for article in new_articles:
    is_us_energy = llm_filter(
        article,
        prompt="""
        Is this article about:
        1. US energy (domestic production, policy, markets)
        2. Energy imports/exports to/from US
        3. US companies in energy sector
        
        Answer: Yes or No
        """
    )
    
    if is_us_energy:
        article.status = 'approved'
    else:
        article.status = 'filtered_out'
```

### 3. Tweet Generation Phase (10 minutes)

```python
# Generate tweets for approved articles
for article in approved_articles:
    tweet_data = llm_generate(
        article,
        prompt="""
        Create an engaging tweet (max 240 chars) about this energy news.
        
        Format:
        - Start with emoji
        - Key fact or headline
        - 1-2 sentence summary
        - End with relevant hashtags
        
        Leave room for link and "via @PPACloud"
        """
    )
    
    # Find best image
    image_url = article.image_url or extract_og_image(article.url)
    
    save_tweet_draft(
        text=tweet_data.text,
        article_id=article.id,
        image_url=image_url,
        link=article.url
    )
```

### 4. Posting Phase (5 minutes)

```python
# Post to X
for tweet_draft in pending_tweets:
    # Download image
    image = download_image(tweet_draft.image_url)
    
    # Post to X
    tweet_id = x_api.post_tweet(
        text=f"{tweet_draft.text}\n\nvia @PPACloud",
        media=[image],
        link=tweet_draft.link
    )
    
    # Track
    mark_as_posted(tweet_draft, tweet_id)
```

---

## News Sources (50+)

### Tier 1: Major News (RSS feeds)
- Bloomberg Energy
- Reuters Energy
- Wall Street Journal Energy
- Financial Times Energy
- Associated Press Energy

### Tier 2: Energy Publications (RSS feeds)
- Utility Dive
- Energy Storage News
- PV Magazine
- Wind Power Monthly
- Greentech Media
- CleanTechnica
- Canary Media
- E&E News
- Power Magazine

### Tier 3: Regional News (RSS feeds)
- California Energy Markets
- Texas Energy Report
- Midwest Energy News
- Southeast Energy News

### Tier 4: Trade Publications (RSS feeds)
- Solar Industry Magazine
- North American Windpower
- Renewable Energy World
- Energy Central

### Tier 5: Government/Policy (RSS feeds)
- DOE News
- FERC News
- EIA Today in Energy
- EPA Energy News

---

## Database Schema

### Table: `articles`

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    image_url TEXT,
    source TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',  -- pending|approved|filtered_out|posted
    us_energy_relevant BOOLEAN,
    filter_reason TEXT
);
```

### Table: `tweets`

```sql
CREATE TABLE tweets (
    id INTEGER PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    tweet_text TEXT NOT NULL,
    tweet_id TEXT,  -- X tweet ID
    image_url TEXT,
    posted_at TIMESTAMP,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    status TEXT DEFAULT 'draft'  -- draft|posted|failed
);
```

### Table: `crawl_log`

```sql
CREATE TABLE crawl_log (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    articles_found INTEGER,
    articles_new INTEGER,
    status TEXT,
    error TEXT
);
```

---

## Configuration Files

### `config/sources.yaml`

```yaml
sources:
  - name: "Bloomberg Energy"
    rss_url: "https://www.bloomberg.com/feeds/energy.rss"
    priority: 1
    enabled: true
    
  - name: "Reuters Energy"
    rss_url: "https://www.reuters.com/business/energy/rss"
    priority: 1
    enabled: true
    
  - name: "Utility Dive"
    rss_url: "https://www.utilitydive.com/feeds/news/"
    priority: 1
    enabled: true
    
  # ... 47 more sources
```

### `config/prompts.yaml`

```yaml
filter_prompt: |
  Is this article about US energy news?
  
  Criteria:
  - US domestic energy (production, policy, markets)
  - Energy imports/exports involving US
  - US companies in energy sector
  - US energy infrastructure
  
  Article: {title}
  Summary: {summary}
  
  Answer: Yes or No
  Reason: (brief explanation)

tweet_prompt: |
  Create an engaging tweet (max 240 chars) about this energy news.
  
  Article: {title}
  Summary: {summary}
  
  Format:
  - Start with relevant emoji (⚡🌞🌬️💡🔋)
  - Key headline or fact
  - 1-2 sentence summary
  - End with 2-3 hashtags
  
  Keep it punchy and newsworthy!
  Leave room for link and "via @PPACloud"
```

### `config/settings.yaml`

```yaml
schedule:
  crawl_times:
    - "09:00"  # 9am ET
    - "18:00"  # 6pm ET
  timezone: "America/New_York"

posting:
  auto_post: true
  require_image: false  # Post even if no image
  max_tweets_per_run: 20
  delay_between_posts: 60  # seconds

llm:
  model: "gpt-4o-mini"
  temperature: 0.7
  max_tokens: 300

x_api:
  consumer_key: "${X_CONSUMER_KEY}"
  consumer_secret: "${X_CONSUMER_SECRET}"
  access_token: "${X_ACCESS_TOKEN}"
  access_token_secret: "${X_ACCESS_TOKEN_SECRET}"
```

---

## Tweet Templates

### Standard Energy News
```
⚡ {headline}

{summary_1_sentence}

#{hashtag1} #{hashtag2} #{hashtag3}

via @PPACloud
```

### Breaking News
```
🚨 BREAKING: {headline}

{key_fact}

More → {link}

#{hashtag1} #{hashtag2}

via @PPACloud
```

### Policy/Regulatory
```
📋 {policy_headline}

{impact_summary}

#{hashtag1} #{hashtag2}

via @PPACloud
```

### Market/Financial
```
💰 {market_headline}

{financial_detail}

#{hashtag1} #{hashtag2}

via @PPACloud
```

---

## Scheduling

### Cron Jobs

```bash
# 9am ET crawl & post
0 9 * * * cd /app/energy-news-bot && python run.py

# 6pm ET crawl & post
0 18 * * * cd /app/energy-news-bot && python run.py
```

### Manual Triggers

```bash
# Run crawler only
python run_crawler.py

# Run filter only
python run_filter.py

# Run tweet generation only
python run_generate.py

# Run posting only
python run_post.py

# Full pipeline
python run.py
```

---

## Monitoring & Analytics

### Dashboard Metrics

- **Articles crawled** (last 24h, 7d, 30d)
- **Articles posted** (last 24h, 7d, 30d)
- **Filter rate** (% of articles posted)
- **Engagement** (likes, retweets, impressions)
- **Top sources** (most posted from)
- **Top hashtags** (most used)
- **Posting frequency** (tweets per day)

### Logs

```python
# Crawl log
2025-10-02 09:00:15 - Crawled Bloomberg Energy: 12 articles, 3 new
2025-10-02 09:00:45 - Crawled Reuters Energy: 8 articles, 2 new
2025-10-02 09:01:30 - Total: 50 sources, 127 articles, 23 new

# Filter log
2025-10-02 09:05:12 - Filtered 23 articles: 15 approved, 8 rejected
2025-10-02 09:05:13 - Rejection reasons: 5 non-US, 3 not energy

# Post log
2025-10-02 09:10:05 - Posted tweet 1/15: "⚡ DOE announces..."
2025-10-02 09:11:10 - Posted tweet 2/15: "🌞 California solar..."
2025-10-02 09:12:15 - Posted tweet 3/15: "🌬️ Offshore wind..."
```

---

## Error Handling

### Crawl Failures
- Retry 3 times with exponential backoff
- Log error and continue to next source
- Alert if >50% of sources fail

### Filter Failures
- Skip article and log error
- Continue with other articles
- Alert if LLM API down

### Posting Failures
- Retry 3 times
- Mark as 'failed' in database
- Alert if >5 consecutive failures
- Can manually retry later

---

## Deployment

### Option 1: DigitalOcean (Same server as PPA Cloud)
- Separate folder
- Separate database
- Separate cron jobs
- Minimal resources needed

### Option 2: Standalone Server
- Cheap VPS ($5/month)
- Only needs Python + SQLite
- Completely isolated

### Option 3: Serverless (AWS Lambda)
- Runs on schedule
- Pay per execution
- No server management

**Recommendation: Option 1 (same server, separate system)**

---

## Cost Estimate

### LLM API (OpenAI)
- 50 articles/day × 2 runs = 100 articles/day
- Filter: 100 × $0.0001 = $0.01/day
- Generate: 50 × $0.0005 = $0.025/day
- **Total: ~$1/month**

### X API
- Free tier: 1,500 tweets/month
- We'll post: ~50 tweets/day = 1,500/month
- **Total: $0/month** (fits in free tier)

### Server
- Already running PPA Cloud
- Minimal extra resources
- **Total: $0/month** (shared)

**Grand Total: ~$1/month** 🎉

---

## Next Steps

1. Create folder structure
2. Build RSS crawler
3. Build LLM filter
4. Build tweet generator
5. Integrate X API
6. Set up cron jobs
7. Test & deploy

**Ready to start building?**
