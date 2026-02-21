"""Core chatbot logic: LLM-routed RAG response generation.

The flow is:
  1. ``analyze_query`` (LLM) classifies intent and generates search queries.
  2. Non-retrieval intents (greeting, farewell, own_plan) are answered
     directly without hitting the vector store.
  3. All other intents go through retrieval → context building → LLM
     response generation.
"""

from typing import List, Dict, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.config import APPEND_SOURCE_CITATIONS
from src.models import get_chat_model
from src.data_loader import load_internet_catalog
from src.retrieval import get_relevant_documents, format_context_documents
from src.prompts import create_system_prompt
from src.query_analyzer import analyze_query


# ── helpers ──────────────────────────────────────────────────────────────


def _clean_response(response: str, user_input: str) -> str:
    """Strip leaked prompt artefacts and accidental echoes of the user's question."""
    response = response.strip()

    for marker in ("User Question:", "Response:", "Bot: ", "Assistant: ", "User: "):
        if marker in response:
            response = response.split(marker)[-1].strip()

    lines = response.split("\n")
    if len(lines) > 1 and lines[0].strip().lower() == user_input.lower().strip():
        response = "\n".join(lines[1:]).strip()

    if response.strip() == user_input.strip():
        return "I understand your concern. How can I help you with that?"

    for wrapper in (f'"{user_input}"', f"'{user_input}'"):
        if response.startswith(wrapper):
            response = response[len(wrapper):].strip()

    for prefix in (
        f'Based on your question "{user_input}"',
        f"Based on your question '{user_input}'",
        f"For {user_input}",
        f"Your {user_input}",
        user_input,
    ):
        if response.startswith(prefix):
            response = response[len(prefix):].strip()

    for leading in (", ", ". ", ": "):
        if response.startswith(leading):
            response = response[len(leading):].strip()

    return response


def _build_comparison_context(user_profile: Dict) -> str:
    """Append structured upgrade/downgrade options from the internet catalog."""
    current_plan = user_profile.get("mobile_plan_name", "")
    raw = user_profile.get("monthly_mobile_data_mb", "0")
    current_mb = int(str(raw)) if str(raw).isdigit() else None
    if not current_mb:
        return ""

    catalog = load_internet_catalog()
    higher = sorted(
        [i for i in catalog if i.get("quota_mb", 0) > current_mb],
        key=lambda x: x["quota_mb"],
    )
    lower = sorted(
        [i for i in catalog if i.get("quota_mb", 0) < current_mb],
        key=lambda x: x["quota_mb"],
        reverse=True,
    )
    if not higher and not lower:
        return ""

    def _fmt(items: List[Dict], limit: int = 5) -> str:
        return "; ".join(
            f"{i['name']} ({i['quota_mb']} MB for {i.get('price_egp', 'N/A')} EGP)"
            for i in items[:limit]
        )

    parts = [
        f"\n\n**User's Current Plan: {current_plan} with {current_mb} MB.**\n"
        "**Available Bundle Options Relative to Current Plan:**\n"
    ]
    if higher:
        parts.append(f"More data: {_fmt(higher)}\n")
    if lower:
        parts.append(f"Less data: {_fmt(lower)}\n")
    return "".join(parts)


# ── public API ───────────────────────────────────────────────────────────


def get_fast_response(
    user_input: str,
    history: Optional[List[Dict]] = None,
    user_profile: Optional[Dict] = None,
) -> str:
    """Generate a response using LLM-based intent routing and RAG.

    Args:
        user_input: The user's question/input.
        history: Previous conversation history (list of
            ``{"user": "…", "assistant": "…"}`` dicts).
        user_profile: Current user's profile information.

    Returns:
        Generated response string.
    """
    try:
        # ── 1. LLM-based intent classification ──────────────────────────
        analysis = analyze_query(user_input)

        # ── 2. Direct responses (no retrieval needed) ───────────────────
        if analysis.intent == "greeting":
            name = user_profile.get("Name", "") if user_profile else ""
            if name:
                return f"Hello {name}! \U0001f44b How can I help you today?"
            return "Hello! \U0001f44b Welcome to Orange Customer Service. How can I assist you today?"

        if analysis.intent == "farewell":
            return "You're welcome! \U0001f60a Is there anything else I can help you with?"

        if analysis.intent == "own_plan":
            if user_profile:
                return (
                    f"You are currently on the "
                    f"{user_profile.get('mobile_plan_name', 'Unknown')} plan "
                    f"with {user_profile.get('monthly_mobile_data_mb', 'Unknown')} MB "
                    f"of data for {user_profile.get('monthly_bill_mobile_amount', 'Unknown')} "
                    f"EGP per month. You have "
                    f"{user_profile.get('remaining_mobile_quota', 'Unknown')} MB remaining "
                    f"in your current quota."
                )
            return (
                "I need your profile information to check your plan details. "
                "Please log in to your account."
            )

        # ── 3. Retrieve context ─────────────────────────────────────────
        relevant_docs = get_relevant_documents(
            user_input,
            search_queries=analysis.search_queries,
            k=10,
            metadata_filter=analysis.metadata_filter,
        )
        context = format_context_documents(relevant_docs)

        # ── 4. Augment context for upgrade / comparison ─────────────────
        if analysis.intent in ("upgrade", "comparison") and user_profile:
            context += _build_comparison_context(user_profile)

        # ── 5. Build message list and generate ──────────────────────────
        system_prompt = create_system_prompt(user_profile)
        messages: list = [SystemMessage(content=system_prompt)]

        if history:
            for exchange in history[-3:]:
                if exchange.get("user"):
                    messages.append(HumanMessage(content=exchange["user"]))
                if exchange.get("assistant"):
                    messages.append(AIMessage(content=exchange["assistant"]))

        user_message = (
            f"Context:\n{context}\n\n"
            f"User Question: {user_input}\n\n"
            "Answering rules:\n"
            "- Be concise (2\u20134 sentences) and directly answer the question.\n"
            "- Quote exact names, prices, quotas, and validity from the Context; do not guess.\n"
            "- If useful, list 2\u20135 relevant options.\n"
            "- If the Context lacks the answer, say so and suggest calling 110, "
            "using My Orange app, or dialing #222#.\n"
            "- Answer ONLY what the user asked. Do NOT add unrelated suggestions.\n"
        )
        messages.append(HumanMessage(content=user_message))

        result = get_chat_model().invoke(messages)
        response = _clean_response(result.content, user_input)

        # ── 6. Optional source citations ────────────────────────────────
        if APPEND_SOURCE_CITATIONS:
            try:
                sources: list[str] = []
                for d in relevant_docs[:3]:
                    src = (d.get("metadata") or {}).get("source")
                    if src and src not in sources:
                        sources.append(src)
                if sources:
                    response = f"{response}\n\nSources: {'; '.join(sources)}"
            except Exception:
                pass

        return response

    except Exception as e:
        print(f"Error in get_fast_response: {e}")
        return f"I apologize, but I encountered an error while processing your request: {e!s}"
