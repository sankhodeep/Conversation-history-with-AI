import streamlit as st
import json
from datetime import datetime
import pyperclip

# ===== SETUP =====
st.set_page_config(page_title="AI Chat Manager", layout="wide")
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# ===== UTILS =====
def create_new_session():
    """Auto-generate session name with timestamp"""
    session_name = f"Chat_{datetime.now().strftime('%b%d_%I%M%p')}"
    st.session_state.sessions[session_name] = []
    st.session_state.current_session = session_name
    return session_name

def get_formatted_prompt(history):
    """Generate the full prompt with context"""
    if not history:
        return ""
    
    convo_history = "\n".join(
        f"{msg['role']}: {msg['content']}" 
        for msg in history
    )
    
    current_msg = st.session_state.get("current_saved_message", "")
    system_prompt = st.session_state.get("system_prompt", 
        "Hello, I've attached our past conversation history below for context.")
    
    return f"""
System: {system_prompt}

Past Conversation History:
{convo_history}

Current Message:
{current_msg}

Please respond naturally considering this context.
"""

# ===== SIDEBAR (Session Management) =====
with st.sidebar:
    st.header("💾 Sessions")
    
    # New session button
    if st.button("➕ New Session"):
        create_new_session()
    
    # Session selector
    session_names = list(st.session_state.sessions.keys())
    if session_names:
        selected_session = st.selectbox(
            "Your Sessions", 
            session_names,
            index=session_names.index(st.session_state.current_session) 
            if st.session_state.current_session else 0
        )
        st.session_state.current_session = selected_session
        
        # Export current session
        st.download_button(
            label="⬇️ Export Session",
            data=json.dumps(st.session_state.sessions[selected_session]),
            file_name=f"{selected_session}.json",
            mime="application/json"
        )
        
        # Import session
        uploaded_file = st.file_uploader("↪️ Import Session", type=["json"])
        if uploaded_file:
            imported_data = json.load(uploaded_file)
            new_name = f"Imported_{datetime.now().strftime('%H%M')}"
            st.session_state.sessions[new_name] = imported_data
            st.session_state.current_session = new_name
            st.rerun()

# ===== MAIN CHAT UI =====
st.title("🤖 AI Chat Manager")

# Initialize session if none exists
if not st.session_state.current_session:
    create_new_session()

current_session = st.session_state.current_session
messages = st.session_state.sessions[current_session]

# Display chat history
for msg in messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

def save_and_clear():
    if st.session_state.user_input:  # Only save if there's a message
        messages.extend([
            {"role": "user", "content": st.session_state.user_input},
            {"role": "assistant", "content": st.session_state.ai_response}
        ])
    st.session_state.user_input = ""
    st.session_state.ai_response = ""

# System Prompt
with st.form("system_prompt_form"):
    system_prompt = st.text_area(
        "⚙️ System Prompt",
        value=st.session_state.get("system_prompt", 
            "Hello, I've attached our past conversation history below for context."),
        key="system_prompt_input",
        height=100
    )
    if st.form_submit_button("💾 Save System Prompt"):
        st.session_state.system_prompt = st.session_state.system_prompt_input
        st.toast("System prompt saved!", icon="💾")

# Input fields
with st.form("chat_form"):
    user_msg = st.text_area("💬 Your Message", key="user_input")
    ai_msg = st.text_area("🤖 AI Response", key="ai_response")
    
    submitted = st.form_submit_button(
        "💾 Save Exchange",
        on_click=save_and_clear
    )
    if submitted:
        st.rerun()

# ===== REAL-TIME PREVIEW =====
with st.expander("🔍 Live Prompt Preview", expanded=True):
    preview = get_formatted_prompt(messages)
    st.code(preview, language="text")
    
    if st.button("📋 Copy Full Prompt"):
        pyperclip.copy(preview)
        st.toast("Copied to clipboard!", icon="✅")

# ===== CURRENT MESSAGE HANDLING =====
st.subheader("Current Message")
current_msg_input = st.text_area(
    "✏️ Enter Current Message", 
    key="current_message_input",
    height=100
)
if st.button("💾 Save Current Message"):
    st.session_state.current_saved_message = st.session_state.current_message_input
    st.toast("Current message saved!", icon="💾")

# ===== SESSION ACTIONS =====
st.caption(f"Current Session: {current_session}")
if st.button("🔄 Rename Session"):
    new_name = st.text_input("New session name", current_session)
    if new_name and new_name != current_session:
        st.session_state.sessions[new_name] = st.session_state.sessions.pop(current_session)
        st.session_state.current_session = new_name
        st.rerun()

