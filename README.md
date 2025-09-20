# 🍊 Orange Customer Service Chatbot

An intelligent AI-powered customer service assistant for Orange telecommunications services, built with Streamlit, ChromaDB, and Ollama for RAG (Retrieval-Augmented Generation).

## ✨ Features

- **Intelligent Chat Interface**: Modern, responsive chat UI with Orange branding
- **RAG-Powered Responses**: Uses ChromaDB for document retrieval and Ollama for LLM responses
- **User Authentication**: Secure login system with customer profile integration
- **Personalized Assistance**: Tailored responses based on user's plan and usage
- **Multi-Service Support**: Handles mobile plans, internet services, billing, and technical support
- **Real-time Data**: Shows current usage, remaining quotas, and billing information
- **Popular Questions**: Quick access to frequently asked questions

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Ollama (for running LLM models locally)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Orange_customer_service
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```
   
   This will:
   - Install all Python dependencies
   - Install and configure Ollama
   - Download required AI models
   - Process sample data
   - Create the vector database

3. **Start the application**
   ```bash
   # Make sure Ollama is running
   ollama serve
   
   # In another terminal, start the app
   streamlit run app.py
   ```

4. **Access the application**
   - Open your browser to the URL shown in the terminal (usually http://localhost:8501)
   - Use the sample credentials:
     - Phone: `01226285272`
     - Password: `12345678`

## 🛠️ Manual Setup

If the automated setup doesn't work, follow these steps:

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install and Setup Ollama

**Windows:**
- Download from https://ollama.ai/download
- Install and restart your terminal

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 3. Start Ollama and Install Models
```bash
# Start Ollama service
ollama serve

# In another terminal, install required models
ollama pull nomic-embed-text
ollama pull llama3.2
```

### 4. Process Data
```bash
# Process raw data
python processing.py

# Build vector database
python rebuild_vectorstore.py
```

### 5. Run the Application
```bash
streamlit run app.py
```

## 📁 Project Structure

```
Orange_customer_service/
├── app.py                 # Main Streamlit application
├── chat_prompts.py        # RAG chatbot logic
├── processing.py          # Data processing script
├── rebuild_vectorstore.py # Vector database builder
├── setup.py              # Automated setup script
├── requirements.txt      # Python dependencies
├── data/
│   ├── raw/              # Raw data files
│   │   ├── Faqs.csv
│   │   ├── internet_data.csv
│   │   └── Orange_document.docx
│   └── processed/        # Processed data
│       ├── customers_stimulation.csv
│       └── documents_for_rag.jsonl
├── chroma_db/            # Vector database (created automatically)
└── orange_logo.png       # Orange logo
```

## 🔧 Configuration

### Models
The application uses two Ollama models:
- **nomic-embed-text**: For document embeddings
- **llama3.2**: For chat responses

You can change these in `chat_prompts.py`:
```python
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2"
```

### Customer Data
Customer data is stored in `data/processed/customers_stimulation.csv`. You can add more customers by following the same format.

### Knowledge Base
The chatbot's knowledge comes from:
- FAQ data (`data/raw/Faqs.csv`)
- Internet plans (`data/raw/internet_data.csv`)
- Orange documentation (`data/raw/Orange_document.docx`)

## 🎯 Usage

### For Customers
1. **Login**: Use your phone number and password
2. **Ask Questions**: Type any question about Orange services
3. **Quick Actions**: Use popular questions in the sidebar
4. **View Information**: Check your data usage, billing, and plan details

### For Developers
1. **Add New Data**: Place new CSV/DOCX files in `data/raw/`
2. **Update Knowledge**: Run `python processing.py` to process new data
3. **Rebuild Database**: Run `python rebuild_vectorstore.py` to update the vector store
4. **Customize Responses**: Modify prompts in `chat_prompts.py`

## 🔍 Troubleshooting

### Common Issues

**"Ollama not found"**
- Make sure Ollama is installed and running
- Check if `ollama serve` is running in the background

**"Model not found"**
- Install required models: `ollama pull nomic-embed-text` and `ollama pull llama3.2`

**"Vectorstore not found"**
- Run `python rebuild_vectorstore.py` to create the vector database

**"No data found"**
- Ensure data files exist in `data/raw/` directory
- Run `python processing.py` to process the data

**Port already in use**
- Streamlit runs on port 8501 by default
- Use `streamlit run app.py --server.port 8502` to use a different port

### Performance Tips

- **Memory**: Ensure you have at least 8GB RAM for smooth operation
- **Models**: Larger models provide better responses but require more resources
- **Data**: More data in the knowledge base improves response quality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

## 🆘 Support

For technical support or questions:
- Check the troubleshooting section above
- Review the logs in the terminal
- Contact the development team

## 🔮 Future Enhancements

- [ ] Voice input/output support
- [ ] Multi-language support
- [ ] Integration with real Orange APIs
- [ ] Advanced analytics and reporting
- [ ] Mobile app version
- [ ] Real-time data synchronization

---

**Note**: This is a demo, not on orange's real database
