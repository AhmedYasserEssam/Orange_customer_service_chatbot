"""Application configuration constants."""

import os

# Vector store
CHROMA_DB_DIR = "chroma_db"
COLLECTION_NAME = "documents"

# Ollama models
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2"

# Data paths
CUSTOMER_DATA_PATH = os.path.join("data", "processed", "customers_stimulation.csv")
INTERNET_DATA_PATH = os.path.join("data", "raw", "internet_data.csv")

# Feature flags
APPEND_SOURCE_CITATIONS = False
