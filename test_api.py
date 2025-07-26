#!/usr/bin/env python3
"""
Test script for NaviFi Financial Agent API
Tests both streaming and non-streaming endpoints
"""

import requests
import json
import time
import asyncio
import aiohttp
import sys
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_complete_chat():
    """Test the complete chat endpoint (non-streaming)"""
    print("\n💬 Testing complete chat endpoint...")
    
    test_prompts = [
        "What is my current net worth?",
        "Help me plan for retirement",
        "I got a salary hike, what should I do with the extra money?",
        "Should I invest in stocks or mutual funds?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n   Test {i}/4: {prompt}")
        try:
            payload = {
                "prompt": prompt,
                "user_id": f"test_user_{i}"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/chat",
                headers=HEADERS,
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Response received in {end_time - start_time:.2f}s")
                print(f"   📝 Response preview: {result['response'][:100]}...")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ Request timed out (30s)")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_streaming_chat():
    """Test the streaming chat endpoint"""
    print("\n🌊 Testing streaming chat endpoint...")
    
    test_prompt = "I'm planning to buy a house next year. Can you help me with financial planning?"
    
    try:
        payload = {
            "prompt": test_prompt,
            "user_id": "test_stream_user"
        }
        
        print(f"   Prompt: {test_prompt}")
        print("   📡 Starting stream...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/chat/stream",
            headers=HEADERS,
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ Stream started successfully")
            chunk_count = 0
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        try:
                            data = json.loads(decoded_line[6:])  # Remove 'data: ' prefix
                            chunk_count += 1
                            
                            if data.get('type') == 'start':
                                print(f"   🚀 {data.get('message')}")
                            elif data.get('type') == 'chunk':
                                content = data.get('content', '')
                                full_response += content
                                print(f"   📦 Chunk {chunk_count}: {content[:30]}...")
                            elif data.get('type') == 'end':
                                end_time = time.time()
                                print(f"   🏁 {data.get('message')}")
                                print(f"   ⏱️  Total time: {end_time - start_time:.2f}s")
                                print(f"   📊 Total chunks: {chunk_count}")
                                print(f"   📝 Full response length: {len(full_response)} characters")
                            elif data.get('type') == 'error':
                                print(f"   ❌ Stream error: {data.get('message')}")
                                
                        except json.JSONDecodeError:
                            print(f"   ⚠️  Invalid JSON in stream: {decoded_line}")
            
        else:
            print(f"   ❌ Stream failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Stream timed out (30s)")
    except Exception as e:
        print(f"   ❌ Stream error: {e}")

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🚨 Testing error handling...")
    
    # Test empty prompt
    print("   Testing empty prompt...")
    try:
        payload = {"prompt": "", "user_id": "test_user"}
        response = requests.post(f"{API_BASE_URL}/chat", headers=HEADERS, json=payload)
        if response.status_code == 400:
            print("   ✅ Empty prompt correctly rejected")
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing empty prompt: {e}")
    
    # Test invalid JSON
    print("   Testing invalid request format...")
    try:
        response = requests.post(f"{API_BASE_URL}/chat", headers=HEADERS, data="invalid json")
        if response.status_code == 422:
            print("   ✅ Invalid JSON correctly rejected")
        else:
            print(f"   ❌ Expected 422, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid JSON: {e}")

async def test_concurrent_requests():
    """Test multiple concurrent requests"""
    print("\n🔀 Testing concurrent requests...")
    
    async def make_request(session, prompt, user_id):
        payload = {"prompt": prompt, "user_id": user_id}
        try:
            async with session.post(f"{API_BASE_URL}/chat", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return f"✅ User {user_id}: Success"
                else:
                    return f"❌ User {user_id}: Failed ({response.status})"
        except Exception as e:
            return f"❌ User {user_id}: Error - {e}"
    
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(3):
                prompt = f"Test concurrent request {i+1}: What should I invest in?"
                task = make_request(session, prompt, f"concurrent_user_{i+1}")
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            print(f"   ⏱️  Concurrent requests completed in {end_time - start_time:.2f}s")
            for result in results:
                print(f"   {result}")
                
    except Exception as e:
        print(f"   ❌ Concurrent test error: {e}")

def run_all_tests():
    """Run all tests"""
    print("🧪 NaviFi Financial Agent API Test Suite")
    print("=" * 50)
    
    # Basic connectivity tests
    if not test_health_check():
        print("\n❌ Server not accessible. Please start the API server first:")
        print("   python api.py")
        return False
    
    test_root_endpoint()
    
    # Core functionality tests
    test_complete_chat()
    test_streaming_chat()
    test_error_handling()
    
    # Performance tests
    try:
        asyncio.run(test_concurrent_requests())
    except Exception as e:
        print(f"❌ Concurrent test failed: {e}")
    
    print("\n🎉 Test suite completed!")
    print("\n📋 To start the API server:")
    print("   python api.py")
    print("\n📋 To test specific endpoints manually:")
    print("   curl -X GET http://localhost:8000/health")
    print("   curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"prompt\":\"Help me plan my finances\"}'")
    
    return True

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import aiohttp
    except ImportError:
        print("Installing required test dependencies...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp
    
    run_all_tests() 