#!/usr/bin/env python3
"""
Test script for Orange Customer Service Chatbot
This script tests the chatbot functionality without the Streamlit UI.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_prompts import get_fast_response, load_customer_data

def test_basic_functionality():
    """Test basic chatbot functionality"""
    print("🧪 Testing Orange Customer Service Chatbot")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What are the available mobile internet plans?",
        "How do I check my data usage?",
        "What is the GO 105 plan?",
        "How can I pay my bill?",
        "What are the available internet bundles?"
    ]
    
    print("\n📋 Running test queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 30)
        
        try:
            response = get_fast_response(query)
            print(f"Response: {response[:200]}...")
            if len(response) > 200:
                print("(Response truncated for display)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Basic functionality test completed")

def test_customer_data():
    """Test customer data loading"""
    print("\n👤 Testing customer data loading...")
    
    try:
        customer_data = load_customer_data()
        print(f"✅ Loaded {len(customer_data)} customer records")
        
        if customer_data:
            sample_customer = customer_data[0]
            print(f"Sample customer: {sample_customer.get('Name', 'Unknown')}")
            print(f"Phone: {sample_customer.get('phone_number', 'Unknown')}")
            print(f"Plan: {sample_customer.get('mobile_plan_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error loading customer data: {e}")

def test_with_user_profile():
    """Test chatbot with user profile"""
    print("\n🔐 Testing with user profile...")
    
    try:
        customer_data = load_customer_data()
        if customer_data:
            user_profile = customer_data[0]  # Use first customer as test
            
            test_query = "What is my current mobile plan?"
            print(f"Query: {test_query}")
            print(f"User: {user_profile.get('Name', 'Unknown')}")
            
            response = get_fast_response(
                test_query, 
                user_profile=user_profile
            )
            print(f"Response: {response[:200]}...")
        else:
            print("❌ No customer data available for testing")
    except Exception as e:
        print(f"❌ Error testing with user profile: {e}")

def main():
    """Main test function"""
    print("🍊 Orange Customer Service Chatbot - Test Suite")
    print("=" * 60)
    
    # Test basic functionality
    test_basic_functionality()
    
    # Test customer data
    test_customer_data()
    
    # Test with user profile
    test_with_user_profile()
    
    print("\n🎉 All tests completed!")
    print("\nTo run the full application:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Run: streamlit run app.py")
    print("3. Open your browser to the URL shown")

if __name__ == "__main__":
    main()
