# Orange Customer Service Chatbot

An AI-powered customer service assistant for Orange telecommunications, built with **Streamlit**, **ChromaDB**, and **Ollama** for RAG (Retrieval-Augmented Generation).

## Features

- **RAG-Powered Responses** &mdash; ChromaDB vector retrieval + Ollama LLM
- **User Authentication** &mdash; Login with customer profile integration
- **Personalized Assistance** &mdash; Answers tailored to the user's plan and usage
- **Multi-Service Support** &mdash; Mobile plans, home internet, billing, and troubleshooting
- **Popular Questions** &mdash; Quick-access sidebar for common queries

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/download) installed and running
- At least 8 GB RAM

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama and pull models (in a separate terminal)
ollama serve
ollama pull nomic-embed-text
ollama pull llama3.2

# 3. Process data and build vector store
python scripts/processing.py
python scripts/rebuild_vectorstore.py

# 4. Launch the app
streamlit run src/app.py
```

Open `http://localhost:8501` and log in with the sample credentials:

| Field    | Value          |
|----------|----------------|
| Phone    | `01226285272`  |
| Password | `12345678`     |

## Project Structure

```
Orange_customer_service_chatbot/
├── src/                           # Application package
│   ├── app.py                     #   Streamlit UI entry point
│   ├── config.py                  #   Configuration constants
│   ├── models.py                  #   Embeddings, chat model, vectorstore
│   ├── query_analyzer.py          #   LLM-based intent classification
│   ├── retrieval.py               #   Document retrieval & context formatting
│   ├── prompts.py                 #   System prompt construction
│   ├── data_loader.py             #   Customer & internet catalog loading
│   └── chatbot.py                 #   RAG response generation
├── scripts/                       # Standalone CLI utilities
│   ├── processing.py              #   Raw data → processed JSONL
│   └── rebuild_vectorstore.py     #   Processed JSONL → ChromaDB
├── tests/                         # Test scripts
│   ├── test_chatbot.py
│   ├── test_home_internet.py
│   └── test_premier_retrieval.py
├── data/
│   ├── raw/                       # Source data files
│   │   ├── Faqs.csv
│   │   ├── internet_data.csv
│   │   └── Orange_document.docx
│   └── processed/                 # Processed outputs
│       ├── customers_stimulation.csv
│       └── documents_for_rag_final.jsonl
├── assets/
│   └── orange_logo.png
├── requirements.txt
├── .gitignore
└── README.md
```

## Configuration

Models are configured in `src/config.py`:

```python
EMBED_MODEL = "nomic-embed-text"   # Document embeddings
CHAT_MODEL  = "llama3.2"           # Chat responses
```

## Knowledge Base

The chatbot's knowledge comes from three sources processed into a ChromaDB vector store:

| Source                  | Contents                         |
|-------------------------|----------------------------------|
| `data/raw/Faqs.csv`    | Frequently asked questions       |
| `data/raw/internet_data.csv` | Internet plans and packages |
| `data/raw/Orange_document.docx` | Orange service documentation |

To refresh after editing source data:

```bash
python scripts/processing.py
python scripts/rebuild_vectorstore.py
```

## Troubleshooting

| Error                    | Fix                                                              |
|--------------------------|------------------------------------------------------------------|
| Ollama not found         | Install from https://ollama.ai/download, then `ollama serve`     |
| Model not found          | `ollama pull nomic-embed-text && ollama pull llama3.2`           |
| Vectorstore not found    | `python scripts/processing.py && python scripts/rebuild_vectorstore.py` |
| Port already in use      | `streamlit run src/app.py --server.port 8502`                    |

## Running Tests

```bash
python tests/test_chatbot.py
python tests/test_home_internet.py
python tests/test_premier_retrieval.py
```

---

**Note:** This is a demo built during an internship for educational purposes and does not use Orange's real database.
