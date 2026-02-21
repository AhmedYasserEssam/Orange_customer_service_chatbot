#!/usr/bin/env python3
"""Test Home DSL and Home Wireless bundle queries."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import get_fast_response

tests = [
    ("What are the Home DSL bundles?", "Home DSL bundles"),
    ("Tell me about Home Wireless packages", "Home Wireless packages"),
    ("What is the difference between Home DSL and Home Wireless?", "Difference"),
    ("How much does Home Wireless cost?", "Home Wireless pricing"),
    ("What are the cheapest home internet options?", "Cheapest options"),
]

if __name__ == "__main__":
    for query, name in tests:
        print(f"\n{'=' * 70}")
        print(f"Test: {name}")
        print(f"Query: {query}")
        print("=" * 70)
        print(get_fast_response(query))
        print()
