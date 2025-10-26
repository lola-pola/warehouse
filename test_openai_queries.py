#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI natural language to SQL conversion
"""
import requests
import json
import sys

BASE_URL = "http://localhost:25000/api/v1"

def test_openai_system():
    """Test the OpenAI natural language to SQL system"""
    
    print("🤖 Testing OpenAI Natural Language to SQL System")
    print("=" * 50)
    
    # Test 1: Get database schema
    print("\n1. Getting database schema...")
    try:
        response = requests.get(f"{BASE_URL}/openai/schema")
        if response.status_code == 200:
            schema_data = response.json()
            print("✅ Schema retrieved successfully!")
            print("Schema preview:")
            print(schema_data['schema'][:300] + "...")
        else:
            print(f"❌ Failed to get schema: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Check if OpenAI key is set
    print("\n2. Testing natural language query...")
    
    # Example queries to test
    test_queries = [
        "Show me all users",
        "Find all active policies", 
        "List users with their email addresses",
        "Show me payment transactions",
        "Get all quotes created this year"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: '{query}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/openai/query",
                json={"query": query, "limit": 5},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SQL Generated: {result.get('sql', 'N/A')}")
                print(f"   📝 Explanation: {result.get('explanation', 'N/A')}")
                print(f"   📊 Rows returned: {result.get('row_count', 0)}")
                
                if result.get('data'):
                    print("   📋 Sample data:")
                    for row in result['data'][:2]:  # Show first 2 rows
                        print(f"      {row}")
                        
            elif response.status_code == 400:
                error_data = response.json()
                if "OpenAI API key not set" in error_data.get('error', ''):
                    print("   ⚠️  OpenAI API key not set. Use the set-key endpoint first.")
                    break
                else:
                    print(f"   ❌ Error: {error_data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 How to use this system:")
    print("1. Set OpenAI API key: POST /openai/set-key")
    print("2. Send plain text queries: POST /openai/query")
    print("3. Get results with SQL, explanation, and data!")
    
    return True

def show_api_examples():
    """Show example API calls"""
    print("\n📚 API Usage Examples:")
    print("-" * 30)
    
    print("\n1. Set OpenAI API Key:")
    print("curl -X POST http://localhost:25000/api/v1/openai/set-key \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"api_key": "your-openai-api-key-here"}\'')
    
    print("\n2. Natural Language Query:")
    print("curl -X POST http://localhost:25000/api/v1/openai/query \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"query": "Show me all users with active policies", "limit": 10}\'')
    
    print("\n3. Get Database Schema:")
    print("curl -X GET http://localhost:25000/api/v1/openai/schema")

if __name__ == "__main__":
    print("Starting OpenAI System Test...")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_api_examples()
    else:
        success = test_openai_system()
        if success:
            show_api_examples()
