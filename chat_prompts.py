#!/usr/bin/env python3
"""
Orange Customer Service Chatbot with RAG (Retrieval-Augmented Generation)
Uses ChromaDB for document retrieval and Ollama for LLM responses.
"""

import os
import json
import csv
from typing import List, Dict, Optional, Any
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    from langchain_chroma import Chroma
    from langchain_ollama import OllamaEmbeddings, ChatOllama
    from langchain.schema import Document as LCDocument
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser
    from langchain.chains import RetrievalQA
    from langchain.memory import ConversationBufferWindowMemory
except ImportError as e:
    print(f"Warning: Missing required packages. Please install: {e}")
    print("Run: pip install -r requirements.txt")

# Configuration
CHROMA_DB_DIR = "chroma_db"
COLLECTION_NAME = "documents"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2"  # or "llama3.1" or "mistral" - whatever you have installed
CUSTOMER_DATA_PATH = "data/processed/customers_stimulation.csv"

# Global variables for caching
_vectorstore = None
_chat_model = None
_embeddings = None
_customer_data = None


def get_embeddings():
    """Get or create embeddings instance"""
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = OllamaEmbeddings(model=EMBED_MODEL)
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            print("Make sure Ollama is running and the model is installed:")
            print(f"ollama pull {EMBED_MODEL}")
            raise
    return _embeddings


def get_chat_model():
    """Get or create chat model instance"""
    global _chat_model
    if _chat_model is None:
        try:
            _chat_model = ChatOllama(
                model=CHAT_MODEL,
                temperature=0.7,
                top_p=0.9,
                num_ctx=4096
            )
        except Exception as e:
            print(f"Error creating chat model: {e}")
            print("Make sure Ollama is running and the model is installed:")
            print(f"ollama pull {CHAT_MODEL}")
            raise
    return _chat_model


def get_vectorstore():
    """Get or create vectorstore instance"""
    global _vectorstore
    if _vectorstore is None:
        try:
            if not os.path.exists(CHROMA_DB_DIR):
                print("Vectorstore not found. Please run rebuild_vectorstore.py first.")
                raise FileNotFoundError(f"Vectorstore directory not found: {CHROMA_DB_DIR}")
            
            embeddings = get_embeddings()
            _vectorstore = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=CHROMA_DB_DIR,
            )
            print(f"✅ Loaded vectorstore with {_vectorstore._collection.count()} documents")
        except Exception as e:
            print(f"Error loading vectorstore: {e}")
            raise
    return _vectorstore


def load_customer_data():
    """Load customer data from CSV"""
    global _customer_data
    if _customer_data is None:
        try:
            _customer_data = []
            if os.path.exists(CUSTOMER_DATA_PATH):
                with open(CUSTOMER_DATA_PATH, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    _customer_data = list(reader)
            print(f"✅ Loaded {len(_customer_data)} customer records")
        except Exception as e:
            print(f"Error loading customer data: {e}")
            _customer_data = []
    return _customer_data


def create_system_prompt(user_profile: Optional[Dict] = None) -> str:
    """Create system prompt based on user profile and context"""
    
    base_prompt = """You are a helpful Orange Customer Service Assistant. Be direct, informative, and concise.

**CRITICAL RULES:**
- PROVIDE USEFUL INFORMATION IMMEDIATELY - Don't ask questions first
- Give specific details, prices, and options right away
- Only ask 1 clarifying question if absolutely necessary
- Be helpful first, ask questions second
- Keep responses to 2-4 sentences maximum

**Orange Services Context:**
- Orange offers COMPREHENSIVE mobile and home services with multiple service plans and bundles

**1. TARIFF PLANS (Main Mobile Service Plans):**
- **PREMIER Plans** (Monthly mobile service plans with minutes, data, and features):
  - PREMIER 400: 13GB + 2,500 min for 400 EGP/month
  - PREMIER 550: 16GB + 3,500 min for 550 EGP/month  
  - PREMIER 750: 25GB + 5,000 min for 750 EGP/month
  - Features: Family lines, home internet discounts, roaming buckets, installment programs
- **ALO Tariffs** (Lower-cost alternative tariff plans):
  - Migration via #100# or #0#
  - Features: Favorite numbers (1 EGP/month each), WhatsApp All Day (20MB daily)
  - Can migrate through #100#, #0#, 400, My Orange App, or website
  - Alternative tariff structure with different pricing than PREMIER
  - Note: ALO tariffs have different pricing structure - contact 110 for current ALO plan details

**2. MOBILE INTERNET BUNDLES (Data-Only Packages):**
- **GO Bundles** (Standard data bundles - 28-day validity):
  - GO 20: 1GB for 20 EGP
  - GO 32: 1.75GB for 32 EGP
  - GO 50: 3.25GB for 50 EGP
  - GO 80: 5.5GB for 80 EGP
  - GO 105: 7.25GB for 105 EGP
  - GO 155: 11.5GB for 155 EGP
  - GO 260: 20GB for 260 EGP
  - GO 390: 31.5GB for 390 EGP
  - GO 520: 49GB for 520 EGP
  - All include: 30 Extra Minutes to Orange Numbers + FREEMAX bonus

- **GO Social Bundles** (Social media focused):
  - GO Social: 100MB for 30 hours at 1.25 EGP
  - Covers: Facebook, WhatsApp, Instagram, Twitter, Snapchat

- **GO Video Bundles** (Video streaming optimized):
  - GO Video Daily: 200MB for 24 hours at 2.5 EGP
  - GO Video Monthly: 450MB for 28 days at 5.5 EGP
  - GO Video Max: 4.5GB for 28 days at 45 EGP
  - Covers: YouTube, TikTok, Shahid, Orange TV, Netflix, BeIN CONNECT, WATCH IT

- **GO By Hour Bundles** (Hourly unlimited data):
  - GO By Hour Social & Maps: 0.5 hours for 2 EGP, 1 hour for 3 EGP, 2 hours for 4.5 EGP
  - GO By Hour Video & Music: Similar pricing structure
  - Covers: TikTok, Instagram, Snapchat, Twitter, Facebook, WhatsApp, Google Maps, Uber, SWVL, YouTube, TOD, Shahid, Netflix, Orange TV, SoundCloud, Spotify

- **GO Play Bundles** (Gaming optimized):
  - GO Play Daily: 100MB for 24 hours at 1.25 EGP
  - GO Play Weekly: 200MB + 75MB weekend only for 7 days at 4 EGP
  - GO Play Monthly: 1000MB + 300MB weekend only for 28 days at 13 EGP

- **GO TikTok Bundles** (TikTok specific):
  - GO TikTok: 450MB for 28 days at 6.5 EGP

- **GO @Home Bundles** (Home internet solutions):
  - GO @Home: 1000MB for 28 days at 13 EGP
  - GO @Home Max: 4500MB for 28 days at 45 EGP

**3. SPECIAL PLANS:**
- **FREEmax Plans** (Credit-based plans with units):
  - FREEmax 40: 1,575 Units (300MB Facebook, 50MB WhatsApp, 25 min Orange) for 40 EGP
  - FREEmax 45: 1,775 Units (300MB Facebook, 50MB WhatsApp, 25 min Orange, Group Minutes) for 45 EGP
  - FREEmax 65: 3,000 Units (600MB Facebook, 100MB WhatsApp, 50 min Orange, Group Minutes) for 65 EGP
  - FREEmax 90: 4,450 Units (1,000MB Facebook, 100MB WhatsApp, 50 min Orange, Group Minutes) for 90 EGP
  - FREEmax 130: 7,825 Units (1,500MB Facebook, 100MB WhatsApp, 225 min Orange, Group Minutes) for 130 EGP
  - FREEmax 195: 13,050 Units (3,000MB Facebook, 100MB WhatsApp, 350 min Orange, Group Minutes) for 195 EGP
  - FREEmax 260: 20,050 Units (5,000MB Facebook, 200MB WhatsApp, 30 Extra Minutes) for 260 EGP

**4. HOME INTERNET SERVICES:**
- **Home DSL**: Uses existing phone line, no additional line needed
- **Home Wireless**: Wireless home internet solution
- Different pricing and features than mobile bundles

**Subscription Methods:**
- Mobile bundles: #222# or Orange website/app
- Tariff migration: #100#, #0#, 400, My Orange App, or website
- Special features: #225# (GO Bonus), #226# (GO Units), #227# (GO Share)

**Important**: GO bundles are MOBILE internet bundles, NOT home internet services. When customers ask about GO bundles, they are asking about mobile internet plans."""

    if user_profile:
        customer_info = f"""
**Current Customer Information:**
- Name: {user_profile.get('Name', 'Customer')}
- Mobile Plan: {user_profile.get('mobile_plan_name', 'Not specified')}
- Monthly Data: {user_profile.get('monthly_mobile_data_mb', 'Not specified')} MB
- Monthly Bill: {user_profile.get('monthly_bill_mobile_amount', 'Not specified')} EGP
- Remaining Quota: {user_profile.get('remaining_mobile_quota', 'Not specified')} MB
- Router Plan: {user_profile.get('router_plan_name', 'Not specified')}
- Router Data: {user_profile.get('monthly_router_quota_mb', 'Not specified')} MB
- Router Bill: {user_profile.get('monthly_bill_router_amount', 'Not specified')} EGP
- Remaining Router Quota: {user_profile.get('remaining_router_quota', 'Not specified')} MB

Use this information to provide personalized assistance when relevant."""

        base_prompt += customer_info

    return base_prompt


def get_relevant_documents(query: str, k: int = 5) -> List[Dict]:
    """Retrieve relevant documents from vectorstore"""
    try:
        vectorstore = get_vectorstore()
        
        # Try multiple search strategies for better results
        search_queries = [query]
        
        # Add variations for different types of plans
        if any(term in query.lower() for term in ['internet', 'bundle', 'tariff', 'plan', 'package', 'service']):
            # Check if asking about TARIFF PLANS (main mobile service plans)
            if any(term in query.lower() for term in ['tariff', 'prepaid', 'postpaid', 'alo', 'premier']):
                search_queries.extend([
                    "tariff plans prepaid postpaid",
                    "ALO tariffs PREMIER plans",
                    "mobile service plans monthly fees",
                    "PREMIER 400 PREMIER 550 PREMIER 750",
                    "ALO tariff migration favorite numbers",
                    "mobile plan monthly fees minutes data"
                ])
            # Check if asking about GO bundles specifically
            elif any(term in query.lower() for term in ['go', 'mobile', 'phone', 'data', 'mb', 'gb', 'internet']):
                search_queries.extend([
                    "mobile internet plans packages pricing",
                    "GO Social Video Amazon Play plans",
                    "mobile data packages offers",
                    "GO 20 GO 32 GO 50 GO 80 GO 105 GO 155 GO 260 GO 390 GO 520",
                    "Social Video Amazon Play bundles",
                    "mobile internet data quota MB pricing",
                    "GO By Hour Social Maps Video Music",
                    "GO Video Daily Monthly Max",
                    "GO Social bundles",
                    "GO Amazon bundles",
                    "GO Play bundles",
                    "GO TikTok bundles",
                    "GO @Home bundles",
                    "mobile internet bundle types alternatives"
                ])
            # Check if asking about special plans
            elif any(term in query.lower() for term in ['freemax', 'kart', 'special', 'unlimited']):
                search_queries.extend([
                    "FREEmax plans unlimited data",
                    "Kart El Kebir plans",
                    "special promotional plans",
                    "unlimited data packages"
                ])
            # Check if asking about home internet specifically
            elif any(term in query.lower() for term in ['home', 'dsl', 'wireless', 'house', 'office']):
                search_queries.extend([
                    "Home DSL internet plans",
                    "Home Wireless internet plans",
                    "home internet packages pricing",
                    "DSL wireless home internet"
                ])
            # General search
            else:
                search_queries.extend([
                    "mobile internet plans packages pricing",
                    "internet bundles data quota pricing",
                    "GO Social Video Amazon Play plans",
                    "mobile data packages offers",
                    "Home DSL internet plans",
                    "all Orange service plans bundles"
                ])
        
        all_docs = []
        seen_ids = set()
        
        for search_query in search_queries:
            docs = vectorstore.similarity_search_with_score(search_query, k=k)
            
            for doc, score in docs:
                doc_id = doc.metadata.get("id", "")
                if doc_id not in seen_ids:
                    all_docs.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score
                    })
                    seen_ids.add(doc_id)
        
        # Sort by score and return top k
        all_docs.sort(key=lambda x: x["score"], reverse=False)  # Lower score = better match
        return all_docs[:k]
        
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []


def format_context_documents(docs: List[Dict]) -> str:
    """Format retrieved documents as context for the LLM"""
    if not docs:
        return "No relevant information found in the knowledge base."
    
    context_parts = []
    for i, doc in enumerate(docs, 1):
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        source = metadata.get("source", "Unknown")
        section = metadata.get("section", "General")
        
        # Clean up the content for better readability
        cleaned_content = content.replace("nan", "N/A").replace("MB", " MB").replace("EGP", " EGP")
        
        context_parts.append(f"**Reference {i}** (Source: {source}, Section: {section}):\n{cleaned_content}\n")
    
    return "\n".join(context_parts)


def get_fast_response(
    user_input: str,
    history: Optional[List[Dict]] = None,
    user_profile: Optional[Dict] = None,
    customer_data: Optional[List[Dict]] = None
) -> str:
    """
    Generate a response using RAG (Retrieval-Augmented Generation)
    
    Args:
        user_input: The user's question/input
        history: Previous conversation history
        user_profile: Current user's profile information
        customer_data: All customer data (for additional context)
    
    Returns:
        Generated response string
    """
    try:
        # Handle simple greetings naturally
        user_input_lower = user_input.lower().strip()
        if user_input_lower in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']:
            if user_profile:
                name = user_profile.get('Name', 'Customer')
                return f"Hello {name}! 👋 How can I help you today?"
            else:
                return "Hello! 👋 Welcome to Orange Customer Service. How can I assist you today?"
        
        # Handle bundles with both minutes and data questions (check this first)
        if any(phrase in user_input_lower for phrase in ['bundles that offers both minutes and internet', 'bundles with both minutes and data', 'plans with minutes and data', 'both minutes and internet', 'minutes and internet quota']):
            return """GO bundles are DATA-ONLY packages - they don't include minutes.

For plans with BOTH minutes and internet, you need TARIFF PLANS:

**PREMIER Plans (Monthly service plans with minutes + data):**
- PREMIER 400: 13GB + 2,500 min for 400 EGP/month
- PREMIER 550: 16GB + 3,500 min for 550 EGP/month  
- PREMIER 750: 25GB + 5,000 min for 750 EGP/month

**ALO Tariffs (Alternative tariff plans):**
- Different pricing structure with minutes and data
- Contact 110 for current ALO plan details

These are your main mobile service plans that include both calling minutes and internet data. GO bundles are additional data packages you can add on top of these plans."""
        
        # Handle recommendation questions (check this first)
        elif any(phrase in user_input_lower for phrase in ['recommend', 'bigger', 'more data', 'upgrade', 'suggest', 'finished my plan', 'ran out', 'used up', 'finished', 'very fast', 'quickly']):
            return get_plan_recommendations(user_profile, user_input)
        
        # Handle current plan questions (check this before "what is" questions)
        elif any(phrase in user_input_lower for phrase in ['my current', 'current plan', 'my plan', 'my bundle', 'my internet bundle', 'what is my', 'show my', 'my mobile plan', 'usage']):
            return get_plan_recommendations(user_profile, user_input)
        
        # Handle common questions more naturally
        elif any(phrase in user_input_lower for phrase in ['what are', 'tell me about', 'show me', 'what is']):
            # Let the RAG system handle these with natural responses
            pass
        elif user_input_lower in ['thanks', 'thank you', 'okay thank you', 'ok thanks', 'bye', 'goodbye']:
            return "You're welcome! 😊 Is there anything else I can help you with?"
        
        # Handle casual conversation questions
        elif any(phrase in user_input_lower for phrase in ['how are you', 'how are you doing', 'how do you do', 'how\'s it going']):
            if user_profile:
                name = user_profile.get('Name', 'Customer')
                return f"I'm doing great, thank you for asking! 😊 How can I help you today, {name}?"
            else:
                return "I'm doing great, thank you for asking! 😊 How can I help you today?"
        
        
        # Handle technical issues that need immediate escalation
        elif any(phrase in user_input_lower for phrase in ['tried', 'checked', 'restarted', 'not working', 'still not working']) and any(phrase in user_input_lower for phrase in ['router', 'internet', 'app', 'connection']):
            return "I understand you've tried the basic troubleshooting steps and it's still not working. Please contact our technical support team at 110 for immediate assistance. They have specialized tools and can help resolve your issue quickly."
        
        # Handle conversation flow - avoid repeating greetings
        elif user_input_lower in ['hello', 'hi', 'hey'] and history and len(history) > 0:
            # If there's conversation history, don't repeat the greeting
            if user_profile:
                name = user_profile.get('Name', 'Customer')
                return f"Hi {name}! What can I help you with?"
            else:
                return "Hi! What can I help you with?"
        
        # Get the chat model
        chat_model = get_chat_model()
        
        # Create system prompt
        system_prompt = create_system_prompt(user_profile)
        
        # Retrieve relevant documents - get more for better coverage
        relevant_docs = get_relevant_documents(user_input, k=8)
        context = format_context_documents(relevant_docs)
        
        # Build conversation history
        messages = [SystemMessage(content=system_prompt)]
        
        if history:
            for exchange in history[-3:]:  # Last 3 exchanges for context
                if exchange.get("user"):
                    messages.append(HumanMessage(content=exchange["user"]))
                if exchange.get("assistant"):
                    messages.append(AIMessage(content=exchange["assistant"]))
        
        # Add current user input
        messages.append(HumanMessage(content=user_input))
        
        # Create the prompt template with conversation context
        conversation_context = ""
        if history:
            conversation_context = "\n**Previous Conversation Context:**\n"
            for exchange in history[-5:]:  # Last 5 exchanges for better context
                if exchange.get("user"):
                    conversation_context += f"User: {exchange['user']}\n"
                if exchange.get("assistant"):
                    # Truncate long assistant responses to keep context focused
                    assistant_msg = exchange['assistant']
                    if len(assistant_msg) > 200:
                        assistant_msg = assistant_msg[:200] + "..."
                    conversation_context += f"Assistant: {assistant_msg}\n"
            conversation_context += "\n**IMPORTANT: Continue the conversation based on the context above. If the user is asking about specific plans or options mentioned in the conversation, focus on those specific options.**\n"
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"""Context Information:
{context}

{conversation_context}User Question: {{question}}

**CRITICAL: PROVIDE USEFUL INFORMATION IMMEDIATELY - DON'T ASK TOO MANY QUESTIONS**

**Response Rules:**
1. **ANSWER THE QUESTION DIRECTLY** - Give specific, useful information right away
2. **NO EXCESSIVE QUESTIONS** - Only ask 1 clarifying question if absolutely necessary
3. **BE HELPFUL FIRST** - Provide information, then ask if they need more details
4. **GIVE EXAMPLES** - Show specific plans, prices, and details from the context
5. **BE CONCISE** - 2-4 sentences maximum for most responses
6. **REMEMBER CONTEXT** - If the user is asking for help choosing from options you just provided, focus on those specific options

**For All Service Plans Questions:**
- IMMEDIATELY provide comprehensive information about all Orange services
- Show TARIFF PLANS (PREMIER plans AND ALO tariffs) with monthly fees, data, and minutes
- Show MOBILE INTERNET BUNDLES (GO, Social, Video, By Hour, Play, TikTok, @Home)
- Show SPECIAL PLANS (FREEmax plans with units and credit balance)
- Show HOME INTERNET SERVICES (DSL, Wireless)
- Organize by service type with specific prices and features
- IMPORTANT: ALO tariffs belong under TARIFF PLANS, not SPECIAL PLANS
- IMPORTANT: FREEmax plans are credit-based with units, not unlimited data
- Only ask "Which service type interests you?" or "Need more details about any specific plan?"

**For Tariff Plans Questions:**
- IMMEDIATELY show PREMIER plans and ALO tariffs with monthly fees, data, and minutes
- Show specific examples: PREMIER 400 (13GB + 2,500 min for 400 EGP), etc.
- Mention features like family lines, discounts, roaming
- Only ask "Which plan interests you?" or "Need more details about migration?"

**For Mobile Internet Bundles:**
- IMMEDIATELY list all GO bundle types with prices and data quotas
- Show GO bundles, Social, Video, Amazon, Play, TikTok, @Home, By Hour
- Show specific examples from the context
- IMPORTANT: GO bundles are DATA-ONLY packages, they don't include minutes
- If user asks for bundles with both minutes and data, direct them to TARIFF PLANS (PREMIER/ALO)
- Only ask "Which one interests you?" or "Need more details about any of these?"

**For Monthly Mobile Bundles:**
- IMMEDIATELY show both GO bundles (28-day = monthly) and TARIFF PLANS (true monthly billing)
- Show GO bundles: GO 20 (1GB for 20 EGP), GO 50 (3.25GB for 50 EGP), GO 105 (7.25GB for 105 EGP), etc.
- Show PREMIER plans: 400 EGP (13GB + 2,500 min), 550 EGP (16GB + 3,500 min), 750 EGP (25GB + 5,000 min)
- Explain: GO bundles = monthly data packages (28-day validity), PREMIER/ALO = monthly service plans with minutes + data
- Only ask "Which monthly plan interests you?" or "Need more details about GO bundles or tariff plans?"

**For Social Media Bundles:**
- IMMEDIATELY show GO Social bundle details (100 MB for 30 hours at 1 EGP)
- Mention what apps are included
- Only ask if they want to subscribe

**For Special Plans:**
- IMMEDIATELY show FREEmax plans with units and credit balance
- Mention credit-based system with Facebook/WhatsApp data and minutes
- Only ask "Which special plan interests you?"

**For Cheaper/Low-Cost Questions:**
- IMMEDIATELY show the most affordable options from each category
- For mobile bundles: Show GO 20 (1GB for 20 EGP), GO Social (100MB for 1.25 EGP)
- For tariff plans: Show PREMIER 400 (400 EGP) as the cheapest PREMIER option, mention ALO tariffs as alternative (contact 110 for details)
- For special plans: Show FREEmax 40 (40 EGP) as the cheapest option
- Be accurate with pricing - don't make up prices or non-existent plans
- Only ask "Which budget option interests you?" or "Need more details about any of these?"

**For iPhone/Mobile Phone Purchase Questions:**
- IMMEDIATELY show available installment options and phone deals
- Mention installment plans up to 36 months at 0% interest through "Aman" or FiN/Ace
- Show specific phone offers available (Samsung Galaxy A36 5G, OPPO Find N3, etc.)
- If asking about iPhone specifically, mention that Orange offers installment plans for various phones including iPhones
- Be accurate about specific phone models - don't mix up different brands
- IMPORTANT: Don't make up specific prices for phones - contact 110 or visit Orange stores for current pricing
- For cash purchases, mention that full payment is required upfront
- Mention easy installment methods for handsets, accessories, or tablets
- Only ask "Which phone model interests you?" or "Need more details about installment options?"

**For "What is" Questions:**
- IMMEDIATELY answer the specific question being asked
- If asking "what is tariff plans?" - explain that tariff plans are main mobile service plans with monthly fees, minutes, data, and features
- If asking "what is internet bundles?" - explain that internet bundles are data-only packages for additional data
- Be direct and educational - explain the concept clearly
- Only ask "Need more details about any specific type?" or "Would you like to see examples?"

**For Current Plan Questions:**
- If user asks about their current plan, use their actual profile data
- Show their main plan (mobile_plan_name) with monthly data, cost, and remaining quota
- Show their internet bundle (internet_bundle_name) with data and price
- Don't make up or guess their current plan details
- If profile data is missing, direct them to check via #222# or contact 110

**For Bundles with Both Minutes and Data:**
- IMMEDIATELY clarify that GO bundles are DATA-ONLY packages
- Direct user to TARIFF PLANS (PREMIER/ALO) for plans with both minutes and data
- Show PREMIER plans: 400 EGP (13GB + 2,500 min), 550 EGP (16GB + 3,500 min), 750 EGP (25GB + 5,000 min)
- Mention ALO tariffs as alternative with different pricing structure (contact 110 for details)
- Explain the difference: Tariff plans = monthly service with minutes+data, GO bundles = additional data only
- Only ask "Which tariff plan interests you?" or "Need more details about PREMIER or ALO?"

**For Router/Technical Issues:**
- IMMEDIATELY provide specific troubleshooting steps
- For router issues: Check power, restart router, check connections, contact technical support
- For internet issues: Check data balance, restart device, check network settings
- For app issues: Restart app, clear cache, reinstall if needed
- IMPORTANT: Don't repeat the same question or get stuck in loops
- IMPORTANT: Don't reference "Reference X" or document sections - provide direct help
- If user says they tried basic steps and it's still not working, IMMEDIATELY direct to technical support at 110
- Don't keep asking the same troubleshooting questions
- Provide contact information: 110 for technical support
- Only ask "Need more specific help?" or "Should I connect you to technical support?"

**For Plan Selection Help:**
- If user asks for help choosing from options you just provided, focus on those specific options
- Provide comparison between the options you mentioned
- Ask about their usage patterns (data needs, budget, features)
- Give recommendations based on their needs
- Don't switch to completely different service types unless asked

**For Monthly Plans:**
- IMMEDIATELY show available monthly options with prices
- Give specific data quotas and validity periods
- Only ask about their data usage needs if unclear


**DON'T DO THIS:**
- "Hello! How can I help you today? You're looking for mobile internet bundles, right? We have several options available! Can you tell me more about your needs? What type of data do you need? How much data do you use? Would you like me to list some options?"
- Asking multiple questions without providing any useful information first

**When discussing internet bundles, ALWAYS include:**
- Package names
- Prices in EGP  
- Data quotas in MB/GB
- Validity periods
- Special features

**IMPORTANT DISTINCTIONS:**
- **TARIFF PLANS** = Main mobile service plans (PREMIER, ALO) with monthly fees, minutes, data, and features
- **INTERNET BUNDLES** = Data-only packages (GO bundles) for additional data on top of tariff plans
- **GO bundles** are MOBILE internet bundles for phones/tablets (data-only)
- **Home DSL/Wireless** are HOME internet services
- Don't confuse tariff plans with internet bundles - they are different services
- **PHONE BRANDS**: Don't mix up different phone brands - iPhone is Apple, Samsung Galaxy A36 5G is Samsung, OPPO Find N3 is OPPO
- **ACCURACY RULE**: Only mention plans that exist - don't make up plan names, prices, or features
- **ALO TARIFFS**: ALO tariffs exist but have different pricing structure - don't make up specific ALO plan names or prices
- **TROUBLESHOOTING RULE**: Don't repeat the same troubleshooting question - if basic steps don't work, direct to technical support

If the context doesn't contain enough information, provide what you can and suggest calling 110 for more details.""")
        ])
        
        # Create the chain
        chain = prompt_template | chat_model | StrOutputParser()
        
        # Generate response
        response = chain.invoke({
            "context": context,
            "question": user_input
        })
        
        # Clean up the response and remove any debugging information
        response = response.strip()
        
        # Remove any debugging information that might leak through
        if "User Question:" in response:
            response = response.split("User Question:")[-1].strip()
        if "Response:" in response:
            response = response.split("Response:")[-1].strip()
        if "User:" in response and "Assistant:" in response:
            # Extract just the assistant response
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()
        
        # Remove any remaining debugging patterns
        if response.startswith("User: "):
            response = response[6:].strip()
        if response.startswith("Bot: "):
            response = response[5:].strip()
        if response.startswith("Assistant: "):
            response = response[11:].strip()
        
        # Remove any repetition of the user's question at the start
        lines = response.split('\n')
        if len(lines) > 1 and lines[0].strip().lower() == user_input.lower().strip():
            response = '\n'.join(lines[1:]).strip()
        
        # Remove any single-line repetition of user input
        if response.strip() == user_input.strip():
            response = "I understand your concern. How can I help you with that?"
        
        # Remove any repetition that might be in quotes or different formats
        if response.startswith(f'"{user_input}"') or response.startswith(f"'{user_input}'"):
            response = response[len(f'"{user_input}"'):].strip()
        if response.startswith(f'"{user_input}"') or response.startswith(f"'{user_input}'"):
            response = response[len(f"'{user_input}'"):].strip()
        
        # Remove any repetition that starts with "Based on your question" or similar patterns
        if response.startswith(f'Based on your question "{user_input}"'):
            response = response[len(f'Based on your question "{user_input}"'):].strip()
        if response.startswith(f'Based on your question \'{user_input}\''):
            response = response[len(f'Based on your question \'{user_input}\''):].strip()
        if response.startswith(f'For {user_input}'):
            response = response[len(f'For {user_input}'):].strip()
        if response.startswith(f'Your {user_input}'):
            response = response[len(f'Your {user_input}'):].strip()
        
        # Remove any remaining patterns that start with user input
        if response.startswith(user_input):
            response = response[len(user_input):].strip()
        
        # Clean up any remaining punctuation or formatting issues
        if response.startswith(', '):
            response = response[2:].strip()
        if response.startswith('. '):
            response = response[2:].strip()
        if response.startswith(': '):
            response = response[2:].strip()
        
        return response
        
    except Exception as e:
        error_msg = f"I apologize, but I encountered an error while processing your request: {str(e)}"
        print(f"Error in get_fast_response: {e}")
        return error_msg


def get_plan_recommendations(user_profile: Optional[Dict] = None, user_question: str = "") -> str:
    """Get personalized plan recommendations based on user profile and question context"""
    if not user_profile:
        return "I need your profile information to provide personalized recommendations. Please log in to your account."
    
    try:
        # Get current usage patterns from user profile
        current_plan = user_profile.get('mobile_plan_name', 'Unknown')
        monthly_data = user_profile.get('monthly_mobile_data_mb', '0')
        monthly_bill = user_profile.get('monthly_bill_mobile_amount', '0')
        remaining_quota = user_profile.get('remaining_mobile_quota', '0')
        
        # Get internet bundle information
        internet_bundle = user_profile.get('internet_bundle_name', 'None')
        internet_bundle_data = user_profile.get('internet_bundle_data_mb', '0')
        internet_bundle_price = user_profile.get('internet_bundle_price', '0')
        
        # Analyze the user's question to provide contextual recommendations
        user_question_lower = user_question.lower()
        
        # Check if user is asking about usage or needs recommendations
        if any(phrase in user_question_lower for phrase in ['usage', 'used', 'finished', 'ran out', 'consumed']):
            # User is asking about their data usage
            if remaining_quota and int(remaining_quota) < 1000:  # Less than 1GB remaining
                return f"You have the {current_plan} plan with {monthly_data} MB total, and you've used most of it! You only have {remaining_quota} MB left. If you need more data, I can recommend GO 155 (11.5GB for 155 EGP), GO 260 (20GB for 260 EGP), or GO 390 (31.5GB for 390 EGP). Which one interests you?"
            else:
                return f"You have the {current_plan} plan with {monthly_data} MB total, and you still have {remaining_quota} MB remaining. Your current plan seems to be working well for your usage pattern."
        
        elif any(phrase in user_question_lower for phrase in ['recommend', 'bigger', 'more data', 'upgrade', 'suggest']):
            # User wants recommendations for a bigger plan
            return f"You currently have the {current_plan} plan with {monthly_data} MB for {monthly_bill} EGP, and you have {remaining_quota} MB left. For more data, I can recommend GO 155 (11.5GB for 155 EGP), GO 260 (20GB for 260 EGP), GO 390 (31.5GB for 390 EGP), or GO 520 (49GB for 520 EGP). If you also need calling minutes, consider PREMIER 550 (16GB + 3,500 min for 550 EGP) or PREMIER 750 (25GB + 5,000 min for 750 EGP). Which option interests you?"
        
        else:
            # General plan information - natural format
            if current_plan and current_plan != 'Unknown':
                if internet_bundle and internet_bundle != 'None':
                    return f"You have the {current_plan} plan with {monthly_data} MB of data for {monthly_bill} EGP, and you also have the {internet_bundle} bundle with {internet_bundle_data} MB for {internet_bundle_price} EGP. You have {remaining_quota} MB remaining."
                else:
                    return f"You have the {current_plan} plan with {monthly_data} MB of data for {monthly_bill} EGP. You have {remaining_quota} MB remaining."
            else:
                return "I don't have access to your current plan details. Please contact Orange customer service at 110 to check your current plan information."
        
    except Exception as e:
        return f"I encountered an error while retrieving your plan information: {str(e)}. Please contact Orange customer service at 110 for assistance."


def check_data_usage(user_profile: Optional[Dict] = None) -> str:
    """Check user's data usage and remaining quota"""
    if not user_profile:
        return "I need your profile information to check your data usage. Please log in to your account."
    
    try:
        mobile_plan = user_profile.get('mobile_plan_name', 'Unknown')
        monthly_data = user_profile.get('monthly_mobile_data_mb', '0')
        remaining_mobile = user_profile.get('remaining_mobile_quota', '0')
        router_plan = user_profile.get('router_plan_name', 'None')
        router_data = user_profile.get('monthly_router_quota_mb', '0')
        remaining_router = user_profile.get('remaining_router_quota', '0')
        
        usage_info = f"""**Your Data Usage Summary:**

**Mobile Plan: {mobile_plan}**
- Monthly Allowance: {monthly_data} MB
- Remaining Quota: {remaining_mobile} MB
- Used: {int(monthly_data) - int(remaining_mobile)} MB

**Router Plan: {router_plan}**
- Monthly Allowance: {router_data} MB  
- Remaining Quota: {remaining_router} MB
- Used: {int(router_data) - int(remaining_router)} MB

**Tips:**
- To check real-time usage, dial *888# on your mobile
- For router usage, check your router's admin panel
- Consider upgrading if you frequently run out of data
- Contact 110 for immediate assistance with data issues"""

        return usage_info
        
    except Exception as e:
        return f"I encountered an error while checking your usage: {str(e)}. Please contact Orange customer service at 110."


def get_billing_info(user_profile: Optional[Dict] = None) -> str:
    """Get user's billing information"""
    if not user_profile:
        return "I need your profile information to check your billing details. Please log in to your account."
    
    try:
        mobile_bill = user_profile.get('monthly_bill_mobile_amount', '0')
        router_bill = user_profile.get('monthly_bill_router_amount', '0')
        total_bill = float(mobile_bill) + float(router_bill)
        
        billing_info = f"""**Your Billing Information:**

**Mobile Services:**
- Monthly Bill: {mobile_bill} EGP
- Plan: {user_profile.get('mobile_plan_name', 'Unknown')}

**Router Services:**
- Monthly Bill: {router_bill} EGP  
- Plan: {user_profile.get('router_plan_name', 'None')}

**Total Monthly Bill: {total_bill} EGP**

**Payment Options:**
- Online: Orange website or mobile app
- Bank transfer to Orange account
- Credit/Debit card
- Orange stores and authorized retailers
- Auto-pay setup available

**Need Help?**
- For billing questions: 110
- For payment issues: 110
- For plan changes: 110"""

        return billing_info
        
    except Exception as e:
        return f"I encountered an error while retrieving billing information: {str(e)}. Please contact Orange customer service at 110."


if __name__ == "__main__":
    # Test the chatbot functionality
    print("🧪 Testing Orange Customer Service Chatbot...")
    
    # Test basic functionality
    test_query = "What are the available mobile internet plans?"
    print(f"\nQuery: {test_query}")
    
    try:
        response = get_fast_response(test_query)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to run rebuild_vectorstore.py first to create the vector database.")
