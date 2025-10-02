#!/bin/bash
# Continuous runner - runs every N minutes in a loop

cd "$(dirname "$0")"
source venv/bin/activate

# Run interval in seconds (60 = 1 minute, 600 = 10 minutes)
INTERVAL=60

echo "Starting continuous runner with ${INTERVAL}s interval..."

while true; do
    echo "$(date): Starting crawl..."
    python3 run.py --hours 0.5 --max-tweets 3
    echo "$(date): Crawl completed. Sleeping ${INTERVAL}s..." >> logs/crawl_runs.log
    sleep $INTERVAL
done
