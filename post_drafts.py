#!/usr/bin/env python3
"""
Post existing draft tweets directly
"""
import os
import sqlite3
from dotenv import load_dotenv

# Python 3.13 compatibility
import imghdr_compat

import tweepy

load_dotenv()

db_path = "database/energy_news.db"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get draft tweets
cursor.execute("""
    SELECT id, tweet_text
    FROM tweets
    WHERE status = 'draft'
    ORDER BY id ASC
    LIMIT 3
""")
draft_tweets = cursor.fetchall()

print(f"Found {len(draft_tweets)} draft tweets to post\n")

# Initialize X client with OAuth 1.0a (same as test_post.py which worked)
client = tweepy.Client(
    consumer_key=os.getenv('X_API_KEY'),
    consumer_secret=os.getenv('X_API_SECRET'),
    access_token=os.getenv('X_ACCESS_TOKEN'),
    access_token_secret=os.getenv('X_ACCESS_TOKEN_SECRET')
)

posted = 0
for tweet_id, tweet_text in draft_tweets:
    try:
        print(f"Posting tweet {tweet_id}...")
        print(f"Text: {tweet_text[:80]}...")
        
        response = client.create_tweet(text=tweet_text)
        x_tweet_id = response.data['id']
        
        # Update database
        cursor.execute("""
            UPDATE tweets
            SET status = 'posted', tweet_id = ?, posted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (x_tweet_id, tweet_id))
        
        posted += 1
        print(f"✅ Posted! Tweet ID: {x_tweet_id}\n")
        
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        cursor.execute("""
            UPDATE tweets
            SET status = 'failed', error = ?
            WHERE id = ?
        """, (str(e), tweet_id))

conn.commit()
conn.close()

print(f"\n{'='*60}")
print(f"Posted {posted} out of {len(draft_tweets)} tweets")
print(f"{'='*60}")
