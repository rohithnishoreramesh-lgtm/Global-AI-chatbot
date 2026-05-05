import os
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from models.llm import get_chatgroq_model
from utils.helpers import read_pdf_text, read_text_file
from utils.rag import SimpleRAG

load_dotenv()

st.set_page_config(
    page_title="Global AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 40%, #fff7ed 100%);
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
.hero {
    background: rgba(255,255,255,0.82);
    padding: 28px;
    border-radius: 28px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.08);
    border: 1px solid rgba(255,255,255,0.7);
    margin-bottom: 22px;
}
.hero h1 {
    font-size: 42px;
    margin-bottom: 8px;
}
.hero p {
    font-size: 18px;
    color: #475569;
}
.card {
    background: rgba(255,255,255,0.85);
    padding: 18px;
    border-radius: 20px;
    box-shadow: 0 6px 22px rgba(0,0,0,0.07);
    border: 1px solid rgba(255,255,255,0.8);
}
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.78);
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
}
.stButton button {
    border-radius: 14px;
    font-weight: 700;
    border: 0;
    padding: 0.6rem 1rem;
}
textarea, input {
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag" not in st.session_state:
    st.session_state.rag = SimpleRAG()

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("⚙️ Controls")

    language = st.selectbox(
        "Language",
        ["English"],
        index=0
    )

    temperature = st.slider(
        "Creativity",
        0.0, 1.0, 0.4, 0.1
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "📄 Upload PDF / TXT",
        type=["pdf", "txt"]
    )

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".pdf"):
                text = read_pdf_text(uploaded_file)
            else:
                text = read_text_file(uploaded_file)

            st.session_state.doc_text = text
            st.session_state.rag.add_text(text)

            st.success("File loaded successfully ✅")

            with st.expander("📄 PDF / File Preview"):
                preview_text = text[:3000] if text else "No text found."
                st.text_area(
                    "Preview",
                    preview_text,
                    height=260
                )

        except Exception as e:
            st.error(f"File reading error: {e}")

    st.divider()

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    chat_json = json.dumps(
        st.session_state.messages,
        indent=2,
        ensure_ascii=False
    )

    st.download_button(
        "⬇️ Download Chat History",
        data=chat_json,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# ---------------- Hero ----------------
st.markdown("""
<div class="hero">
    <h1>🤖 Global AI Chatbot</h1>
    <p>Ask questions, upload PDFs, get smart answers, and download your chat history.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Suggested Prompts ----------------
st.markdown("### 💡 Suggested Prompts")

c1, c2, c3, c4 = st.columns(4)

suggestions = [
    "Summarize this PDF",
    "Explain this document simply",
    "Give key points from the file",
    "Create interview questions from this PDF"
]

cols = [c1, c2, c3, c4]

for col, prompt_text in zip(cols, suggestions):
    with col:
        if st.button(prompt_text):
            st.session_state.suggested_prompt = prompt_text

# ---------------- Voice Input ----------------
st.markdown("### 🎙️ Voice Input")

audio_file = None

try:
    audio_file = st.audio_input("Record your voice")
except Exception:
    st.info("Voice recorder needs latest Streamlit version.")

voice_text = ""

if audio_file is not None:
    st.audio(audio_file)

    if st.button("Transcribe Voice"):
        try:
            from groq import Groq

            client = Groq(api_key=os.getenv("GROQ_API_KEY"))

            transcription = client.audio.transcriptions.create(
                file=("voice.wav", audio_file.getvalue()),
                model="whisper-large-v3-turbo",
                response_format="text"
            )

            voice_text = transcription
            st.success("Voice transcribed ✅")
            st.write(voice_text)
            st.session_state.suggested_prompt = voice_text

        except Exception as e:
            st.error(f"Voice transcription error: {e}")
            st.info("Install required package: pip install groq")

# ---------------- Chat Display ----------------
st.markdown("### 💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

default_prompt = st.session_state.suggested_prompt
user_input = st.chat_input("Ask anything...")

if default_prompt and not user_input:
    user_input = default_prompt
    st.session_state.suggested_prompt = None

# ---------------- LLM Response ----------------
if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                llm = get_chatgroq_model()

                retrieved_chunks = st.session_state.rag.retrieve(user_input)

                context = "\n\n".join(retrieved_chunks) if retrieved_chunks else ""

                system_prompt = f"""
You are a helpful AI assistant.
Language: {language}

Use the uploaded document context if available.
If context is empty, answer normally.

Context:
{context}
"""

                full_prompt = f"""
{system_prompt}

User question:
{user_input}
"""

                response = llm.invoke(full_prompt)

                if hasattr(response, "content"):
                    answer = response.content
                else:
                    answer = str(response)

            except Exception as e:
                answer = f"Error: {e}"

            st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })