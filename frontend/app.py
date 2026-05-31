import requests
import streamlit as st
import time

# =====================
# CONFIGURATION & STATE
# =====================
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Nexus AI", layout="wide", initial_sidebar_state="expanded")

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "audio_messages" not in st.session_state:
    st.session_state.audio_messages = []
if "pdf_messages" not in st.session_state:
    st.session_state.pdf_messages = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

# =====================
# GALAXY GLASSMORPHISM UI
# =====================
dynamic_ui_css = """
<style>
    /* ── GOOGLE FONTS & MATERIAL ICONS ── */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Rajdhani:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

    /* ── ANIMATIONS ── */
    @keyframes glowPulse {
        0%, 100% { text-shadow: 0 0 10px rgba(139,92,246,0.8), 0 0 30px rgba(59,130,246,0.4); }
        50%       { text-shadow: 0 0 20px rgba(168,85,247,1),   0 0 60px rgba(99,102,241,0.6); }
    }
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(99,102,241,0.25); }
        50%      { border-color: rgba(168,85,247,0.55); }
    }

    /* ── CRITICAL FIX: PROTECT MATERIAL ICONS ── */
    .material-symbols-rounded, 
    .material-icons, 
    [class*="icon"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="chatAvatarIcon-user"] svg,
    [data-testid="chatAvatarIcon-assistant"] svg {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-weight: normal !important;
        font-style: normal !important;
    }

    /* ── DEEP SPACE BACKGROUND ── */
    .stApp {
        background-color: #020408 !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 20% 30%, rgba(88,28,135,0.18) 0%, transparent 60%),
            radial-gradient(ellipse 60% 70% at 80% 70%, rgba(30,58,138,0.15) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 50% 10%, rgba(124,58,237,0.10) 0%, transparent 60%),
            radial-gradient(ellipse 40% 60% at 10% 85%, rgba(55,48,163,0.12) 0%, transparent 60%),
            linear-gradient(135deg, #020408 0%, #05091a 30%, #080416 60%, #020a12 100%) !important;
        background-attachment: fixed !important;
        color: #e2e8f0 !important;
        min-height: 100vh;
    }

    p, label, li, input, textarea, .stMarkdown {
        font-family: 'Space Grotesk', sans-serif;
        color: #cbd5e1 !important;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(5,8,30,0.92) 0%, rgba(10,5,25,0.95) 100%) !important;
        backdrop-filter: blur(30px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
        border-right: 1px solid rgba(139,92,246,0.25) !important;
        box-shadow: 4px 0 40px rgba(88,28,135,0.3) !important;
    }

    /* ── MAIN BLOCK CONTAINER ── */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        background: transparent !important;
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        max-width: 1100px !important;
    }

    /* ── HEADINGS ── */
    h1 {
        font-family: 'Orbitron', monospace !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        letter-spacing: 3px !important;
        color: transparent !important;
        background: linear-gradient(135deg, #e0e7ff 0%, #a78bfa 30%, #60a5fa 60%, #c084fc 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        animation: glowPulse 4s ease-in-out infinite !important;
        text-transform: uppercase !important;
        margin: 0 0 0.75rem 0 !important;
        line-height: 1.2 !important;
    }
    h2 {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        color: #a78bfa !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        font-size: 1.15rem !important;
        margin-top: 1rem !important;
    }
    h3 {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 500 !important;
        color: #93c5fd !important;
        letter-spacing: 1px !important;
    }

    /* ── LAYOUT FIX: NO GLASS-BOX ON EVERY COLUMN ── */
    div[data-testid="column"] {
        background: transparent !important;
        backdrop-filter: none !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.75rem !important;
        align-items: center !important;
    }

    /* ── CHAT MESSAGE BUBBLES ── */
    .stChatMessage {
        background: rgba(15, 10, 40, 0.55) !important;
        backdrop-filter: blur(20px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
        border: 1px solid rgba(139,92,246,0.2) !important;
        border-radius: 16px !important;
        margin-bottom: 12px !important;
        padding: 14px 18px !important;
        animation: borderGlow 6s ease-in-out infinite !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px rgba(88,28,135,0.2) !important;
    }
    .stChatMessage:hover {
        background: rgba(20, 15, 55, 0.7) !important;
        border-color: rgba(167,139,250,0.5) !important;
        box-shadow: 0 12px 48px rgba(139,92,246,0.3) !important;
    }
    
    .stChatMessage div[data-testid="stHorizontalBlock"] { 
        align-items: center !important; 
    }
    .stChatMessage div[data-testid="column"] {
        display: flex !important;
        align-items: center !important;
    }
    .stChatMessage .stMarkdown {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    /* ── CHAT AVATAR ICONS ── */
    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #ec4899, #a855f7) !important;
        box-shadow: 0 0 20px rgba(236,72,153,0.6) !important;
        border: 1px solid rgba(236,72,153,0.4) !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #06b6d4, #3b82f6) !important;
        box-shadow: 0 0 20px rgba(6,182,212,0.6) !important;
        border: 1px solid rgba(6,182,212,0.4) !important;
    }

    /* ── CHAT INPUT ── */
    [data-testid="stChatInput"] {
        background: transparent !important;
    }
    [data-testid="stChatInput"] > div {
        background: rgba(5,8,30,0.85) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(99,102,241,0.4) !important;
        border-radius: 50px !important;
        box-shadow: 0 0 30px rgba(99,102,241,0.2) !important;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: rgba(167,139,250,0.8) !important;
        box-shadow: 0 0 50px rgba(139,92,246,0.4) !important;
    }
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #e2e8f0 !important;
        caret-color: #a78bfa !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(167,139,250,0.5) !important;
        font-style: italic !important;
    }

    /* ── TEXT INPUTS ── */
    div[data-testid="stTextInput"] > div > div > input,
    div[data-testid="stTextArea"] > div > div > textarea {
        background: rgba(8,5,25,0.7) !important;
        border: 1px solid rgba(99,102,241,0.35) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus,
    div[data-testid="stTextArea"] > div > div > textarea:focus {
        border-color: rgba(139,92,246,0.8) !important;
        box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important;
        outline: none !important;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: linear-gradient(135deg, rgba(79,70,229,0.85), rgba(124,58,237,0.85), rgba(139,92,246,0.85)) !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        border-radius: 50px !important;
        color: #f0e6ff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        padding: 0.5rem 1.25rem !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
        box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 40px rgba(139,92,246,0.6) !important;
        border-color: rgba(196,181,253,0.6) !important;
    }
    
    /* ── SMALL PURGE (TRASH) ICON IN CHAT ── */
    .stChatMessage .stButton > button {
        padding: 0 !important;
        width: 32px !important;
        height: 32px !important;
        min-height: 32px !important;
        border-radius: 50% !important; 
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        line-height: 1 !important;
    }

    /* ── FILE UPLOADER ── */
    div[data-testid="stFileUploader"] {
        background: rgba(8,5,30,0.6) !important;
        border: 2px dashed rgba(99,102,241,0.4) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(167,139,250,0.7) !important;
        background: rgba(12,8,40,0.7) !important;
    }
    div[data-testid="stFileUploader"] button {
        background: rgba(99,102,241,0.2) !important;
        border-radius: 8px !important;
    }

    /* ── RADIO ── */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        background: transparent !important;
        gap: 6px !important;
        flex-direction: column !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label {
        background: rgba(20,15,50,0.5) !important;
        border: 1px solid rgba(99,102,241,0.15) !important;
        border-radius: 10px !important;
        padding: 8px 14px !important;
        margin: 0 !important;
        transition: all 0.25s ease !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background: rgba(99,102,241,0.2) !important;
        border-color: rgba(167,139,250,0.4) !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(5,5,20,0.6) !important;
        border-radius: 50px !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        padding: 4px !important;
        gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #94a3b8 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 8px 24px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #c4b5fd !important;
        background: rgba(99,102,241,0.15) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.7), rgba(139,92,246,0.7)) !important;
        color: #f0e6ff !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem !important; }

    /* ── EXPANDER (HIDE/SHOW HISTORY) ── */
    [data-testid="stExpander"] {
        background: rgba(20,15,50,0.4) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] > summary {
        background: rgba(10,5,25,0.6) !important;
        padding: 10px 15px !important;
    }

    /* ── STATUS / ALERTS ── */
    [data-testid="stStatusWidget"],
    [data-testid="stAlert"] {
        background: rgba(10,8,35,0.85) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 12px !important;
    }

    /* ── DIVIDER ── */
    hr {
        border: none !important;
        border-top: 1px solid rgba(99,102,241,0.2) !important;
        margin: 1.25rem 0 !important;
    }

    /* ── SIDEBAR HEADINGS ── */
    [data-testid="stSidebar"] h1 {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.1rem !important;
        letter-spacing: 3px !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(5,5,20,0.5); border-radius: 4px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #4f46e5, #7c3aed);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #6366f1, #8b5cf6); }

    /* ── HIDE DEPLOY BUTTON & FIX HEADER ── */
    .stDeployButton {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: rgba(2,4,8,0.6) !important;
        backdrop-filter: blur(20px) !important;
        border-bottom: 1px solid rgba(99,102,241,0.15) !important;
    }

    /* ── SPINNER COLOR ── */
    [data-testid="stSpinner"] > div { border-top-color: #a78bfa !important; }
</style>
"""

st.markdown(dynamic_ui_css, unsafe_allow_html=True)

# =====================
# SIDEBAR NAVIGATION & DATA MANAGEMENT
# =====================
st.sidebar.title("🌌 NEXUS AI")
page = st.sidebar.radio(
    "Navigation Menu",
    ["💬 Universal Chat", "🎧 Audio Intelligence", "📄 PDF Analyzer"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

# Wrap the memory inside an expander so it can be hidden/shown easily
with st.sidebar.expander("🗄️ Database Memory", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Refresh"):
            st.rerun()
                
    # NEW FEATURE: Erase Everything Option
    with col_b:
        if st.button("🚨 Erase All"):
            try:
                response = requests.delete(
                    f"{BASE_URL}/system/wipe-all",
                    timeout=60
                )
                if response.status_code == 200:

                    for key in list(st.session_state.keys()):
                        del st.session_state[key]

                    st.success(
                    "Everything Deleted Successfully!"
                    )

                    time.sleep(1)

                    st.rerun()

                else:

                    st.error(
                        f"Backend Error [{response.status_code}]"
                )
            except Exception as e:

                st.error(
                f"Failed: {str(e)}"
            )    
                     
                
            
            

    st.markdown("---")

# =====================
# CHAT PAGE
# =====================
if page == "💬 Universal Chat":
    st.title("💬 Universal Neural Chat")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Initialize New Session", key="new_session_btn"):
            st.session_state.chat_id = None
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🚨 Purge Entire History", key="purge_history_btn"):
            if st.session_state.chat_id:
                try:
                    requests.delete(f"{BASE_URL}/chat/history/{st.session_state.chat_id}", timeout=5)
                except Exception:
                    pass
            st.session_state.messages = []
            st.rerun()

    if st.session_state.chat_id is None:

        try:

            history_res = requests.get(
                f"{BASE_URL}/chat/history",
                timeout=5
            )

            if history_res.status_code == 200:

                chats = history_res.json()

                if chats:

                    latest_chat = chats[0]

                    st.session_state.chat_id = latest_chat["id"]

                    msg_res = requests.get(
                        f"{BASE_URL}/chat/messages/{latest_chat['id']}",
                        timeout=5
                    )

                    if msg_res.status_code == 200:

                     st.session_state.messages = msg_res.json()

                else:

                    res = requests.post(
                    f"{BASE_URL}/chat/new-chat",
                    timeout=5
                    )

                    if res.status_code == 200:

                        st.session_state.chat_id = (
                        res.json()["chat_id"]
                        )

                        st.session_state.messages = []

        except requests.exceptions.RequestException:

            st.error(
            "Neural link severed. Cannot connect to backend."
         )

    st.markdown("---")

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            mcol, bcol = st.columns([12, 1])
            mcol.markdown(msg["content"])
            if bcol.button("🗑️", key=f"del_msg_{i}"):
                try:
                    requests.delete(f"{BASE_URL}/chat/message/{msg.get('id', i)}", timeout=5)
                except Exception: pass
                st.session_state.messages.pop(i)
                st.rerun()

    prompt = st.chat_input("Transmit message to the cosmos...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        try:
            response = requests.post(
                f"{BASE_URL}/chat/send",
                json={"chat_id": st.session_state.chat_id, "message": prompt},
                timeout=60,
            )
            # Upgraded error handling 
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", data.get("answer", "No response received."))
                st.session_state.messages[-1] = {
                "id": data.get("user_message_id"),
                "role": "user",
                "content": prompt
                }

                st.session_state.messages.append(
                {
                "id": data.get("assistant_message_id"),
                 "role": "assistant",
                 "content": answer
                }
                )
                with st.chat_message("assistant"):
                    st.markdown(answer)
            else:
                st.error(f"Backend Error [{response.status_code}]: {response.text}")
        except Exception as e:
            st.error(f"Failed to transmit signal: {str(e)}")

# =====================
# AUDIO PAGE
# =====================
elif page == "🎧 Audio Intelligence":
    st.title("🎧 Audio Intelligence Core")
    st.markdown("Extract knowledge from videos or local audio files.")

    tab1, tab2 = st.tabs(["📺 Process YouTube Link", "🎵 Upload Local Audio"])

    with tab1:
        st.subheader("Extract from YouTube")
        youtube_url = st.text_input(
            "YouTube URL",
            label_visibility="collapsed",
            placeholder="https://youtube.com/watch?v=...",
        )
        if st.button("Initiate YouTube Processing", key="yt_btn"):
            with st.status("📡 Connecting to YouTube Data Stream...", expanded=True) as status:
                st.write("Downloading audio footprint...")
                try:
                    response = requests.post(f"{BASE_URL}/audio/youtube", data={"url": youtube_url}, timeout=3600)
                    if response.status_code == 200:
                        status.update(label="Transcription Complete!", state="complete", expanded=False)
                        result = response.json()
                        # result = response.json()

                        # st.write("DEBUG RESPONSE:")
                        # st.json(result)

                        st.session_state.audio_session = result.get("session_id", "default")
                        st.subheader("📋Summary")
                        st.write(
                                result.get(
                                    "summary",
                                    "No summary available."
                                )
                            )

                        st.subheader("✅ Action Items")
                        st.write(
                                result.get(
                                    "actions",
                                    []
                                )
                            )

                        st.subheader("🎯 Key Decisions")
                        st.write(
                                result.get(
                                    "decisions",
                                    []
                                )
                            )

                        st.subheader("❓ Questions Raised")
                        st.write(
                                result.get(
                                    "questions",
                                    []
                                )
                            )
                    else:
                        status.update(label=f"Error: {response.status_code}", state="error")
                except Exception as e:
                    status.update(label=f"Link failed: {str(e)}", state="error")

    with tab2:
        st.subheader("Process Local File")
        uploaded_audio = st.file_uploader("Drop your .mp3, .wav, or .m4a file here", type=["mp3", "wav", "m4a"])
        if uploaded_audio:
            if st.button("Initiate Local Processing", key="upload_btn"):
                with st.status("🎵 Analyzing Local Audio Frequencies...", expanded=True) as status:
                    st.write("Uploading file to neural net...")
                    try:
                        files = {"file": (uploaded_audio.name, uploaded_audio, uploaded_audio.type)}
                        response = requests.post(f"{BASE_URL}/audio/upload", files=files, timeout=120)
                        if response.status_code == 200:
                            status.update(label="Audio Successfully Processed!", state="complete", expanded=False)
                            result = response.json()
                            st.session_state.audio_session = result.get("session_id", "default")
                            st.session_state.audio_messages = []

                            # st.session_state.audio_summary = result.get("summary", "")
                            # st.session_state.audio_actions = result.get("actions", [])
                            # st.session_state.audio_decisions = result.get("decisions", [])
                            # st.session_state.audio_questions = result.get("questions", [])
                            st.subheader("📋Summary")
                            st.write(
                                result.get(
                                    "summary",
                                    "No summary available."
                                )
                            )

                            st.subheader("✅ Action Items")
                            st.write(
                                result.get(
                                    "actions",
                                    []
                                )
                            )

                            st.subheader("🎯 Key Decisions")
                            st.write(
                                result.get(
                                    "decisions",
                                    []
                                )
                            )

                            st.subheader("❓ Questions Raised")
                            st.write(
                                result.get(
                                    "questions",
                                    []
                                )
                            )
                        else:
                            status.update(label=f"Upload corrupted: {response.status_code}", state="error")
                    except Exception as e:
                        status.update(label=f"Link failed: {str(e)}", state="error")
                    # if st.session_state.get("audio_summary"):

                    #     st.subheader("📋 Meeting Summary")
                    #     st.write(st.session_state.audio_summary)

                    #     st.subheader("✅ Action Items")
                    #     st.write(st.session_state.audio_actions)

                    #     st.subheader("🎯 Key Decisions")
                    #     st.write(st.session_state.audio_decisions)

                    #     st.subheader("❓ Questions Raised")
                    #     st.write(st.session_state.audio_questions)

    st.markdown("---")

    if "audio_session" in st.session_state:
        st.subheader("🧠 Interrogate Audio Data")
        if st.button("🧹 Clear Audio Context Chat", key="clear_audio_btn"):
            st.session_state.audio_messages = []
            st.rerun()
            
        for msg in st.session_state.audio_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        question = st.chat_input("Ask a question regarding the transcribed audio...")
        if question:
            st.session_state.audio_messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            try:
                res = requests.post(
                    f"{BASE_URL}/audio/ask",
                    json={"session_id": st.session_state.audio_session, "question": question},
                    timeout=3600,
                )
                # Upgraded Error Handling & JSON Fallbacks
                if res.status_code == 200:
                    data = res.json()
                    ans = data.get("answer", data.get("response", "No response output from API."))
                    st.session_state.audio_messages.append({"role": "assistant", "content": ans})
                    with st.chat_message("assistant"):
                        st.markdown(ans)
                else:
                    st.error(f"Backend Error [{res.status_code}]: {res.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")

# =====================
# PDF PAGE
# =====================
elif page == "📄 PDF Analyzer":
    st.title("📄 PDF Matrix Analyzer")
    st.markdown("Upload documents for deep text extraction and AI analysis.")

    pdf_file = st.file_uploader("Drop your PDF document here", type=["pdf"])

    if pdf_file:
        if st.button("Analyze PDF Matrix", key="pdf_btn"):
            with st.status("🔮 Scanning Document Architecture...", expanded=True) as status:
                st.write("Extracting raw text data...")
                try:
                    files = {"file": (pdf_file.name, pdf_file, "application/pdf")}
                    response = requests.post(f"{BASE_URL}/pdf/upload", files=files, timeout=120)
                    if response.status_code == 200:
                        status.update(label="PDF Fully Ingested!", state="complete", expanded=False)
                        st.success("Document added to memory matrix successfully.")
                        result = response.json()
                        
                        # NEW: Bind the PDF session to enable chat
                        st.session_state.pdf_session = result.get("session_id", "default_pdf")
                        st.session_state.pdf_messages = []
                        st.subheader("📄 PDF Summary")

                        st.write(
                            result.get(
                                "summary",
                                "No summary available."
                            )
                        )
                    else:
                        status.update(label=f"Analysis Failed [{response.status_code}]", state="error")
                except Exception as e:
                    status.update(label=f"Connection Severed: {str(e)}", state="error")

    # NEW FEATURE: Full chat UI specifically for the PDF document
    if "pdf_session" in st.session_state:
        st.markdown("---")
        st.subheader("🧠 Interrogate Document Data")
        if st.button("🧹 Clear PDF Context Chat", key="clear_pdf_btn"):
            st.session_state.pdf_messages = []
            st.rerun()
            
        for msg in st.session_state.pdf_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        question = st.chat_input("Ask a question regarding the PDF...")
        if question:
            st.session_state.pdf_messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            try:
                # Assuming your backend uses /pdf/ask. If it uses /chat/send, you can update the URL below.
                res = requests.post(
                    f"{BASE_URL}/pdf/ask",
                    json={"session_id": st.session_state.pdf_session, "question": question},
                    timeout=60,
                )
                if res.status_code == 200:
                    data = res.json()
                    ans = data.get("answer", data.get("response", "No response output from API."))
                    st.session_state.pdf_messages.append({"role": "assistant", "content": ans})
                    with st.chat_message("assistant"):
                        st.markdown(ans)
                else:
                    st.error(f"Backend Error [{res.status_code}]: {res.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")