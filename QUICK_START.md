# 🚀 Quick Start Guide - Orange Customer Service Chatbot

## ⚡ Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Ollama (Required for AI responses)
```bash
# Download and install Ollama from https://ollama.ai/download
# Then start the service:
ollama serve

# In another terminal, install the AI models:
ollama pull nomic-embed-text
ollama pull llama3.2
```

### 3. Run the Application
```bash
streamlit run app.py
```

**That's it!** Open your browser to `http://localhost:8501`

## 🔑 Login Credentials
- **Phone**: `01226285272`
- **Password**: `12345678`

## 🎯 What You Can Do

### Ask Questions About:
- Mobile internet plans and packages
- Data usage and remaining quotas
- Billing and payment options
- Technical support and troubleshooting
- Orange services and promotions

### Example Questions:
- "What are the available mobile internet plans?"
- "How do I check my data usage?"
- "What is my current mobile plan?"
- "How can I pay my bill?"
- "What are the available internet bundles?"

## 🛠️ Troubleshooting

### If you get "Ollama not found":
1. Install Ollama from https://ollama.ai/download
2. Restart your terminal
3. Run `ollama serve`

### If you get "Model not found":
1. Make sure Ollama is running: `ollama serve`
2. Install models: `ollama pull nomic-embed-text` and `ollama pull llama3.2`

### If you get "Vectorstore not found":
1. Run: `python processing.py`
2. Run: `python rebuild_vectorstore.py`

### If the app is slow:
- Close other applications to free up RAM
- Use smaller models (e.g., `llama3.2:7b`)

## 📁 Project Files

- `app.py` - Main Streamlit application
- `chat_prompts.py` - AI chatbot logic
- `processing.py` - Data processing script
- `rebuild_vectorstore.py` - Vector database builder
- `setup.py` - Automated setup script
- `test_chatbot.py` - Test the chatbot functionality

## 🔧 Configuration

To change AI models, edit `chat_prompts.py`:
```python
EMBED_MODEL = "nomic-embed-text"  # For document embeddings
CHAT_MODEL = "llama3.2"           # For chat responses
```

## 📊 Data Sources

The chatbot learns from:
- `data/raw/Faqs.csv` - Frequently asked questions
- `data/raw/internet_data.csv` - Internet plans and packages
- `data/raw/Orange_document.docx` - Orange documentation
- `data/processed/customers_stimulation.csv` - Customer profiles

## 🆘 Need Help?

1. Check the terminal for error messages
2. Run `python test_chatbot.py` to test functionality
3. Review `INSTALLATION.md` for detailed setup instructions
4. Check `README.md` for complete documentation

---

**Note**: This is a demonstration application. For production use, ensure proper security measures and integration with real Orange systems.
