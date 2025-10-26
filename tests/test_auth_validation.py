#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI authentication validation
"""
import requests
import json


def test_openai_auth_validation():
    """Test OpenAI authentication validation endpoints"""
    base_url = "http://localhost:5000/api/v1/openai"
    
    print("🔍 Testing OpenAI Authentication Validation")
    print("=" * 50)
    
    # Test 1: Check authentication status without API key
    print("\n1. Testing authentication status (no API key set):")
    try:
        response = requests.get(f"{base_url}/status")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Try to make a query without authentication
    print("\n2. Testing natural language query (no API key):")
    try:
        query_data = {
            "query": "Show me all users",
            "limit": 10
        }
        response = requests.post(f"{base_url}/query", json=query_data)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Try to set an invalid API key
    print("\n3. Testing with invalid API key:")
    try:
        key_data = {"api_key": "invalid-key-12345"}
        response = requests.post(f"{base_url}/set-key", json=key_data)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check authentication status after invalid key
    print("\n4. Testing authentication status (after invalid key):")
    try:
        response = requests.get(f"{base_url}/status")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Authentication validation test completed!")
    print("\nTo test with a valid API key:")
    print("1. Get your OpenAI API key from https://platform.openai.com/")
    print("2. Use POST /api/v1/openai/set-key with your real API key")
    print("3. Check GET /api/v1/openai/status to verify authentication")
    print("4. Try POST /api/v1/openai/query with a natural language query")


if __name__ == "__main__":
    test_openai_auth_validation()
