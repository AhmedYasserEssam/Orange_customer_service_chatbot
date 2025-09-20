# 🚀 Installation Guide - Orange Customer Service Chatbot

This guide will help you set up and run the Orange Customer Service Chatbot on your local machine.

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8 or higher** installed
- **Git** installed
- **At least 8GB RAM** (for running AI models)
- **Stable internet connection** (for downloading models)

## 🎯 Quick Installation (Recommended)

### Step 1: Download and Setup
```bash
# Clone or download the project
cd Orange_customer_service

# Run the automated setup
python setup.py
```

The setup script will automatically:
- Install all Python dependencies
- Install Ollama (if not present)
- Download required AI models
- Process sample data
- Create the vector database

### Step 2: Start the Application
```bash
# Start Ollama service (in one terminal)
ollama serve

# Start the chatbot (in another terminal)
streamlit run app.py
```

### Step 3: Access the Application
- Open your browser to `http://localhost:8501`
- Use sample credentials:
  - **Phone**: `01226285272`
  - **Password**: `12345678`

## 🔧 Manual Installation

If the automated setup doesn't work, follow these manual steps:

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Ollama

**Windows:**
1. Download from https://ollama.ai/download
2. Run the installer
3. Restart your terminal

**macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 3: Start Ollama and Install Models
```bash
# Start Ollama service
ollama serve

# In another terminal, install required models
ollama pull nomic-embed-text
ollama pull llama3.2
```

### Step 4: Process Data
```bash
# Process raw data into structured format
python processing.py

# Build the vector database
python rebuild_vectorstore.py
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "Ollama not found" Error
**Problem**: The system can't find Ollama
**Solution**:
```bash
# Check if Ollama is installed
ollama --version

# If not installed, install it
# Windows: Download from https://ollama.ai/download
# macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. "Model not found" Error
**Problem**: Required AI models are not installed
**Solution**:
```bash
# Make sure Ollama is running
ollama serve

# Install required models
ollama pull nomic-embed-text
ollama pull llama3.2
```

#### 3. "Vectorstore not found" Error
**Problem**: The vector database doesn't exist
**Solution**:
```bash
# Process the data first
python processing.py

# Then build the vectorstore
python rebuild_vectorstore.py
```

#### 4. "Port already in use" Error
**Problem**: Port 8501 is already in use
**Solution**:
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

#### 5. "Permission denied" Error (Linux/macOS)
**Problem**: Scripts don't have execute permissions
**Solution**:
```bash
chmod +x start_app.sh
chmod +x setup.py
```

#### 6. Memory Issues
**Problem**: Application crashes due to insufficient memory
**Solution**:
- Close other applications to free up RAM
- Use smaller models (e.g., `llama3.2:7b` instead of `llama3.2:70b`)
- Increase virtual memory/swap space

#### 7. Slow Performance
**Problem**: Application is slow to respond
**Solution**:
- Ensure you have at least 8GB RAM
- Close unnecessary applications
- Use SSD storage for better I/O performance
- Consider using GPU acceleration (if available)

### Performance Optimization

#### For Better Performance:
1. **Use SSD Storage**: Faster data access
2. **Increase RAM**: More memory for model loading
3. **Close Background Apps**: Free up system resources
4. **Use Smaller Models**: Faster but less accurate responses

#### Model Size Options:
- **Small**: `llama3.2:7b` (faster, less accurate)
- **Medium**: `llama3.2:13b` (balanced)
- **Large**: `llama3.2:70b` (slower, more accurate)

To change model size, edit `chat_prompts.py`:
```python
CHAT_MODEL = "llama3.2:7b"  # Change this line
```

## 🔍 Verification

### Test the Installation
```bash
# Run the test script
python test_chatbot.py
```

This will test:
- Basic chatbot functionality
- Customer data loading
- User profile integration

### Check System Status
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check Ollama status
ollama list

# Check if models are running
ollama ps
```

## 📱 Using the Application

### Login
- Use the sample credentials provided
- Or add your own customer data to `data/processed/customers_stimulation.csv`

### Features
- **Chat Interface**: Ask questions about Orange services
- **Popular Questions**: Quick access to common queries
- **User Profile**: View your plan and usage information
- **Data Usage**: Check remaining quotas and billing

### Sample Questions
- "What are the available mobile internet plans?"
- "How do I check my data usage?"
- "What is my current mobile plan?"
- "How can I pay my bill?"
- "What are the available internet bundles?"

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** in the terminal for error messages
2. **Verify all prerequisites** are installed correctly
3. **Run the test script** to identify specific problems
4. **Check the troubleshooting section** above
5. **Review the README.md** for additional information

## 🔄 Updating the Application

To update the application:

1. **Pull latest changes** (if using Git)
2. **Update dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
3. **Rebuild vectorstore** (if data changed):
   ```bash
   python rebuild_vectorstore.py
   ```
4. **Restart the application**

## 📊 System Requirements

### Minimum Requirements:
- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 8GB
- **Storage**: 10GB free space
- **CPU**: 4 cores

### Recommended Requirements:
- **OS**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **RAM**: 16GB or more
- **Storage**: 20GB free space (SSD preferred)
- **CPU**: 8 cores or more
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster inference)

---

**Note**: This application is designed for demonstration purposes. For production use, ensure proper security measures, data validation, and integration with real Orange systems.
