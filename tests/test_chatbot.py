#!/usr/bin/env python3
"""Test script for Orange Customer Service Chatbot."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import get_fast_response
from src.data_loader import load_customer_data


def test_basic_functionality():
    """Test basic chatbot functionality."""
    print("Testing Orange Customer Service Chatbot")
    print("=" * 50)

    test_queries = [
        "What are the available mobile internet plans?",
        "How do I check my data usage?",
        "What is the GO 105 plan?",
        "How can I pay my bill?",
        "What are the available internet bundles?",
    ]

    print("\nRunning test queries...")

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 30)
        try:
            response = get_fast_response(query)
            print(f"Response: {response[:200]}...")
            if len(response) > 200:
                print("(Response truncated for display)")
        except Exception as e:
            print(f"Error: {e}")

    print("\nBasic functionality test completed")


def test_customer_data():
    """Test customer data loading."""
    print("\nTesting customer data loading...")
    try:
        customer_data = load_customer_data()
        print(f"Loaded {len(customer_data)} customer records")
        if customer_data:
            sample = customer_data[0]
            print(f"Sample customer: {sample.get('Name', 'Unknown')}")
            print(f"Phone: {sample.get('phone_number', 'Unknown')}")
            print(f"Plan: {sample.get('mobile_plan_name', 'Unknown')}")
    except Exception as e:
        print(f"Error loading customer data: {e}")


def test_with_user_profile():
    """Test chatbot with user profile."""
    print("\nTesting with user profile...")
    try:
        customer_data = load_customer_data()
        if customer_data:
            user_profile = customer_data[0]
            test_query = "What is my current mobile plan?"
            print(f"Query: {test_query}")
            print(f"User: {user_profile.get('Name', 'Unknown')}")
            response = get_fast_response(test_query, user_profile=user_profile)
            print(f"Response: {response[:200]}...")
        else:
            print("No customer data available for testing")
    except Exception as e:
        print(f"Error testing with user profile: {e}")


if __name__ == "__main__":
    print("Orange Customer Service Chatbot - Test Suite")
    print("=" * 60)
    test_basic_functionality()
    test_customer_data()
    test_with_user_profile()
    print("\nAll tests completed!")
