#!/usr/bin/env python3
"""
Quick manual test script for NaviFi API with Security Guardrails
Simple interactive testing
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_chat(prompt, user_id="test_user"):
    """Test chat endpoint"""
    print(f"\n🧪 Testing Chat: '{prompt}'")
    print("-" * 50)
    
    payload = {
        "prompt": prompt,
        "user_id": user_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS")
            print(f"Response: {data.get('response', '')[:200]}...")
            print(f"Security Info: {data.get('security_info')}")
        elif response.status_code == 403:
            print("🚫 BLOCKED (Security Guardrail)")
            print(f"Error: {response.text}")
        elif response.status_code == 400:
            print("❌ BAD REQUEST")
            print(f"Error: {response.text}")
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

def test_security_status():
    """Test security status"""
    print("\n🔒 Testing Security Status")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/security/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Security Status:")
            print(f"  Allowed Tools: {len(data.get('allowed_tools', []))}")
            print(f"  Rate Limit Store Size: {data.get('rate_limit_store_size')}")
            print(f"  Security Features: {data.get('security_features')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Interactive testing"""
    print("🚀 NaviFi API Quick Test")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Test valid chat")
        print("2. Test malicious chat (should be blocked)")
        print("3. Test security status")
        print("4. Custom test")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_chat("What is my net worth?")
            
        elif choice == "2":
            print("\nTesting malicious inputs (should be blocked):")
            test_chat("<script>alert('xss')</script>What is my net worth?")
            test_chat("password=123456 What is my net worth?")
            test_chat("api_key=sk-1234567890abcdef What is my net worth?")
            
        elif choice == "3":
            test_security_status()
            
        elif choice == "4":
            prompt = input("Enter your test prompt: ").strip()
            if prompt:
                test_chat(prompt)
            else:
                print("❌ Empty prompt not allowed")
                
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main() 