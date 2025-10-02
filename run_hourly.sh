#!/bin/bash
# Energy news crawler and poster (runs every 10-15 minutes)

cd "$(dirname "$0")"
source venv/bin/activate

# Run the pipeline with 30 minute lookback, post up to 3 tweets
# Using 30 min lookback to catch any articles we might have missed
python3 run.py --hours 0.5 --max-tweets 3

# Log the run
echo "$(date): Crawl completed" >> logs/crawl_runs.log
