# src/ui/streamlit_app.py
# Round 2 — Visual Polish
# Added: animated gradient bg, floating particles, pulsing cover glow,
#        hover glow on rows, arc/ring emotion chart, typing animation

import os
import base64
import random
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from datetime import datetime

from src.pipeline.generate_playlist import generate_playlist
from src.ui.emotion_messages import get_support_message
from src.evaluation.evaluator import measure_response_time, get_full_evaluation

@st.cache_resource(show_spinner="Starting up LYRA's emotion brain... ☕ this takes a few seconds")
def load_transformer():
    from src.emotion_detection.transformer_detector import _load_pipeline
    return _load_pipeline()

load_transformer()

# ── Try importing plotly — used for arc chart ─────────────────────────────────
try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ── Asset maps ────────────────────────────────────────────────────────────────
COVER_MAP = {
    "calm":     [
        "assets/covers/calm.png",
        "assets/covers/calm1.png",
        "assets/covers/calm2.png",
        "assets/covers/calm3.png",
        "assets/covers/calm4.png",
        "assets/covers/calm5.png",
        "assets/covers/calm6.png",
        "assets/covers/calm7.png",
        "assets/covers/calm8.png",
        "assets/covers/calm9.png",
        "assets/covers/calm10.png",
    ],
    "happy":    [
        "assets/covers/happy.png",
        "assets/covers/happy1.png",
        "assets/covers/happy2.png",
        "assets/covers/happy3.png",
        "assets/covers/happy4.png",
        "assets/covers/happy5.png",
        "assets/covers/happy6.png",
        "assets/covers/happy7.png",
        "assets/covers/happy8.png",
        "assets/covers/happy9.png",
        "assets/covers/happy10.png",
    ],
    "sad":      [
        "assets/covers/sad.png",
        "assets/covers/sad1.png",
        "assets/covers/sad2.png",
        "assets/covers/sad3.png",
        "assets/covers/sad4.png",
        "assets/covers/sad5.png",
        "assets/covers/sad6.png",
        "assets/covers/sad7.png",
        "assets/covers/sad8.png",
        "assets/covers/sad9.png",
        "assets/covers/sad10.png",
        "assets/covers/sad11.png",
    ],
    "angry":    [
        "assets/covers/angry.png",
        "assets/covers/angry1.png",
        "assets/covers/angry2.png",
        "assets/covers/angry3.png",
        "assets/covers/angry4.png",
        "assets/covers/angry5.png",
        "assets/covers/angry6.png",
        "assets/covers/angry7.png",
        "assets/covers/angry8.png",
        "assets/covers/angry9.png",
        "assets/covers/angry10.png",
        "assets/covers/angry11.png",
    ],
    "anxious":  [
        "assets/covers/anxious.png",
        "assets/covers/anxious1.png",
        "assets/covers/anxious2.png",
        "assets/covers/anxious3.png",
        "assets/covers/anxious4.png",
        "assets/covers/anxious5.png",
        "assets/covers/anxious6.png",
        "assets/covers/anxious7.png",
        "assets/covers/anxious8.png",
        "assets/covers/anxious9.png",
        "assets/covers/anxious10.png",
        "assets/covers/anxious11.png",
        "assets/covers/anxious12.png",
        "assets/covers/anxious13.png",
    ],
    "stressed": [
        "assets/covers/stressed.png",
        "assets/covers/stressed1.png",
        "assets/covers/stressed2.png",
        "assets/covers/stressed3.png",
        "assets/covers/stressed4.png",
        "assets/covers/stressed5.png",
        "assets/covers/stressed6.png",
        "assets/covers/stressed7.png",
        "assets/covers/stressed8.png",
        "assets/covers/stressed9.png",
        "assets/covers/stressed10.png",
        "assets/covers/stressed11.png",
    ],
    "excited":  [
        "assets/covers/excited.png",
        "assets/covers/excited1.png",
        "assets/covers/excited2.png",
        "assets/covers/excited3.png",
        "assets/covers/excited4.png",
        "assets/covers/excited5.png",
        "assets/covers/excited6.png",
        "assets/covers/excited7.png",
        "assets/covers/excited8.png",
        "assets/covers/excited9.png",
        "assets/covers/excited10.png",
    ],
    "neutral":  [
        "assets/covers/neutral.png",
        "assets/covers/neutral1.png",
        "assets/covers/neutral2.png",
        "assets/covers/neutral3.png",
        "assets/covers/neutral4.png",
        "assets/covers/neutral5.png",
        "assets/covers/neutral6.png",
    ],
    "romance":  [
        "assets/covers/romance.png",
        "assets/covers/romance1.png",
        "assets/covers/romance2.png",
        "assets/covers/romance3.png",
        "assets/covers/romance4.png",
        "assets/covers/romance5.png",
        "assets/covers/romance6.png",
        "assets/covers/romance7.png",
        "assets/covers/romance8.png",
        "assets/covers/romance9.png",
        "assets/covers/romance10.png",
    ],
    "motivated": [
        "assets/covers/motivated.png",
        "assets/covers/motivated1.png",
        "assets/covers/motivated2.png",
        "assets/covers/motivated3.png",
        "assets/covers/motivated4.png",
        "assets/covers/motivated5.png",
        "assets/covers/motivated6.png",
        "assets/covers/motivated7.png",
        "assets/covers/motivated8.png",
        "assets/covers/motivated9.png",
        "assets/covers/motivated10.png",
    ],
}

def get_cover_path(emotion: str) -> str:
    """
    Returns a random cover image path for the given emotion.
    Falls back to neutral if emotion not found or image missing.
    """
    options = COVER_MAP.get(emotion, COVER_MAP["neutral"])
    # Filter to only existing files
    existing = [p for p in options if os.path.exists(p)]
    if not existing:
        existing = [p for p in COVER_MAP["neutral"] if os.path.exists(p)]
    if not existing:
        return None
    return random.choice(existing)

CONTEXT_ICONS = {
    "study":      "📚", "workout":    "🏋️", "sleep":       "🌙",
    "heartbreak": "💔", "motivation": "🚀", "relaxation":  "🌿",
    "anxious":    "🌪️", "general":    "🎵", "anger":       "🔥",
    "romance": "🌹",
}

CONTEXT_ADJUSTMENT_LABELS = {
    "study":      "Reduced energy & tempo for focus",
    "workout":    "Boosted energy & tempo for performance",
    "sleep":      "Minimised energy & tempo for drifting off",
    "heartbreak": "Softened emotional profile for comfort",
    "motivation": "Lifted valence & energy for drive",
    "relaxation": "Eased energy & tempo for calm",
    "anxious":    "Calmed the audio profile for you",
    "general":    "Pure emotion-based selection",
    "anger":      "Channelled intensity into powerful tracks",
    "romance":    "Softened tempo and lifted warmth for intimate listening",
}

# Emotion → (bg_color, bg_color_2, text_color, accent_color)
# bg_color_2 is the second gradient stop — slightly lighter/warmer variant
EMOTION_THEMES = {
    "calm":     ("#1a2a35", "#0f1e2a", "#e8f4f8", "#93C9E2"),
    "sad":      ("#0d1535", "#060d24", "#dde4ff", "#4154BD"),
    "happy":    ("#2a2000", "#1a1500", "#fff8dc", "#EAC559"),
    "angry":    ("#2a0a08", "#1a0505", "#fcfcfc", "#D7392A"),
    "anxious":  ("#1c1528", "#110d1c", "#ede8ff", "#917BBB"),
    "stressed": ("#0f2320", "#081714", "#e0f5f0", "#78B1A0"),
    "excited":  ("#2a0a1a", "#1a0510", "#ffe8f0", "#BA3B6E"),
    "neutral":  ("#161a0e", "#0e1108", "#f0f2e8", "#596B0A"),
    "romance":  ("#2a1020", "#1a0815", "#ffe0ec", "#E8749A"),
    "motivated": ("#1a2010", "#101508", "#edffd6", "#7BC67E"),
}

CLOSING_MESSAGES = {
    "sad":      "You showed up for yourself today. That takes courage. Come back anytime 🌙",
    "stressed": "You took a breath. That matters more than you think. Rest up 🌿",
    "anxious":  "One moment of stillness at a time. LYRA will always be here 🌼",
    "happy":    "Carry that lightness with you. See you next time ✨",
    "calm":     "Stay in that gentle rhythm. You deserve this peace 🌊",
    "excited":  "Keep that energy going! Come back whenever you need a boost ⚡",
    "angry":    "You let yourself feel it. That's healthy. Take care of you 🔥",
    "neutral":  "Sometimes steady is exactly enough. See you soon 🌤",
    "romance":  "Love looks beautiful on you. Come back whenever you need a soundtrack for it 🌹",
    "motivated": "That strength you showed today? It's always been in you. Keep going 💪",
}

SONGS_PATH = os.path.join("data", "processed", "songs_clean_final.csv")


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_mood_tooltip(valence: float, energy: float) -> str:
    if valence >= 0.6 and energy >= 0.6:
        return "Uplifting & energetic"
    elif valence >= 0.6 and energy < 0.6:
        return "Warm & gentle"
    elif valence < 0.4 and energy >= 0.6:
        return "Intense & raw"
    elif valence < 0.4 and energy < 0.4:
        return "Deep & introspective"
    elif valence >= 0.4 and energy < 0.4:
        return "Soft & soothing"
    else:
        return "Balanced & steady"


def img_to_base64(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    ext  = path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


# ── Arc/ring emotion chart ─────────────────────────────────────────────────────
def render_emotion_arc(selected_emotions: list, accent: str, bg: str):
    """
    Renders a Plotly donut chart showing the emotion blend.
    Falls back to progress bars if Plotly unavailable.
    """
    if not PLOTLY_OK or not selected_emotions:
        # Fallback — plain progress bars
        for emo, weight in selected_emotions:
            pct = round(weight * 100, 1)
            st.markdown(
                f"<div style='display:flex; justify-content:space-between; "
                f"margin-bottom:2px; font-size:0.9rem;'>"
                f"<span>{emo.title()}</span>"
                f"<span style='opacity:0.55'>{pct}%</span></div>",
                unsafe_allow_html=True,
            )
            st.progress(float(weight))
        return

    labels  = [e.title() for e, _ in selected_emotions]
    values  = [w for _, w in selected_emotions]

    # Build pastel color variants from accent
    # Use accent at different opacities for each segment
    colors = []
    alphas = [1.0, 0.55, 0.30]
    for i in range(len(labels)):
        # Convert hex accent to rgba segments
        r = int(accent[1:3], 16)
        g = int(accent[3:5], 16)
        b = int(accent[5:7], 16)
        a = alphas[i] if i < len(alphas) else 0.2
        colors.append(f"rgba({r},{g},{b},{a})")

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker=dict(
            colors=colors,
            line=dict(color=bg, width=2),
        ),
        textinfo="label+percent",
        textfont=dict(size=11, color="#ffffff"),
        hovertemplate="%{label}: %{percent}<extra></extra>",
        direction="clockwise",
        sort=False,
    ))

    # Center text — dominant emotion
    dominant = selected_emotions[0][0].title()
    fig.add_annotation(
        text=f"<b>{dominant}</b>",
        x=0.5, y=0.5,
        font=dict(size=14, color="#ffffff"),
        showarrow=False,
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=200,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Typing animation component ────────────────────────────────────────────────
def render_typing_animation(text: str, accent: str, speed_ms: int = 38):
    """
    Renders text with a typewriter effect using JS inside an iframe.
    """
    safe_text = text.replace("'", "\\'").replace("\n", " ")
    components.html(
        f"""
        <div id="typed" style="
            font-family: 'DM Sans', sans-serif;
            font-size: 0.9rem;
            font-style: italic;
            color: #ffffff;
            padding: 12px 16px;
            background: {accent}18;
            border-left: 3px solid {accent};
            border-radius: 0 10px 10px 0;
            min-height: 44px;
            line-height: 1.5;
        "></div>
        <script>
            const text  = '{safe_text}';
            const el    = document.getElementById('typed');
            let   i     = 0;
            function type() {{
                if (i < text.length) {{
                    el.innerHTML += text.charAt(i);
                    i++;
                    setTimeout(type, {speed_ms});
                }}
            }}
            type();
        </script>
        """,
        height=70,
    )


# ── Floating music note particles (landing screen only) ──────────────────────
def render_particles(accent: str):
    """
    Full screen floating music note particles.
    Uses st.components.v1.html() since Streamlit strips script tags from st.markdown.
    The iframe is made invisible and fixed-position via CSS injected separately,
    while the canvas inside fills the viewport.
    """
    # Inject CSS to make the iframe full screen and behind everything
    st.markdown(
        """
        <style>
        iframe[title="st.iframe"] {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 0 !important;
            pointer-events: none !important;
            border: none !important;
            background: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        f"""
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background: transparent;
            }}
            canvas {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                pointer-events: none;
            }}
        </style>
        <canvas id="c"></canvas>
        <script>
        (function() {{
            const canvas = document.getElementById('c');
            const ctx    = canvas.getContext('2d');

            function resize() {{
                canvas.width  = window.innerWidth;
                canvas.height = window.innerHeight;
            }}
            resize();
            window.addEventListener('resize', resize);

            const notes  = ['♩','♪','♫','♬','𝅘𝅥𝅮','𝅗𝅥','♭','♮','♯'];
            const accent = '{accent}';
            const count  = 40;
            const items  = [];

            for (let i = 0; i < count; i++) {{
                items.push({{
                    x:     Math.random() * window.innerWidth,
                    y:     Math.random() * window.innerHeight,
                    note:  notes[Math.floor(Math.random() * notes.length)],
                    size:  12 + Math.random() * 18,
                    speed: 0.3 + Math.random() * 0.6,
                    drift: (Math.random() - 0.5) * 0.4,
                    alpha: 0.07 + Math.random() * 0.15,
                }});
            }}

            function draw() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                items.forEach(p => {{
                    ctx.globalAlpha = p.alpha;
                    ctx.fillStyle   = accent;
                    ctx.font        = p.size + 'px serif';
                    ctx.fillText(p.note, p.x, p.y);
                    p.y -= p.speed;
                    p.x += p.drift;
                    if (p.y < -30) {{
                        p.y    = canvas.height + 20;
                        p.x    = Math.random() * canvas.width;
                        p.alpha = 0.07 + Math.random() * 0.15;
                    }}
                    if (p.x < -30 || p.x > canvas.width + 30) {{
                        p.x = Math.random() * canvas.width;
                    }}
                }});
                ctx.globalAlpha = 1;
                requestAnimationFrame(draw);
            }}
            draw();
        }})();
        </script>
        """,
        height=0,
    )


# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LYRA – Emotional Music",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("session_active",    False),
    ("result",            None),
    ("feedback_saved",    False),
    ("last_rating",       None),
    ("elapsed_ms",        None),
    ("current_track_idx", 0),
    ("playlist_expanded", False),
    ("emotion_history",   []),
    ("tracks_order",      []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Theme injection ───────────────────────────────────────────────────────────
def set_page_theme(emotion: str):
    theme = EMOTION_THEMES.get(emotion, EMOTION_THEMES["neutral"])
    bg, bg2, text, accent = theme

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* ── Animated gradient background ── */
    @keyframes gradientShift {{
        0%   {{ background-position: 0%   50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0%   50%; }}
    }}

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"], .main {{
        background: linear-gradient(135deg, {bg}, {bg2}, {bg}, {accent}18) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 12s ease infinite !important;
        color: {text} !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
        visibility: visible !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {bg} !important;
        border-right: 1px solid {accent}33;
    }}

    h1,h2,h3,h4,h5,h6,p,label,.stMarkdown {{ color: {text} !important; }}

    textarea, .stTextArea textarea {{
        background-color: {bg}cc !important;
        color: {text} !important;
        border: 1px solid {accent}66 !important;
        border-radius: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 15px !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }}
    textarea:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px {accent}33 !important;
    }}

    input, .stTextInput input {{
        background-color: {bg}cc !important;
        color: {text} !important;
        border: 1px solid {accent}66 !important;
        border-radius: 10px !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background-color: {accent} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 28px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        transition: all 0.25s ease !important;
    }}
    .stButton > button:hover {{
        opacity: 0.88 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px {accent}55 !important;
    }}
    .stButton > button:active {{
        transform: translateY(0px) !important;
    }}

    /* ── Song row buttons — hover glow ── */
    [data-testid="stHorizontalBlock"] .stButton > button {{
        background-color: transparent !important;
        color: {text} !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        text-align: left !important;
        font-weight: 400 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0 !important;
        transition: background-color 0.2s ease,
                    box-shadow 0.2s ease,
                    color 0.2s ease !important;
    }}
    [data-testid="stHorizontalBlock"] .stButton > button:hover {{
        background-color: {accent}22 !important;
        box-shadow: 0 0 12px {accent}33 !important;
        color: {accent} !important;
        transform: none !important;
    }}

    .stProgress > div > div {{
        background-color: {accent} !important;
        border-radius: 4px !important;
    }}
    .stProgress > div {{
        background-color: {accent}22 !important;
        border-radius: 4px !important;
    }}

    [data-testid="stMetric"] {{
        background-color: {accent}15 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        border: 1px solid {accent}30 !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {accent} !important;
        font-size: 1.4rem !important;
    }}

    hr {{ border-color: {accent}33 !important; }}

    .stAlert {{
        background-color: {accent}15 !important;
        border: 1px solid {accent}40 !important;
        border-radius: 12px !important;
        color: {text} !important;
    }}

    [data-testid="stExpander"] {{
        background-color: {accent}10 !important;
        border: 1px solid {accent}30 !important;
        border-radius: 12px !important;
    }}

    .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background-color: {accent} !important;
    }}

    #MainMenu, footer {{ visibility: hidden; }}

    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {bg}; }}
    ::-webkit-scrollbar-thumb {{ background: {accent}66; border-radius: 3px; }}

    /* ── Fade slide up animation ── */
    @keyframes fadeSlideUp {{
        from {{ opacity: 0; transform: translateY(18px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .lyra-fade {{ animation: fadeSlideUp 0.6s ease forwards; }}

    /* ── Waveform bars for active track ── */
    @keyframes wave {{
        0%, 100% {{ height: 5px; }}
        50%       {{ height: 14px; }}
    }}
    .lyra-bar {{
        display: inline-block;
        width: 3px;
        margin: 0 1px;
        background: {accent};
        border-radius: 2px;
        animation: wave 0.8s ease infinite;
        vertical-align: middle;
    }}
    .lyra-bar:nth-child(2) {{ animation-delay: 0.15s; }}
    .lyra-bar:nth-child(3) {{ animation-delay: 0.30s; }}

    /* ── Pulsing glow on cover art ── */
    @keyframes coverPulse {{
        0%, 100% {{ box-shadow: 0 8px 32px {accent}44,
                                0 0 0 0 {accent}00; }}
        50%       {{ box-shadow: 0 8px 40px {accent}66,
                                0 0 24px 6px {accent}33; }}
    }}
    .lyra-cover-pulse {{
        animation: coverPulse 3s ease-in-out infinite;
        border-radius: 16px;
    }}

    /* ── Playlist background container ── */
    .lyra-playlist-wrap {{
        position: relative;
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid {accent}22;
    }}
    .lyra-playlist-wrap::before {{
        content: '';
        position: absolute;
        inset: 0;
        background-size: cover;
        background-position: center;
        opacity: 0.18;
        z-index: 0;
    }}
    .lyra-playlist-inner {{
        position: relative;
        z-index: 1;
        background: {bg}cc;
        padding: 14px 10px;
        border-radius: 18px;
    }}
    </style>
    """, unsafe_allow_html=True)


def set_default_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    @keyframes gradientShift {
        0%   { background-position: 0%   50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0%   50%; }
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
        background: linear-gradient(135deg, #111318, #0a0c12, #111318, #1a1f2e) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 12s ease infinite !important;
        color: #e8eaf0 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
        visibility: visible !important;
    }
    h1,h2,h3,h4,h5,h6,p,label,.stMarkdown { color: #e8eaf0 !important; }
    textarea, .stTextArea textarea {
        background-color: #1e2128cc !important;
        color: #e8eaf0 !important;
        border: 1px solid #3a3f50 !important;
        border-radius: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
        transition: border-color 0.3s ease !important;
    }
    textarea:focus {
        border-color: #6c7ae0 !important;
        box-shadow: 0 0 0 3px #6c7ae033 !important;
    }
    .stButton > button {
        background-color: #6c7ae0 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px #6c7ae055 !important;
    }
    #MainMenu, footer { visibility: hidden; }
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .lyra-fade { animation: fadeSlideUp 0.6s ease forwards; }
    @keyframes coverPulse {
        0%, 100% { box-shadow: 0 8px 32px #6c7ae044, 0 0 0 0 #6c7ae000; }
        50%       { box-shadow: 0 8px 40px #6c7ae066, 0 0 24px 6px #6c7ae033; }
    }
    .lyra-cover-pulse { animation: coverPulse 3s ease-in-out infinite; border-radius: 16px; }
    </style>
    """, unsafe_allow_html=True)


# ── Apply theme ───────────────────────────────────────────────────────────────
if st.session_state.result:
    set_page_theme(st.session_state.result["dominant_emotion"])
else:
    set_default_theme()


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN A — Landing
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.session_active:

    # ── Particles OUTSIDE columns — true full screen ──────────────────────
    _landing_accent = "#56eec8"
    if st.session_state.get("result"):
        _landing_accent = EMOTION_THEMES.get(
            st.session_state.result.get("dominant_emotion", "neutral"),
            EMOTION_THEMES["neutral"]
        )[3]
        
    render_particles(accent=_landing_accent)

    # ── Centered content column ───────────────────────────────────────────
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        logo_path = "assets/lyra_logo.png"
        if os.path.exists(logo_path):
            st.image(Image.open(logo_path), use_container_width=True)

        st.markdown("""
        <div class='lyra-fade' style='text-align:center; padding:8px 0 4px 0;'>
            <span style='font-family:"DM Serif Display",serif;
                         font-size:2.8rem; letter-spacing:-1px;'>LYRA</span>
            <p style='font-size:1rem; opacity:0.6; margin-top:4px; font-weight:300;'>
                Share your mood, let the music follow
            </p>
        </div>
        """, unsafe_allow_html=True)

        user_text = st.text_area(
            label="",
            height=130,
            placeholder="...anything straight out of your mind. How are you feeling right now?",
            key="input_text",
        )

        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            generate_btn = st.button(
                "Generate My Playlist", use_container_width=True)

    if generate_btn:
        if not user_text.strip():
            st.warning("Share a little about how you're feeling first 🌿")
        else:
            # ── Crisis check FIRST — before any emotion detection ─────────────
            from src.safety.crisis_detector import check_crisis
            crisis = check_crisis(user_text)

            if crisis["is_crisis"]:
                st.markdown(
                    f"""
                    <div style='padding:24px 28px; background:#173d37;
                        border-left:4px solid #7ee0d0; border-radius:0 16px 16px 0;
                        margin:16px 0; line-height:1.8;'>
                        <div style='font-size:1.1rem; font-weight:600;
                            color:#fcfcfc; margin-bottom:12px;'>
                            🤍 LYRA hears you. You don't have to face this alone.
                        </div>
                        <div style='font-size:0.9rem; color:#e6fff9; margin-bottom:16px;'>
                            What you're feeling right now is real, and it matters.
                            Please reach out to someone who can help:
                        </div>
                        <div style='font-size:0.92rem; color:#fcfcfc; margin-bottom:8px;'>
                            📞 <b>Befrienders Malaysia</b> — 03-7627 2929 (24 hours, free)
                        </div>
                        <div style='font-size:0.92rem; color:#fcfcfc; margin-bottom:8px;'>
                            📞 <b>Talian Kasih</b> — 15999 (24 hours)
                        </div>
                        <div style='font-size:0.92rem; color:#fcfcfc; margin-bottom:16px;'>
                            📞 <b>MIASA</b> — 03-2780 6803
                        </div>
                        <div style='font-size:0.85rem; color:#e6fff9; font-style:italic;'>
                            LYRA will be here with music whenever you're ready. 🤍
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ── Optional gentle song — placed below hotlines, never the focus ────────
                st.markdown(
                    """
                    <div style='margin-top:8px; font-size:0.82rem; opacity:0.65;
                        font-style:italic;'>
                        If it helps to have something to listen to while you reach out —
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    """<div style="margin-top:8px; border-radius:14px; overflow:hidden;
                        max-width:480px;">
                        <iframe src="https://open.spotify.com/embed/track/5tz69p7tJuGPeMGwNTxYuV?utm_source=generator&theme=0"
                            width="100%" height="152" frameborder="0"
                            allow="autoplay; clipboard-write; encrypted-media;
                                   fullscreen; picture-in-picture"
                            loading="lazy"
                            style="border-radius:14px; display:block;">
                        </iframe></div>""",
                    unsafe_allow_html=True,
                )
                
                st.markdown(
                    "<div style='text-align:center; font-size:12px; opacity:0.75; padding-top:10px;'>"
                    "Music previews powered by Spotify. All rights belong to respective copyright holders."
                    "</div>",
                    unsafe_allow_html=True
                )
    
            elif crisis["is_distress"]:
                # Softer distress — still generate playlist but show support first
                st.markdown(
                    f"""
                    <div style='padding:16px 20px; background:#0d1535;
                        border-left:3px solid #4154BD; border-radius:0 12px 12px 0;
                        margin-bottom:12px;'>
                        <div style='font-size:0.92rem; color:#dde4ff;'>
                            💙 LYRA noticed you might be going through something heavy.
                            If you ever need to talk to someone, Befrienders Malaysia
                            is available 24/7 at <b>03-7627 2929</b>. You're not alone.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Still generate playlist for distress (not full crisis)
                with st.spinner("LYRA is reading your vibe..."):
                    result, elapsed = measure_response_time(
                        generate_playlist,
                        user_text=user_text,
                        songs_csv_path=SONGS_PATH,
                        top_n=40,
                        session_rating=st.session_state.get("last_rating"),
                    )
                st.session_state.result            = result
                st.session_state.elapsed_ms        = elapsed
                st.session_state.session_active    = True
                st.session_state.feedback_saved    = False
                st.session_state.playlist_expanded = False
                st.session_state.current_track_idx = 0
                st.session_state.tracks_order      = list(range(len(result["tracks"])))
                st.session_state.user_text         = user_text
                emo     = result["dominant_emotion"]
                history = st.session_state.emotion_history
                if not history or history[-1] != emo:
                    history.append(emo)
                st.session_state.emotion_history = history[-6:]
                st.rerun()
                

            else:
                # Normal flow
                with st.spinner("LYRA is reading your vibe..."):
                    result, elapsed = measure_response_time(
                        generate_playlist,
                        user_text=user_text,
                        songs_csv_path=SONGS_PATH,
                        top_n=40,
                        session_rating=st.session_state.get("last_rating"),
                    )
                st.session_state.result            = result
                st.session_state.elapsed_ms        = elapsed
                st.session_state.session_active    = True
                st.session_state.feedback_saved    = False
                st.session_state.playlist_expanded = False
                st.session_state.current_track_idx = 0
                st.session_state.tracks_order      = list(range(len(result["tracks"])))
                st.session_state.user_text         = user_text
                emo     = result["dominant_emotion"]
                history = st.session_state.emotion_history
                if not history or history[-1] != emo:
                    history.append(emo)
                st.session_state.emotion_history = history[-6:]
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN B + C — Results
# ─────────────────────────────────────────────────────────────────────────────
else:
    result   = st.session_state.result
    emotion  = result["dominant_emotion"]
    theme    = EMOTION_THEMES.get(emotion, EMOTION_THEMES["neutral"])
    bg, bg2, text, accent = theme

    all_tracks = result["tracks"]
    order      = st.session_state.tracks_order
    if len(order) != len(all_tracks):
        order = list(range(len(all_tracks)))
        st.session_state.tracks_order = order
    tracks = [all_tracks[i] for i in order]

    idx = st.session_state.current_track_idx
    if idx >= len(tracks):
        idx = 0
        st.session_state.current_track_idx = 0
    current_track = tracks[idx]

    cover_path = get_cover_path(emotion)
    cover_b64  = img_to_base64(cover_path)


    # ── LYRA logo header stamp ────────────────────────────────────────────────
    logo_path = "assets/lyra_logo.png"
    _logo_b64 = img_to_base64(logo_path)
    if _logo_b64:
        st.markdown(
            f"<div style='text-align:center; padding:0px 0 0px 0; margin-top:-120px;'>"
            f"<img src='{_logo_b64}' style='width:180px; opacity:0.92;'/>"
            f"</div>",
            unsafe_allow_html=True,
        )
              
    # ── TOP BAR ───────────────────────────────────────────────────────────────
    top_l, top_m, top_r = st.columns([1, 3, 1])

    with top_l:
        if st.button("← New Session"):
            st.session_state.session_active    = False
            st.session_state.result            = None
            st.session_state.feedback_saved    = False
            st.session_state.playlist_expanded = False
            st.session_state.current_track_idx = 0
            st.session_state.tracks_order      = []
            st.rerun()

    with top_m:
        history = st.session_state.emotion_history
        if history:
            pills = ""
            for h in history:
                h_accent = EMOTION_THEMES.get(h, EMOTION_THEMES["neutral"])[3]
                pills += (
                    f"<span style='display:inline-block; margin:2px 4px; "
                    f"padding:3px 12px; border-radius:20px; font-size:0.75rem; "
                    f"background:{h_accent}22; border:1px solid {h_accent}55; "
                    f"color:{h_accent};'>{h.title()}</span>"
                )
            st.markdown(
                f"<div style='text-align:center; margin-bottom:6px;'>{pills}</div>",
                unsafe_allow_html=True,
            )

    with top_r:
        st.markdown(
            f"<div style='text-align:right; opacity:0.5; font-size:0.8rem; "
            f"padding-top:10px;'>{len(tracks)} songs</div>",
            unsafe_allow_html=True,
        )

    st.write("")

    # ══════════════════════════════════════════════════════════════════════════
    # SCREEN B — HERO
    # ══════════════════════════════════════════════════════════════════════════
    if not st.session_state.playlist_expanded:

        left_col, right_col = st.columns([1, 1.6])

        with left_col:
            st.markdown(
                f"<div class='lyra-fade' style='font-size:0.72rem; "
                f"text-transform:uppercase; letter-spacing:2px; opacity:0.5; "
                f"margin-bottom:10px;'>YOUR EMOTIONAL BLEND</div>",
                unsafe_allow_html=True,
            )

            # Arc/ring chart instead of progress bars
            render_emotion_arc(result["selected_emotions"], accent, bg)

            st.write("")

            # Typing animation for support message
            support_msg = get_support_message(emotion)
            render_typing_animation(support_msg, accent)

            st.write("")

            icon    = CONTEXT_ICONS.get(result["context"], "🎵")
            adj_lbl = CONTEXT_ADJUSTMENT_LABELS.get(result["context"], "")
            st.markdown(
                f"<div style='display:inline-flex; align-items:center; gap:8px; "
                f"padding:6px 14px; background:{accent}20; border-radius:20px; "
                f"border:1px solid {accent}44; font-size:0.82rem;'>"
                f"{icon} <b>{result['context'].title()}</b>"
                f"<span style='opacity:0.55; font-size:0.76rem;'>"
                f"— {adj_lbl}</span></div>",
                unsafe_allow_html=True,
            )

            st.write("")
            with st.expander("💡 Why these songs?", expanded=False):
                st.markdown(
                    f"<div style='font-size:0.85rem; line-height:1.6; "
                    f"opacity:0.85;'>{result['explanation']}</div>",
                    unsafe_allow_html=True,
                )

        with right_col:
            st.markdown("<div class='lyra-fade'>", unsafe_allow_html=True)

            st.markdown(
                f"<h1 style='font-family:\"DM Serif Display\",serif; "
                f"font-size:2.2rem; line-height:1.2; margin-bottom:6px; "
                f"letter-spacing:-0.5px;'>{result['playlist_title']}</h1>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='opacity:0.5; font-size:0.85rem; margin-bottom:20px;'>"
                f"Dominant mood: {emotion.title()} &nbsp;·&nbsp; "
                f"{len(tracks)} tracks</p>",
                unsafe_allow_html=True,
            )

            # Cover art with pulsing glow
            if cover_b64:
                st.markdown(
                    f"<div style='text-align:center; margin-bottom:24px;'>"
                    f"<img src='{cover_b64}' "
                    f"class='lyra-cover-pulse' "
                    f"style='width:260px; height:260px; object-fit:cover; "
                    f"border-radius:16px;'/></div>",
                    unsafe_allow_html=True,
                )
            elif cover_path and os.path.exists(cover_path):
                _, ic, _ = st.columns([1, 2, 1])
                with ic:
                    st.image(cover_path, use_container_width=True)

            _, btn_c, _ = st.columns([1, 2, 1])
            with btn_c:
                if st.button("▼  Open Playlist", use_container_width=True,
                             key="open_playlist_btn"):
                    st.session_state.playlist_expanded = True
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SCREEN C — EXPANDED PLAYLIST
    # ══════════════════════════════════════════════════════════════════════════
    else:
        left_col, right_col = st.columns([1.1, 1.9])

        with left_col:
            st.markdown(
                f"<div style='font-size:0.72rem; text-transform:uppercase; "
                f"letter-spacing:2px; opacity:0.5; margin-bottom:8px;'>"
                f"YOUR EMOTIONAL BLEND</div>",
                unsafe_allow_html=True,
            )

            # Arc chart in expanded view too
            render_emotion_arc(result["selected_emotions"], accent, bg)

            # Typing animation for support message
            support_msg = get_support_message(emotion)
            render_typing_animation(support_msg, accent, speed_ms=28)

            st.divider()

            st.markdown(
                f"<div style='font-size:0.72rem; text-transform:uppercase; "
                f"letter-spacing:2px; opacity:0.5; margin-bottom:8px;'>"
                f"NOW PLAYING</div>",
                unsafe_allow_html=True,
            )

            # Cover with pulsing glow
            if cover_b64:
                st.markdown(
                    f"<img src='{cover_b64}' "
                    f"class='lyra-cover-pulse' "
                    f"style='width:100%; border-radius:12px;'/>",
                    unsafe_allow_html=True,
                )
            elif cover_path and os.path.exists(cover_path):
                st.image(cover_path, use_container_width=True)

            st.markdown(
                f"<div style='margin-top:10px;'>"
                f"<div style='font-size:1.05rem; font-weight:600; "
                f"white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>"
                f"{current_track.get('name','Unknown Track')}</div>"
                f"<div style='font-size:0.82rem; opacity:0.55; margin-top:2px;'>"
                f"{current_track.get('artist_main','Unknown Artist')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            st.write("")
            c_prev, c_open, c_next = st.columns([1, 1, 1])
            with c_prev:
                if st.button("⏮", use_container_width=True, key="prev_btn"):
                    st.session_state.current_track_idx = max(0, idx - 1)
                    st.rerun()
            with c_open:
                url = current_track.get("spotify_url")
                if url:
                    st.markdown(
                        f"<a href='{url}' target='_blank' style='display:block; "
                        f"text-align:center; background:{accent}; color:#fff; "
                        f"padding:8px; border-radius:30px; text-decoration:none; "
                        f"font-weight:600; font-size:0.85rem;'>▶ Open</a>",
                        unsafe_allow_html=True,
                    )
            with c_next:
                if st.button("⏭", use_container_width=True, key="next_btn"):
                    st.session_state.current_track_idx = min(
                        len(tracks)-1, idx+1)
                    st.rerun()

            embed_url = current_track.get("spotify_embed")
            if embed_url:
                st.markdown(
                    f"""<div style="margin-top:14px; border-radius:14px;
                        overflow:hidden; box-shadow:0 4px 24px {accent}44;">
                        <iframe src="{embed_url}?utm_source=generator&theme=0"
                            width="100%" height="152" frameborder="0"
                            allow="autoplay; clipboard-write; encrypted-media;
                                   fullscreen; picture-in-picture"
                            loading="lazy"
                            style="border-radius:14px; display:block;">
                        </iframe></div>""",
                    unsafe_allow_html=True,
                )
                
                st.markdown(
                    "<div style='text-align:center; font-size:12px; opacity:0.75; padding-top:10px;'>"
                    "Music previews powered by Spotify. All rights belong to respective copyright holders."
                    "</div>",
                    unsafe_allow_html=True
                )
    
            st.write("")
            if st.button("▲ Back to Hero", use_container_width=True,
                         key="back_hero_btn"):
                st.session_state.playlist_expanded = False
                st.rerun()

        # ── RIGHT: playlist with cover background ─────────────────────────────
        with right_col:

            ph_l, ph_r = st.columns([3, 1])
            with ph_l:
                st.markdown(
                    f"<div style='font-size:0.72rem; text-transform:uppercase; "
                    f"letter-spacing:2px; opacity:0.5; margin-bottom:4px;'>"
                    f"PLAYLIST</div>"
                    f"<div style='font-family:\"DM Serif Display\",serif; "
                    f"font-size:1.5rem; letter-spacing:-0.3px;'>"
                    f"{result['playlist_title']}</div>",
                    unsafe_allow_html=True,
                )
            with ph_r:
                st.write("")
                if st.button("🔀 Shuffle", use_container_width=True,
                             key="shuffle_btn"):
                    shuffled = list(range(len(all_tracks)))
                    random.shuffle(shuffled)
                    st.session_state.tracks_order      = shuffled
                    st.session_state.current_track_idx = 0
                    st.rerun()

            st.write("")
            

            # Cover as darkened background
            if cover_b64:
                st.markdown(
                    f"""
                    <style>
                    .lyra-playlist-wrap::before {{
                        background-image: url('{cover_b64}');
                    }}
                    </style>
                    <div class="lyra-playlist-wrap">
                    <div class="lyra-playlist-inner">
                    """,
                    unsafe_allow_html=True,
                )

            # Column headers
            h1, h2, h3, h4 = st.columns([2.5, 2.2, 0.7, 0.7])
            with h1:
                st.markdown(
                    "<div style='font-size:0.72rem; opacity:0.4; "
                    "padding-bottom:4px;'>#  TITLE</div>",
                    unsafe_allow_html=True)
            with h2:
                st.markdown(
                    "<div style='font-size:0.72rem; opacity:0.4;'>ARTIST</div>",
                    unsafe_allow_html=True)
            with h3:
                st.markdown(
                    "<div style='font-size:0.72rem; opacity:0.4;'>NRG</div>",
                    unsafe_allow_html=True)
            with h4:
                st.markdown(
                    "<div style='font-size:0.72rem; opacity:0.4;'>VAL</div>",
                    unsafe_allow_html=True)

            st.markdown(
                f"<hr style='margin:4px 0 8px 0; border-color:{accent}33;'>",
                unsafe_allow_html=True,
            )

            # Song rows
            for i, track in enumerate(tracks):
                is_playing = (i == idx)

                try:
                    energy_val  = float(track.get("energy",  0))
                    valence_val = float(track.get("valence", 0))
                except (TypeError, ValueError):
                    energy_val  = 0.0
                    valence_val = 0.0

                tooltip = get_mood_tooltip(valence_val, energy_val)

                r1, r2, r3, r4, r5 = st.columns([0.3, 2.2, 2, 0.7, 0.7])

                with r1:
                    if is_playing:
                        st.markdown(
                            f"<div style='padding:9px 0;'>"
                            f"<span class='lyra-bar'></span>"
                            f"<span class='lyra-bar'></span>"
                            f"<span class='lyra-bar'></span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<div style='padding:9px 0; font-size:0.78rem; "
                            f"opacity:0.4;'>{i+1}</div>",
                            unsafe_allow_html=True,
                        )

                with r2:
                    label = ("♪ " if is_playing else "") + \
                            track.get("name", "Unknown")[:32]
                    if st.button(label, key=f"track_{i}",
                                 use_container_width=True):
                        st.session_state.current_track_idx = i
                        st.rerun()

                with r3:
                    st.markdown(
                        f"<div title='{tooltip}' style='padding:9px 0; "
                        f"font-size:0.82rem; opacity:0.6; white-space:nowrap; "
                        f"overflow:hidden; text-overflow:ellipsis; cursor:help;'>"
                        f"{track.get('artist_main','')[:26]}</div>",
                        unsafe_allow_html=True,
                    )

                with r4:
                    bar_w = max(4, int(energy_val * 36))
                    st.markdown(
                        f"<div title='Energy: {energy_val:.2f} — {tooltip}' "
                        f"style='padding:11px 0; cursor:help;'>"
                        f"<div style='width:{bar_w}px; height:4px; "
                        f"background:{accent}; border-radius:2px; "
                        f"opacity:0.75;'></div></div>",
                        unsafe_allow_html=True,
                    )

                with r5:
                    bar_w2 = max(4, int(valence_val * 36))
                    st.markdown(
                        f"<div title='Valence: {valence_val:.2f} — {tooltip}' "
                        f"style='padding:11px 0; cursor:help;'>"
                        f"<div style='width:{bar_w2}px; height:4px; "
                        f"background:{accent}88; border-radius:2px; "
                        f"opacity:0.75;'></div></div>",
                        unsafe_allow_html=True,
                    )

                if i < len(tracks) - 1:
                    st.markdown(
                        f"<hr style='margin:0; border-color:{accent}11;'>",
                        unsafe_allow_html=True,
                    )

            if cover_b64:
                st.markdown("</div></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # BOTTOM — Feedback + Evaluation
    # ══════════════════════════════════════════════════════════════════════════
    st.write("")
    st.divider()

    bot_l, bot_r = st.columns([1, 1])

    with bot_l:
        st.markdown("### 🌿 Quick Feedback")

        if not st.session_state.feedback_saved:
            st.markdown(
                "<div style='font-size:0.85rem; opacity:0.6; margin-bottom:8px;'>"
                "How well did this playlist match your mood?</div>",
                unsafe_allow_html=True,
            )
            rating  = st.slider("", 1, 5, 3, key="rating_slider",
                                 label_visibility="collapsed")
            comment = st.text_input("Any thoughts? (optional)",
                                    key="comment_input")

            if st.button("Submit Feedback"):
                os.makedirs(os.path.join("outputs", "feedback"), exist_ok=True)
                fb_path = os.path.join("outputs", "feedback", "feedback.csv")
                new_row = pd.DataFrame([{
                    "text":             st.session_state.get("user_text", ""),
                    "detected_emotion": result["dominant_emotion"],
                    "context":          result["context"],
                    "rating":           rating,
                    "comment":          comment,
                    "emotion_blend":    str([e for e, _ in
                                            result["selected_emotions"]]),
                    "num_candidates":   result["num_candidates"],
                    "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }])
                if os.path.exists(fb_path):
                    old = pd.read_csv(fb_path)
                    pd.concat([old, new_row], ignore_index=True).to_csv(
                        fb_path, index=False)
                else:
                    new_row.to_csv(fb_path, index=False)

                st.session_state.feedback_saved = True
                st.session_state.last_rating    = rating
                st.rerun()

        else:
            closing = CLOSING_MESSAGES.get(
                emotion if emotion else "neutral",
                "Thank you for spending time with LYRA today 🎧"
            )
            st.markdown(
                f"<div style='padding:16px 20px; background:{accent}18; "
                f"border-left:4px solid {accent}; border-radius:0 14px 14px 0; "
                f"font-size:0.95rem; font-style:italic; line-height:1.6;'>"
                f"{closing}</div>",
                unsafe_allow_html=True,
            )

        st.write("")
        if st.button("End Session", key="end_session_btn"):
            st.session_state.session_active    = False
            st.session_state.result            = None
            st.session_state.feedback_saved    = False
            st.session_state.playlist_expanded = False
            st.session_state.current_track_idx = 0
            st.session_state.tracks_order      = []
            st.rerun()

    with bot_r:
        with st.expander("📊 LYRA Evaluation Metrics", expanded=False):
            if st.session_state.get("elapsed_ms") is not None:
                ev = get_full_evaluation(
                    result=result,
                    total_songs=result.get("total_songs", 1),
                    elapsed_ms=st.session_state.elapsed_ms,
                    top_n=40,
                )
                e1, e2, e3 = st.columns(3)
                with e1:
                    st.metric("⚡ Response",
                              f"{ev['response_time']['elapsed_ms']} ms",
                              ev['response_time']['verdict'])
                with e2:
                    cov = ev["candidate_coverage"]
                    st.metric("🎯 Coverage", f"{cov['coverage_pct']}%",
                              f"{cov['num_candidates']} songs")
                with e3:
                    div = ev["diversity"]
                    st.metric("🎨 Diversity",
                              f"{round(div['diversity_ratio']*100,1)}%",
                              f"{div['unique_artists']} artists")
                st.write("")
                cons = ev["emotion_consistency"]
                st.markdown(
                    f"**🎭 Emotion Consistency:** {cons['overall_score']}%"
                    f" — {cons['verdict']}"
                )
                for feat, data in cons["per_feature"].items():
                    st.markdown(
                        f"&nbsp;&nbsp;`{feat}` — mean **{data['mean_val']}**, "
                        f"**{data['in_range_pct']}% in range**",
                        unsafe_allow_html=True,
                    )
                sat = ev["user_satisfaction"]
                st.write("")
                if sat["avg_rating"] is not None:
                    st.markdown(
                        f"**⭐ Satisfaction:** {sat['avg_rating']}/5 "
                        f"({sat['pct_positive']}% positive) — {sat['verdict']}")
                else:
                    st.markdown(f"**⭐ Satisfaction:** {sat['verdict']}")
                    
                    
                