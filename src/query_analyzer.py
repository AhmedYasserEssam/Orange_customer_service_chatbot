"""LLM-based query analysis for intent classification and retrieval planning.

Instead of hard-coded keyword matching, the chat model itself decides:
  - the user's intent
  - which search queries to run against the vector store
  - which metadata filters (if any) to apply
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import CHAT_MODEL


@dataclass
class QueryAnalysis:
    """Structured output of the query analyzer."""
    intent: str = "general"
    needs_retrieval: bool = True
    search_queries: List[str] = field(default_factory=list)
    metadata_filter: Optional[Dict[str, str]] = None


# A dedicated low-temperature instance for deterministic classification.
# It reuses the same Ollama model already in memory so there is no extra cost.
_classifier: Optional[ChatOllama] = None


def _get_classifier() -> ChatOllama:
    global _classifier
    if _classifier is None:
        _classifier = ChatOllama(model=CHAT_MODEL, temperature=0, num_ctx=2048)
    return _classifier


def _extract_json(text: str) -> dict:
    """Extract a JSON object from LLM output, tolerating markdown wrappers."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON object found in classifier response")


_SYSTEM = (
    "You are a query classifier for Orange Egypt telecom customer service. "
    "Return ONLY a valid JSON object. No markdown, no explanation, no extra text."
)

_HUMAN = """\
Classify this customer question and plan a retrieval strategy.

The knowledge base contains:
- FAQ entries about Orange Egypt services
- Mobile internet bundles (GO, Social, Video, Amazon, Play, @Home, TikTok) \
with prices in EGP and quotas in MB
- Tariff plans with voice minutes (PREMIER 400/550/750, ALO, FREEmax)
- Home internet plans (Home DSL, Home Wireless) with speeds and quotas
- General service documentation (billing, roaming, support procedures)

Return a JSON object with exactly these fields:
{{
  "intent": "<see list below>",
  "needs_retrieval": true or false,
  "search_queries": ["query1", "query2", ...],
  "metadata_filter": null or {{"key": "string_value"}}
}}

Intents (pick exactly one):
- greeting       : Hello, hi, good morning, etc.
- farewell       : Thanks, bye, goodbye
- own_plan       : User asks about THEIR OWN plan / subscription / usage \
(contains "my plan", "my data", "my subscription", etc.)
- mobile_internet: GO bundles, mobile data packages (data-only, no voice)
- tariff_plans   : PREMIER, ALO, FREEmax — monthly plans with voice + data
- home_internet  : Home DSL or Home Wireless packages
- hardware       : Modems, routers, devices, CPE equipment
- comparison     : Comparing two or more plans/services ("difference between …")
- upgrade        : Wanting more/less data, upgrade, downgrade, alternatives
- billing        : Payments, bills, charges, invoices
- troubleshooting: Technical issues, connection problems, slow speed
- general        : Any other Orange service question

Rules:
- needs_retrieval is false ONLY for greeting, farewell, and own_plan.
- search_queries: 1-5 diverse queries optimised for semantic similarity \
search; empty list when needs_retrieval is false.
- metadata_filter: use {{"has_minutes": "true"}} for tariff plans, \
{{"bundle_type": "Home DSL"}} for DSL only, \
{{"bundle_type": "Home Wireless"}} for wireless only. \
Use null for everything else, including comparisons.

Customer question: {question}"""

_prompt = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM),
    ("human", _HUMAN),
])


def analyze_query(query: str) -> QueryAnalysis:
    """Classify the user's question and generate retrieval parameters."""
    try:
        chain = _prompt | _get_classifier() | StrOutputParser()
        raw = chain.invoke({"question": query})
        data = _extract_json(raw)

        intent = data.get("intent", "general")
        needs_retrieval = data.get("needs_retrieval", True)
        search_queries = data.get("search_queries") or []
        metadata_filter = data.get("metadata_filter")

        if isinstance(metadata_filter, dict):
            metadata_filter = {k: str(v) for k, v in metadata_filter.items()}

        return QueryAnalysis(
            intent=intent,
            needs_retrieval=needs_retrieval,
            search_queries=search_queries,
            metadata_filter=metadata_filter,
        )
    except Exception as e:
        print(f"Query analysis fallback ({e}); treating as general question")
        return QueryAnalysis(
            intent="general",
            needs_retrieval=True,
            search_queries=[query],
            metadata_filter=None,
        )
