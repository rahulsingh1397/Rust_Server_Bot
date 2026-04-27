#!/usr/bin/env python3
"""
Simplified Rust Discord Bot - Works with Render Web Service
No threading - runs bot logic on web requests
"""

import requests
import datetime
import time
import json
import os
from flask import Flask
from threading import Lock

app = Flask(__name__)

# Configuration
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SERVER_NAME = os.getenv("SERVER_NAME", "IND-US Valley [Vanilla+ | Weekly | Merged Outpost | Max : 5]")
BATTLEMETRICS_URL = f"https://api.battlemetrics.com/servers?filter[search]={SERVER_NAME}"

# Cooldown tracking (using file for persistence)
COOLDOWN_FILE = "cooldowns.json"

# Thread safety
lock = Lock()

def load_cooldowns():
    """Load cooldowns from file"""
    try:
        with open(COOLDOWN_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "high_pop": None,
            "wipe_hype": None,
            "restart_alert": None,
            "daily_status": None
        }

def save_cooldowns(cooldowns):
    """Save cooldowns to file"""
    try:
        with open(COOLDOWN_FILE, 'w') as f:
            json.dump(cooldowns, f)
    except:
        pass

def send_message(message):
    """Send a message to Discord webhook"""
    try:
        data = {"content": message}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 204:
            print(f"✅ Message sent: {message}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def get_server_data():
    """Get server data from BattleMetrics API"""
    try:
        response = requests.get(BATTLEMETRICS_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                return data['data'][0]
        return None
    except Exception as e:
        print(f"❌ Error fetching server data: {e}")
        return None

def check_cooldown(alert_type, cooldown_minutes=60):
    """Check if cooldown has expired"""
    with lock:
        cooldowns = load_cooldowns()
        last_sent = cooldowns.get(alert_type)
        
        if last_sent is None:
            return True
        
        last_sent_time = datetime.datetime.fromisoformat(last_sent)
        now = datetime.datetime.now()
        time_diff = (now - last_sent_time).total_seconds() / 60
        
        return time_diff >= cooldown_minutes

def update_cooldown(alert_type):
    """Update cooldown timestamp"""
    with lock:
        cooldowns = load_cooldowns()
        cooldowns[alert_type] = datetime.datetime.now().isoformat()
        save_cooldowns(cooldowns)

def get_wipe_info(server_data):
    """Get wipe information from server data"""
    attributes = server_data.get('attributes', {})
    details = attributes.get('details', {})
    
    last_wipe_str = details.get('rust_last_wipe', None)
    
    if not last_wipe_str:
        return None, None, None
    
    try:
        last_wipe = datetime.datetime.fromisoformat(last_wipe_str.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        
        next_wipe = last_wipe + datetime.timedelta(days=7)
        time_until_wipe = next_wipe - now
        
        days_until = time_until_wipe.days
        hours_until = time_until_wipe.seconds // 3600
        
        return last_wipe, next_wipe, (days_until, hours_until)
    except Exception as e:
        print(f"Error parsing wipe date: {e}")
        return None, None, None

def run_bot_checks():
    """Run all bot checks and send messages"""
    print("🤖 Running bot checks...")
    
    server_data = get_server_data()
    if not server_data:
        return "❌ Failed to get server data"
    
    attributes = server_data.get('attributes', {})
    players = attributes.get('players', 0)
    max_players = attributes.get('maxPlayers', 0)
    
    messages_sent = []
    
    # High population alert
    if players > 30 and check_cooldown("high_pop"):
        msg = f"👥 **Server is POPPING!**\n{players}/{max_players} players online!"
        if send_message(msg):
            update_cooldown("high_pop")
            messages_sent.append("High pop alert")
    
    # Daily status update (every hour)
    if check_cooldown("daily_status", 60):
        last_wipe, next_wipe, time_until = get_wipe_info(server_data)
        
        message = f"🌐 **Server Status**\n\n"
        message += f"👥 **Players**: {players}/{max_players} online\n"
        message += f"🟢 **Status**: Online ✅\n"
        
        if last_wipe:
            message += f"🗓️ **Last Wipe**: {last_wipe.strftime('%B %d, %Y')}\n"
        
        if next_wipe and time_until:
            days_until, hours_until = time_until
            message += f"⏰ **Next Wipe**: {next_wipe.strftime('%B %d, %Y')}\n"
            message += f"📅 **Days Until Wipe**: {days_until} days, {hours_until} hours\n"
            
            if days_until <= 1:
                message += f"⚠️ **Wipe coming soon!**"
            elif days_until <= 3:
                message += f"📢 **Wipe this week!**"
            else:
                message += f"🕐 **Plenty of time to build!**"
        
        if send_message(message):
            update_cooldown("daily_status")
            messages_sent.append("Daily status")
    
    return f"✅ Checks completed. Messages sent: {', '.join(messages_sent) if messages_sent else 'None'}"

# Flask routes
@app.route('/')
def home():
    return {"status": "Rust Discord Bot Web Service", "service": "active"}

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "ready"}

@app.route('/status')
def status():
    server_data = get_server_data()
    if server_data:
        attributes = server_data.get('attributes', {})
        return {
            "server": SERVER_NAME,
            "players": f"{attributes.get('players', 0)}/{attributes.get('maxPlayers', 0)}",
            "status": "online",
            "last_check": datetime.datetime.now().isoformat()
        }
    return {"status": "api_error"}

@app.route('/run-bot')
def run_bot():
    """Run bot checks manually"""
    result = run_bot_checks()
    return {"result": result, "timestamp": datetime.datetime.now().isoformat()}

@app.route('/test')
def test():
    """Test endpoint"""
    return {"test": "working", "time": datetime.datetime.now().isoformat()}

if __name__ == "__main__":
    # Send startup message
    send_message("✅ Rust Discord Bot Web Service is online!")
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting web service on port {port}...")
    app.run(host='0.0.0.0', port=port)
