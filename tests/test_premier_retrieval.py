#!/usr/bin/env python3
"""Test PREMIER document retrieval."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval import get_relevant_documents


def _print_results(label: str, docs):
    print(f"\n{'=' * 70}")
    print(f"Testing: '{label}'")
    print("=" * 70)
    print(f"\nFound {len(docs)} documents:\n")
    for i, d in enumerate(docs, 1):
        content = d.get("content", "")
        metadata = d.get("metadata", {})
        score = d.get("score", "N/A")
        print(f"Doc {i} (score: {score}):")
        print(f"  ID: {metadata.get('id', 'Unknown')}")
        print(f"  Source: {metadata.get('source', 'Unknown')}")
        print(f"  Section: {metadata.get('section', 'Unknown')}")
        print(f"  Content preview: {content[:250]}...")
        print()


if __name__ == "__main__":
    _print_results(
        "plans with both minutes and data",
        get_relevant_documents("plans with both minutes and data", k=8),
    )
    _print_results(
        "PREMIER tariff plans",
        get_relevant_documents("PREMIER tariff plans", k=8),
    )
