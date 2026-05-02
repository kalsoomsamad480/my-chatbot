from groq import Groq
import streamlit as st
import time
import base64
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Groq 2.0 - AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0f1117;
    }
    .stChatMessage {
        background-color: #1e2130;
        border-radius: 15px;
        padding: 10px;
        margin: 5px 0;
    }
    .sidebar .sidebar-content {
        background-color: #1e2130;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #4a90e2;
        color: white;
        border: none;
        padding: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #357abd;
    }
    .message-count {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        color: #4a90e2;
        font-size: 18px;
        font-weight: bold;
        margin: 10px 0;
    }
    .bot-header {
        display: flex;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 20px;
    }
    .stSelectbox {
        background-color: #1e2130;
    }
    div[data-testid="stSidebarContent"] {
        background-color: #1e2130;
    }
</style>
""", unsafe_allow_html=True)

# Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Personality prompts
personalities = {
    "🤖 Assistant": "You are a helpful and friendly assistant named Aria. Always reply in simple and clear words.",
    "📚 Teacher": "You are a patient and knowledgeable teacher named Aria. Explain everything in simple steps, use examples, and make learning fun.",
    "👨‍⚕️ Doctor": "You are a helpful medical assistant named Aria. Provide general health information clearly. Always remind users to consult a real doctor for medical advice.",
    "😄 Friend": "You are a fun and casual friend named Aria. Use informal language, be funny, supportive and entertaining.",
    "💼 Business Advisor": "You are a professional business advisor named Aria. Give clear, strategic, and practical business advice."
}

# Sidebar
with st.sidebar:
    st.image("https://api.dicebear.com/7.x/bottts/svg?seed=Aria", width=100)
    st.title("⚙️ Settings")
    st.divider()

    # User name input
    user_name = st.text_input("👤 Your Name", placeholder="Enter your name...")
    if user_name:
        st.success(f"Hello, {user_name}! 👋")

    st.divider()

    # Personality selector
    st.subheader("🎭 Bot Personality")
    selected_personality = st.selectbox(
        "Choose a personality:",
        list(personalities.keys())
    )

    st.divider()

    # Message counter
    st.subheader("📊 Chat Stats")
    if "conversation_history" in st.session_state:
        user_messages = len([m for m in st.session_state.conversation_history if m["role"] == "user"])
        st.markdown(f"""
        <div class='message-count'>
            💬 {user_messages} messages sent
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.conversation_history = [
            {
                "role": "system",
                "content": personalities[selected_personality]
            }
        ]
        st.rerun()

    st.divider()

    # Download chat history
    if st.button("📥 Download Chat"):
        if "conversation_history" in st.session_state:
            chat_text = f"Chat History - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            chat_text += "=" * 50 + "\n\n"
            for msg in st.session_state.conversation_history:
                if msg["role"] == "user":
                    name = user_name if user_name else "You"
                    chat_text += f"{name}: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    chat_text += f"Aria: {msg['content']}\n\n"
            b64 = base64.b64encode(chat_text.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">Click here to download</a>'
            st.markdown(href, unsafe_allow_html=True)

    st.divider()

    # Instructions
    st.subheader("📖 How to Use")
    st.markdown("""
    1. Enter your name above
    2. Choose a personality
    3. Type your message below
    4. Press Enter to chat
    5. Use Clear Chat to start fresh
    6. Download your chat anytime
    """)

# Main chat area
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    # Header
    st.markdown("""
        <div class='bot-header'>
            <h1>🤖 Aria - AI Assistant</h1>
        </div>
    """, unsafe_allow_html=True)

    if user_name:
        st.markdown(f"### Welcome, {user_name}! How can I help you today?")
    else:
        st.markdown("### Hello! How can I help you today?")

    st.divider()

    # Initialize conversation
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [
            {
                "role": "system",
                "content": personalities[selected_personality]
            }
        ]

    # Update personality if changed
    if st.session_state.conversation_history[0]["content"] != personalities[selected_personality]:
        st.session_state.conversation_history[0]["content"] = personalities[selected_personality]

    # Display chat messages
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            name = user_name if user_name else "You"
            with st.chat_message("user", avatar="👤"):
                st.write(f"**{name}:** {message['content']}")
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message["content"])
                # Copy button
                st.code(message["content"], language=None)

    # Chat input
    user_input = st.chat_input(f"Type your message here...")

    if user_input:
        # Add user message
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user", avatar="👤"):
            name = user_name if user_name else "You"
            st.write(f"**{name}:** {user_input}")

        # Typing indicator
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Aria is thinking..."):
                time.sleep(0.5)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.conversation_history
                )
                bot_reply = response.choices[0].message.content

        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": bot_reply
        })

        st.rerun()
