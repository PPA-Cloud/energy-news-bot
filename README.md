# Energy News Bot

**Automated X (Twitter) bot for US energy news**

## What It Does

1. **Crawls** 50+ energy news sites twice daily (9am & 6pm ET)
2. **Filters** for US-related energy news
3. **Generates** engaging tweets with LLM
4. **Posts** automatically to X with images and links
5. **Tracks** all posted content

## Architecture

```
energy-news-bot/
├── crawler/          # News crawling
├── processor/        # LLM filtering & tweet generation
├── poster/           # X API integration
├── database/         # SQLite for articles & tweets
├── config/           # Settings & prompts
└── scheduler/        # Cron jobs
```

## Separate from PPA Cloud

- **Different database** (SQLite: `energy_news.db`)
- **Different dependencies** (minimal)
- **Different deployment** (can run anywhere)
- **No interference** with PPA Cloud data platform

## Quick Start

```bash
cd energy-news-bot
pip install -r requirements.txt
python setup_db.py
python run_crawler.py
```

## Features

✅ Crawls 50+ news sources
✅ Filters for US energy news
✅ Auto-generates tweets
✅ Finds and attaches images
✅ Posts to X automatically
✅ Tracks engagement
✅ Customizable prompts
✅ Runs twice daily

## Configuration

Edit `config/settings.yaml`:
- News sources
- Crawl schedule
- Tweet templates
- X API credentials
- LLM prompts
