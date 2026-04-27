#!/usr/bin/env python3
"""
Rust Server Discord Bot - Cloud Version
Uses environment variables for secure webhook configuration
"""

import requests
import datetime
import time
import json
import os

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
    "daily_status": 240  # 4 hours
}

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
                return data['data'][0]['attributes']
        return None
    except Exception as e:
        print(f"❌ Error fetching server data: {e}")
        return None

def check_cooldown(alert_type):
    """Check if we can send an alert (cooldown expired)"""
    if last_sent[alert_type] is None:
        return True
    
    now = datetime.datetime.now()
    time_diff = (now - last_sent[alert_type]).total_seconds() / 60  # Convert to minutes
    
    return time_diff >= COOLDOWNS[alert_type]

def update_cooldown(alert_type):
    """Update the last sent time for an alert type"""
    last_sent[alert_type] = datetime.datetime.now()

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
    """Check server player count and send alerts"""
    server_data = get_server_data()
    if not server_data:
        return
    
    players = server_data.get('players', 0)
    max_players = server_data.get('maxPlayers', 0)
    
    # High population alert (adjusted for 50-player server)
    if players > 40 and check_cooldown("high_pop"):
        send_message(f"👥 **Server is POPPING!**\n{players}/{max_players} players online!")
        update_cooldown("high_pop")
    
    # Daily status update (every 4 hours)
    if check_cooldown("daily_status"):
        send_message(f"📊 **Server Status**\n{players}/{max_players} players online")
        update_cooldown("daily_status")

def send_restart_alert():
    """Send server restart alert"""
    if check_cooldown("restart_alert"):
        send_message("⚠️ **Server restarting in 5 minutes!**\nPlease log out to avoid losing progress.")
        update_cooldown("restart_alert")

def main():
    """Main bot loop"""
    print("🤖 Rust Discord Bot started...")
    print(f"🔧 Monitoring server: {SERVER_NAME}")
    send_message("✅ Rust Discord Bot is online!")
    
    while True:
        try:
            now = datetime.datetime.now()
            
            # Check wipe schedule (Thursdays)
            check_wipe_schedule()
            
            # Check server status
            check_server_status()
            
            # Sleep for 5 minutes (300 seconds)
            time.sleep(300)
            
        except KeyboardInterrupt:
            send_message("🛑 Rust Discord Bot shutting down...")
            print("Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()
