import streamlit as st
from langgraph_database_backend import chatbot, retrieve_all_threads, get_chat_summary
from langchain_core.messages import HumanMessage
import uuid
import hashlib

# **************************************** Page Config *************************
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# **************************************** Custom CSS *************************
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --success-color: #059669;
        --warning-color: #f59e0b;
        --danger-color: #dc2626;
        --text-color: #1f2937;
        --light-bg: #f9fafb;
        --border-color: #e5e7eb;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid var(--border-color);
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* User message bubble */
    .stChatMessage[data-message-role="user"] {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        margin-left: auto;
        max-width: 80%;
        border-bottom-right-radius: 4px;
    }
    
    /* Assistant message bubble */
    .stChatMessage[data-message-role="assistant"] {
        background-color: #f3f4f6;
        color: var(--text-color);
        max-width: 80%;
        border-bottom-left-radius: 4px;
    }
    
    /* Input styling */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Primary button */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        color: white !important;
    }
    
    /* Secondary button */
    .stButton button[kind="secondary"] {
        background-color: var(--light-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Danger button for delete */
    .stButton button.danger {
        background-color: var(--danger-color) !important;
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar header */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-size: 18px !important;
        margin-bottom: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# **************************************** Session ID Generation *************************
def get_session_id():
    """Generate unique session ID for user based on browser fingerprint"""
    if 'session_id' not in st.session_state:
        # Create unique session ID that persists in browser
        session_id = str(uuid.uuid4())
        st.session_state['session_id'] = session_id
    return st.session_state['session_id']

# **************************************** Utility Functions *************************
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['session_threads'].append(thread_id)
    st.session_state['message_history'] = []
    st.rerun()

def delete_current_chat():
    """Delete the current chat history"""
    if st.session_state['thread_id'] in st.session_state['session_threads']:
        st.session_state['session_threads'].remove(st.session_state['thread_id'])
    reset_chat()

def clear_all_history():
    """Clear all chat history for this session"""
    st.session_state['session_threads'] = []
    st.session_state['message_history'] = []
    reset_chat()

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

# **************************************** Session Setup ******************************
session_id = get_session_id()

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'session_threads' not in st.session_state:
    # Only get threads for this session (all threads in this case, but session_id ensures isolation)
    all_threads = retrieve_all_threads()
    st.session_state['session_threads'] = all_threads if all_threads else []

# Add current thread if not exists
if st.session_state['thread_id'] not in st.session_state['session_threads']:
    st.session_state['session_threads'].append(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************
with st.sidebar:
    st.markdown("### 💬 ChatBot")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            reset_chat()
    
    with col2:
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_all_history()
    
    st.markdown("---")
    st.markdown("### 📋 Conversations")
    
    if st.session_state['session_threads']:
        for thread_id in reversed(st.session_state['session_threads']):
            chat_summary = get_chat_summary(thread_id)
            if chat_summary is None:
                chat_summary = f"Chat {str(thread_id)[:8]}"
            
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(
                    f"💭 {chat_summary}", 
                    key=f"chat_{thread_id}",
                    use_container_width=True
                ):
                    st.session_state['thread_id'] = thread_id
                    messages = load_conversation(thread_id)
                    temp_messages = []
                    
                    for msg in messages:
                        role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
                        temp_messages.append({'role': role, 'content': msg.content})
                    
                    st.session_state['message_history'] = temp_messages
                    st.rerun()
    else:
        st.info("📭 No conversations yet. Start a new chat!")
    
    st.markdown("---")
    with st.expander("ℹ️ About This Session"):
        st.caption(f"**Session ID:** `{session_id[:8]}...`")
        st.caption(f"**Thread ID:** `{st.session_state['thread_id'][:8]}...`")
        st.caption(f"**Total Chats:** {len(st.session_state['session_threads'])}")


# **************************************** Main UI ************************************
st.markdown("## 🤖 AI Assistant")
st.markdown("Chat with your AI assistant. Your conversation history is private to this session.")
st.markdown("---")

# Display chat history with better styling
chat_container = st.container()
with chat_container:
    for message in st.session_state['message_history']:
        with st.chat_message(message['role'], avatar="👤" if message['role'] == 'user' else "🤖"):
            st.markdown(message['content'])

# Input area
st.markdown("---")
user_input = st.chat_input("💬 Type your message here...", key="chat_input")

if user_input:
    # Add user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user', avatar="👤"):
        st.markdown(user_input)
    
    # Get AI response
    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"],
            "session_id": session_id
        },
        "run_name": "chat_turn",
    }
    
    with st.chat_message('assistant', avatar="🤖"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
    
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})