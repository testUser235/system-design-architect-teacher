import streamlit as st
import google.generativeai as genai

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

# Initialize chat history in session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter a system design topic..."):
    
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
                    st.error("Quota exceeded. Please wait a moment and try again.")
                else:
                    st.error(f"An error occurred: {e}")