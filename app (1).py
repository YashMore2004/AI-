import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import re

analyzer = SentimentIntensityAnalyzer()

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Anxiety Checker — Exam Anxiety Detector",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a40 55%, #0d1117 100%);
    min-height: 100vh;
}

/* Hero */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.2rem;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #38bdf8, #34d399, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem;
}




/* Divider */
.fancy-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.45), transparent);
    margin: 1.4rem 0;
}

/* Section label */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.5rem;
}

/* Textarea */
.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(167,139,250,0.35) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.97rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: none !important;
    resize: none !important;
    caret-color: #a78bfa !important;
}
.stTextArea textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.15) !important;
}
.stTextArea label { color: #cbd5e1 !important; font-weight: 500 !important; }

/* Primary button */
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
    width: 100% !important;
}

/* Streamlit native alerts — give them dark glass look */
.stAlert {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.05) !important;
    border-width: 1px !important;
}

/* Native progress bar */
.stProgress > div > div > div > div {
    border-radius: 999px !important;
}
.stProgress > div > div {
    border-radius: 999px !important;
    height: 10px !important;
    background: rgba(255,255,255,0.08) !important;
}

/* Tip card */
.tip-card {
    background: rgba(167,139,250,0.06);
    border-left: 3px solid #7c3aed;
    border-radius: 0 10px 10px 0;
    padding: 0.65rem 1rem;
    margin-bottom: 0.55rem;
    color: #cbd5e1;
    font-size: 0.93rem;
    line-height: 1.55;
}

/* Result badge */
.level-badge {
    display: inline-block;
    padding: 0.35rem 1.1rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.88rem;
    letter-spacing: 0.06em;
    margin-bottom: 0.5rem;
}
.badge-low      { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid #34d399; }
.badge-moderate { background: rgba(251,191,36,0.13); color: #fbbf24; border: 1px solid #fbbf24; }
.badge-high     { background: rgba(248,113,113,0.13); color: #f87171; border: 1px solid #f87171; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.97) !important;
    border-right: 1px solid rgba(167,139,250,0.12) !important;
}
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }

/* History card */
.history-card {
    background: rgba(167,139,250,0.07);
    border: 1px solid rgba(167,139,250,0.15);
    border-radius: 10px;
    padding: 0.6rem 0.85rem;
    margin-bottom: 0.6rem;
}

/* Metrics row */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.25rem;
}
.metric-box {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.metric-box .mval { font-size: 1.6rem; font-weight: 700; }
.metric-box .mlbl { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.09em; margin-top: 0.15rem; }

/* Footer */
.footer-text {
    text-align: center;
    color: #334155;
    font-size: 0.76rem;
    margin-top: 0.5rem;
}

/* Layout */
.main .block-container { padding: 0 1.5rem 3rem !important; max-width: 720px; }

/* Hide default Streamlit footer/menu */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Anxiety keywords ─────────────────────────────────────────────────────────
ANXIETY_KEYWORDS = {
    'nervous': 0.15, 'panic': 0.25, 'fail': 0.20, 'failing': 0.20,
    'anxious': 0.15, "can't sleep": 0.20, 'cannot sleep': 0.20,
    'scared': 0.15, 'terrified': 0.25, 'worried': 0.10,
    'overwhelmed': 0.20, 'blank': 0.15, 'sweat': 0.10,
    'racing heart': 0.20, 'stress': 0.15, 'stressed': 0.15,
    'pressure': 0.10, 'dread': 0.20, 'give up': 0.25, 'doom': 0.25
}

def analyze_anxiety(text):
    if not text.strip():
        return 0.0, "Low"
    text_lower = text.lower()
    sentiment  = analyzer.polarity_scores(text)
    compound   = sentiment['compound']
    base_score = abs(compound) if compound < 0 else 0.0
    boost = 0.0
    for keyword, weight in ANXIETY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            boost += weight
    final_score = min(1.0, base_score + boost)
    if final_score < 0.3:
        level = "Low"
    elif final_score <= 0.6:
        level = "Moderate"
    else:
        level = "High"
    return final_score, level

def get_tips(level):
    if level == "Low":
        return [
            "✅  You're calm and composed — maintain that steady focus.",
            "📖  Do a light review of key concepts; avoid last-minute cramming.",
            "💤  Prioritise deep sleep tonight. Rest is your best revision tool."
        ]
    elif level == "Moderate":
        return [
            "⏸️  Step away from your desk for 10–15 minutes and breathe.",
            "💧  Hydrate, stretch, and release physical tension.",
            "🌟  Recall what you already know well and build confidence from there."
        ]
    else:
        return [
            "🫁  Box breathe: inhale 4 s → hold 4 s → exhale 4 s. Repeat 4 ×.",
            "🌿  Ground yourself: name 3 things you see, 2 you can touch, 1 you hear.",
            "🛑  Stop studying now. A rested brain outperforms an exhausted one."
        ]

# ─── Session state ─────────────────────────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state.history = []

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂 Session History")
    st.markdown("<hr style='border-color:rgba(167,139,250,0.2);margin:0.5rem 0 1rem'>", unsafe_allow_html=True)

    if st.button("🗑 Clear History", use_container_width=True):
        st.session_state.history = []
        st.success("History cleared.")

    recent = list(reversed(st.session_state.history))[:5]
    if not recent:
        st.markdown(
            "<p style='color:#475569;font-size:0.84rem;text-align:center;margin-top:1rem'>"
            "No analyses yet.</p>",
            unsafe_allow_html=True
        )
    for item in recent:
        color = {"Low": "#34d399", "Moderate": "#fbbf24", "High": "#f87171"}.get(item['level'], "#a78bfa")
        st.markdown(f"""
        <div class="history-card">
            <div style="font-size:0.82rem;font-weight:600;color:{color}">{item['level']} · {item['score']:.2f}</div>
            <div style="font-size:0.7rem;color:#475569">{item['timestamp']}</div>
            <div style="font-size:0.8rem;color:#64748b;font-style:italic;margin-top:0.2rem">
                "{item['text'][:48]}…"
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">Anxiety Checker</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

# ─── Input Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📝 Share Your Feelings</div>', unsafe_allow_html=True)

user_input = st.text_area(
    "How are you feeling about your upcoming exam?",
    height=150,
    placeholder="e.g. I've been studying hard but I'm terrified I'll blank out during the paper tomorrow…",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_clicked = st.button("✦  Analyse My Feelings", use_container_width=True)

# ─── Results ───────────────────────────────────────────────────────────────────
if analyze_clicked:
    if not user_input.strip():
        st.error("⚠️ Please enter how you're feeling before running the analysis.")
    else:
        score, level = analyze_anxiety(user_input)

        # Save to history
        st.session_state.history.append({
            "text": user_input,
            "score": score,
            "level": level,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })

        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

        # ── Level headline ───────────────────────────────────────────────────
        st.markdown('<div class="section-label">📊 Analysis Results</div>', unsafe_allow_html=True)

        badge_class = {"Low": "badge-low", "Moderate": "badge-moderate", "High": "badge-high"}[level]
        level_msg   = {
            "Low":      "You appear calm and composed. Great mindset heading into your exam!",
            "Moderate": "Some tension detected — perfectly normal. A few small resets will help.",
            "High":     "High anxiety detected. Please pause and take care of yourself right now."
        }[level]
        level_emoji = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}[level]

        st.markdown(
            f'<span class="level-badge {badge_class}">{level_emoji}  {level} Anxiety</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='color:#94a3b8;font-size:0.93rem;margin:0.25rem 0 0.75rem'>{level_msg}</p>",
            unsafe_allow_html=True
        )

        # ── Metric boxes ─────────────────────────────────────────────────────
        pct       = int(score * 100)
        pct_color = {"Low": "#34d399", "Moderate": "#fbbf24", "High": "#f87171"}[level]
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="mval" style="color:{pct_color}">{pct}%</div>
                <div class="mlbl">Anxiety Score</div>
            </div>
            <div class="metric-box">
                <div class="mval" style="color:#a78bfa">{level}</div>
                <div class="mlbl">Severity Level</div>
            </div>
            <div class="metric-box">
                <div class="mval" style="color:#38bdf8">{len(st.session_state.history)}</div>
                <div class="mlbl">Analyses Today</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Native Streamlit progress bar ────────────────────────────────────
        st.progress(score)
        st.caption(f"**Anxiety score:** {score:.2f} / 1.00")

        # ── Tips ─────────────────────────────────────────────────────────────
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">💡 Personalised Calming Tips</div>', unsafe_allow_html=True)
        for tip in get_tips(level):
            st.markdown(f'<div class="tip-card">{tip}</div>', unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='footer-text'>Anxiety Checker · Built with VADER NLP · "
    "Not a substitute for professional mental health support.</div>",
    unsafe_allow_html=True
)
