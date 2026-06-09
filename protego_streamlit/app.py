"""
app.py — PROTEGO Streamlit App
Multi-page: Chat · Admin Dashboard · About
"""

import sys, os, json, time
from datetime import datetime
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from protego.api.chatbot_service import handle_message

# ──────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PROTEGO",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ─── Hide default Streamlit chrome ─── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label { color: rgba(255,255,255,0.6) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }

/* ─── Sidebar nav buttons ─── */
.nav-btn {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px; border-radius: 10px;
    cursor: pointer; transition: all 0.2s;
    margin-bottom: 4px; font-size: 14px; font-weight: 500;
    color: rgba(255,255,255,0.7); background: transparent;
    border: none; width: 100%; text-align: left;
}
.nav-btn:hover { background: rgba(255,255,255,0.08); color: white; }
.nav-btn.active { background: linear-gradient(135deg,#667eea,#764ba2); color: white !important; }

/* ─── Metric cards ─── */
.metric-card {
    background: white; border-radius: 16px;
    padding: 20px 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0; height: 100%;
}
.metric-card .label {
    font-size: 11px; font-weight: 600; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
}
.metric-card .value {
    font-size: 32px; font-weight: 800; color: #1a1a2e; line-height: 1;
}
.metric-card .sub { font-size: 12px; color: #9ca3af; margin-top: 4px; }
.metric-card .icon { font-size: 28px; float: right; margin-top: -4px; }

/* ─── Chat bubbles ─── */
.bubble-wrap-user { display: flex; justify-content: flex-end; margin: 10px 0 4px; }
.bubble-wrap-bot  { display: flex; justify-content: flex-start; margin: 4px 0 10px; }

.bubble-user {
    background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    color: white; padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 72%; font-size: 14px; line-height: 1.6;
    box-shadow: 0 3px 12px rgba(102,126,234,0.35);
}
.bubble-bot {
    background: white; color: #1a1a2e;
    padding: 14px 18px; border-radius: 4px 20px 20px 20px;
    max-width: 75%; font-size: 14px; line-height: 1.65;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07); white-space: pre-wrap;
    border-left: 4px solid #10b981;
}
.bubble-bot.risk-medium { border-left-color: #f59e0b; }
.bubble-bot.risk-high   { border-left-color: #ef4444; }
.bubble-bot.risk-emergency { border-left-color: #dc2626; background: #fff8f8; }

/* ─── Tags row ─── */
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
.tag {
    font-size: 11px; font-weight: 600; padding: 3px 10px;
    border-radius: 20px; letter-spacing: 0.3px;
}
.tag-low       { background:#d1fae5; color:#065f46; }
.tag-medium    { background:#fef3c7; color:#92400e; }
.tag-high      { background:#fee2e2; color:#991b1b; }
.tag-emergency { background:#dc2626; color:white; }
.tag-emotion   { background:#ede9fe; color:#5b21b6; }
.tag-sentiment { background:#e0f2fe; color:#075985; }
.tag-score     { background:#f0fdf4; color:#166534; }

/* ─── Emergency panel ─── */
.emergency-panel {
    background: linear-gradient(135deg,#fff1f2,#ffe4e6);
    border: 2px solid #f87171; border-radius: 16px;
    padding: 18px 20px; margin: 8px 0 8px 0;
}
.emergency-panel h5 {
    color:#dc2626; font-size:12px; font-weight:700;
    text-transform:uppercase; letter-spacing:1px; margin:0 0 12px;
}
.contact-row {
    display:flex; align-items:center; gap:12px;
    background:white; border-radius:10px;
    padding:10px 14px; margin:6px 0;
    box-shadow:0 1px 4px rgba(0,0,0,0.06);
}
.contact-num { font-size:20px; font-weight:800; color:#dc2626; min-width:100px; }
.contact-info { font-size:12px; color:#374151; }
.contact-info small { color:#9ca3af; }

/* ─── Admin chart area ─── */
.chart-card {
    background: white; border-radius: 16px;
    padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0; margin-bottom: 16px;
}
.chart-card h4 {
    font-size: 13px; font-weight: 700; color: #374151;
    text-transform: uppercase; letter-spacing: 0.8px;
    margin: 0 0 16px;
}

/* ─── Timeline item ─── */
.timeline-item {
    display: flex; gap: 12px; padding: 10px 0;
    border-bottom: 1px solid #f3f4f6;
    font-size: 13px; align-items: flex-start;
}
.timeline-dot {
    width: 10px; height: 10px; border-radius: 50%;
    margin-top: 4px; flex-shrink: 0;
}
.dot-low { background:#10b981; }
.dot-medium { background:#f59e0b; }
.dot-high { background:#ef4444; }
.dot-emergency { background:#dc2626; box-shadow:0 0 6px #dc2626; }

/* ─── Page header ─── */
.page-header {
    background: linear-gradient(135deg,#0f0c29 0%,#302b63 60%,#24243e 100%);
    padding: 28px 36px 24px; color: white;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.page-header h1 { font-size: 22px; font-weight: 800; margin: 0; letter-spacing: -0.3px; }
.page-header p  { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0; }

/* ─── Scrollable chat ─── */
.chat-scroll {
    height: 540px; overflow-y: auto; padding: 16px 24px;
    background: #f8f9ff; border-radius: 0;
}

/* ─── Input bar ─── */
.stTextInput input {
    border-radius: 30px !important; border: 2px solid #e0e7ff !important;
    padding: 12px 22px !important; font-size: 14px !important;
    background: white !important;
}
.stTextInput input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.15) !important;
}

/* ─── Streamlit button override ─── */
.stButton > button {
    border-radius: 30px !important; font-weight: 600 !important;
    border: none !important; transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important; }

/* ─── Progress bar override ─── */
.stProgress > div > div { border-radius: 4px !important; }

/* ─── About cards ─── */
.about-card {
    background: white; border-radius: 16px; padding: 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-top: 4px solid #667eea; margin-bottom: 16px;
}
.about-card h3 { font-size: 15px; font-weight: 700; color:#1a1a2e; margin:0 0 10px; }
.about-card p  { font-size: 13px; color: #6b7280; line-height: 1.6; margin: 0; }

/* ─── Risk gauge ─── */
.gauge-wrap { text-align: center; padding: 8px 0; }
.gauge-bar {
    height: 10px; border-radius: 5px; margin: 6px 0;
    background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444, #dc2626);
}
.gauge-needle { font-size: 11px; color: #6b7280; }

/* ─── Timestamp ─── */
.ts { font-size: 10px; color: #d1d5db; margin-top: 4px; text-align: right; }

/* ─── Scrollbar styling ─── */
.chat-scroll::-webkit-scrollbar { width: 5px; }
.chat-scroll::-webkit-scrollbar-track { background: transparent; }
.chat-scroll::-webkit-scrollbar-thumb { background: #ddd; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "country": "India",
    "page": "chat",
    "input_key": 0,
    "session_logs": [],   # admin log: each completed turn
    "total_messages": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 8px 10px;text-align:center;'>
      <div style='font-size:40px;'>🛡️</div>
      <div style='font-size:18px;font-weight:800;color:white;letter-spacing:-0.5px;margin-top:6px;'>PROTEGO</div>
      <div style='font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px;'>AI Safety Chatbot</div>
    </div>
    <hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0 0 16px;'>
    """, unsafe_allow_html=True)

    # Navigation
    for label, icon, key in [("Chat", "💬", "chat"), ("Admin Dashboard", "📊", "admin"), ("About", "ℹ️", "about")]:
        active = "active" if st.session_state.page == key else ""
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0;'>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:10px;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1px;padding:0 4px 6px;'>Settings</div>", unsafe_allow_html=True)
    country = st.selectbox("Country", ["India", "USA", "UK", "Global"],
                           index=["India","USA","UK","Global"].index(st.session_state.country))
    st.session_state.country = country

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0;'>", unsafe_allow_html=True)

    # Session stats mini
    total = len(st.session_state.session_logs)
    if total > 0:
        risks = [t["risk_level"] for t in st.session_state.session_logs]
        rc = Counter(risks)
        st.markdown(f"""
        <div style='font-size:10px;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:1px;padding:0 4px 6px;'>Session</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.6);padding:0 4px;line-height:1.8;'>
          💬 {total} messages<br>
          🟢 {rc.get('low',0)} low &nbsp; 🟡 {rc.get('medium',0)} med<br>
          🔴 {rc.get('high',0)} high &nbsp; 🆘 {rc.get('emergency',0)} emg
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:12px 0;'>", unsafe_allow_html=True)

    if st.button("🗑️  Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_logs = []
        st.session_state.total_messages = 0
        st.rerun()

    st.markdown("""
    <div style='position:absolute;bottom:20px;left:0;right:0;text-align:center;font-size:10px;color:rgba(255,255,255,0.2);padding:0 16px;'>
      Not a substitute for professional help.<br>
      In danger? Call emergency services now.
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────
RISK_COLOR = {"low":"#10b981","medium":"#f59e0b","high":"#ef4444","emergency":"#dc2626"}
RISK_EMOJI = {"low":"🟢","medium":"🟡","high":"🔴","emergency":"🆘"}
RISK_NUM   = {"low":1,"medium":2,"high":3,"emergency":4}

def risk_score_pct(risk):
    return {"low":18,"medium":45,"high":72,"emergency":95}.get(risk, 18)

def render_bubble_user(text, ts):
    st.markdown(f"""
    <div class="bubble-wrap-user">
      <div>
        <div class="bubble-user">{text}</div>
        <div class="ts">{ts}</div>
      </div>
    </div>""", unsafe_allow_html=True)

def render_bubble_bot(turn):
    risk = turn["risk_level"]
    reply = turn["reply"].replace("\n","<br>")
    score_pct = risk_score_pct(risk)
    score_val = turn.get("risk_score", "—")
    score_display = f"{score_val:.1f}" if isinstance(score_val, float) else score_val

    st.markdown(f"""
    <div class="bubble-wrap-bot">
      <div style="max-width:78%;">
        <div class="bubble-bot risk-{risk}">{reply}
          <div class="tag-row" style="margin-top:12px;">
            <span class="tag tag-{risk}">{RISK_EMOJI[risk]} {risk.title()}</span>
            <span class="tag tag-emotion">😶 {turn.get('emotion','—')}</span>
            <span class="tag tag-sentiment">💬 {turn.get('sentiment','—')}</span>
            <span class="tag tag-score">⚡ score {score_display}</span>
          </div>
        </div>
        <div class="ts">{turn['ts']}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if turn.get("show_emergency") and turn.get("emergency_contacts"):
        contacts = turn["emergency_contacts"]
        rows_html = ""
        for key, info in contacts.items():
            label = key.replace("_"," ").title()
            rows_html += f"""
            <div class="contact-row">
              <div class="contact-num">{info['number']}</div>
              <div class="contact-info">{label}<br><small>{info['description']} · {info['available']}</small></div>
            </div>"""
        st.markdown(f"""
        <div class="emergency-panel">
          <h5>🆘 Emergency Contacts — {st.session_state.country}</h5>
          {rows_html}
        </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# PAGE: CHAT
# ──────────────────────────────────────────────────────────
def page_chat():
    st.markdown("""
    <div class="page-header">
      <h1>💬 PROTEGO Chat</h1>
      <p>AI-powered safety & emotional distress detection · Talk to me, I'm listening</p>
    </div>""", unsafe_allow_html=True)

    # ── Main layout: chat left, panel right
    chat_col, panel_col = st.columns([3, 1])

    with chat_col:
        # Chat area
        if not st.session_state.messages:
            st.markdown("""
            <div style="height:540px;background:#f8f9ff;display:flex;flex-direction:column;
                        align-items:center;justify-content:center;color:#9ca3af;">
              <div style="font-size:52px;margin-bottom:12px;">🛡️</div>
              <div style="font-weight:700;font-size:16px;color:#6b7280;">PROTEGO is here</div>
              <div style="font-size:13px;margin-top:6px;text-align:center;max-width:280px;line-height:1.5;">
                Tell me how you're feeling.<br>Everything is confidential and I'm not here to judge.
              </div>
              <div style="margin-top:24px;display:flex;gap:10px;flex-wrap:wrap;justify-content:center;">
                <span style="background:#ede9fe;color:#5b21b6;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:500;">I feel scared</span>
                <span style="background:#ede9fe;color:#5b21b6;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:500;">I need help</span>
                <span style="background:#ede9fe;color:#5b21b6;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:500;">I feel hopeless</span>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            with st.container():
                st.markdown('<div class="chat-scroll" id="chatbox">', unsafe_allow_html=True)
                for turn in st.session_state.messages:
                    render_bubble_user(turn["user"], turn["ts"])
                    render_bubble_bot(turn)
                st.markdown('</div>', unsafe_allow_html=True)

        # Input
        st.markdown("<div style='padding:12px 0 4px;'>", unsafe_allow_html=True)
        with st.form(key=f"cf_{st.session_state.input_key}", clear_on_submit=True):
            c1, c2 = st.columns([9, 1])
            with c1:
                user_input = st.text_input("msg", placeholder="Type your message…",
                                           label_visibility="collapsed")
            with c2:
                sent = st.form_submit_button("➤", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;font-size:10px;color:#c4c4c4;padding:2px 0 8px;">
          PROTEGO is an AI tool. Always contact emergency services if you are in immediate danger.
        </div>""", unsafe_allow_html=True)

    # ── Right panel
    with panel_col:
        st.markdown("<div style='padding:16px 0 0 8px;'>", unsafe_allow_html=True)

        # Live risk gauge
        if st.session_state.messages:
            last = st.session_state.messages[-1]
            risk = last["risk_level"]
            pct = risk_score_pct(risk)
            color = RISK_COLOR[risk]
            score_val = last.get("risk_score","—")
            score_str = f"{score_val:.1f}" if isinstance(score_val, float) else score_val

            st.markdown(f"""
            <div class="chart-card">
              <h4>Live Risk</h4>
              <div style="text-align:center;padding:6px 0;">
                <div style="font-size:40px;">{RISK_EMOJI[risk]}</div>
                <div style="font-size:20px;font-weight:800;color:{color};margin:4px 0;">{risk.upper()}</div>
                <div style="font-size:11px;color:#9ca3af;">score: {score_str}</div>
              </div>
              <div style="background:#f3f4f6;border-radius:6px;height:8px;margin:10px 0 4px;overflow:hidden;">
                <div style="background:{color};height:100%;width:{pct}%;border-radius:6px;transition:all 0.4s;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:10px;color:#d1d5db;">
                <span>Low</span><span>Emergency</span>
              </div>
            </div>""", unsafe_allow_html=True)

            # Last detected
            st.markdown(f"""
            <div class="chart-card" style="margin-top:0;">
              <h4>Detections</h4>
              <div style="font-size:13px;line-height:2;color:#374151;">
                <b>Emotion:</b> {last.get('emotion','—')}<br>
                <b>Sentiment:</b> {last.get('sentiment','—')}<br>
                <b>Turn:</b> #{len(st.session_state.messages)}
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="chart-card">
              <h4>Live Risk</h4>
              <div style="text-align:center;color:#d1d5db;padding:20px 0;font-size:28px;">──</div>
              <div style="font-size:12px;text-align:center;color:#9ca3af;">Send a message to begin</div>
            </div>""", unsafe_allow_html=True)

        # Recent history
        if len(st.session_state.session_logs) > 0:
            st.markdown('<div class="chart-card"><h4>History</h4>', unsafe_allow_html=True)
            for t in reversed(st.session_state.session_logs[-6:]):
                color = RISK_COLOR.get(t["risk_level"], "#ccc")
                short_msg = t["user"][:28] + "…" if len(t["user"]) > 28 else t["user"]
                st.markdown(f"""
                <div class="timeline-item">
                  <div class="timeline-dot dot-{t['risk_level']}"></div>
                  <div>
                    <div style="font-size:12px;color:#374151;">{short_msg}</div>
                    <div style="font-size:10px;color:#9ca3af;">{t['ts']} · {t['emotion']}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Handle submit
    if sent and user_input and user_input.strip():
        with st.spinner(""):
            try:
                result = handle_message(
                    message=user_input.strip(),
                    country=st.session_state.country,
                    debug=True
                )
                ts = datetime.now().strftime("%H:%M")
                debug = result.get("debug", {})
                risk_score = debug.get("risk_score", None) if isinstance(debug, dict) else None

                turn = {
                    "user": user_input.strip(),
                    "reply": result.get("reply", "I'm here with you 🤍"),
                    "risk_level": result.get("risk_level", "low"),
                    "emotion": result.get("emotion", "—"),
                    "sentiment": result.get("sentiment", "—"),
                    "show_emergency": result.get("show_emergency", False),
                    "emergency_contacts": result.get("emergency_contacts"),
                    "risk_score": risk_score,
                    "ts": ts,
                    "ml_risk": debug.get("ml_risk","—") if isinstance(debug, dict) else "—",
                    "rule_triggered": debug.get("rule_triggered", False) if isinstance(debug, dict) else False,
                    "rule_reason": debug.get("rule_reason","") if isinstance(debug, dict) else "",
                }
                st.session_state.messages.append(turn)
                st.session_state.session_logs.append(turn)
                st.session_state.total_messages += 1
            except Exception as e:
                st.error(f"Error: {e}")
        st.session_state.input_key += 1
        st.rerun()

# ──────────────────────────────────────────────────────────
# PAGE: ADMIN DASHBOARD
# ──────────────────────────────────────────────────────────
def page_admin():
    import pandas as pd

    st.markdown("""
    <div class="page-header">
      <h1>📊 Admin Dashboard</h1>
      <p>Session analytics · Risk trends · Message log</p>
    </div>""", unsafe_allow_html=True)

    logs = st.session_state.session_logs
    total = len(logs)

    st.markdown("<div style='padding:20px 28px;'>", unsafe_allow_html=True)

    if total == 0:
        st.markdown("""
        <div style="text-align:center;padding:80px 0;color:#9ca3af;">
          <div style="font-size:48px;">📭</div>
          <div style="font-size:16px;font-weight:600;color:#6b7280;margin-top:12px;">No session data yet</div>
          <div style="font-size:13px;margin-top:6px;">Start a conversation in the Chat tab</div>
        </div>""", unsafe_allow_html=True)
        return

    risks = [t["risk_level"] for t in logs]
    emotions = [t["emotion"] for t in logs]
    sentiments = [t["sentiment"] for t in logs]
    rc = Counter(risks)
    ec = Counter(emotions)
    sc = Counter(sentiments)

    max_risk = max(risks, key=lambda r: RISK_NUM.get(r, 0))
    emergency_count = rc.get("emergency", 0) + rc.get("high", 0)

    # ── KPI row
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("💬", "Total Messages", str(total), "this session"),
        (RISK_EMOJI.get(max_risk,"🟢"), "Peak Risk", max_risk.title(), f"{rc.get(max_risk,0)} times"),
        ("🆘", "High / Emergency", str(emergency_count), f"{round(emergency_count/total*100)}% of session"),
        ("😶", "Top Emotion", ec.most_common(1)[0][0].title() if ec else "—",
         f"{ec.most_common(1)[0][1]} occurrences" if ec else ""),
    ]
    for col, (icon, label, value, sub) in zip([k1,k2,k3,k4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">{label}</div>
              <div class="value">{value} <span class="icon">{icon}</span></div>
              <div class="sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown('<div class="chart-card"><h4>Risk Distribution</h4>', unsafe_allow_html=True)
        risk_df = pd.DataFrame(
            {"Risk": list(rc.keys()), "Count": list(rc.values())}
        ).sort_values("Risk", key=lambda x: x.map(RISK_NUM))
        st.bar_chart(risk_df.set_index("Risk"), color="#667eea", height=200)
        st.markdown("</div>", unsafe_allow_html=True)

    with ch2:
        st.markdown('<div class="chart-card"><h4>Emotion Breakdown</h4>', unsafe_allow_html=True)
        if ec:
            emo_df = pd.DataFrame({"Emotion": list(ec.keys()), "Count": list(ec.values())})
            st.bar_chart(emo_df.set_index("Emotion"), color="#764ba2", height=200)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Risk trend line
    st.markdown('<div class="chart-card"><h4>Risk Level Over Conversation</h4>', unsafe_allow_html=True)
    trend_df = pd.DataFrame({
        "Turn": list(range(1, total+1)),
        "Risk Score": [RISK_NUM.get(t["risk_level"],1) for t in logs]
    }).set_index("Turn")
    st.line_chart(trend_df, height=160, color="#ef4444")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Message log table
    st.markdown('<div class="chart-card"><h4>Message Log</h4>', unsafe_allow_html=True)
    table_data = []
    for i, t in enumerate(logs, 1):
        table_data.append({
            "#": i,
            "Time": t["ts"],
            "Message": t["user"][:55] + ("…" if len(t["user"])>55 else ""),
            "Risk": f"{RISK_EMOJI.get(t['risk_level'],'')} {t['risk_level'].title()}",
            "Emotion": t["emotion"],
            "Sentiment": t["sentiment"],
            "Score": f"{t['risk_score']:.1f}" if isinstance(t.get('risk_score'), float) else "—",
            "Rule": "⚠️ Yes" if t.get("rule_triggered") else "No",
        })
    st.dataframe(
        pd.DataFrame(table_data).set_index("#"),
        use_container_width=True,
        hide_index=False
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── AI Decision trace (last message)
    if logs:
        last = logs[-1]
        debug_info = {
            "ML Risk Prediction": last.get("ml_risk","—"),
            "Final Risk After Rules": last.get("risk_level","—"),
            "Rule Triggered": str(last.get("rule_triggered", False)),
            "Rule Reason": last.get("rule_reason","None") or "None",
            "Emotion": last.get("emotion","—"),
            "Sentiment": last.get("sentiment","—"),
            "Risk Score": f"{last['risk_score']:.2f}" if isinstance(last.get('risk_score'), float) else "—",
            "Emergency Shown": str(last.get("show_emergency", False)),
        }
        st.markdown('<div class="chart-card"><h4>🧠 AI Decision Trace — Last Message</h4>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (key, val) in enumerate(debug_info.items()):
            with cols[i % 4]:
                color = "#dc2626" if "emergency" in str(val).lower() or val=="True" else "#374151"
                st.markdown(f"""
                <div style="background:#f9fafb;border-radius:10px;padding:12px 14px;margin-bottom:10px;">
                  <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.5px;">{key}</div>
                  <div style="font-size:15px;font-weight:700;color:{color};margin-top:4px;">{val}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# PAGE: ABOUT
# ──────────────────────────────────────────────────────────
def page_about():
    st.markdown("""
    <div class="page-header">
      <h1>ℹ️ About PROTEGO</h1>
      <p>Architecture · Tech stack · How it works</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:24px 28px;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f0c29,#302b63);border-radius:20px;
                padding:32px 36px;color:white;margin-bottom:24px;">
      <div style="font-size:13px;color:rgba(255,255,255,0.5);letter-spacing:2px;text-transform:uppercase;">Project</div>
      <div style="font-size:28px;font-weight:800;margin:8px 0 6px;letter-spacing:-0.5px;">
        PROTEGO 🛡️
      </div>
      <div style="font-size:14px;color:rgba(255,255,255,0.6);max-width:520px;line-height:1.6;">
        An AI-powered chatbot that detects emotional distress and safety risk in real time.
        It uses NLP, ML classification, and rule-based safety logic to assess each message
        and respond with empathy — escalating to emergency contacts when needed.
      </div>
    </div>""", unsafe_allow_html=True)

    # Tech stack
    a1, a2 = st.columns(2)
    with a1:
        for title, body in [
            ("🤖 ML Pipeline",
             "Three independent scikit-learn classifiers (TF-IDF + LinearSVC/LogisticRegression) "
             "trained on labelled datasets for Emotion, Sentiment, and Risk detection."),
            ("⚙️ Risk Engine",
             "Fuses ML output with linguistic features (urgency, intensity, repetition) "
             "and keyword banks. Applies a weighted scoring formula to produce a final risk level."),
            ("📖 Response Engine",
             "Priority-based response selector. Keyword-matched responses first (most human), "
             "falling back to risk-level guidance templates with random openers for variety."),
        ]:
            st.markdown(f"""
            <div class="about-card">
              <h3>{title}</h3>
              <p>{body}</p>
            </div>""", unsafe_allow_html=True)

    with a2:
        for title, body in [
            ("🧠 Context Memory",
             "Rolling window (last 5 turns) tracking risk and emotion history. "
             "Detects escalation trends, repeated high-risk patterns, and dominant emotions."),
            ("🚨 Safety Rules",
             "Deterministic rule engine that acts as final authority, overriding ML when "
             "explicit emergency keywords, physical abuse signals, or sustained high risk are detected."),
            ("🌐 Streamlit UI",
             "Fully client-side Streamlit app. No FastAPI server needed. "
             "Runs locally or deploys to Streamlit Cloud with a single command."),
        ]:
            st.markdown(f"""
            <div class="about-card">
              <h3>{title}</h3>
              <p>{body}</p>
            </div>""", unsafe_allow_html=True)

    # Pipeline flow
    st.markdown("""
    <div class="chart-card">
      <h4>Processing Pipeline</h4>
      <div style="display:flex;align-items:center;gap:0;flex-wrap:wrap;padding:12px 0;font-size:13px;">
    """, unsafe_allow_html=True)

    steps = [
        ("📥","Input"), ("🧹","Preprocess"), ("🔢","Vectorise"),
        ("🤖","Classify"), ("⚖️","Risk Fusion"), ("🚨","Safety Rules"),
        ("💬","Response"), ("📤","Output")
    ]
    arrows = ""
    for icon, label in steps:
        arrows += f"""
        <div style="text-align:center;padding:0 4px;">
          <div style="background:#f0f0ff;border-radius:10px;padding:8px 12px;min-width:72px;">
            <div style="font-size:20px;">{icon}</div>
            <div style="font-size:11px;color:#374151;font-weight:600;margin-top:2px;">{label}</div>
          </div>
        </div>
        <div style="font-size:18px;color:#d1d5db;padding:0 2px;align-self:center;">→</div>"""
    # remove last arrow
    arrows = arrows.rsplit("→", 1)[0]
    st.markdown(f"{arrows}</div></div>", unsafe_allow_html=True)

    # Tech stack badges
    st.markdown("""
    <div class="chart-card">
      <h4>Tech Stack</h4>
      <div style="display:flex;flex-wrap:wrap;gap:8px;padding:4px 0;">
    """, unsafe_allow_html=True)
    for tech, color in [
        ("Python 3.12","#3776ab"),("Streamlit","#ff4b4b"),("scikit-learn","#f89939"),
        ("NLTK","#3c6e71"),("TF-IDF","#6366f1"),("joblib","#10b981"),
        ("pandas","#130654"),("NumPy","#4dabcf"),
    ]:
        st.markdown(f"""
        <span style="background:{color};color:white;padding:6px 14px;
                     border-radius:20px;font-size:12px;font-weight:600;">{tech}</span>""",
                    unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────────────────
page = st.session_state.page
if page == "chat":
    page_chat()
elif page == "admin":
    page_admin()
elif page == "about":
    page_about()
