#!/usr/bin/env python3
"""
Rust Server Discord Bot - Web Service Version for Render
Runs as a web service but functions as a background bot
"""

import requests
import datetime
import time
import json
import os
from flask import Flask
from threading import Thread
import signal
import sys

# Flask app for Render web service requirement
app = Flask(__name__)

# Configuration from environment variables
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SERVER_NAME = os.getenv("SERVER_NAME", "IND-US Valley [Vanilla+ | Weekly | Merged Outpost | Max : 5]")
BATTLEMETRICS_URL = f"https://api.battlemetrics.com/servers?filter[search]={SERVER_NAME}"

# Validate required environment variables
if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL environment variable is required")

# Cooldown tracking to prevent spam
last_sent = {
    "high_pop": None,
    "wipe_hype": None,
    "restart_alert": None,
    "daily_status": None
}

# Cooldown periods in minutes
COOLDOWNS = {
    "high_pop": 60,      # 1 hour
    "wipe_hype": 60,     # 1 hour  
    "restart_alert": 15, # 15 minutes
    "daily_status": 60   # 1 hour
}

# Global flag for bot shutdown
shutdown_flag = False

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

def check_cooldown(alert_type):
    """Check if we can send an alert (cooldown expired)"""
    if last_sent[alert_type] is None:
        return True
    
    now = datetime.datetime.now()
    time_diff = (now - last_sent[alert_type]).total_seconds() / 60
    return time_diff >= COOLDOWNS[alert_type]

def update_cooldown(alert_type):
    """Update the last sent time for an alert type"""
    last_sent[alert_type] = datetime.datetime.now()

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

def check_wipe_schedule():
    """Check if it's time for wipe announcements"""
    now = datetime.datetime.now()
    
    # Thursday wipe (weekday 3 = Thursday)
    if now.weekday() == 3:
        # Wipe hype 1 hour before (2 PM if wipe at 3 PM)
        if now.hour == 14 and check_cooldown("wipe_hype"):
            send_message("⚠️ **WIPE IN 1 HOUR!** 🔥\nGet ready for the weekly wipe!")
            update_cooldown("wipe_hype")
        
        # Wipe announcement at 3 PM
        if now.hour == 15 and now.minute < 5 and check_cooldown("wipe_hype"):
            send_message("🔥 **WEEKLY WIPE JUST HAPPENED!** 🔥\nFresh start! Join now!")
            update_cooldown("wipe_hype")

def check_server_status():
    """Check server status and send enhanced stats"""
    server_data = get_server_data()
    if not server_data:
        return
    
    attributes = server_data.get('attributes', {})
    players = attributes.get('players', 0)
    max_players = attributes.get('maxPlayers', 0)
    
    # High population alert (adjusted for 50-player server)
    if players > 30 and check_cooldown("high_pop"):
        send_message(f"👥 **Server is POPPING!**\n{players}/{max_players} players online!")
        update_cooldown("high_pop")
    
    # Enhanced status update (every 1 hour)
    if check_cooldown("daily_status"):
        # Get wipe information
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
            
            # Add urgency indicator
            if days_until <= 1:
                message += f"⚠️ **Wipe coming soon!**"
            elif days_until <= 3:
                message += f"📢 **Wipe this week!**"
            else:
                message += f"🕐 **Plenty of time to build!**"
        
        send_message(message)
        update_cooldown("daily_status")

def send_restart_alert():
    """Send server restart alert"""
    if check_cooldown("restart_alert"):
        send_message("⚠️ **Server restarting in 5 minutes!**\nPlease log out to avoid losing progress.")
        update_cooldown("restart_alert")

def bot_worker():
    """Main bot loop running in background thread"""
    global shutdown_flag
    print("🤖 Rust Discord Bot worker started...")
    send_message("✅ Rust Discord Bot is online!")
    
    while not shutdown_flag:
        try:
            now = datetime.datetime.now()
            
            # Check wipe schedule (Thursdays)
            check_wipe_schedule()
            
            # Check server status
            check_server_status()
            
            # Sleep for 5 minutes (300 seconds)
            time.sleep(300)
            
        except Exception as e:
            print(f"❌ Error in bot loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying
    
    print("🛑 Bot worker shutting down...")

# Flask routes for Render health checks
@app.route('/')
def home():
    return {"status": "Rust Discord Bot is running!", "service": "active"}

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "running"}

@app.route('/status')
def status():
    server_data = get_server_data()
    if server_data:
        attributes = server_data.get('attributes', {})
        return {
            "server": SERVER_NAME,
            "players": f"{attributes.get('players', 0)}/{attributes.get('maxPlayers', 0)}",
            "status": "online"
        }
    return {"status": "api_error"}

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    global shutdown_flag
    print("\n🛑 Shutdown signal received...")
    shutdown_flag = True
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start bot worker in background thread
    bot_thread = Thread(target=bot_worker, daemon=True)
    bot_thread.start()
    
    # Run Flask app (required for Render Web Service)
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting web service on port {port}...")
    app.run(host='0.0.0.0', port=port, threaded=True)
