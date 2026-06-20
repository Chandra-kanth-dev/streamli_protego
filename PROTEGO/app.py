import streamlit as st
import sys
import os
import uuid
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from protego.api.chatbot_service import handle_message
from protego.logic.context_memory import ContextMemory
import protego.logic.db_helper as db
from protego.logic.rag_engine import query_kb

# ---------------------------------------------------------
# Page Configurations & Design System
# ---------------------------------------------------------
st.set_page_config(
    page_title="PROTEGO AI — Safety & Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling & Typography & Safety Listeners
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,300&family=DM+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .stApp {
        background-color: #06060c;
        background-image:
          radial-gradient(ellipse 900px 600px at 10% 15%, rgba(230,52,98,0.06) 0%, transparent 60%),
          radial-gradient(ellipse 700px 500px at 85% 80%, rgba(0,212,170,0.05) 0%, transparent 60%),
          radial-gradient(ellipse 600px 400px at 60% 20%, rgba(91,141,238,0.05) 0%, transparent 60%);
        color: #eeeef8;
        font-family: 'DM Sans', sans-serif;
    }
    
    /* High-tech Blueprint Grid overlay */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: linear-gradient(rgba(255, 255, 255, 0.012) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255, 255, 255, 0.012) 1px, transparent 1px);
        background-size: 36px 36px;
        pointer-events: none;
        z-index: 0;
    }
    
    /* Custom Sidebar Overwrite */
    [data-testid="stSidebar"] {
        background-color: #090911 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        color: #e63462 !important;
    }
    
    /* Header Customization */
    h1, h2, h3, h4, h5, h6, .brand-text {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        color: #ffffff !important;
    }
    
    /* General text contrast normalization (Prevents dark gray text merge) */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #d1d1e0 !important;
    }
    
    /* Widget Labels (White text for high contrast) */
    [data-testid="stWidgetLabel"] p, label, .stWidgetLabel, [data-testid="stWidgetLabel"] {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }
    
    /* Sidebar text fields & controls contrast */
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] div[data-testid="stRadio"] label p,
    [data-testid="stSidebar"] div[data-testid="stRadio"] label span {
        color: #ffffff !important;
    }
    
    /* Command Center KPI Metrics card styling */
    .metric-card {
        background: rgba(14, 14, 25, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s ease-in-out !important;
        margin-bottom: 15px !important;
    }
    .metric-card:hover {
        border-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    .metric-lbl {
        font-size: 0.82rem !important;
        color: rgba(240, 240, 248, 0.55) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 6px !important;
    }
    .metric-val {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        font-family: 'Syne', sans-serif !important;
        line-height: 1.0 !important;
        margin-bottom: 4px !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(230, 52, 98, 0.35);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(230, 52, 98, 0.55);
    }
    
    /* Premium Glassmorphism Cards */
    .glass-card {
        background: rgba(14, 14, 25, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .glass-card:hover {
        border-color: rgba(230, 52, 98, 0.25);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 15px rgba(230, 52, 98, 0.1);
        transform: translateY(-2px);
    }
    
    .glass-card-header {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 15px;
        color: #ffffff !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        padding-bottom: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Input Elements high contrast backgrounds & text */
    input[type="text"], input[type="number"], textarea, .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #121224 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }
    input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
        border-color: #00d4aa !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.15) !important;
        color: #ffffff !important;
    }
    
    /* Selectboxes overrides */
    div[data-baseweb="select"] > div {
        background-color: #121224 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    /* Dropdown popovers (unifies options listing) */
    div[role="listbox"], div[data-baseweb="popover"], [data-baseweb="popover"] {
        background-color: #121224 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    div[role="option"] {
        color: #eeeef8 !important;
    }
    div[role="option"]:hover, div[role="option"][aria-selected="true"] {
        background-color: rgba(230, 52, 98, 0.2) !important;
        color: #e63462 !important;
    }
    
    /* Expanders design */
    [data-testid="stExpander"] {
        background-color: rgba(18, 18, 32, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] details summary {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* Tab Styling Overwrites */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-bottom: none !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 18px !important;
        color: rgba(238, 238, 248, 0.5) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(230, 52, 98, 0.1) !important;
        border-color: rgba(230, 52, 98, 0.35) !important;
        color: #e63462 !important;
    }
    
    /* Segmented Control Overwrites */
    .stSegmentedControl button {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: rgba(238, 238, 248, 0.6) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
    }
    .stSegmentedControl button[aria-checked="true"] {
        background-color: rgba(230, 52, 98, 0.15) !important;
        border-color: rgba(230, 52, 98, 0.45) !important;
        color: #e63462 !important;
        font-weight: bold !important;
    }
    
    /* Chat Input Custom Styling */
    [data-testid="stChatInput"] textarea {
        background-color: rgba(14, 14, 25, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 12px !important;
        color: #eeeef8 !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #00d4aa !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.15) !important;
    }
    
    /* Chat Bubble Design */
    .chat-bubble-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-height: 520px;
        overflow-y: auto;
        padding: 10px;
        margin-bottom: 15px;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #00d4aa, #00b896);
        color: #001a14;
        font-weight: 500;
        border-radius: 16px;
        border-bottom-right-radius: 4px;
        padding: 12px 18px;
        align-self: flex-end;
        max-width: 75%;
        word-break: break-word;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.15);
        font-size: 0.88rem;
    }
    
    .bot-bubble {
        background: rgba(22, 22, 38, 0.85);
        color: #eeeef8;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        border-bottom-left-radius: 4px;
        padding: 12px 18px;
        align-self: flex-start;
        max-width: 75%;
        word-break: break-word;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        font-size: 0.88rem;
    }
    
    .bot-bubble.emergency {
        border: 1.5px solid #e63462;
        background: rgba(230, 52, 98, 0.12);
        box-shadow: 0 0 20px rgba(230, 52, 98, 0.25);
    }
    
    .emergency-toast {
        background: linear-gradient(135deg, #2a0a12, #1a0610);
        border: 1.5px solid #e63462;
        border-radius: 12px;
        padding: 18px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(230, 52, 98, 0.35);
    }
    
    /* Dataframes/Tables borders overrides */
    [data-testid="stDataFrame"] {
        background-color: #0c0c16 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }
    
    /* Quick Escape Button */
    .stButton>button.quick-escape-btn {
        background: linear-gradient(135deg, #e63462, #991234) !important;
        color: white !important;
        border: none !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 20px rgba(230, 52, 98, 0.4) !important;
        transition: all 0.3s !important;
    }
    .stButton>button.quick-escape-btn:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(230, 52, 98, 0.6) !important;
    }
</style>

<script>
    // Physical Escape Key event listener for Quick Redirect
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            window.location.href = 'https://google.com';
        }
    });
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = "u_" + str(uuid.uuid4())[:8]

if "user_name" not in st.session_state:
    st.session_state.user_name = "Anonymous Survivor"

if "user_email" not in st.session_state:
    st.session_state.user_email = "anonymous@protego.org"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "text": "Hello 🤍 I'm here for you. Whatever you're going through, you don't have to face it alone. How can I help you today?", "risk": "low"}
    ]

if "context_memory" not in st.session_state:
    st.session_state.context_memory = ContextMemory(max_history=5)

if "active_risk" not in st.session_state:
    st.session_state.active_risk = "low"

# RAG default search article
if "current_rag_insight" not in st.session_state:
    st.session_state.current_rag_insight = {
        "title": "Digital Privacy & Device Security",
        "category": "Technology Safety",
        "content": "To secure your digital privacy: 1. Turn off location sharing services (GPS) in your phone settings. 2. Clear your browser history regularly, or use incognito/private tabs. 3. Change passwords for emails and banking; use strong, unique passwords not easily guessed. 4. If safe, use a separate, hidden phone or a public library computer for safety planning.",
        "score": 1.0
    }

# Countries List for Selectors & Emergency Grid
COUNTRIES_DATA = {
    "India": {"flag": "🇮🇳", "region": "South Asia", "police": "100", "ambulance": "102", "helpline": "1091", "dv_hotline": "181"},
    "United States": {"flag": "🇺🇸", "region": "Americas", "police": "911", "ambulance": "911", "helpline": "Text HOME to 741741", "dv_hotline": "1-800-799-7233"},
    "United Kingdom": {"flag": "🇬🇧", "region": "Europe", "police": "999", "ambulance": "999", "helpline": "111 (NHS)", "dv_hotline": "0808 2000 247"},
    "Australia": {"flag": "🇦🇺", "region": "Oceania", "police": "000", "ambulance": "000", "helpline": "13 11 14 (Lifeline)", "dv_hotline": "1800 737 732"},
    "Canada": {"flag": "🇨🇦", "region": "Americas", "police": "911", "ambulance": "911", "helpline": "1-833-456-4566", "dv_hotline": "1-866-863-0511"},
    "Germany": {"flag": "🇩🇪", "region": "Europe", "police": "110", "ambulance": "112", "helpline": "116 006", "dv_hotline": "08000 116 016"},
    "Pakistan": {"flag": "🇵🇰", "region": "Asia", "police": "15", "ambulance": "1122", "helpline": "1242 (Legal Aid)", "dv_hotline": "1099"},
    "South Africa": {"flag": "🇿🇦", "region": "Africa", "police": "10111", "ambulance": "10177", "helpline": "112 (Mobile)", "dv_hotline": "0800 428 428"},
    "Brazil": {"flag": "🇧🇷", "region": "Americas", "police": "190", "ambulance": "192", "helpline": "193 (Fire)", "dv_hotline": "180"},
    "Kenya": {"flag": "🇰🇪", "region": "Africa", "police": "999", "ambulance": "112", "helpline": "116 (Child)", "dv_hotline": "1195"},
    "Japan": {"flag": "🇯🇵", "region": "Asia", "police": "110", "ambulance": "119", "helpline": "0120-279-338", "dv_hotline": "0570-0-55210"},
    "France": {"flag": "🇫🇷", "region": "Europe", "police": "17", "ambulance": "15", "helpline": "112", "dv_hotline": "3919"}
}

# ---------------------------------------------------------
# Sidebar Layout & Quick Escape
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 class='brand-text' style='color:#e63462; font-size:2.2rem;'>🛡️ PROTEGO</h1><small style='color:rgba(240,240,248,0.5); font-family:\"DM Mono\"'>V1.2 — AI Safety Portal</small></div>", unsafe_allow_html=True)
    
    # 🚨 QUICK ESCAPE BUTTON
    # Instantly navigates user away from the site to Google.com
    if st.button("🚨 QUICK ESCAPE (ESC)", width="stretch", type="primary", key="quick_escape", help="Redirects this page to Google immediately for safety"):
        st.markdown("<script>window.location.href = 'https://google.com';</script>", unsafe_allow_html=True)
        st.info("Redirecting to Google...")
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 15px 0;'/>", unsafe_allow_html=True)
    
    # Navigation Selector
    page = st.radio(
        "Navigation",
        options=["💬 PROTEGO Assistant", "📊 Admin Console", "🆘 Emergency Directory", "⚙️ How It Works & Safety Planning"],
        index=0
    )
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 15px 0;'/>", unsafe_allow_html=True)
    
    # Quick Configs
    selected_country = st.selectbox(
        "Your Country",
        options=list(COUNTRIES_DATA.keys()),
        index=0,
        help="Surfaces your local country emergency services dynamically."
    )
    
    # User Profile Customization (No Login needed)
    with st.expander("👤 Customize User Profile (Optional)"):
        new_name = st.text_input("Name", value=st.session_state.user_name)
        new_email = st.text_input("Email", value=st.session_state.user_email)
        if st.button("Save Profile"):
            st.session_state.user_name = new_name
            st.session_state.user_email = new_email
            # Insert/update user in SQLite
            db.add_user(st.session_state.user_id, new_name, new_email)
            st.success("Profile saved!")
            
    # Reset Chat History button
    if st.button("🗑️ Reset Chat Session"):
        st.session_state.chat_history = [
            {"role": "bot", "text": "Hello 🤍 I'm here for you. Whatever you're going through, you don't have to face it alone. How can I help you today?", "risk": "low"}
        ]
        st.session_state.context_memory.reset()
        st.session_state.active_risk = "low"
        st.session_state.current_rag_insight = {
            "title": "Digital Privacy & Device Security",
            "category": "Technology Safety",
            "content": "To secure your digital privacy: 1. Turn off location sharing services (GPS) in your phone settings. 2. Clear your browser history regularly, or use incognito/private tabs. 3. Change passwords for emails and banking; use strong, unique passwords not easily guessed. 4. If safe, use a separate, hidden phone or a public library computer for safety planning.",
            "score": 1.0
        }
        st.rerun()

# ---------------------------------------------------------
# Page 1: 💬 PROTEGO AI Assistant
# ---------------------------------------------------------
if page == "💬 PROTEGO Assistant":
    st.markdown("<h1>You Are <span style='background: linear-gradient(135deg, #e63462, #f4b942); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Not Alone.</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(240,240,248,0.65); font-size:1.1rem; margin-top:-10px;'>24/7 confidential crisis prevention assistant. Powered by risk-assessment AI.</p>", unsafe_allow_html=True)
    
    # Show active Emergency alert panel if risk levels trigger it
    if st.session_state.active_risk in {"high", "emergency"}:
        st.markdown(f"""
        <div class="emergency-toast">
            <h3 style="margin-top:0; color:#e63462; font-family:'Syne'">🚨 IMMEDIATE CRISIS CONTACTS FOR {selected_country.upper()}</h3>
            <p style="margin-bottom:12px; font-size:0.92rem; color:rgba(255,255,255,0.85)">
                PROTEGO has detected high stress or emergency signals. If you are in immediate danger, please reach out to the authorities immediately. Your safety is paramount.
            </p>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <a href="tel:{COUNTRIES_DATA[selected_country]['police']}" style="background:#e63462; color:white; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:0.85rem;">📞 Call Police ({COUNTRIES_DATA[selected_country]['police']})</a>
                <a href="tel:{COUNTRIES_DATA[selected_country]['dv_hotline']}" style="background:#f4b942; color:#0a0a12; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:0.85rem;">🆘 DV Hotline ({COUNTRIES_DATA[selected_country]['dv_hotline']})</a>
                <a href="tel:{COUNTRIES_DATA[selected_country]['ambulance']}" style="background:rgba(255,255,255,0.15); color:white; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:0.85rem;">🚑 Ambulance ({COUNTRIES_DATA[selected_country]['ambulance']})</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_chat, col_info = st.columns([2.2, 1])
    
    with col_chat:
        st.markdown("<div class='glass-card' style='padding:15px; min-height:510px; display:flex; flex-direction:column; justify-content:space-between;'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-header' style='font-size:1rem; display:flex; align-items:center; gap:8px;'><span>🛡️ PROTEGO CHAT BOX</span><div style='width:8px; height:8px; background:#7fffbf; border-radius:50%; box-shadow:0 0 8px #7fffbf'></div><small style='color:rgba(240,240,248,0.4); font-size:0.75rem;'>Confidential & Encrypted</small></div>", unsafe_allow_html=True)
        
        # Render Chat Bubbles
        chat_container_html = "<div class='chat-bubble-container'>"
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_container_html += f"<div class='user-bubble'>{msg['text']}</div>"
            else:
                risk_class = "bot-bubble emergency" if msg.get("risk") in {"high", "emergency"} else "bot-bubble"
                chat_container_html += f"<div class='{risk_class}'>{msg['text']}</div>"
        chat_container_html += "</div>"
        st.markdown(chat_container_html, unsafe_allow_html=True)
        
        # Chat Input Interface
        user_input = st.chat_input("Type your message confidentially...")
        
        if user_input:
            # 1. Save user message in session state
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            
            # 2. Call local NLP message handler
            nlp_res = handle_message(
                message=user_input,
                country=selected_country,
                debug=False,
                context_memory=st.session_state.context_memory
            )
            
            reply_text = nlp_res.get("reply", "I'm here with you 🤍")
            risk_level = nlp_res.get("risk_level", "low")
            
            # 3. Update session state active risk
            st.session_state.active_risk = risk_level
            
            # 4. Save response in session state
            st.session_state.chat_history.append({"role": "bot", "text": reply_text, "risk": risk_level})
            
            # 5. Insert chat log to database (local SQLite with sync fallback)
            db.save_chat(
                user_id=st.session_state.user_id,
                message=user_input,
                response=reply_text,
                risk=risk_level
            )
            
            # 6. Query RAG local knowledge base for semantic guidance match
            rag_docs = query_kb(user_input, top_k=1, min_score=0.04)
            if rag_docs:
                st.session_state.current_rag_insight = rag_docs[0]
            
            # 7. If emergency level is flagged, add a location pin randomly for the admin map showing location
            if risk_level == "emergency":
                coords = {
                    "India": (20.5937, 78.9629),
                    "United States": (37.0902, -95.7129),
                    "United Kingdom": (55.3781, -3.4360),
                    "Australia": (-25.2744, 133.7751),
                    "Canada": (56.1304, -106.3468),
                    "Germany": (51.1657, 10.4515),
                    "South Africa": (-30.5595, 22.9375),
                    "Brazil": (-14.2350, -51.9253),
                    "Kenya": (-0.0236, 37.9062),
                    "Japan": (36.2048, 138.2529),
                    "France": (46.2276, 2.2137),
                    "Pakistan": (30.3753, 69.3451)
                }.get(selected_country, (20.0, 77.0))
                
                offset_lat = random.uniform(-0.15, 0.15)
                offset_lon = random.uniform(-0.15, 0.15)
                db.save_location(st.session_state.user_id, coords[0] + offset_lat, coords[1] + offset_lon)
                
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_info:
        # Dynamic RAG Insight Panel
        if "current_rag_insight" in st.session_state and st.session_state.current_rag_insight:
            insight = st.session_state.current_rag_insight
            score_badge = ""
            if "score" in insight and insight["score"] < 1.0:
                score_badge = f"<span style='float:right; font-size:0.75rem; background:rgba(0,212,170,0.15); color:#00d4aa; padding:2px 8px; border-radius:100px; font-family:\"DM Mono\"'>Match: {int(insight['score']*100)}%</span>"
                
            st.markdown(f"""
            <div class="glass-card" style="border-left: 3px solid #00d4aa; padding: 18px 20px;">
                <div class="glass-card-header" style="font-size:0.92rem; margin-bottom:8px;">💡 SEMANTIC SAFETY ADVICE {score_badge}</div>
                <div style="font-family:'Syne'; font-weight:700; font-size:1rem; color:#f0f0f8; margin-bottom:2px;">{insight['title']}</div>
                <small style="color:rgba(240,240,248,0.4); text-transform:uppercase; font-size:0.67rem; font-family:'DM Mono';">{insight['category']}</small>
                <p style="margin-top:10px; font-size:0.82rem; color:rgba(240,240,248,0.78); line-height:1.5; white-space:pre-wrap;">{insight['content']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="glass-card">
            <div class="glass-card-header">🌍 YOUR LOCAL CONTACTS</div>
            <div style="font-family:'Syne'; font-weight:700; font-size:1.1rem; color:#e63462; margin-bottom:8px;">{selected_country.upper()}</div>
            <table style="width:100%; border-collapse:collapse; font-size:0.88rem;">
                <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                    <td style="padding:8px 0; color:rgba(240,240,248,0.5);">Emergency Line</td>
                    <td style="padding:8px 0; text-align:right; font-weight:bold;"><a href="tel:{COUNTRIES_DATA[selected_country]['police']}" style="color:#00d4aa; text-decoration:none;">{COUNTRIES_DATA[selected_country]['police']}</a></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                    <td style="padding:8px 0; color:rgba(240,240,248,0.5);">DV Hotline</td>
                    <td style="padding:8px 0; text-align:right; font-weight:bold;"><a href="tel:{COUNTRIES_DATA[selected_country]['dv_hotline']}" style="color:#e63462; text-decoration:none;">{COUNTRIES_DATA[selected_country]['dv_hotline']}</a></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                    <td style="padding:8px 0; color:rgba(240,240,248,0.5);">Ambulance</td>
                    <td style="padding:8px 0; text-align:right; font-weight:bold;"><a href="tel:{COUNTRIES_DATA[selected_country]['ambulance']}" style="color:#00d4aa; text-decoration:none;">{COUNTRIES_DATA[selected_country]['ambulance']}</a></td>
                </tr>
                <tr>
                    <td style="padding:8px 0; color:rgba(240,240,248,0.5);">Other Crisis</td>
                    <td style="padding:8px 0; text-align:right; font-size:0.8rem; font-weight:bold; color:#f0f0f8;">{COUNTRIES_DATA[selected_country]['helpline']}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # Calming Breathing Guide Card (Pulsing bubble visualizer)
        st.markdown("""
        <div class="glass-card" style="text-align: center; border-left: 3px solid #5b8dee; padding: 18px 20px;">
            <div class="glass-card-header" style="font-size:0.92rem; margin-bottom:8px;">🌊 CALMING BREATHING CYCLE</div>
            <p style="font-size:0.78rem; color:rgba(240,240,248,0.5); line-height:1.4; margin-bottom:0px; padding: 0 10px;">
                If you feel panicked or overwhelmed, rest your eyes on the bubble and sync your breathing with it.
            </p>
            <style>
            @keyframes breathe {
              0%, 100% { transform: scale(1); background: rgba(0, 212, 170, 0.15); box-shadow: 0 0 10px rgba(0, 212, 170, 0.3); }
              40%, 60% { transform: scale(1.3); background: rgba(0, 212, 170, 0.45); box-shadow: 0 0 30px rgba(0, 212, 170, 0.6); }
            }
            .breathing-circle {
              width: 80px;
              height: 80px;
              border-radius: 50%;
              margin: 25px auto;
              animation: breathe 10s infinite ease-in-out;
              display: flex;
              align-items: center;
              justify-content: center;
              font-family: 'Syne', sans-serif;
              font-weight: bold;
              color: #f0f0f8;
              font-size: 0.8rem;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            }
            .breathe-text::after {
              content: 'Inhale';
              animation: textChange 10s infinite ease-in-out;
            }
            @keyframes textChange {
              0%, 100% { content: 'Inhale'; }
              40%, 60% { content: 'Hold'; }
              60.1%, 99.9% { content: 'Exhale'; }
            }
            </style>
            <div class="breathing-circle"><span class="breathe-text"></span></div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Page 2: 📊 Admin Console
# ---------------------------------------------------------
elif page == "📊 Admin Console":
    st.markdown("<h1>Command <span style='background: linear-gradient(135deg, #e63462, #5b8dee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Center</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(240,240,248,0.65); font-size:1.1rem; margin-top:-10px;'>Real-time AI threat monitoring system & geographic response coordinator.</p>", unsafe_allow_html=True)
    
    # Fetch Data from Local Database/Supabase
    users = db.get_users()
    chats = db.get_chats()
    locations = db.get_locations()
    
    # Calculate Live Statistics
    total_users = len(users)
    total_chats = len(chats)
    high_risk_chats = [c for c in chats if c["risk"] == "high"]
    emergency_chats = [c for c in chats if c["risk"] == "emergency"]
    
    total_high_risk = len(high_risk_chats)
    total_emergency = len(emergency_chats)
    
    # Live Alarm sound trigger simulation if emergency cases exist
    if total_emergency > 0:
        st.markdown("""
        <div class="emergency-toast" style="border-color:#e63462; background:rgba(230,52,98,0.15)">
            <h4 style="color:#e63462; margin-top:0; font-family:'Syne'">🚨 HOSTILE INCIDENT DETECTED</h4>
            <p style="font-size:0.82rem; margin:0; color:rgba(255,255,255,0.8);">
                Active emergency alerts registered. Verify user positions and prepare direct alerts.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    # Standard metric columns (custom styled glass KPI cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card' style='border-top: 3px solid #00d4aa;'><div class='metric-lbl'>Total Users</div><div class='metric-val' style='color:#00d4aa;'>{total_users}</div><small style='font-size:0.72rem; color:rgba(240,240,248,0.4); font-family:\"DM Mono\"'>ACTIVE ACCOUNTS</small></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card' style='border-top: 3px solid #5b8dee;'><div class='metric-lbl'>Total Chats</div><div class='metric-val' style='color:#5b8dee;'>{total_chats}</div><small style='font-size:0.72rem; color:rgba(240,240,248,0.4); font-family:\"DM Mono\"'>LOGGED CONVERSATIONS</small></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card' style='border-top: 3px solid #f4b942;'><div class='metric-lbl'>High Risk</div><div class='metric-val' style='color:#f4b942;'>{total_high_risk}</div><small style='font-size:0.72rem; color:rgba(240,240,248,0.4); font-family:\"DM Mono\"'>DISTRESS SIGNALS</small></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card' style='border-top: 3px solid #e63462; box-shadow: 0 4px 20px rgba(230, 52, 98, 0.15) !important;'><div class='metric-lbl'>Emergency</div><div class='metric-val' style='color:#e63462;'>{total_emergency}</div><small style='font-size:0.72rem; color:rgba(240,240,248,0.4); font-family:\"DM Mono\"'>IMMEDIATE DANGER</small></div>", unsafe_allow_html=True)
        
    # Main Dashboard row
    col_graphs, col_map = st.columns([1, 1])
    
    with col_graphs:
        st.markdown("<div class='glass-card' style='height:400px;'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-header'>📊 Threat Assessment & Activity Trend</div>", unsafe_allow_html=True)
        
        # Risk distribution chart (gorgeous plotly doughnut)
        risk_counts = {"low": 0, "medium": 0, "high": 0, "emergency": 0}
        for c in chats:
            r = c["risk"]
            if r in risk_counts:
                risk_counts[r] += 1
                
        df_risk = pd.DataFrame({
            "Risk Level": [k.upper() for k in risk_counts.keys()],
            "Cases": list(risk_counts.values())
        })
        
        fig = px.pie(
            df_risk, 
            values='Cases', 
            names='Risk Level', 
            hole=0.6,
            color='Risk Level',
            color_discrete_map={
                'LOW': '#00d4aa',
                'MEDIUM': '#f4b942',
                'HIGH': '#e63462',
                'EMERGENCY': '#ff6b9d'
            }
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#eeeef8',
            font_family='Syne',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=10, b=50, l=10, r=10),
            height=280
        )
        st.plotly_chart(fig, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_map:
        st.markdown("<div class='glass-card' style='height:400px;'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-header'>🗺️ Geographic Incident Tracking</div>", unsafe_allow_html=True)
        
        # Render a gorgeous dark Plotly map of coordinates (using modern scatter_map)
        if locations:
            # Join locations with their last chat risk level for color coding
            map_data = []
            for l in locations:
                user_id = l["user_id"]
                lat = l["latitude"]
                lon = l["longitude"]
                
                # Find last chat risk for this user
                user_chats = [c for c in chats if c["user_id"] == user_id]
                risk = user_chats[0]["risk"] if user_chats else "low"
                
                map_data.append({
                    "user_id": user_id[:8] + "...",
                    "latitude": lat,
                    "longitude": lon,
                    "risk": risk.upper(),
                    "size": 15 if risk == "emergency" else 10
                })
                
            df_map = pd.DataFrame(map_data)
            
            fig_map = px.scatter_map(
                df_map,
                lat="latitude",
                lon="longitude",
                color="risk",
                size="size",
                hover_name="user_id",
                hover_data=["risk", "latitude", "longitude"],
                color_discrete_map={
                    'LOW': '#00d4aa',
                    'MEDIUM': '#f4b942',
                    'HIGH': '#e63462',
                    'EMERGENCY': '#ff6b9d'
                },
                zoom=1,
                size_max=15
            )
            
            fig_map.update_layout(
                map_style="carto-darkmatter",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=False,
                height=290
            )
            st.plotly_chart(fig_map, width="stretch")
        else:
            st.info("No geographic markers recorded yet.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Second Row: Data Tables & Live Feed
    col_feed, col_tables = st.columns([1, 1.8])
    
    with col_feed:
        st.markdown("<div class='glass-card' style='height:420px; overflow:hidden;'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-header'>📡 Live Activity Feed (Latest 5)</div>", unsafe_allow_html=True)
        
        latest_chats = chats[:5]
        if latest_chats:
            feed_html = "<div style='display:flex; flex-direction:column; gap:12px; height:320px; overflow-y:auto;'>"
            for c in latest_chats:
                color = {"low": "#00d4aa", "medium": "#f4b942", "high": "#e63462", "emergency": "#ff6b9d"}.get(c["risk"], "#f0f0f8")
                icon = {"low": "💚", "medium": "🟡", "high": "🔴", "emergency": "🆘"}.get(c["risk"], "•")
                msg_snip = c["message"][:45] + "..." if len(c["message"]) > 45 else c["message"]
                
                feed_html += f"""
                <div style="border-left: 3.5px solid {color} !important; background: rgba(255, 255, 255, 0.02) !important; padding: 10px 14px !important; margin-bottom: 8px !important; border-radius: 0 8px 8px 0 !important; box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;">
                    <div style="font-size:0.84rem !important; font-weight:bold !important; color:{color} !important; display: flex !important; align-items: center !important; gap: 6px !important;">
                        <span>{icon}</span> <span style="color:{color} !important; text-transform: uppercase !important; letter-spacing: 0.5px !important;">RISK: {c['risk'].upper()}</span>
                    </div>
                    <div style="font-size:0.82rem !important; font-style:italic !important; margin:4px 0 !important; color:#eeeef8 !important;">"{msg_snip}"</div>
                    <div style="font-size:0.7rem !important; color:rgba(240,240,248,0.45) !important; font-family:'DM Mono', monospace !important;">User: {c['user_id'][:8]}... | {c.get('created_at', 'Just now')}</div>
                </div>
                """
            feed_html += "</div>"
            st.markdown(feed_html, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:rgba(240,240,248,0.4); text-align:center; padding-top:100px;'>No activity registered.</p>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_tables:
        st.markdown("<div class='glass-card' style='min-height:420px;'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-header'>👥 Database Command Center</div>", unsafe_allow_html=True)
        
        tab_users, tab_chats, tab_risk = st.tabs(["👥 Users", "💬 Chat Logs", "🚨 High Risk & Incident cases"])
        
        with tab_users:
            if users:
                df_u = pd.DataFrame(users)
                cols = [c for c in ["id", "name", "email", "role", "created_at"] if c in df_u.columns]
                st.dataframe(df_u[cols], width="stretch", height=250)
            else:
                st.write("No users registered.")
                
        with tab_chats:
            if chats:
                df_c = pd.DataFrame(chats)
                cols = [c for c in ["id", "user_id", "message", "response", "risk", "created_at"] if c in df_c.columns]
                st.dataframe(df_c[cols], width="stretch", height=250)
            else:
                st.write("No logs recorded.")
                
        with tab_risk:
            risk_logs = [c for c in chats if c["risk"] in {"high", "emergency"}]
            if risk_logs:
                df_r = pd.DataFrame(risk_logs)
                cols = [c for c in ["id", "user_id", "message", "response", "risk", "created_at"] if c in df_r.columns]
                st.dataframe(df_r[cols], width="stretch", height=250)
                
                # Command Actions Simulation
                st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 10px 0;'/>", unsafe_allow_html=True)
                st.markdown("##### Administrative Actions")
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    resolved_id = st.text_input("Resolve Case ID", placeholder="e.g. 1")
                    if st.button("Mark Case as Safe"):
                        if resolved_id:
                            st.toast(f"✅ Case ID {resolved_id} marked as RESOLVED and SAFE.", icon="💚")
                        else:
                            st.error("Please enter a valid Case ID")
                with action_col2:
                    alert_user_id = st.text_input("Send Warning/Alert User ID", placeholder="e.g. u1")
                    if st.button("Trigger Emergency Support"):
                        if alert_user_id:
                            st.toast(f"🚨 Support alert dispatched to emergency coordinator for User {alert_user_id}.", icon="⚠️")
                        else:
                            st.error("Please enter a valid User ID")
            else:
                st.write("Clear. No active high risk or emergency cases registered.")
                
        st.markdown("</div>", unsafe_allow_html=True)

    # Geo-location Alert Injection Simulator (Interactive live demo)
    with st.expander("📡 Sim-Alert Coordinator (Interactive Demo Controller)"):
        st.markdown("<p style='font-size:0.85rem; color:rgba(240,240,248,0.55);'>This simulator lets you test the active geographic tracking in the admin panel by injecting an emergency text from a custom location.</p>", unsafe_allow_html=True)
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            sim_msg = st.text_input("Distress Message Text", value="Help me now, my husband has a gun!")
            sim_country = st.selectbox("Trigger Country", options=list(COUNTRIES_DATA.keys()), index=1)
        with col_sim2:
            sim_lat = st.number_input("Target Latitude (approx)", value=COUNTRIES_DATA[sim_country]["police"] != "100" and 37.7749 or 28.6139)
            sim_lon = st.number_input("Target Longitude (approx)", value=COUNTRIES_DATA[sim_country]["police"] != "100" and -122.4194 or 77.2090)
            
        if st.button("Inject simulated Alert", width="stretch"):
            # Process alert through classifier
            sim_res = handle_message(message=sim_msg, country=sim_country, debug=False)
            # Add to local SQLite DB
            db.save_chat(
                user_id="sim_user",
                message=sim_msg,
                response=sim_res["reply"],
                risk=sim_res["risk_level"]
            )
            db.save_location("sim_user", sim_lat, sim_lon)
            st.success("Incident injected! The Admin metrics, charts, tables, and map have been updated.")
            st.rerun()

# ---------------------------------------------------------
# Page 3: 🆘 Emergency Directory
# ---------------------------------------------------------
elif page == "🆘 Emergency Directory":
    st.markdown("<h1>Emergency <span style='background: linear-gradient(135deg, #e63462, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Directory</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(240,240,248,0.65); font-size:1.1rem; margin-top:-10px;'>Surfacing instant emergency contact points & hotlines by country and region.</p>", unsafe_allow_html=True)
    
    # Regional filter buttons
    selected_region = st.segmented_control(
        "Region Filter",
        options=["All", "Asia", "Europe", "Americas", "Africa", "Oceania"],
        default="All"
    )
    
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
    
    # Generate cards grid
    cols = st.columns(3)
    idx = 0
    for name, c in COUNTRIES_DATA.items():
        if selected_region == "All" or c["region"] == selected_region:
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="glass-card" style="padding:18px; border-bottom: 2.5px solid #e63462;">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                        <span style="font-size:2rem; line-height:1;">{c['flag']}</span>
                        <div>
                            <div style="font-family:'Syne'; font-weight:700; font-size:1.1rem; color:#f0f0f8;">{name}</div>
                            <small style="color:rgba(240,240,248,0.4); text-transform:uppercase; font-size:0.67rem; font-family:'DM Mono'; letter-spacing:0.5px;">{c['region']}</small>
                        </div>
                    </div>
                    <table style="width:100%; border-collapse:collapse; font-size:0.83rem;">
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                            <td style="padding:6px 0; color:rgba(240,240,248,0.5);">Police Line</td>
                            <td style="padding:6px 0; text-align:right; font-weight:bold;"><a href="tel:{c['police']}" style="color:#00d4aa; text-decoration:none;">{c['police']}</a></td>
                        </tr>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                            <td style="padding:6px 0; color:rgba(240,240,248,0.5);">Ambulance</td>
                            <td style="padding:6px 0; text-align:right; font-weight:bold;"><a href="tel:{c['ambulance']}" style="color:#00d4aa; text-decoration:none;">{c['ambulance']}</a></td>
                        </tr>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                            <td style="padding:6px 0; color:rgba(240,240,248,0.5);">Women Helpline</td>
                            <td style="padding:6px 0; text-align:right; font-weight:bold; color:#f0f0f8;">{c['helpline']}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0; color:rgba(240,240,248,0.5); font-weight:bold; color:#e63462;">🆘 DV Hotline</td>
                            <td style="padding:6px 0; text-align:right; font-weight:bold; font-size:0.95rem; text-shadow:0 0 10px rgba(230,52,98,0.2);"><a href="tel:{c['dv_hotline']}" style="color:#e63462; text-decoration:none;">{c['dv_hotline']}</a></td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                idx += 1
                
    if idx == 0:
        st.info("No countries found for this region.")

# ---------------------------------------------------------
# Page 4: ⚙️ How It Works & Safety Planning
# ---------------------------------------------------------
elif page == "⚙️ How It Works & Safety Planning":
    st.markdown("<h1>AI Logic & <span style='background: linear-gradient(135deg, #e63462, #f4b942); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Safety Planning</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(240,240,248,0.65); font-size:1.1rem; margin-top:-10px;'>Learn how our classification engine maps risks, and construct a downloadable safety plan.</p>", unsafe_allow_html=True)
    
    tab_sim, tab_builder = st.tabs(["⚙️ NLP Diagnostic Simulator", "📋 Interactive Safety Plan Builder"])
    
    with tab_sim:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-header'>🧠 Real-Time NLP Diagnostics & Reasoning Logs</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.88rem; color:rgba(240,240,248,0.6);'>Type any text below to see how our scikit-learn models, negation handlers, feature extractors, and safety rule tables process inputs to yield threat levels.</p>", unsafe_allow_html=True)
        
        diag_input = st.text_input("Enter diagnostic text to analyze:", value="My spouse grabbed me and is locking me inside the house.")
        
        if diag_input:
            # Run handle_message in debug mode
            debug_res = handle_message(
                message=diag_input,
                country=selected_country,
                debug=True,
                context_memory=st.session_state.context_memory
            )
            
            st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 15px 0;'/>", unsafe_allow_html=True)
            
            # Outputs
            col_out1, col_out2, col_out3 = st.columns(3)
            with col_out1:
                color = {"low": "#00d4aa", "medium": "#f4b942", "high": "#e63462", "emergency": "#ff6b9d"}.get(debug_res["risk_level"], "#f0f0f8")
                st.markdown(f"**Final Risk Category:**")
                st.markdown(f"<h3 style='color:{color}; font-family:\"Syne\"; font-size:1.8rem; margin:0;'>{debug_res['risk_level'].upper()}</h3>", unsafe_allow_html=True)
            with col_out2:
                st.markdown(f"**Detected Emotion:**")
                st.markdown(f"<h3 style='color:#5b8dee; font-family:\"Syne\"; font-size:1.8rem; margin:0;'>{debug_res['emotion'].upper()}</h3>", unsafe_allow_html=True)
            with col_out3:
                st.markdown(f"**Sentiment Baseline:**")
                st.markdown(f"<h3 style='color:#00d4aa; font-family:\"Syne\"; font-size:1.8rem; margin:0;'>{debug_res['sentiment'].upper()}</h3>", unsafe_allow_html=True)
                
            # Details / Debug Logs
            st.markdown("<br/>", unsafe_allow_html=True)
            debug_info = debug_res.get("debug", {})
            
            log_col1, log_col2 = st.columns(2)
            with log_col1:
                st.markdown("##### 🛠️ Feature Extraction Logs")
                st.json({
                    "ML Risk Score": debug_info.get("risk_score"),
                    "Linguistic Features": debug_info.get("features", {}),
                    "Context Risks History": debug_info.get("context_summary", {}).get("recent_risks", [])
                })
            with log_col2:
                st.markdown("##### 🛡️ Safety Rule Resolution")
                st.json({
                    "Rule Triggered": debug_info.get("rule_triggered", "None"),
                    "Rule Trigger Reason": debug_info.get("rule_reason", "ML score fell within standard thresholds"),
                    "Escalation Strength": debug_info.get("context_summary", {}).get("escalation_strength", 0.0),
                    "Repeated High Risk Pattern": debug_info.get("context_summary", {}).get("repeated_high_risk", False)
                })
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_builder:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-header'>📋 Build & Export Personal Safety Plan</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.88rem; color:rgba(240,240,248,0.6);'>Preparing a plan ahead of time is critical. Fill in the safe contacts and escape routines below to save to your local profile or export a text file.</p>", unsafe_allow_html=True)
        
        # Load existing plan if available in local SQLite database
        existing_plan = db.get_safety_plan(st.session_state.user_id)
        
        plan_col1, plan_col2 = st.columns(2)
        with plan_col1:
            safe_contacts = st.text_area("Safe Contacts (Names & Phone Numbers)", 
                                         value=existing_plan.get("safe_contacts", ""),
                                         placeholder="e.g. Uncle John: 555-0199, Neighbor Susan: 555-0144")
            warning_signs = st.text_area("Early Warning Signs (When to trigger exit)", 
                                         value=existing_plan.get("warning_signs", ""),
                                         placeholder="e.g. Escalating tone of voice, throwing minor objects, checks location logs")
            safe_places = st.text_input("Safe Exit Locations (Where to meet/go)", 
                                        value=existing_plan.get("safe_places", ""),
                                        placeholder="e.g. Local public library, Fire station, Susan's house")
        with plan_col2:
            escape_steps = st.text_area("Emergency Escape Steps", 
                                        value=existing_plan.get("escape_steps", ""),
                                        placeholder="e.g. 1. Exit through kitchen door. 2. Text John code word 'GREEN'. 3. Run to library.")
            pack_list = st.text_area("Emergency Pack List (Where are they hidden?)", 
                                     value=existing_plan.get("pack_list", ""),
                                     placeholder="e.g. Spare keys, ID documents, $100 cash in secondary wallet behind bookshelf")
            code_word = st.text_input("Crisis Code Word", 
                                      value=existing_plan.get("code_word", ""),
                                      placeholder="e.g. BLUEBERRY (sends immediate alert when texted)")
            
        # Format Plan document
        plan_text = f"""=========================================
PROTEGO PERSONAL CONFIDENTIAL SAFETY PLAN
=========================================
Generated At: {datetime.date.today()}

1. crisis contacts:
-----------------
{safe_contacts or "Not Specified"}

2. Early Warning Signs:
---------------------
{warning_signs or "Not Specified"}

3. Safe Places to Go:
-------------------
{safe_places or "Not Specified"}

4. Escape Route & Steps:
----------------------
{escape_steps or "Not Specified"}

5. Emergency Pack Checklist:
--------------------------
{pack_list or "Not Specified"}

6. Emergency Code Word:
---------------------
{code_word or "Not Specified"}

-----------------------------------------
KEEP THIS PLAN SECURE AND CONFIDENTIAL.
========================================="""
        
        st.markdown("<br/>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("💾 Save Plan to Profile", width="stretch"):
                success = db.save_safety_plan(
                    st.session_state.user_id,
                    safe_contacts,
                    warning_signs,
                    safe_places,
                    escape_steps,
                    pack_list,
                    code_word
                )
                if success:
                    st.toast("Safety Plan successfully saved to your private local profile!", icon="💚")
                else:
                    st.error("Error saving Safety Plan.")
                    
        with btn_col2:
            st.download_button(
                label="📥 Download Plan as Text File",
                data=plan_text,
                file_name="protego_safety_plan.txt",
                mime="text/plain",
                width="stretch"
            )
        st.markdown("</div>", unsafe_allow_html=True)
