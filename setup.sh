#!/bin/bash

# Energy News Bot - Setup Script

echo "🚀 Setting up Energy News Bot..."
echo ""

# Check Python version
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup database
echo "🗄️  Setting up database..."
python3 database/setup.py

# Check .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your API keys!"
else
    echo "✓ .env file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: python3 run.py --hours 24 --max-tweets 5"
echo ""
