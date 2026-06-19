import streamlit as st
import requests
import plotly.graph_objects as go
from audio_recorder_streamlit import audio_recorder

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CEFR Speech Analyzer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = "http://127.0.0.1:5000"

PARAMETERS = [
    "Vowel Sounds", "Consonant Sounds", "Word Stress", "Intonation",
    "Sentence Construction", "Comprehensibility (Accent)", "Clarity of Speech",
    "Projection of Voice", "Avoided Fillers/Foghorns", "Confidence",
    "Rate of Speech", "Thought Flow"
]

SHORT_PARAMS = [
    "Vowel", "Consonant", "Stress", "Intonation",
    "Sentence", "Accent", "Clarity", "Projection",
    "Fillers", "Confidence", "Rate", "Thought Flow"
]

PALETTE = {
    "bg":        "#0D1117",
    "surface":   "#161B22",
    "surface2":  "#1C2333",
    "border":    "#30363D",
    "accent":    "#2F81F7",
    "success":   "#3FB950",
    "warning":   "#D29922",
    "danger":    "#F85149",
    "text":      "#E6EDF3",
    "muted":     "#7D8590",
    "highlight": "#1F6FEB",
}

LLM_COLORS = {
    "Groq (Llama 3.3 70B)":  "#F78166",
    "Gemini 2.5 Flash Lite": "#79C0FF",
    "Ollama (Gemma4 31B)":   "#56D364",
}

CEFR_COLORS = {
    "A1": "#F85149", "A2": "#FF8C42",
    "B1": "#D29922", "B2": "#3FB950",
    "C1": "#2F81F7", "C2": "#BC8CFF"
}

CEFR_LABELS = {
    "A1": "Beginner", "A2": "Elementary",
    "B1": "Intermediate", "B2": "Upper-Intermediate",
    "C1": "Advanced", "C2": "Proficient"
}

# ── Session State Init ─────────────────────────────────────────────────────────
if "audio_bytes"    not in st.session_state: st.session_state.audio_bytes    = None
if "audio_filename" not in st.session_state: st.session_state.audio_filename = "audio.wav"
if "audio_mime"     not in st.session_state: st.session_state.audio_mime     = "audio/wav"
if "result"         not in st.session_state: st.session_state.result         = None

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {PALETTE['bg']};
    color: {PALETTE['text']};
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1.5rem !important; max-width: 1200px; }}

[data-testid="metric-container"] {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    padding: 16px 20px;
}}
[data-testid="metric-container"] label {{
    color: {PALETTE['muted']} !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {PALETTE['text']} !important;
    font-size: 1.5rem !important;
    font-weight: 700;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {PALETTE['surface']};
    border-radius: 8px;
    padding: 4px;
    border: 1px solid {PALETTE['border']};
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    color: {PALETTE['muted']};
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.88rem;
}}
.stTabs [aria-selected="true"] {{
    background: {PALETTE['highlight']} !important;
    color: white !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, #1F6FEB, #388BFD) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: opacity 0.2s !important;
}}
.stButton > button:hover {{ opacity: 0.88 !important; }}
.stButton > button:disabled {{
    background: {PALETTE['surface2']} !important;
    color: {PALETTE['muted']} !important;
    opacity: 0.6 !important;
}}

.stTextInput > div > div > input {{
    background: {PALETTE['surface']} !important;
    border: 1px solid {PALETTE['border']} !important;
    border-radius: 8px !important;
    color: {PALETTE['text']} !important;
    font-size: 0.95rem !important;
    padding: 10px 14px !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {PALETTE['accent']} !important;
    box-shadow: 0 0 0 3px {PALETTE['accent']}22 !important;
}}
.stTextInput label {{ color: {PALETTE['muted']} !important; font-size: 0.82rem !important; }}

.stFileUploader {{
    background: {PALETTE['surface']};
    border: 1px dashed {PALETTE['border']};
    border-radius: 10px;
    padding: 16px;
}}

.card {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}}
.card-winner {{
    border-color: {PALETTE['accent']} !important;
    box-shadow: 0 0 28px {PALETTE['accent']}28;
}}
.section-header {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {PALETTE['muted']};
    margin: 28px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid {PALETTE['border']};
}}
.cefr-pill {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.88rem;
    letter-spacing: 1.5px;
}}
.transcript-box {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    padding: 16px 20px;
    font-size: 0.9rem;
    color: {PALETTE['text']};
    line-height: 1.8;
    max-height: 140px;
    overflow-y: auto;
}}
.param-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px solid {PALETTE['surface2']};
    font-size: 0.82rem;
}}
.score-bar-bg {{
    background: {PALETTE['surface2']};
    border-radius: 4px;
    height: 5px;
    width: 100%;
    margin: 2px 0 7px 0;
}}
.score-bar-fill {{ border-radius: 4px; height: 5px; }}
.ai-comment {{
    background: {PALETTE['surface2']};
    border-left: 3px solid {PALETTE['accent']};
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: {PALETTE['muted']};
    line-height: 1.6;
    margin-top: 12px;
    font-style: italic;
}}
.input-panel {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 12px;
    padding: 20px 24px;
}}
.avg-score-bar-track {{
    background: {PALETTE['surface2']};
    border-radius: 6px;
    height: 8px;
    width: 100%;
    margin: 6px 0 2px 0;
    overflow: hidden;
}}
.avg-score-bar-fill {{
    height: 8px;
    border-radius: 6px;
    transition: width 0.4s ease;
}}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_cefr(total):
    for level, (lo, hi) in [("A1",(0,10)),("A2",(11,20)),("B1",(21,30)),
                              ("B2",(31,40)),("C1",(41,50)),("C2",(51,60))]:
        if lo <= total <= hi:
            return level
    return "A1"

def score_color(score):
    if score <= 1: return PALETTE["danger"]
    if score == 2: return PALETTE["warning"]
    if score == 3: return "#4FC3F7"
    if score == 4: return PALETTE["success"]
    return PALETTE["accent"]

def llm_color(name):
    for k, v in LLM_COLORS.items():
        if k in name or name in k:
            return v
    return PALETTE["accent"]

def hex_rgba(hex_color, alpha=0.12):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Charts ─────────────────────────────────────────────────────────────────────
def gauge_chart(name, total, cefr):
    color = llm_color(name)
    cefr_color = CEFR_COLORS.get(cefr, PALETTE["accent"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total,
        number={"font": {"size": 34, "color": color, "family": "Inter"}, "suffix": "/60"},
        gauge={
            "axis": {"range": [0, 60], "tickwidth": 1, "tickcolor": PALETTE["muted"],
                     "tickfont": {"color": PALETTE["muted"], "size": 9}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": PALETTE["surface2"],
            "bordercolor": PALETTE["border"],
            "steps": [
                {"range": [0, 10],  "color": "rgba(248,81,73,0.09)"},
                {"range": [10, 20], "color": "rgba(255,140,66,0.09)"},
                {"range": [20, 30], "color": "rgba(210,153,34,0.09)"},
                {"range": [30, 40], "color": "rgba(63,185,80,0.09)"},
                {"range": [40, 50], "color": "rgba(47,129,247,0.09)"},
                {"range": [50, 60], "color": "rgba(188,140,255,0.09)"},
            ],
            "threshold": {"line": {"color": cefr_color, "width": 3},
                          "thickness": 0.85, "value": total}
        }
    ))
    fig.update_layout(
        paper_bgcolor=PALETTE["surface"],
        plot_bgcolor=PALETTE["surface"],
        height=210,
        margin=dict(t=16, b=8, l=16, r=16),
        font={"family": "Inter", "color": PALETTE["text"]},
        annotations=[dict(
            x=0.5, y=0.15,
            text=f'<b>{cefr}</b>',
            showarrow=False,
            font=dict(size=20, color=cefr_color, family="Inter"),
            xanchor="center"
        )]
    )
    return fig

def radar_chart(done):
    fig = go.Figure()
    theta = SHORT_PARAMS + [SHORT_PARAMS[0]]
    for name, result in done.items():
        scores = result.get("scores", {})
        values = [scores.get(p, 0) for p in PARAMETERS] + [scores.get(PARAMETERS[0], 0)]
        color = llm_color(name)
        fig.add_trace(go.Scatterpolar(
            r=values, theta=theta,
            fill="toself",
            name=name.split("(")[0].strip(),
            line=dict(color=color, width=2),
            fillcolor=hex_rgba(color, 0.15),
            marker=dict(size=5, color=color)
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=PALETTE["surface2"],
            radialaxis=dict(visible=True, range=[0, 5],
                            tickfont=dict(color=PALETTE["muted"], size=9),
                            gridcolor=PALETTE["border"], linecolor=PALETTE["border"]),
            angularaxis=dict(tickfont=dict(color=PALETTE["text"], size=10),
                             gridcolor=PALETTE["border"], linecolor=PALETTE["border"])
        ),
        paper_bgcolor=PALETTE["surface"],
        plot_bgcolor=PALETTE["surface"],
        legend=dict(font=dict(color=PALETTE["text"], size=11), bgcolor=PALETTE["surface"],
                    bordercolor=PALETTE["border"], borderwidth=1),
        height=400,
        margin=dict(t=40, b=30, l=60, r=60),
        font=dict(family="Inter", color=PALETTE["text"]),
        title=dict(text="Parameter Profile — All LLMs",
                   font=dict(size=13, color=PALETTE["muted"]), x=0.5)
    )
    return fig

def bar_chart(done):
    fig = go.Figure()
    for name, result in done.items():
        scores = result.get("scores", {})
        values = [scores.get(p, 0) for p in PARAMETERS]
        color = llm_color(name)
        fig.add_trace(go.Bar(
            name=name.split("(")[0].strip(),
            x=SHORT_PARAMS,
            y=values,
            marker=dict(color=color, opacity=0.85),
            text=values,
            textposition="outside",
            textfont=dict(size=9, color=PALETTE["muted"]),
        ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor=PALETTE["surface"],
        plot_bgcolor=PALETTE["surface"],
        height=380,
        margin=dict(t=40, b=60, l=40, r=20),
        font=dict(family="Inter", color=PALETTE["text"]),
        legend=dict(font=dict(color=PALETTE["text"], size=11), bgcolor=PALETTE["surface"],
                    bordercolor=PALETTE["border"], borderwidth=1,
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickfont=dict(color=PALETTE["text"], size=10),
                   gridcolor=PALETTE["border"], linecolor=PALETTE["border"]),
        yaxis=dict(range=[0, 6], tickfont=dict(color=PALETTE["muted"], size=10),
                   gridcolor=PALETTE["border"], linecolor=PALETTE["border"],
                   title="Score (0–5)"),
        title=dict(text="Parameter Scores by LLM",
                   font=dict(size=13, color=PALETTE["muted"]), x=0.5),
        bargap=0.18, bargroupgap=0.06
    )
    return fig

# ── Score Card ─────────────────────────────────────────────────────────────────
def render_card(name, result, is_winner):
    color     = llm_color(name)
    cefr      = result.get("cefr", "?")
    total     = result.get("total", 0)
    latency   = result.get("latency", 0)
    summary   = result.get("summary", "")
    scores    = result.get("scores", {})
    cefr_col  = CEFR_COLORS.get(cefr, PALETTE["accent"])
    win_class = "card-winner" if is_winner else ""

    st.markdown(f"""
    <div class="card {win_class}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
            <div>
                <div style="color:{color};font-weight:700;font-size:0.88rem;margin-bottom:6px;">
                    {"🏆 " if is_winner else ""}{name.split("(")[0].strip()}
                </div>
                <span class="cefr-pill"
                      style="background:{cefr_col}18;color:{cefr_col};border:1px solid {cefr_col}44;">
                    {cefr}
                </span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.8rem;font-weight:700;font-family:'JetBrains Mono';color:{color};">
                    {total}<span style="font-size:0.82rem;color:{PALETTE['muted']};">/60</span>
                </div>
                <div style="color:{PALETTE['muted']};font-size:0.72rem;">
                    {latency}s · {round((total/60)*100, 1)}%
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for param in PARAMETERS:
        score  = scores.get(param, 0)
        bar_c  = score_color(score)
        bar_w  = (score / 5) * 100
        st.markdown(f"""
        <div class="param-row">
            <span style="color:{PALETTE['muted']};">{param}</span>
            <span style="font-weight:600;color:{PALETTE['text']};
                  font-family:'JetBrains Mono';font-size:0.82rem;">{score}/5</span>
        </div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{bar_w}%;background:{bar_c};"></div>
        </div>
        """, unsafe_allow_html=True)

    if summary:
        st.markdown(f'<div class="ai-comment">💬 {summary}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:4px;">
    <div style="background:linear-gradient(135deg,#1F6FEB,#388BFD);border-radius:12px;
         width:46px;height:46px;display:flex;align-items:center;justify-content:center;
         font-size:1.5rem;">🎙️</div>
    <div>
        <div style="font-size:1.65rem;font-weight:700;color:{PALETTE['text']};">
            CEFR Speech Analyzer
        </div>
        <div style="font-size:0.82rem;color:{PALETTE['muted']};">
            Multi-LLM English Proficiency Evaluation System
        </div>
    </div>
</div>
<div style="height:1px;background:{PALETTE['border']};margin:16px 0 28px 0;"></div>
""", unsafe_allow_html=True)

# ── Scenarios ─────────────────────────────────────────────────────────────────
SCENARIOS = [
    {"type": "💼 Professional", "topic": "Describe your dream job",
     "prompt": "Talk about your ideal career, what skills it requires, why you are drawn to it, and how you plan to get there."},
    {"type": "💼 Professional", "topic": "A time you solved a difficult problem at work or in a team",
     "prompt": "Describe the situation, what the challenge was, how you approached it, and what the outcome was."},
    {"type": "💼 Professional", "topic": "How would you handle a disagreement with a colleague?",
     "prompt": "Walk through your approach to conflict resolution, communication style, and how you ensure a positive outcome."},
    {"type": "🎓 Academic", "topic": "Explain a concept you recently learned",
     "prompt": "Pick any topic from your studies and explain it as if you were teaching it to someone who knows nothing about it."},
    {"type": "🎓 Academic", "topic": "Should universities make attendance mandatory?",
     "prompt": "Share your opinion, give at least two reasons supporting your view, and acknowledge the other side of the argument."},
    {"type": "🎓 Academic", "topic": "How has technology changed the way students learn?",
     "prompt": "Discuss both the benefits and drawbacks of technology in education based on your own experience."},
    {"type": "🌍 General", "topic": "Describe a place you have visited or would like to visit",
     "prompt": "Talk about the location, what makes it special, what you did or would do there, and why you would recommend it."},
    {"type": "🌍 General", "topic": "What is a hobby or skill you are passionate about?",
     "prompt": "Explain what the hobby is, how you got into it, what you enjoy most about it, and what you have learned from it."},
    {"type": "🌍 General", "topic": "Talk about a person who has influenced you greatly",
     "prompt": "Describe who they are, what they did, how they impacted your life, and what you have taken away from knowing them."},
]

if "scenario_idx" not in st.session_state:
    st.session_state.scenario_idx = 0

scenario = SCENARIOS[st.session_state.scenario_idx]

st.markdown(f'<div class="section-header">🎯 Speaking Prompt</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
     border-radius:12px;padding:20px 24px;margin-bottom:8px;">
    <span style="background:{PALETTE['highlight']}22;color:{PALETTE['accent']};
          border:1px solid {PALETTE['accent']}44;
          padding:3px 10px;border-radius:12px;font-size:0.75rem;font-weight:600;">
        {scenario['type']}
    </span>
    <div style="font-size:1.1rem;font-weight:700;color:{PALETTE['text']};margin:10px 0 6px 0;">
        {scenario['topic']}
    </div>
    <div style="font-size:0.85rem;color:{PALETTE['muted']};line-height:1.6;">
        {scenario['prompt']}
    </div>
    <div style="margin-top:14px;padding-top:12px;border-top:1px solid {PALETTE['border']};
         font-size:0.78rem;color:{PALETTE['muted']};">
        ⏱️ Speak for <b style="color:{PALETTE['text']};">1 to 3 minutes</b> on this topic
    </div>
</div>
""", unsafe_allow_html=True)

col_btn, _ = st.columns([1, 4])
with col_btn:
    if st.button("🎲 New Prompt"):
        st.session_state.scenario_idx = (st.session_state.scenario_idx + 1) % len(SCENARIOS)
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Input Panel ───────────────────────────────────────────────────────────────
st.markdown('<div class="input-panel">', unsafe_allow_html=True)

col_name, col_audio = st.columns([1, 2], gap="large")

with col_name:
    st.markdown(f'<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:{PALETTE["muted"]};margin-bottom:8px;">👤 Speaker Name</div>', unsafe_allow_html=True)
    username = st.text_input(
        "Full name",
        placeholder="Your Name",
        label_visibility="collapsed",
        key="username_input"
    )

with col_audio:
    st.markdown(f'<div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:{PALETTE["muted"]};margin-bottom:8px;">🎤 Audio Input</div>', unsafe_allow_html=True)
    tab_rec, tab_up = st.tabs(["🎙️ Record", "📁 Upload"])

    with tab_rec:
        st.markdown(
            f"<div style='color:{PALETTE['muted']};font-size:0.82rem;margin:8px 0;'>"
            "Click the mic to start recording. It stops automatically after 3s of silence.</div>",
            unsafe_allow_html=True
        )
        recorded = audio_recorder(
            pause_threshold=3.0,
            sample_rate=16000,
            text="",
            recording_color=PALETTE["accent"],
            neutral_color=PALETTE["border"],
            icon_size="2x"
        )
        if recorded:
            st.session_state.audio_bytes    = recorded
            st.session_state.audio_filename = "recording.wav"
            st.session_state.audio_mime     = "audio/wav"
            st.audio(recorded, format="audio/wav")
            st.success("✅ Recording captured!")

    with tab_up:
        uploaded = st.file_uploader(
            "Audio file",
            type=["mp3", "wav", "m4a", "ogg", "flac", "webm"],
            label_visibility="collapsed",
            key="audio_upload"
        )
        if uploaded:
            st.session_state.audio_bytes    = uploaded.read()
            st.session_state.audio_filename = uploaded.name
            st.session_state.audio_mime     = uploaded.type or "audio/mpeg"
            st.audio(st.session_state.audio_bytes, format=st.session_state.audio_mime)

st.markdown("</div>", unsafe_allow_html=True)

# ── Analyze Button ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
ready = bool(st.session_state.audio_bytes) and bool(username.strip())
analyze_btn = st.button(
    "🚀  Analyze Speech",
    use_container_width=True,
    disabled=not ready
)

if not ready:
    missing = []
    if not username.strip():          missing.append("speaker name")
    if not st.session_state.audio_bytes: missing.append("audio")
    st.markdown(
        f"<div style='text-align:center;font-size:0.8rem;color:{PALETTE['muted']};margin-top:6px;'>"
        f"Please provide: {' and '.join(missing)}</div>",
        unsafe_allow_html=True
    )

# ── Run Analysis ──────────────────────────────────────────────────────────────
if analyze_btn and ready:
    with st.spinner("Transcribing with Groq Whisper and scoring across LLMs…"):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/analyze",
                files={"audio": (
                    st.session_state.audio_filename,
                    st.session_state.audio_bytes,
                    st.session_state.audio_mime
                )},
                data={"username": username.strip()},
                timeout=300
            )
            resp.raise_for_status()
            st.session_state.result = resp.json()
        except Exception as e:
            st.error(f"❌ Backend error: {e}")
            st.stop()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    data        = st.session_state.result
    transcript  = data.get("transcript", "")
    features    = data.get("features", {})
    llm_results = data.get("llm_results", {})
    done        = {k: v for k, v in llm_results.items() if v.get("status") == "done"}
    errors      = {k: v for k, v in llm_results.items() if v.get("status") == "error"}

    # ── Transcript ─────────────────────────────────────────────────────────────
    st.markdown(f'<div class="section-header">📝 Transcript</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="transcript-box">{transcript}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Duration",       f"{features.get('duration_seconds', 0)}s")
    m2.metric("Word Count",     features.get("word_count", 0))
    m3.metric("Speaking Rate",  f"{features.get('wpm', 0)} WPM")
    m4.metric("Fillers Detected", features.get("filler_count", 0))

    if not done:
        st.warning("No LLM results available.")
    else:
        avg_total = round(sum(v["total"] for v in done.values()) / len(done), 1)
        consensus = get_cefr(int(avg_total))
        cefr_col  = CEFR_COLORS.get(consensus, PALETTE["accent"])
        winner    = max(done, key=lambda k: done[k].get("total", 0))

        # ── Consensus Banner ───────────────────────────────────────────────────
        st.markdown(f'<div class="section-header">🏅 Consensus Score</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
             border-radius:14px;padding:24px 32px;
             display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px;">
            <div>
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;
                     color:{PALETTE['muted']};margin-bottom:8px;">Combined CEFR Level</div>
                <span style="font-size:3rem;font-weight:800;color:{cefr_col};">{consensus}</span>
                <span style="font-size:0.9rem;color:{PALETTE['muted']};margin-left:12px;">
                    {CEFR_LABELS.get(consensus, '')}
                </span>
                <div style="margin-top:10px;">
                    <div style="font-size:0.8rem;color:{PALETTE['muted']};margin-bottom:4px;">
                        Avg score: <b style="color:{PALETTE['text']};">{avg_total}/60</b>
                        &nbsp;·&nbsp; {round((avg_total/60)*100, 1)}%
                    </div>
                    <div class="avg-score-bar-track">
                        <div class="avg-score-bar-fill"
                             style="width:{round((avg_total/60)*100, 1)}%;background:{cefr_col};">
                        </div>
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:40px;flex-wrap:wrap;">
                <div style="text-align:center;">
                    <div style="font-size:1.8rem;font-weight:700;color:{PALETTE['text']};">
                        {len(done)}
                    </div>
                    <div style="font-size:0.73rem;color:{PALETTE['muted']};margin-top:2px;">
                        Models used
                    </div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.8rem;font-weight:700;color:{PALETTE['success']};">
                        {avg_total}
                    </div>
                    <div style="font-size:0.73rem;color:{PALETTE['muted']};margin-top:2px;">
                        Avg score
                    </div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.2rem;font-weight:700;color:{llm_color(winner)};">
                        {winner.split("(")[0].strip()}
                    </div>
                    <div style="font-size:0.73rem;color:{PALETTE['muted']};margin-top:2px;">
                        Top scorer
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Per-LLM Averaged Param Summary ────────────────────────────────────
        st.markdown(f'<div class="section-header">📊 Averaged Parameter Scores</div>',
                    unsafe_allow_html=True)
        avg_scores = {}
        for param in PARAMETERS:
            vals = [v["scores"].get(param, 0) for v in done.values() if "scores" in v]
            avg_scores[param] = round(sum(vals) / len(vals), 1) if vals else 0

        rows = [PARAMETERS[i:i+3] for i in range(0, len(PARAMETERS), 3)]
        for row in rows:
            cols = st.columns(len(row))
            for col, param in zip(cols, row):
                s    = avg_scores[param]
                bar_c = score_color(int(round(s)))
                bar_w = (s / 5) * 100
                col.markdown(f"""
                <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                     border-radius:10px;padding:12px 14px;margin-bottom:4px;">
                    <div style="font-size:0.72rem;color:{PALETTE['muted']};margin-bottom:6px;
                         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{param}</div>
                    <div style="font-size:1.3rem;font-weight:700;
                         font-family:'JetBrains Mono';color:{bar_c};">{s}</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill"
                             style="width:{bar_w}%;background:{bar_c};margin-top:6px;">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Per-LLM Individual Parameter Scores ──────────────────────────────
        st.markdown(f'<div class="section-header">📋 Individual LLM Parameter Scores</div>',
                    unsafe_allow_html=True)
        llm_tab_labels = [name.split("(")[0].strip() for name in done]
        llm_tabs = st.tabs(llm_tab_labels)
        for tab, (name, result) in zip(llm_tabs, done.items()):
            with tab:
                scores = result.get("scores", {})
                c = llm_color(name)
                cefr_c = CEFR_COLORS.get(result.get("cefr", "A1"), PALETTE["accent"])
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:16px;margin:10px 0 16px 0;">' +
                    f'<span style="font-size:2rem;font-weight:800;color:{c};">{result.get("total",0)}/60</span>' +
                    f'<span class="cefr-pill" style="background:{cefr_c}18;color:{cefr_c};border:1px solid {cefr_c}44;">{result.get("cefr","?")}</span>' +
                    f'<span style="font-size:0.8rem;color:{PALETTE["muted"]};">{result.get("latency",0)}s response time</span>' +
                    '</div>',
                    unsafe_allow_html=True
                )
                param_rows = [PARAMETERS[i:i+3] for i in range(0, len(PARAMETERS), 3)]
                for row in param_rows:
                    pcols = st.columns(len(row))
                    for pcol, param in zip(pcols, row):
                        s = scores.get(param, 0)
                        bar_c = score_color(s)
                        bar_w = (s / 5) * 100
                        pcol.markdown(f"""
                        <div style="background:{PALETTE['surface']};border:1px solid {PALETTE['border']};
                             border-radius:10px;padding:12px 14px;margin-bottom:4px;">
                            <div style="font-size:0.72rem;color:{PALETTE['muted']};margin-bottom:6px;
                                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{param}</div>
                            <div style="font-size:1.3rem;font-weight:700;
                                 font-family:'JetBrains Mono';color:{bar_c};">{s}/5</div>
                            <div class="score-bar-bg">
                                <div class="score-bar-fill"
                                     style="width:{bar_w}%;background:{bar_c};margin-top:6px;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                if result.get("summary"):
                    st.markdown(f'<div class="ai-comment">💬 {result["summary"]}</div>',
                                unsafe_allow_html=True)

        # ── Gauge Charts ───────────────────────────────────────────────────────
        st.markdown(f'<div class="section-header">📈 Overall Scores per LLM</div>',
                    unsafe_allow_html=True)
        gauge_cols = st.columns(len(done))
        for i, (name, result) in enumerate(done.items()):
            with gauge_cols[i]:
                lbl = name.split("(")[0].strip()
                c   = llm_color(name)
                st.markdown(
                    f"<div style='text-align:center;font-size:0.82rem;font-weight:600;"
                    f"color:{c};margin-bottom:4px;'>{lbl}</div>",
                    unsafe_allow_html=True
                )
                st.plotly_chart(
                    gauge_chart(name, result.get("total", 0), result.get("cefr", "A1")),
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

        # ── Radar + Bar ────────────────────────────────────────────────────────
        st.markdown(f'<div class="section-header">🔍 Visual Comparison</div>', unsafe_allow_html=True)
        chart_l, chart_r = st.columns([1, 1], gap="large")
        with chart_l:
            st.plotly_chart(radar_chart(done), use_container_width=True,
                            config={"displayModeBar": False})
        with chart_r:
            st.plotly_chart(bar_chart(done), use_container_width=True,
                            config={"displayModeBar": False})

        # ── Detailed LLM Score Cards ───────────────────────────────────────────
        st.markdown(f'<div class="section-header">🤖 Detailed LLM Score Cards</div>',
                    unsafe_allow_html=True)
        card_cols = st.columns(len(done))
        for i, (name, result) in enumerate(done.items()):
            with card_cols[i]:
                render_card(name, result, name == winner)

        # ── Parameter Breakdown Table ──────────────────────────────────────────
        st.markdown(f'<div class="section-header">🗂 Parameter Breakdown Table</div>',
                    unsafe_allow_html=True)
        h_cols = st.columns([2] + [1] * len(done))
        h_cols[0].markdown(
            f"<span style='font-size:0.75rem;font-weight:600;color:{PALETTE['muted']};'>"
            "PARAMETER</span>",
            unsafe_allow_html=True
        )
        for i, name in enumerate(done):
            h_cols[i+1].markdown(
                f"<span style='font-size:0.75rem;font-weight:600;color:{llm_color(name)};'>"
                f"{name.split('(')[0].strip().upper()}</span>",
                unsafe_allow_html=True
            )

        for param in PARAMETERS:
            r_cols       = st.columns([2] + [1] * len(done))
            param_scores = [done[n].get("scores", {}).get(param, 0) for n in done]
            max_s        = max(param_scores) if param_scores else 0
            r_cols[0].markdown(
                f"<span style='font-size:0.82rem;color:{PALETTE['muted']};'>{param}</span>",
                unsafe_allow_html=True
            )
            for i, name in enumerate(done):
                s    = done[name].get("scores", {}).get(param, 0)
                col  = PALETTE["success"] if s == max_s else PALETTE["text"]
                bold = "700" if s == max_s else "400"
                r_cols[i+1].markdown(
                    f"<span style='color:{col};font-weight:{bold};font-size:0.85rem;'>{s}/5</span>",
                    unsafe_allow_html=True
                )
        # ── Improvement Tips ───────────────────────────────────────────────────
        st.markdown(f'<div class="section-header">💡 Areas of Improvement</div>', unsafe_allow_html=True)

        if "improvements" not in st.session_state:
            st.session_state.improvements = None

        if st.button("💡 Get Improvement Tips"):
            with st.spinner("Generating personalized improvement tips..."):
                try:
                    imp_resp = requests.post(
                        f"{BACKEND_URL}/improve",
                        json={"transcript": transcript, "avg_scores": avg_scores},
                        timeout=60
                    )
                    imp_resp.raise_for_status()
                    st.session_state.improvements = imp_resp.json()
                except Exception as e:
                    st.error(f"❌ Could not fetch improvement tips: {e}")

        if st.session_state.improvements:
            imp_data = st.session_state.improvements
            improvements = imp_data.get("improvements", [])
            encouragement = imp_data.get("overall_encouragement", "")

            if improvements:
                for item in improvements:
                    st.markdown(f"""
                    <div class="card" style="margin-bottom:12px;">
                        <div style="font-size:1rem;font-weight:700;color:{PALETTE['accent']};margin-bottom:8px;">
                            🎯 {item.get('parameter', '')}
                        </div>
                        <div style="font-size:0.85rem;color:{PALETTE['muted']};margin-bottom:8px;line-height:1.6;">
                            {item.get('why_it_matters', '')}
                        </div>
                        <div style="font-size:0.85rem;color:{PALETTE['text']};margin-bottom:6px;line-height:1.6;">
                            <b style="color:{PALETTE['success']};">Tip:</b> {item.get('tip', '')}
                        </div>
                        <div style="font-size:0.85rem;color:{PALETTE['text']};line-height:1.6;">
                            <b style="color:{PALETTE['warning']};">Practice:</b> {item.get('exercise', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No major weak areas detected — great performance!")

            if encouragement:
                st.markdown(f"""
                <div style="background:{hex_rgba(PALETTE['accent'], 0.1)};border:1px solid {PALETTE['accent']}44;
                     border-radius:10px;padding:16px 20px;margin-top:12px;font-size:0.88rem;
                     color:{PALETTE['text']};line-height:1.7;">
                    ✨ {encouragement}
                </div>
                """, unsafe_allow_html=True)
        

    if errors:
        st.markdown("---")
        st.markdown(f'<div class="section-header">⚠️ LLM Errors</div>', unsafe_allow_html=True)
        for name, err in errors.items():
            st.error(f"**{name}**: {err.get('error', 'Unknown error')}")