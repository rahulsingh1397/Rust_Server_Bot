#!/usr/bin/env python3
"""
Test script to verify server connection with BattleMetrics
"""

import requests
from rust_discord_bot import SERVER_NAME, BATTLEMETRICS_URL

def test_server_connection():
    """Test if we can fetch server data"""
    print(f"🔍 Testing connection to server: '{SERVER_NAME}'")
    print(f"📡 BattleMetrics URL: {BATTLEMETRICS_URL}")
    
    try:
        response = requests.get(BATTLEMETRICS_URL, timeout=10)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            servers_found = len(data['data'])
            print(f"🎮 Servers found: {servers_found}")
            
            if servers_found > 0:
                server = data['data'][0]['attributes']
                players = server.get('players', 0)
                max_players = server.get('maxPlayers', 0)
                server_name = server.get('name', 'Unknown')
                
                print(f"✅ SUCCESS!")
                print(f"📛 Server name: {server_name}")
                print(f"👥 Players: {players}/{max_players}")
                print(f"🌐 Server ID: {data['data'][0]['id']}")
                return True
            else:
                print("❌ No servers found with that name")
                print("💡 Try searching for your server on BattleMetrics")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing BattleMetrics server connection...")
    print("=" * 50)
    
    if SERVER_NAME == "YOUR_SERVER_NAME":
        print("⚠️  Please update SERVER_NAME in rust_discord_bot.py first!")
        print("💡 Find your server name on: https://www.battlemetrics.com/servers")
    else:
        test_server_connection()
