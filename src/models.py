"""Singleton initialization for embeddings, chat model, and vector store."""

import os

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama

from src.config import CHROMA_DB_DIR, COLLECTION_NAME, EMBED_MODEL, CHAT_MODEL

_vectorstore = None
_chat_model = None
_embeddings = None


def get_embeddings():
    """Get or create embeddings instance."""
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = OllamaEmbeddings(model=EMBED_MODEL)
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            print(f"Make sure Ollama is running and the model is installed: ollama pull {EMBED_MODEL}")
            raise
    return _embeddings


def get_chat_model():
    """Get or create chat model instance."""
    global _chat_model
    if _chat_model is None:
        try:
            _chat_model = ChatOllama(
                model=CHAT_MODEL,
                temperature=0.2,
                top_p=0.9,
                num_ctx=4096,
            )
        except Exception as e:
            print(f"Error creating chat model: {e}")
            print(f"Make sure Ollama is running and the model is installed: ollama pull {CHAT_MODEL}")
            raise
    return _chat_model


def get_vectorstore():
    """Get or create vectorstore instance."""
    global _vectorstore
    if _vectorstore is None:
        try:
            if not os.path.exists(CHROMA_DB_DIR):
                raise FileNotFoundError(
                    f"Vectorstore directory not found: {CHROMA_DB_DIR}. "
                    "Please run rebuild_vectorstore.py first."
                )
            embeddings = get_embeddings()
            _vectorstore = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=CHROMA_DB_DIR,
            )
            print(f"Loaded vectorstore with {_vectorstore._collection.count()} documents")
        except Exception as e:
            print(f"Error loading vectorstore: {e}")
            raise
    return _vectorstore
