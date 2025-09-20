#!/usr/bin/env python3
"""
Setup script for Orange Customer Service Chatbot
This script will install dependencies, set up Ollama, and prepare the application.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python dependencies...")
    return run_command("pip install -r requirements.txt", "Installing requirements")

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is already installed")
            return True
    except:
        pass
    
    print("❌ Ollama is not installed")
    return False

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    if system == "windows":
        print("🔄 Installing Ollama on Windows...")
        print("Please download and install Ollama from: https://ollama.ai/download")
        print("After installation, restart your terminal and run this script again.")
        return False
    elif system == "darwin":  # macOS
        print("🔄 Installing Ollama on macOS...")
        return run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installing Ollama")
    elif system == "linux":
        print("🔄 Installing Ollama on Linux...")
        return run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installing Ollama")
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def start_ollama_service():
    """Start Ollama service"""
    print("🔄 Starting Ollama service...")
    try:
        # Start Ollama in background
        subprocess.Popen("ollama serve", shell=True)
        print("✅ Ollama service started")
        return True
    except Exception as e:
        print(f"❌ Failed to start Ollama service: {e}")
        return False

def install_ollama_models():
    """Install required Ollama models"""
    models = ["nomic-embed-text", "llama3.2"]
    
    for model in models:
        print(f"🔄 Installing Ollama model: {model}")
        if not run_command(f"ollama pull {model}", f"Installing {model}"):
            print(f"⚠️  Failed to install {model}. You can install it manually later with: ollama pull {model}")
            return False
    
    return True

def process_data():
    """Process raw data and create vectorstore"""
    print("\n📊 Processing data and creating vectorstore...")
    
    # Check if raw data exists
    raw_files = [
        "data/raw/Faqs.csv",
        "data/raw/internet_data.csv", 
        "data/raw/Orange_document.docx"
    ]
    
    missing_files = [f for f in raw_files if not os.path.exists(f)]
    if missing_files:
        print(f"⚠️  Missing raw data files: {missing_files}")
        print("Please ensure all data files are in the data/raw/ directory")
        return False
    
    # Run data processing
    if not run_command("python processing.py", "Processing raw data"):
        return False
    
    # Rebuild vectorstore
    if not run_command("python rebuild_vectorstore.py", "Building vectorstore"):
        return False
    
    return True

def create_sample_data():
    """Create sample data if it doesn't exist"""
    print("\n📝 Creating sample data...")
    
    # Create data directories
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Create sample customer data if it doesn't exist
    customer_file = "data/processed/customers_stimulation.csv"
    if not os.path.exists(customer_file):
        sample_customers = [
            "phone_number,Name,password,mobile_plan_name,monthly_mobile_data_mb,monthly_bill_mobile_amount,remaining_mobile_quota,router_plan_name,monthly_router_quota_mb,monthly_bill_router_amount,remaining_router_quota",
            "01226285272,Ahmed Yasser Essam Hussein Emad,12345678,GO 105,7250,105.0,100.0,Home DSL,250000,570.0,10000",
            "01234567890,Test User,password123,Social 50,5000,50.0,2000.0,None,0,0.0,0"
        ]
        
        with open(customer_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sample_customers))
        print("✅ Created sample customer data")
    
    # Create sample FAQ data if it doesn't exist
    faq_file = "data/raw/Faqs.csv"
    if not os.path.exists(faq_file):
        sample_faqs = [
            "question,answer,category",
            "How do I check my data usage?,You can check your data usage by dialing *888# on your mobile phone or through the Orange mobile app.,Data Usage",
            "What are the available mobile plans?,Orange offers various mobile plans including GO, Social, Video, Amazon, Play, and @Home plans with different data allowances and pricing.,Mobile Plans",
            "How can I pay my bill?,You can pay your Orange bill online through the Orange website or mobile app, at Orange stores, or through bank transfer.,Billing"
        ]
        
        with open(faq_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sample_faqs))
        print("✅ Created sample FAQ data")
    
    # Create sample internet data if it doesn't exist
    internet_file = "data/raw/internet_data.csv"
    if not os.path.exists(internet_file):
        sample_internet = [
            "Internet type,Internet Bundle Type,Internet Bundle,Price(EGP),To subscribe call,Inclusive Volume(MBS),Gift,Duration_days,Duration_hours,Internet Speed (MB)",
            "Mobile Internet,GO,GO 105,105,#222#,7250,None,30,0,4G",
            "Mobile Internet,Social,Social 50,50,#222#,5000,None,30,0,4G",
            "Mobile Internet,Video,Video 200,200,#222#,20000,None,30,0,4G"
        ]
        
        with open(internet_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sample_internet))
        print("✅ Created sample internet data")
    
    return True

def create_run_script():
    """Create a run script for easy startup"""
    if platform.system().lower() == "windows":
        script_content = """@echo off
echo Starting Orange Customer Service Chatbot...
echo Make sure Ollama is running (ollama serve)
echo.
streamlit run app.py
pause
"""
        with open("run.bat", "w") as f:
            f.write(script_content)
    else:
        script_content = """#!/bin/bash
echo "Starting Orange Customer Service Chatbot..."
echo "Make sure Ollama is running (ollama serve)"
echo ""
streamlit run app.py
"""
        with open("run.sh", "w") as f:
            f.write(script_content)
        os.chmod("run.sh", 0o755)
    
    print("✅ Created run script")

def main():
    """Main setup function"""
    print("🍊 Orange Customer Service Chatbot Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install Python requirements
    if not install_requirements():
        print("❌ Failed to install Python requirements")
        return False
    
    # Create sample data
    if not create_sample_data():
        print("❌ Failed to create sample data")
        return False
    
    # Check/Install Ollama
    if not check_ollama_installed():
        if not install_ollama():
            print("❌ Failed to install Ollama")
            print("Please install Ollama manually from https://ollama.ai/download")
            return False
    
    # Start Ollama service
    if not start_ollama_service():
        print("⚠️  Could not start Ollama service automatically")
        print("Please start it manually with: ollama serve")
    
    # Install Ollama models
    if not install_ollama_models():
        print("⚠️  Some models failed to install")
        print("You can install them manually later")
    
    # Process data
    if not process_data():
        print("❌ Failed to process data")
        return False
    
    # Create run script
    create_run_script()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Start the application:")
    if platform.system().lower() == "windows":
        print("   - Double-click run.bat, or")
        print("   - Run: streamlit run app.py")
    else:
        print("   - Run: ./run.sh, or")
        print("   - Run: streamlit run app.py")
    print("\n3. Open your browser to the URL shown in the terminal")
    print("4. Use the sample credentials:")
    print("   - Phone: 01226285272")
    print("   - Password: 12345678")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
