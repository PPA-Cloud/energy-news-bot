# Energy News Bot Scheduler Setup

## Option 1: macOS Launchd (Recommended for Mac)

**Run every 10 minutes for near real-time news:**

```bash
# Create the plist
cat > ~/Library/LaunchAgents/com.ppacloud.energynews.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ppacloud.energynews</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/leulayemaskal/dev/ppa-cloud-new/energy-news-bot/run_hourly.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>600</integer>
    <key>StandardOutPath</key>
    <string>/Users/leulayemaskal/dev/ppa-cloud-new/energy-news-bot/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/leulayemaskal/dev/ppa-cloud-new/energy-news-bot/logs/launchd_error.log</string>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.ppacloud.energynews.plist

# Check status
launchctl list | grep energynews
```

**Note:** `StartInterval` of 600 = runs every 10 minutes (600 seconds)

## Option 2: Cron (Alternative)

```bash
# Edit crontab
crontab -e

# Add this line (runs every 10 minutes)
*/10 * * * * /Users/leulayemaskal/dev/ppa-cloud-new/energy-news-bot/run_hourly.sh

# Or every 15 minutes:
*/15 * * * * /Users/leulayemaskal/dev/ppa-cloud-new/energy-news-bot/run_hourly.sh
```

## Option 3: Cloud Deployment (Production)

For production, deploy to a cloud service:
- **AWS Lambda** with EventBridge (hourly trigger)
- **Google Cloud Run** with Cloud Scheduler
- **Heroku** with Heroku Scheduler
- **DigitalOcean App Platform** with cron

## Manual Testing

Test the hourly script manually:

```bash
cd /Users/leulayemaskal/dev/ppa-cloud-new/energy-news-bot
./run_hourly.sh
```

## Monitoring

Check logs:
```bash
tail -f logs/hourly_runs.log
tail -f logs/launchd.log
```
