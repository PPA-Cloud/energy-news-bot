#!/bin/bash

# Energy News Bot - Test Script
# Tests each component individually

echo "🧪 Testing Energy News Bot Components..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Test 1: Database setup
echo "1️⃣  Testing database setup..."
python3 database/setup.py
echo ""

# Test 2: RSS Crawler
echo "2️⃣  Testing RSS crawler..."
python3 crawler/rss_crawler.py
echo ""

# Test 3: LLM Processor
echo "3️⃣  Testing LLM processor..."
python3 processor/llm_processor.py
echo ""

# Test 4: X Poster (dry run - don't actually post)
echo "4️⃣  Testing X poster (checking connection only)..."
echo "   (Skipping actual posting in test mode)"
echo ""

# Test 5: Full pipeline (limited)
echo "5️⃣  Testing full pipeline (1 tweet max)..."
python3 run.py --hours 24 --max-tweets 1
echo ""

echo "✅ All tests complete!"
echo ""
echo "Check energy_news_bot.log for details"
