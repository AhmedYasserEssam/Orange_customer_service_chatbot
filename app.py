import streamlit as st
import time
from datetime import datetime
from chat_prompts import get_fast_response, load_customer_data
import warnings
import csv
from typing import Optional, Dict
import base64
import os

# Suppress warnings for cleaner UI
warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Orange Customer Service Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper to safely load + base64-encode an image for inline HTML
def get_base64_image(path: str) -> str:
    """Return a base64-encoded string for the given file path. Returns empty string on error."""
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

# Pre-encode logo once so we don't repeatedly read the file
ENCODED_LOGO = get_base64_image("orange_logo.png")

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --orange-primary: #FF6600;
        --orange-secondary: #FF8533;
        --orange-light: #FFB366;
        --dark-bg: #1a1a1a;
        --card-bg: #2d2d2d;
        --text-primary: #ffffff;
        --text-secondary: #b3b3b3;
        --border-color: #404040;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        min-height: 100vh;
        padding: 20px;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(90deg, var(--orange-primary) 0%, var(--orange-secondary) 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(255, 102, 0, 0.3);
    }
    
    .header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header p {
        color: white;
        margin: 10px 0 0 0;
        text-align: center;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Chat container */
    .chat-container {
        background: transparent;
        border-radius: 20px;
        padding: 30px;
        box-shadow: none;
        border: none;
        min-height: 500px;
    }
    
    /* Message bubbles */
    .user-message {
        background: linear-gradient(135deg, var(--orange-primary) 0%, var(--orange-secondary) 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        margin-left: 20%;
        margin-right: 0;
        box-shadow: 0 4px 15px rgba(255, 102, 0, 0.3);
        animation: slideInRight 0.3s ease-out;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .bot-message {
        background: var(--dark-bg);
        color: var(--text-primary);
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        margin-right: 20%;
        margin-left: 0;
        border: 1px solid var(--border-color);
        animation: slideInLeft 0.3s ease-out;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    /* Typing indicator */
    .typing-indicator {
        background: var(--dark-bg);
        color: var(--text-secondary);
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        margin-right: 20%;
        margin-left: 0;
        border: 1px solid var(--border-color);
        font-style: italic;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .typing-dots {
        display: inline-block;
        animation: typing 1.5s infinite;
    }
    
    /* Input area */
    .input-container {
        background: var(--card-bg);
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        border: 1px solid var(--border-color);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: var(--card-bg);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid var(--border-color);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, var(--orange-primary) 0%, var(--orange-secondary) 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 102, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 102, 0, 0.4);
    }
    
    /* Popular questions buttons */
    .stButton > button[data-testid*="popular_q_"] {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--dark-bg) 100%);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 12px 15px;
        font-weight: 500;
        font-size: 0.9rem;
        text-align: left;
        margin: 5px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button[data-testid*="popular_q_"]:hover {
        background: linear-gradient(135deg, var(--orange-primary) 0%, var(--orange-secondary) 100%);
        color: white;
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(255, 102, 0, 0.3);
        border-color: var(--orange-primary);
    }
    
    /* Animations */
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes typing {
        0%, 20% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--orange-primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--orange-secondary);
    }
    /* Keep sidebar always visible by hiding collapse button */
    [data-testid="stSidebarCollapseButton"] {
        display: none;
    }
    /* Force sidebar to stay pinned open */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        transform: none !important;
        visibility: visible !important;
        min-width: 300px;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None


def render_fullscreen_login():
    """Render a full-window login page and handle authentication."""
    # Centered login card; adjust column ratios so the card sits in the middle
    col_left, col_center, col_right = st.columns([1, 0.9, 1])
    with col_center:
        # Use the pre-encoded logo. If not available, the src will be empty which gracefully
        # falls back to nothing; you can optionally replace the empty case with text.
        st.markdown(
            """
            <div style="background: #2d2d2d; border: 1px solid #404040; padding: 24px; border-radius: 16px; width: 100%; max-width: 520px; margin: 0 auto; box-shadow: 0 12px 32px rgba(255,102,0,0.18); text-align:center;">
                <div style="display:flex; align-items:center; justify-content:center; gap:15px; margin-bottom: 12px;">
                    <img src="data:image/png;base64,{}" alt="Orange Logo" style="height: 40px; width: auto;">
                    <div style="color:#fff; font-weight:600; font-size: 1.1rem;">Customer Service Assistant</div>
                </div>
                <div style="color:#b3b3b3; font-size: 0.95rem; margin-bottom: 8px;">Sign in to continue</div>
            </div>
            """.format(ENCODED_LOGO), unsafe_allow_html=True,
        )
        with st.form(key="login_form_center", clear_on_submit=False):
            phone = st.text_input("Phone number", placeholder="Enter your Orange number")
            pwd = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign in")
        if submitted:
            profile = authenticate_user((phone or "").strip(), pwd or "")
            if profile:
                st.session_state.authenticated = True
                st.session_state.user_profile = profile
                st.success(f"Welcome, {profile.get('Name','Customer')}")
                st.rerun()
            else:
                st.error("Invalid phone number or password.")


def load_customers(filepath: str = "data/processed/customers_stimulation.csv") -> list[dict]:
    """Load customers from CSV into a list of dicts."""
    customers: list[dict] = []
    try:
        with open(filepath, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                customers.append(row)
    except FileNotFoundError:
        st.error("Customer database file not found.")
    return customers


def authenticate_user(phone_number: str, password: str) -> Optional[Dict[str, str]]:
    """Validate phone and password against customers CSV. Returns user profile if valid."""
    customers = load_customers()
    for customer in customers:
        if customer.get("phone_number") == phone_number and customer.get("password") == password:
            return customer
    return None


def display_chat_message(role, content, timestamp=None):
    """Display a chat message with proper styling"""
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>You</strong> {f'<small style="opacity: 0.7;">({timestamp})</small>' if timestamp else ''}<br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-message">
            <strong>🍊 Orange Assistant</strong> {f'<small style="opacity: 0.7;">({timestamp})</small>' if timestamp else ''}<br>
            {content}
        </div>
        """, unsafe_allow_html=True)


def display_typing_indicator():
    """Display typing indicator"""
    st.markdown("""
    <div class="typing-indicator">
        <strong>🍊 Orange Assistant</strong> is typing<span class="typing-dots">...</span>
    </div>
    """, unsafe_allow_html=True)


def get_bot_response(user_input):
    """Get response from the chatbot"""
    try:
        # Get conversation history for current session only (last 3 exchanges for context)
        history = []
        for msg in st.session_state.conversation_history[-6:]:  # Last 6 messages (3 exchanges)
            if msg["role"] == "user":
                history.append({"user": msg["content"], "assistant": ""})
            elif msg["role"] == "assistant" and history:
                history[-1]["assistant"] = msg["content"]
        
        # Get response from the chatbot
        customer_data = load_customer_data()
        response = get_fast_response(
            user_input,
            history=history if history else None,
            user_profile=st.session_state.user_profile,
            customer_data=customer_data,
        )
        return response
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again or contact support if the issue persists."


def main():
    """Main application function"""
    initialize_session_state()
    
    # If not authenticated, show full-screen login and stop rendering chat
    if not st.session_state.authenticated:
        render_fullscreen_login()
        return

    # Header
    st.markdown("""
    <div class="header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px;">
            <img src="data:image/png;base64,{}" alt="Orange Logo" style="height: 60px; width: auto;">
            <div>
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">Orange Customer Service Assistant</h1>
                <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Your intelligent AI assistant for all Orange services and support</p>
            </div>
        </div>
    </div>
    """.format(ENCODED_LOGO), unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        profile = st.session_state.user_profile or {}
        masked_phone = str(profile.get("phone_number",""))
        if len(masked_phone) >= 4:
            masked_phone = "*" * (len(masked_phone) - 4) + masked_phone[-4:]
        st.markdown(f"**Signed in as:** {profile.get('Name','Customer')}")
        st.caption(f"Phone: {masked_phone}")
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_profile = None
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()

        st.markdown("### ❓ Popular Questions")
        st.markdown("Click any question below to ask the assistant:")
        
        # Popular questions
        popular_questions = [
            "How do I check my mobile data usage?",
            "What are the available internet plans?",
            "How to set up mobile internet?",
            "How to pay my Orange bill online?",
            "What is my current mobile plan?",
            "How to contact Orange customer service?",
            "How to change my mobile plan?",
            "How to troubleshoot internet connection?",
            "How to activate roaming services?"
        ]
        
        # Display question buttons
        for i, question in enumerate(popular_questions):
            if st.button(f"💬 {question}", key=f"popular_q_{i}", use_container_width=True):
                # Add the question to chat
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "user", 
                    "content": question,
                    "timestamp": timestamp
                })
                st.session_state.conversation_history.append({
                    "role": "user", 
                    "content": question
                })
                
                # Get bot response
                with st.spinner(""):
                    bot_response = get_bot_response(question)
                    timestamp = datetime.now().strftime("%H:%M")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": bot_response,
                        "timestamp": timestamp
                    })
                    st.session_state.conversation_history.append({
                        "role": "assistant", 
                        "content": bot_response
                    })
                
                # Rerun to update the display
                st.rerun()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
    
    # Main chat interface - full width
    st.markdown('<div style="padding-right: 20px; overflow-y: auto; max-height: 70vh;">', unsafe_allow_html=True)
    # Display chat messages directly without container
    for message in st.session_state.messages:
        display_chat_message(
            message["role"], 
            message["content"], 
            message.get("timestamp")
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask me anything about Orange services...", key="chat_input")
    
    if user_input:
        # Add user message to chat
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": timestamp
        })
        st.session_state.conversation_history.append({
            "role": "user", 
            "content": user_input
        })
        
        # Display user message
        display_chat_message("user", user_input, timestamp)
        
        # Show typing indicator
        with st.spinner(""):
            display_typing_indicator()
            placeholder = st.empty()
            
            # Get bot response
            bot_response = get_bot_response(user_input)
            
            # Clear typing indicator and show response
            placeholder.empty()
            timestamp = datetime.now().strftime("%H:%M")
            display_chat_message("assistant", bot_response, timestamp)
        
        # Add bot response to chat
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_response,
            "timestamp": timestamp
        })
        st.session_state.conversation_history.append({
            "role": "assistant", 
            "content": bot_response
        })
        
        # Rerun to update the display
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--text-secondary); padding: 20px;">
        <p>🍊 Orange Customer Service Assistant | Powered by AI & RAG Technology</p>
        <p><small>For immediate assistance, call Orange customer service at 110</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
