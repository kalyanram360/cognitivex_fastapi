#!/usr/bin/env python3
"""
Test script to verify all game generation endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_endpoint(endpoint, test_query, endpoint_name):
    print(f"\n🧪 Testing {endpoint_name}...")
    print(f"🔍 Query: {test_query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"message": test_query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {endpoint_name} - SUCCESS")
            print(f"📊 Response keys: {list(data.keys())}")
            
            # Check if it has the expected structure
            if endpoint == "/generate-tax-game":
                if "monthlyIncomes" in data and "monthlyOptions" in data:
                    print(f"💰 Sample income month 1: ₹{data['monthlyIncomes']['1']:,}")
                    print(f"🎯 Sample tax option: {data['monthlyOptions']['1']['high'][0]['label']}")
                else:
                    print("⚠️  Missing expected keys for tax game")
                    
            elif endpoint == "/generate-investment-game":
                if "monthlyBudgets" in data and "monthlyOptions" in data:
                    print(f"💰 Sample budget month 1: ₹{data['monthlyBudgets']['1']:,}")
                    print(f"📈 Sample investment: {data['monthlyOptions']['1']['safe'][0]['label']}")
                else:
                    print("⚠️  Missing expected keys for investment game")
                    
            elif endpoint == "/generate-savings-game":
                if "monthlyIncomes" in data and "monthlyOptions" in data:
                    print(f"💰 Sample income month 1: ₹{data['monthlyIncomes']['1']:,}")
                    print(f"💵 Sample savings: {data['monthlyOptions']['1']['aggressive'][0]['label']}")
                else:
                    print("⚠️  Missing expected keys for savings game")
                    
        else:
            print(f"❌ {endpoint_name} - FAILED (Status: {response.status_code})")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ {endpoint_name} - EXCEPTION: {str(e)}")

def test_chat_endpoint():
    print(f"\n🧪 Testing Chat Classification...")
    
    test_queries = [
        "I want to save tax on my salary",
        "Help me invest 15000 monthly", 
        "I need to save money for emergency fund"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Category: {data.get('category', 'unknown')}")
                print(f"📝 Response: {data.get('response', 'No response')[:100]}...")
            else:
                print(f"❌ Chat failed (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Chat exception: {str(e)}")

def main():
    print("🚀 Testing All Finance Bot Endpoints")
    print("=" * 50)
    
    # Test individual game endpoints
    test_endpoint(
        "/generate-tax-game",
        "I earn 8 lakh annually and want to save maximum tax using 80C deductions",
        "Tax Game API"
    )
    
    test_endpoint(
        "/generate-investment-game", 
        "I'm 28 years old, earn ₹80,000 monthly, want to invest ₹15,000 per month for retirement",
        "Investment Game API"
    )
    
    test_endpoint(
        "/generate-savings-game",
        "I earn ₹60,000 monthly, spend ₹35,000, want to save ₹5 lakhs in 2 years",
        "Savings Game API"
    )
    
    # Test chat classification
    test_chat_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 All tests completed!")

if __name__ == "__main__":
    main()
