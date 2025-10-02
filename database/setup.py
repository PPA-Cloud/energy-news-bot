"""
Database setup for Energy News Bot
"""
import sqlite3
import yaml
from pathlib import Path

def setup_database(db_path: str = "./database/energy_news.db"):
    """Create database and tables."""
    
    # Create database directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    # Load and insert news sources
    sources_path = Path(__file__).parent.parent / "config" / "sources.yaml"
    with open(sources_path, 'r') as f:
        sources_config = yaml.safe_load(f)
    
    # Insert sources from all priority levels
    for priority_level, sources in sources_config.items():
        priority = int(priority_level.split('_')[1])  # Extract number from 'priority_1'
        
        for source in sources:
            cursor.execute("""
                INSERT OR IGNORE INTO sources (name, rss_url, website_url, priority, enabled)
                VALUES (?, ?, ?, ?, 1)
            """, (source['name'], source['rss_url'], source.get('website', ''), priority))
    
    conn.commit()
    
    # Print summary
    cursor.execute("SELECT COUNT(*) FROM sources")
    source_count = cursor.fetchone()[0]
    
    print(f"✅ Database setup complete!")
    print(f"   Database: {db_path}")
    print(f"   Sources loaded: {source_count}")
    
    conn.close()

if __name__ == "__main__":
    setup_database()
