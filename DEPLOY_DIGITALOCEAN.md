# Deploy to DigitalOcean

## Option 1: DigitalOcean App Platform (Recommended - Easiest)

### Step 1: Push to GitHub
```bash
cd /Users/leulayemaskal/dev/ppa-cloud-new/energy-news-bot
git init
git add .
git commit -m "Initial commit - Energy News Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/energy-news-bot.git
git push -u origin main
```

### Step 2: Create App on DigitalOcean
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect your GitHub repo
4. Select "Worker" (not Web Service)
5. Set Run Command: `./run_hourly.sh`
6. Set Schedule: `*/10 * * * *` (every 10 minutes)

### Step 3: Add Environment Variables
In App Settings → Environment Variables, add:
- `OPENAI_API_KEY`
- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`
- `DATABASE_PATH=./database/energy_news.db`
- `LOG_LEVEL=INFO`

### Step 4: Deploy
Click "Deploy" - done! 🎉

**Cost: $5/month**

---

## Option 2: DigitalOcean Droplet (More Control)

### Step 1: Create Droplet
1. Go to https://cloud.digitalocean.com/droplets
2. Create Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic - $6/month (1GB RAM)
   - **Region**: Closest to you
   - Add SSH key

### Step 2: SSH into Droplet
```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11+
apt install -y python3.11 python3.11-venv python3-pip git sqlite3

# Install system dependencies
apt install -y build-essential libssl-dev libffi-dev python3-dev
```

### Step 4: Clone & Setup Bot
```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/energy-news-bot.git
cd energy-news-bot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Paste your environment variables, save (Ctrl+X, Y, Enter)

# Create logs directory
mkdir -p logs

# Test it works
./run_hourly.sh
```

### Step 5: Setup Cron
```bash
# Edit crontab
crontab -e

# Add this line (runs every 10 minutes)
*/10 * * * * /root/energy-news-bot/run_hourly.sh >> /root/energy-news-bot/logs/cron.log 2>&1
```

### Step 6: Monitor
```bash
# View logs
tail -f /root/energy-news-bot/logs/crawl_runs.log

# Check cron is running
crontab -l
```

**Cost: $6/month**

---

## Option 3: AWS Lambda (Serverless)

**Most cost-effective for intermittent tasks:**

- Only pay when running
- ~$0.20/month for this workload
- Requires more setup (Lambda + EventBridge + RDS for SQLite)

---

## Recommendation:

**Start with DigitalOcean App Platform ($5/month)**
- Easiest to set up
- Managed service (no server maintenance)
- Auto-scaling if needed
- Built-in monitoring

**Upgrade to Droplet later if you need:**
- More control
- Custom configurations
- Multiple bots on same server
