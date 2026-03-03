import streamlit as st
import google.generativeai as genai
import time

# Configure API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Page config
st.set_page_config(page_title="System Design Architect", page_icon="🏗️")
st.title("🏗️ System Design Architect")
st.caption("Ask me anything about system design!")

# Initialize model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="""
    You are a 20-year experienced Software Architect and an excellent teacher.
    Your goal is to explain system design topics in a simple, precise, and easy to understand way.
    
    Whenever a user gives you a system design topic, you MUST always follow this exact structure:
    
    1. What is it? — Explain the concept simply as if teaching a beginner
    2. Where is it used? — Industries, scenarios, or contexts where it appears
    3. Why is it used? — The reasoning and motivation behind using it
    4. Advantages — Clear bullet points of the benefits
    5. Disadvantages — Honest bullet points of the drawbacks
    6. How were the disadvantages overcome? — Evolution, alternatives, or solutions people adopted
    7. Real world examples — Actual companies or products that use or used it
    8. Reference links — Share credible article or documentation links to learn more
    9. YouTube videos — Suggest relevant YouTube searches or channels for visual learning
    
    Always be conversational, use analogies where possible, and never use unnecessary jargon.
    If the user asks anything outside system design, politely redirect them back to system design topics.
    """
)

# ─── Session state setup ───────────────────────────────────────────
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_count" not in st.session_state:
    st.session_state.message_count = 0

if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

# ─── Sidebar with reset button & stats ────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Reset Conversation"):
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.last_message_time = 0
        st.success("Conversation reset!")
        st.rerun()

    st.divider()
    st.metric("Messages sent", st.session_state.message_count)
    st.caption("Max 50 messages per session")
    st.caption("Max 500 characters per message")

# ─── Display chat history ──────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─── Chat input ────────────────────────────────────────────────────
if prompt := st.chat_input("Enter a system design topic..."):

    # Guardrail 1 — Empty input check
    if not prompt.strip():
        st.warning("⚠️ Please enter a topic!")
        st.stop()

    # Guardrail 2 — Input length limit
    if len(prompt) > 500:
        st.warning(f"⚠️ Your message is {len(prompt)} characters. Please keep it under 500!")
        st.stop()

    # Guardrail 3 — Rate limiting (max 1 message per 3 seconds)
    current_time = time.time()
    time_since_last = current_time - st.session_state.last_message_time
    if time_since_last < 3:
        st.warning(f"⚠️ Slow down! Please wait {3 - int(time_since_last)} seconds before sending again.")
        st.stop()

    # Guardrail 4 — Max messages per session
    if st.session_state.message_count >= 50:
        st.error("⚠️ You've reached the 50 message limit. Please reset the conversation!")
        st.stop()

    # Update tracking
    st.session_state.last_message_time = current_time
    st.session_state.message_count += 1

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Quota exceeded. Please wait a moment and try again.")
                else:
                    st.error(f"⚠️ An error occurred: {e}")