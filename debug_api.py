#!/usr/bin/env python3
"""
Debug script to check BattleMetrics API response
"""

import requests
import json

SERVER_NAME = "IND-US Valley [Vanilla+ | Weekly | Merged Outpost | Max : 5]"
BATTLEMETRICS_URL = f"https://api.battlemetrics.com/servers?filter[search]={SERVER_NAME}"

def debug_api_response():
    """Debug the API response structure"""
    print(f"🔍 Debugging API for: {SERVER_NAME}")
    print(f"📡 URL: {BATTLEMETRICS_URL}")
    print("=" * 60)
    
    try:
        response = requests.get(BATTLEMETRICS_URL, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Data Structure:")
            print(f"   - Total servers found: {len(data.get('data', []))}")
            
            if data.get('data'):
                server = data['data'][0]
                print(f"   - Server ID: {server.get('id', 'N/A')}")
                print(f"   - Server Type: {server.get('type', 'N/A')}")
                
                attributes = server.get('attributes', {})
                print(f"\n📋 Server Attributes:")
                
                # Print all available attributes
                for key, value in attributes.items():
                    if key in ['players', 'maxPlayers', 'name', 'status', 'details']:
                        print(f"   - {key}: {value}")
                
                # Check players specifically
                players = attributes.get('players', 'NOT FOUND')
                max_players = attributes.get('maxPlayers', 'NOT FOUND')
                
                print(f"\n👥 Player Info:")
                print(f"   - Players: {players}")
                print(f"   - Max Players: {max_players}")
                print(f"   - Type: {type(players)}")
                print(f"   - Max Type: {type(max_players)}")
                
                # Check if there's a nested structure
                if isinstance(players, dict):
                    print(f"   - Players Dict Keys: {list(players.keys())}")
                if isinstance(max_players, dict):
                    print(f"   - Max Players Dict Keys: {list(max_players.keys())}")
                
                # Look for alternative player fields
                print(f"\n🔍 Alternative Player Fields:")
                for key in attributes:
                    if 'player' in key.lower() or 'slot' in key.lower():
                        print(f"   - {key}: {attributes[key]}")
                
            else:
                print("❌ No servers found!")
                
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_api_response()
