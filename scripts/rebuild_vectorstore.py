#!/usr/bin/env python3
"""
Rebuild or load the Chroma vectorstore from processed JSONL documents.
Safe to import into other scripts for RAG/chatbot usage.
"""

import os
import json
import shutil
from typing import List, Dict

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document as LCDocument

# --- Config ---
PROCESSED_PATH = os.path.join("data", "processed", "documents_for_rag_final.jsonl")
PROCESSED_FALLBACKS = [
    os.path.join("data", "processed", "documents_for_rag.jsonl"),
]
CHROMA_DB_DIR = "chroma_db"
COLLECTION = "documents"
EMBED_MODEL = "nomic-embed-text"


def flatten_metadata(meta: Dict) -> Dict:
    """
    Convert nested dict values and lists into JSON strings to make them compatible with Chroma.
    """
    flat = {}
    for k, v in meta.items():
        if isinstance(v, (dict, list)):
            flat[k] = json.dumps(v)
        else:
            flat[k] = v
    return flat


def load_jsonl(path: str) -> List[Dict]:
    """
    Load JSONL file and return list of dicts.
    """
    docs: List[Dict] = []
    if not os.path.exists(path):
        return docs

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return docs


def get_vectorstore() -> Chroma:
    """
    Rebuilds or loads the Chroma vectorstore from processed documents.
    Returns the Chroma vectorstore instance.
    """
    target_path = PROCESSED_PATH
    if not os.path.exists(target_path):
        # Try fallbacks
        for fb in PROCESSED_FALLBACKS:
            if os.path.exists(fb):
                target_path = fb
                print(f"⚠️ Using fallback processed file: {fb}")
                break
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Processed file not found: {PROCESSED_PATH}")

    print("Loading processed documents...")
    rows = load_jsonl(target_path)
    print(f"Loaded {len(rows)} documents")

    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    # Remove existing DB to rebuild
    if os.path.exists(CHROMA_DB_DIR):
        print("Clearing existing Chroma directory to rebuild...")
        shutil.rmtree(CHROMA_DB_DIR, ignore_errors=True)
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)

    print("Building vectorstore...")
    vectorstore = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR,
    )

    # Convert rows to LangChain Documents
    lc_docs: List[LCDocument] = []
    for r in rows:
        page_content = r.get("content", "")
        metadata = r.get("metadata", {}) or {}
        # Keep helpful fields in metadata
        metadata.update({
            "section": r.get("section"),
            "title": r.get("title"),
            "id": r.get("id"),
        })
        metadata = flatten_metadata(metadata)
        if page_content:
            lc_docs.append(LCDocument(page_content=page_content, metadata=metadata))

    if lc_docs:
        print(f"Adding {len(lc_docs)} documents to vectorstore...")
        vectorstore.add_documents(lc_docs)
    else:
        print("❌ No documents to index.")

    print(f"Vectorstore ready at: {CHROMA_DB_DIR}")
    print(f"Total documents in vectorstore: {vectorstore._collection.count()}")

    return vectorstore


if __name__ == "__main__":
    # For standalone rebuild
    get_vectorstore()
