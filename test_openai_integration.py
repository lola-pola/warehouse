#!/usr/bin/env python3
"""
Test script for OpenAI integration
"""
import requests
import json


def test_openai_endpoints():
    """Test the OpenAI endpoints"""
    base_url = "http://localhost:25000/api/v1/openai"
    
    print("Testing OpenAI Integration Endpoints")
    print("=" * 50)
    
    # Test 1: Get database schema
    print("\n1. Testing database schema endpoint...")
    try:
        response = requests.get(f"{base_url}/schema")
        if response.status_code == 200:
            schema_data = response.json()
            print("✓ Schema endpoint working")
            print("Schema preview:")
            print(schema_data['schema'][:200] + "...")
        else:
            print(f"✗ Schema endpoint failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Schema endpoint error: {e}")
    
    # Test 2: Set OpenAI API key (this will fail without a real key)
    print("\n2. Testing set API key endpoint...")
    try:
        test_key = "sk-test-key-not-real"
        response = requests.post(
            f"{base_url}/set-key",
            json={"api_key": test_key}
        )
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"✗ Set API key error: {e}")
    
    # Test 3: Test natural language query (will fail without valid API key)
    print("\n3. Testing natural language query endpoint...")
    try:
        response = requests.post(
            f"{base_url}/query",
            json={
                "query": "Show me all users with their email addresses",
                "limit": 10
            }
        )
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"✗ Natural language query error: {e}")
    
    # Test 4: Test direct SQL execution
    print("\n4. Testing direct SQL execution endpoint...")
    try:
        response = requests.post(
            f"{base_url}/sql",
            json={
                "sql": "SELECT * FROM user LIMIT 5",
                "limit": 5
            }
        )
        if response.status_code == 200:
            result = response.json()
            print("✓ Direct SQL execution working")
            print(f"Query: {result['sql']}")
            print(f"Rows returned: {result['row_count']}")
            print(f"Columns: {result['columns']}")
        else:
            print(f"✗ Direct SQL failed: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"✗ Direct SQL error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo use the OpenAI features:")
    print("1. Install openai package: pip install openai==1.3.0")
    print("2. Set your OpenAI API key using POST /api/v1/openai/set-key")
    print("3. Use natural language queries with POST /api/v1/openai/query")


if __name__ == "__main__":
    test_openai_endpoints()
