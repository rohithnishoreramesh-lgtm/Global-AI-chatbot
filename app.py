import os
import sys
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# -------------------- PATH SETUP --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../..")))

from models.llm import get_chatgroq_model
from utils.helpers import read_pdf_text, read_text_file
from utils.rag import SimpleRAG

load_dotenv()

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Global AI | Neural Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- CSS - NEON MULTI-COLOR GLOBAL AI UI --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&family=Space+Grotesk:wght@400;500;600&display=swap');

/* ═══════════════ ROOT VARIABLES - NEON GLOBAL PALETTE ═══════════════ */
:root {
    --bg-deep:       #05050a;
    --bg-surface:    #0a0a0f;
    --bg-card:       #0e0e16;
    --border-dim:    rgba(255,255,255,0.05);
    --neon-blue:     #3b82f6;
    --neon-purple:   #a855f7;
    --neon-pink:     #ec4899;
    --neon-cyan:     #06b6d4;
    --neon-green:    #10b981;
    --neon-yellow:   #eab308;
    --neon-orange:   #f97316;
    --neon-red:      #ef4444;
    --text-bright:   #f8fafc;
    --text-muted:    #94a3b8;
    --glow-sm:       0 0 5px;
    --glow-md:       0 0 12px;
    --glow-lg:       0 0 22px;
}

* {
    box-sizing: border-box;
}

.stApp {
    background: radial-gradient(circle at 0% 0%, #0a0a12, #020206, #000000);
    font-family: 'Inter', 'Space Grotesk', sans-serif;
}

.block-container {
    padding: 1.2rem 1.8rem !important;
    max-width: 1300px;
    margin: 0 auto;
}

/* ═══════════════ SIDEBAR - PREMIUM GLASS NEON ═══════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8, 8, 14, 0.95), rgba(2, 2, 8, 0.98)) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(59, 130, 246, 0.5) !important;
    box-shadow: -4px 0 30px rgba(59, 130, 246, 0.15), 4px 0 20px rgba(0,0,0,0.6);
}

[data-testid="stSidebar"] * {
    color: var(--text-bright) !important;
}

/* sidebar brand - GLOBAL AI */
.sidebar-brand-global {
    text-align: center;
    padding: 24px 12px 20px;
    margin-bottom: 24px;
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(168,85,247,0.1), rgba(236,72,153,0.08));
    border-radius: 30px;
    border: 1px solid rgba(59,130,246,0.4);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4), 0 0 15px rgba(59,130,246,0.2);
    position: relative;
    overflow: hidden;
}
.sidebar-brand-global::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #3b82f6, #a855f7, #ec4899, transparent);
    animation: slideGlow 3s infinite;
}
@keyframes slideGlow {
    0% { left: -100%; }
    100% { left: 100%; }
}

.brand-icon-global {
    font-size: 58px;
    filter: drop-shadow(0 0 15px #3b82f6);
    animation: globalFloat 3s infinite ease;
    display: inline-block;
}
@keyframes globalFloat {
    0%,100% { transform: translateY(0px); text-shadow: 0 0 5px #3b82f6; }
    50% { transform: translateY(-6px); text-shadow: 0 0 20px #a855f7, 0 0 10px #06b6d4; }
}

.brand-title-global {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #c084fc, #f472b6, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin-top: 8px;
}

.brand-sub-global {
    font-size: 10px;
    letter-spacing: 2px;
    color: #6b7280;
    margin-top: 6px;
}

.global-pulse {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.5);
    border-radius: 40px;
    padding: 5px 16px;
    font-size: 11px;
    font-weight: 600;
    margin-top: 14px;
    backdrop-filter: blur(4px);
}

.pulse-dot-global {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 10px #10b981;
    animation: pulseGreenGlow 1.2s infinite;
}

@keyframes pulseGreenGlow {
    0%,100% { opacity: 1; transform: scale(1); box-shadow: 0 0 5px #10b981; }
    50% { opacity: 0.6; transform: scale(1.25); box-shadow: 0 0 18px #10b981; }
}

/* sidebar sections */
.sb-card-global {
    background: rgba(14, 14, 22, 0.7);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 22px;
    padding: 16px 18px;
    margin: 18px 0;
    transition: all 0.25s;
}

.sb-card-global:hover {
    border-color: rgba(168,85,247,0.6);
    box-shadow: 0 0 16px rgba(168,85,247,0.2);
}

.sb-label-global {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #60a5fa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* radio buttons - neon */
[data-testid="stRadio"] > div {
    gap: 12px;
}
[data-testid="stRadio"] label {
    background: rgba(20,20,35,0.9) !important;
    border: 1px solid rgba(59,130,246,0.5) !important;
    border-radius: 40px !important;
    padding: 6px 20px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
[data-testid="stRadio"] label:hover {
    border-color: #ec4899 !important;
    box-shadow: 0 0 10px #ec4899;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    color: #f1f5f9 !important;
}

/* buttons */
.stButton > button {
    width: 100%;
    background: linear-gradient(95deg, rgba(59,130,246,0.12), rgba(6,182,212,0.08)) !important;
    border: 1px solid rgba(59,130,246,0.5) !important;
    border-radius: 16px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px !important;
    transition: all 0.25s !important;
    color: #f0f3fa !important;
}
.stButton > button:hover {
    background: linear-gradient(95deg, rgba(59,130,246,0.3), rgba(236,72,153,0.2)) !important;
    border-color: #ec4899 !important;
    box-shadow: 0 0 18px rgba(59,130,246,0.5) !important;
    transform: translateY(-2px);
}

/* file uploader */
[data-testid="stFileUploader"] {
    background: rgba(14,14,22,0.9) !important;
   git init
    border-radius: 20px !important;
}
[data-testid="stFileUploader"] * {
    color: black !important;
    
}

/* ═══════════════ MAIN HEADER - GLOBAL NEON BANNER ═══════════════ */
.global-header {
    background: linear-gradient(105deg, rgba(59,130,246,0.1), rgba(168,85,247,0.08), rgba(6,182,212,0.05));
    border: 1px solid rgba(59,130,246,0.4);
    border-radius: 36px;
    padding: 22px 32px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(8px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    margin-top:70px;
}
.global-header::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -30%;
    width: 80%;
    height: 3px;
    background: linear-gradient(90deg, transparent, #3b82f6, #a855f7, #ec4899, #06b6d4, transparent);
    animation: shimmerGlobal 4s infinite linear;
}
@keyframes shimmerGlobal {
    0% { left: -40%; }
    100% { left: 120%; }
}
.global-header h1 {
    font-size: 38px;
    font-weight: 800;
    background: linear-gradient(125deg, #60a5fa, #c084fc, #f472b6, #22d3ee, #facc15);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}
.global-header p {
    color: #a5b4fc;
    font-size: 15px;
    font-weight: 400;
}

.badge-global {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,0,0,0.45);
    border-radius: 40px;
    padding: 5px 16px;
    font-size: 12px;
    font-weight: 500;
    margin-right: 10px;
    backdrop-filter: blur(4px);
}
.badge-blue { border-left: 3px solid #3b82f6; color: #93c5fd; }
.badge-purple { border-left: 3px solid #a855f7; color: #d8b4fe; }
.badge-pink { border-left: 3px solid #ec4899; color: #fbcfe8; }
.badge-cyan { border-left: 3px solid #06b6d4; color: #67e8f9; }
.badge-green { border-left: 3px solid #10b981; color: #bbf7d0; }

/* ═══════════════ WELCOME CARD - GLOWING GLOBAL ═══════════════ */
.welcome-global {
    background: rgba(10,10,18,0.75);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(59,130,246,0.5);
    border-radius: 48px;
    padding: 52px 28px 48px;
    text-align: center;
    margin: 16px 0 30px;
    box-shadow: 0 20px 40px -12px rgba(0,0,0,0.6), 0 0 0 1px rgba(59,130,246,0.2);
}
.welcome-icon-global {
    font-size: 88px;
    filter: drop-shadow(0 0 22px #3b82f6);
    animation: floatGlowGlobal 3s infinite;
}
@keyframes floatGlowGlobal {
    0%,100% { transform: translateY(0); filter: drop-shadow(0 0 12px #3b82f6); }
    50% { transform: translateY(-10px); filter: drop-shadow(0 0 32px #a855f7); }
}
.welcome-title-global {
    font-size: 46px;
    font-weight: 800;
    background: linear-gradient(125deg, #a5f3fc, #c084fc, #f9a8d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 20px 0 12px;
}
.chip-global {
    display: inline-block;
    background:bisque;
    border: 1px solid rgba(59,130,246,0.4);
    border-radius: 50px;
    padding: 8px 20px;
    margin: 6px 8px;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s;
    cursor: default;
}
.chip-global:hover {
    border-color: #ec4899;
    box-shadow: 0 0 14px rgba(236,72,153,0.5);
    background: rgba(59,130,246,0.15);
    transform: scale(1.02);
}

/* ═══════════════ CHAT MESSAGES - CLEAN NEON BUBBLES ═══════════════ */
[data-testid="stChatMessage"] {
    animation: fadeSlide 0.3s ease-out;
    margin: 12px 0;
}
@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
[data-testid="stChatMessageContent"] {
    font-size: 14.5px !important;
    line-height: 1.65 !important;
    padding: 14px 22px !important;
    border-radius: 24px !important;
    color: #f1f5f9 !important;
}
/* user bubble - blue/purple neon */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) 
[data-testid="stChatMessageContent"] {
    background: linear-gradient(115deg, rgba(59,130,246,0.2), rgba(168,85,247,0.15)) !important;
    border: 1px solid rgba(59,130,246,0.6) !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.2);
}
/* assistant bubble - cyan glow clean */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) 
[data-testid="stChatMessageContent"] {
    background: rgba(12, 20, 35, 0.85) !important;
    border: 1px solid rgba(6,182,212,0.5) !important;
    box-shadow: 0 2px 12px rgba(6,182,212,0.15);
}
/* code blocks */
[data-testid="stChatMessageContent"] pre {
    background: #01010c !important;
    border-left: 4px solid #3b82f6 !important;
    border-radius: 16px !important;
    padding: 14px !important;
}
[data-testid="stChatMessageContent"] code {
    background: rgba(59,130,246,0.2) !important;
    color: #c084fc !important;
    border-radius: 6px;
}

/* ═══════════════ CHAT INPUT - CLEAR NEON BORDER ═══════════════ */
[data-testid="stChatInput"] > div {
    border: 2px solid rgba(59,130,246,0.6) !important;
    border-radius: 36px !important;
    background: whitesmoke !important;
    backdrop-filter: blur(12px);
    transition: all 0.2s;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #ec4899 !important;
    box-shadow: 0 0 0 3px rgba(236,72,153,0.25), 0 0 25px rgba(6,182,212,0.3) !important;
}
[data-testid="stChatInput"] textarea {
    color: white !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #7e8aa8 !important;
}
[data-testid="stChatInput"] button svg {
    fill: #3b82f6 !important;
    filter: drop-shadow(0 0 4px #3b82f6);
}

/* alerts */
[data-testid="stAlert"] {
    border-radius: 20px !important;
    background: rgba(0,0,0,0.7) !important;
    border-left: 4px solid #10b981 !important;
}

hr {
    border-color: rgba(59,130,246,0.3);
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
def init_session():
    defaults = {
        "messages":         [],
        "rag":              SimpleRAG(),
        "knowledge_loaded": False,
        "response_mode":    "Detailed",
        "uploaded_text":    "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# -------------------- SYSTEM PROMPT --------------------
def build_system_prompt(response_mode):
    mode_instruction = (
        "Be concise and direct — answer in 2-4 sentences."
        if response_mode == "Concise"
        else "Be comprehensive — provide detailed explanations, examples, and practical insights."
    )
    return f"""You are Global AI, a powerful, friendly, and highly capable assistant. Answer ANY question accurately.

CAPABILITIES: Coding (Python, JavaScript, SQL, React), Writing, Science, History, Math, Document Analysis, Creative tasks.

GUIDELINES:
- Always be helpful, clear, and professional.
- For code, give working examples with explanations.
- If documents are uploaded, prioritize that context.
- Be honest if uncertain.

RESPONSE STYLE: {mode_instruction}
"""

def build_user_prompt(question, retrieved_chunks=None):
    if retrieved_chunks:
        context = "\n\n".join(retrieved_chunks)
        return f"""USER QUESTION: {question}

📄 DOCUMENT CONTEXT (use if relevant):
{context}

Please provide a helpful, accurate response."""
    return question

def get_chat_response(chat_model, question, history, system_prompt, retrieved_chunks=None):
    try:
        messages = [SystemMessage(content=system_prompt)]
        for msg in history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=build_user_prompt(question, retrieved_chunks)))
        response = chat_model.invoke(messages)
        return response.content
    except Exception as e:
        return f"⚠️ Global AI encountered an error: {str(e)}. Please try again."

# -------------------- SIDEBAR RENDER --------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand-global">
            <div class="brand-icon-global">🌐🤖</div>
            <div class="brand-title-global">Global AI</div>
            <div class="brand-sub-global">Artificial Intelligence</div>
            <div class="global-pulse">
                <div class="pulse-dot-global"></div> Active · Groq Ultra
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-card-global">', unsafe_allow_html=True)
        st.markdown('<div class="sb-label-global"><i class="fas fa-sliders-h"></i> RESPONSE MODE</div>', unsafe_allow_html=True)
        mode = st.radio(
            "",
            ["🎯 Concise", "📚 Detailed"],
            index=1,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.response_mode = mode.split()[1]
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sb-card-global">', unsafe_allow_html=True)
        st.markdown('<div class="sb-label-global"><i class="fas fa-brain"></i> KNOWLEDGE BASE</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
             " Upload PDF or TXT",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="global_uploader",
        )
        if st.button("🚀 Process Documents", use_container_width=True):
            if uploaded_files:
                try:
                    full_text = ""
                    for file in uploaded_files:
                        text = read_pdf_text(file) if file.name.endswith('.pdf') else read_text_file(file)
                        full_text += text + "\n\n"
                    if full_text.strip():
                        st.session_state.rag = SimpleRAG(full_text)
                        st.session_state.knowledge_loaded = True
                        st.session_state.uploaded_text = full_text
                        st.success(f"✅ Processed {len(uploaded_files)} document(s)")
                    else:
                        st.warning("No text extracted from files.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.info("Upload files for document Q&A")
        if st.session_state.knowledge_loaded:
            st.success("🧠 Document knowledge ACTIVE")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sb-card-global">', unsafe_allow_html=True)
        st.markdown('<div class="sb-label-global"><i class="fas fa-tools"></i> CONTROLS</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.button("🔄 Reset Knowledge", use_container_width=True):
            st.session_state.rag = SimpleRAG()
            st.session_state.knowledge_loaded = False
            st.session_state.uploaded_text = ""
            st.success("Knowledge base reset successfully!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- HEADER RENDER --------------------
def render_header():
    st.markdown("""
    <div class="global-header">
        <h1><i class="fas fa-globe-americas"></i> Global AI Assistant</h1>
        <p>Limitless intelligence — Code, Write, Analyze, Research, Create</p>
        <div>
            <span class="badge-global badge-blue"><i class="fas fa-code"></i> Code Expert</span>
            <span class="badge-global badge-purple"><i class="fas fa-pen-fancy"></i> Writing</span>
            <span class="badge-global badge-pink"><i class="fas fa-microscope"></i> Science</span>
            <span class="badge-global badge-cyan"><i class="fas fa-file-alt"></i> Document Q&A</span>
            <span class="badge-global badge-green"><i class="fas fa-chart-line"></i> Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_welcome():
    st.markdown("""
    <div class="welcome-global">
        <div class="welcome-icon-global">🌍✨</div>
        <div class="welcome-title-global">How can I assist you today?</div>
        <p style="color: #cbd5e1; max-width: 600px; margin: 12px auto;">Your universal AI companion for coding, writing, research, and everyday questions.</p>
        <div style="margin-top: 28px;">
            <span class="chip-global"><i class="fas fa-chart-simple"></i>Startup & Business</span>
            <span class="chip-global"><i class="fas fa-envelope"></i> Professional Work </span>
            <span class="chip-global"><i class="fas fa-atom"></i> Learning & Tech</span>
            <span class="chip-global"><i class="fas fa-file-pdf"></i> Travel & Tourism</span>
            <span class="chip-global"><i class="fas fa-history"></i> General Knowledge</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# -------------------- MAIN --------------------
def main():
    init_session()
    render_sidebar()

    with st.container():
        render_header()

        if not st.session_state.messages:
            render_welcome()
        else:
            render_messages()

        question = st.chat_input("Ask me anything...")

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("🌐 Global AI is thinking..."):
                    retrieved_chunks = []
                    if st.session_state.knowledge_loaded and st.session_state.uploaded_text:
                        retrieved_chunks = st.session_state.rag.retrieve(question)

                    groq_key = os.getenv("GROQ_API_KEY")
                    if not groq_key:
                        st.error("GROQ_API_KEY not found. Please check your .env file.")
                        st.stop()

                    chat_model = get_chatgroq_model()
                    response = get_chat_response(
                        chat_model=chat_model,
                        question=question,
                        history=st.session_state.messages[:-1],
                        system_prompt=build_system_prompt(st.session_state.response_mode),
                        retrieved_chunks=retrieved_chunks,
                    )
                    st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()