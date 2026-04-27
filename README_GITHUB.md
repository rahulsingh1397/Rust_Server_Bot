# Rust Server Discord Bot

Automatically send messages about your Rust server to Discord channels including wipe announcements, player count alerts, and restart notifications.

## 🚀 Features

- **Wipe Announcements**: Automatic Thursday wipe alerts (1 hour before and when it happens)
- **Player Count Monitoring**: Real-time server population alerts when >40 players
- **Restart Alerts**: 5-minute warnings before server restarts
- **Spam Prevention**: Built-in cooldowns to prevent message flooding
- **BattleMetrics Integration**: Real server data from BattleMetrics API

## 🌐 Cloud Deployment (Railway)

This version is optimized for cloud hosting on Railway using environment variables.

### Quick Deploy to Railway

1. **Click the button below** to deploy instantly:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/rust-discord-bot)

2. **Set Environment Variables** in Railway dashboard:
   ```
   DISCORD_WEBHOOK_URL = https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
   SERVER_NAME = IND-US Valley [Vanilla+ | Weekly | Merged Outpost | Max : 5]
   ```

### Manual Setup

1. **Fork this repository**
2. **Connect to Railway**
3. **Set environment variables**
4. **Deploy**

## 🔧 Environment Variables

Required:
- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
- `SERVER_NAME`: Your BattleMetrics server name (optional, defaults to configured server)

## 📁 Files for Cloud Hosting

- `app.py` - Main bot script (cloud version)
- `requirements.txt` - Python dependencies
- `Procfile` - Railway process definition
- `railway.json` - Railway configuration
- `runtime.txt` - Python version specification

## 🚀 Local Development

For local testing, use the local version:
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables or create `.env` file
3. Run: `python app.py`

## 📊 Message Examples

```
🔥 WEEKLY WIPE JUST HAPPENED! 🔥
Fresh start! Join now!

⚠️ WIPE IN 1 HOUR! 🔥
Get ready for the weekly wipe!

👥 Server is POPPING!
45/50 players online!

⚠️ Server restarting in 5 minutes!
Please log out to avoid losing progress.

📊 Server Status
5/50 players online
```

## 🔒 Security

- Webhook URL stored in environment variables (not in code)
- No sensitive information in repository
- Safe for public GitHub repositories

## 🛠️ Customization

### Wipe Schedule
Default: Thursday at 3 PM (15:00)
Edit `check_wipe_schedule()` in `app.py` to change day/time.

### Alert Thresholds
- High population: Change `if players > 40` to your preferred threshold
- Cooldown periods: Edit `COOLDOWNS` dictionary

## 📝 License

MIT License - feel free to fork and modify!
