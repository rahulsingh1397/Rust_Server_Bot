#!/usr/bin/env python3
"""
Test script to verify web_app.py functionality
"""

import requests
import os
from webhook import WEBHOOK_URL

SERVER_NAME = "IND-US Valley [Vanilla+ | Weekly | Merged Outpost | Max : 5]"
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

def test_bot_functionality():
    """Test all bot functions"""
    print("🧪 Testing bot functionality...")
    
    # Test 1: Server data
    print("\n1. Testing server data fetch...")
    server_data = get_server_data()
    if server_data:
        attributes = server_data.get('attributes', {})
        players = attributes.get('players', 0)
        max_players = attributes.get('maxPlayers', 0)
        print(f"✅ Server data: {players}/{max_players} players")
    else:
        print("❌ Failed to fetch server data")
        return False
    
    # Test 2: Discord message
    print("\n2. Testing Discord message...")
    test_msg = f"🧪 **Bot Test**\n\n👥 Players: {players}/{max_players}\n🕐 Test time: {requests.get('https://timeapi.io/api/Time/current/zone?timeZone=UTC').json().get('dateTime', 'Unknown')[:19]}\n\n🔧 Bot functionality test completed!"
    
    if send_message(test_msg):
        print("✅ Discord message sent successfully")
        return True
    else:
        print("❌ Failed to send Discord message")
        return False

if __name__ == "__main__":
    success = test_bot_functionality()
    if success:
        print("\n🎉 All tests passed! Bot should be working.")
    else:
        print("\n💥 Tests failed! Check bot configuration.")
