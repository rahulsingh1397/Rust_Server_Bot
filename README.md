# Rust Server Discord Bot

Automatically send messages about your Rust server to Discord channels including wipe announcements, player count alerts, and restart notifications.

## 🚀 Features

- **Wipe Announcements**: Automatic Thursday wipe alerts (1 hour before and when it happens)
- **Player Count Monitoring**: Real-time server population alerts when >100 players
- **Restart Alerts**: 5-minute warnings before server restarts
- **Spam Prevention**: Built-in cooldowns to prevent message flooding
- **BattleMetrics Integration**: Real server data from BattleMetrics API

## 📋 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Server Name
Edit `rust_discord_bot.py` and change:
```python
SERVER_NAME = "YOUR_SERVER_NAME"  # Replace with your actual server name
```

### 3. Test Webhook
```bash
python test_webhook.py
```
You should see a test message in your Discord channel.

### 4. Run the Bot
```bash
python rust_discord_bot.py
```

## ⚙️ Configuration

### Webhook Setup
Your webhook URL is already configured in `webhook.py`. This file is automatically added to `.gitignore` for security.

### Automation Setup

#### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger → Daily
4. Action → Start Program
5. Program: `python`
6. Argument: `path\to\rust_discord_bot.py`

#### Linux/Mac (cron)
```bash
crontab -e
```
Add:
```bash
*/5 * * * * python3 /path/to/rust_discord_bot.py
```

## 📁 File Structure

```
RustServer/
├── rust_discord_bot.py    # Main bot script
├── webhook.py             # Discord webhook URL (private, gitignored)
├── test_webhook.py        # Webhook testing script
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🔧 Customization

### Wipe Schedule
Default: Thursday at 3 PM (15:00)
Edit `check_wipe_schedule()` in `rust_discord_bot.py` to change:
- Day: `now.weekday()` (0=Monday, 6=Sunday)
- Time: `now.hour` values

### Alert Thresholds
- High population: Change `if players > 100` to your preferred threshold
- Cooldown periods: Edit `COOLDOWNS` dictionary

### Manual Restart Alert
Uncomment this line in the main loop:
```python
send_restart_alert()
```

## 🛡️ Security

- `webhook.py` contains your webhook URL and is `.gitignore`d
- Never share your webhook URL publicly
- Keep your bot script private

## 🐛 Troubleshooting

### Webhook Not Working
1. Check Discord channel permissions
2. Verify webhook URL is correct
3. Run `test_webhook.py` to debug

### Server Data Not Loading
1. Verify your `SERVER_NAME` matches BattleMetrics exactly
2. Check if your server is listed on BattleMetrics

### Bot Not Sending Messages
1. Check cooldown periods
2. Verify current time matches schedule conditions
3. Check console output for errors

## 📊 Message Examples

```
🔥 WEEKLY WIPE JUST HAPPENED! 🔥
Fresh start! Join now!

⚠️ WIPE IN 1 HOUR! 🔥
Get ready for the weekly wipe!

👥 Server is POPPING!
120/150 players online!

⚠️ Server restarting in 5 minutes!
Please log out to avoid losing progress.

📊 Server Status
45/150 players online
```

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify your configuration
3. Test with `test_webhook.py` first
