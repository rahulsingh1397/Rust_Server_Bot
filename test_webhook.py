#!/usr/bin/env python3
"""
Test script to verify Discord webhook is working
"""

import requests
from webhook import WEBHOOK_URL

def send_message(msg):
    """Send a test message to Discord webhook"""
    try:
        data = {"content": msg}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        
        if response.status_code == 204:
            print(f"✅ Success! Message sent: {msg}")
            return True
        else:
            print(f"❌ Failed! Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Discord webhook...")
    
    # Test basic message
    success = send_message("✅ Rust bot is working!")
    
    if success:
        print("\n🎉 Webhook test passed!")
        print("You should see a message in your Discord channel.")
    else:
        print("\n💥 Webhook test failed!")
        print("Check your webhook URL and Discord channel permissions.")
