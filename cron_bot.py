#!/usr/bin/env python3
"""
Cron-triggered Rust Discord Bot - Perfect for Render Web Service
Runs when called by external cron service
"""

import requests
import datetime
import json
import os
from flask import Flask

app = Flask(__name__)

# Configuration
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SERVER_NAME = os.getenv("SERVER_NAME", "IND-US Valley [Vanilla+ | Weekly | Merged Outpost | Max : 5]")
BATTLEMETRICS_URL = f"https://api.battlemetrics.com/servers?filter[search]={SERVER_NAME}"

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

def send_status_update():
    """Send server status update"""
    server_data = get_server_data()
    if not server_data:
        return False
    
    attributes = server_data.get('attributes', {})
    players = attributes.get('players', 0)
    max_players = attributes.get('maxPlayers', 0)
    
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
        
        if days_until <= 1:
            message += f"⚠️ **Wipe coming soon!**"
        elif days_until <= 3:
            message += f"📢 **Wipe this week!**"
        else:
            message += f"🕐 **Plenty of time to build!**"
    
    return send_message(message)

def check_high_population():
    """Check and send high population alert"""
    server_data = get_server_data()
    if not server_data:
        return False
    
    attributes = server_data.get('attributes', {})
    players = attributes.get('players', 0)
    max_players = attributes.get('maxPlayers', 0)
    
    if players > 30:
        message = f"👥 **Server is POPPING!**\n{players}/{max_players} players online!"
        return send_message(message)
    
    return False

# Flask routes
@app.route('/')
def home():
    return {"status": "Rust Discord Bot", "service": "active", "type": "cron-triggered"}

@app.route('/hourly-update')
def hourly_update():
    """Run hourly status update"""
    result = send_status_update()
    return {"status": "hourly_update", "success": result, "time": datetime.datetime.now().isoformat()}

@app.route('/check-population')
def check_population():
    """Check population and send alert if needed"""
    result = check_high_population()
    return {"status": "population_check", "success": result, "time": datetime.datetime.now().isoformat()}

@app.route('/status')
def status():
    """Get current server status"""
    server_data = get_server_data()
    if server_data:
        attributes = server_data.get('attributes', {})
        return {
            "server": SERVER_NAME,
            "players": f"{attributes.get('players', 0)}/{attributes.get('maxPlayers', 0)}",
            "status": "online",
            "time": datetime.datetime.now().isoformat()
        }
    return {"status": "api_error"}

@app.route('/manual-update')
def manual_update():
    """Manual trigger for status update"""
    result = send_status_update()
    return {"status": "manual_update", "success": result, "time": datetime.datetime.now().isoformat()}

if __name__ == "__main__":
    # Send startup message
    send_message("✅ Rust Discord Bot (Cron Version) is online!")
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting cron bot on port {port}...")
    app.run(host='0.0.0.0', port=port)
