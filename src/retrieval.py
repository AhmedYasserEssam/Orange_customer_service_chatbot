"""Document retrieval and context formatting for RAG.

Retrieval is now parameterised: search queries and metadata filters are
decided upstream by the LLM-based query analyzer, not by keyword matching.
"""

from typing import List, Dict, Optional

from src.models import get_vectorstore


def get_relevant_documents(
    query: str,
    search_queries: Optional[List[str]] = None,
    k: int = 5,
    metadata_filter: Optional[Dict[str, str]] = None,
) -> List[Dict]:
    """Retrieve relevant documents from the vector store.

    Args:
        query: The original user query (always included in searches).
        search_queries: Additional search strings produced by the query
            analyzer.  When *None*, only *query* is used.
        k: Maximum number of documents to return.
        metadata_filter: Optional Chroma metadata filter dict
            (e.g. ``{"has_minutes": "true"}``).

    Returns:
        List of document dicts sorted by relevance (lower score = better).
    """
    try:
        vectorstore = get_vectorstore()

        queries = [query]
        if search_queries:
            queries.extend(q for q in search_queries if q != query)

        all_docs: List[Dict] = []
        seen_ids: set = set()

        for sq in queries:
            # --- Cosine similarity search ---
            try:
                if metadata_filter:
                    docs = vectorstore.similarity_search_with_score(
                        sq, k=k * 2, filter=metadata_filter,
                    )
                else:
                    docs = vectorstore.similarity_search_with_score(sq, k=k)
            except Exception:
                try:
                    docs = vectorstore.similarity_search_with_score(sq, k=k)
                except Exception:
                    docs = []

            # --- MMR for diversity ---
            try:
                mmr_kwargs: dict = dict(
                    k=min(k, 6),
                    fetch_k=min(24, max(k * 3, 12)),
                    lambda_mult=0.3,
                )
                if metadata_filter:
                    mmr_kwargs["filter"] = metadata_filter
                mmr_docs = vectorstore.max_marginal_relevance_search(sq, **mmr_kwargs)
            except Exception:
                mmr_docs = []

            # --- Merge results ---
            for doc, score in docs:
                doc_id = doc.metadata.get("id", "")
                if doc_id and doc_id not in seen_ids:
                    all_docs.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score,
                    })
                    seen_ids.add(doc_id)

            for doc in mmr_docs:
                doc_id = doc.metadata.get("id", "")
                if doc_id and doc_id not in seen_ids:
                    all_docs.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": 0.5,
                    })
                    seen_ids.add(doc_id)

        all_docs.sort(key=lambda x: x["score"])
        return all_docs[:k]

    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []


def format_context_documents(docs: List[Dict]) -> str:
    """Format retrieved documents as context for the LLM."""
    if not docs:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for doc in docs:
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        source = metadata.get("source", "Unknown")
        section = metadata.get("section", "General")
        cleaned = content.replace("nan", "N/A").replace("MB", " MB").replace("EGP", " EGP")
        context_parts.append(f"Source: {source} | Section: {section}\n{cleaned}\n")

    return "\n".join(context_parts)
