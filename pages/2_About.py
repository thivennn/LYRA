# explains LYRA to a new user

import os
import base64
import streamlit as st

st.set_page_config(
    page_title="About LYRA",
    page_icon="💡",
    layout="wide",
)

ACCENT = "#6ce0c9"
BG     = "#111318"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {{
    background: linear-gradient(135deg, #111318, #0a0c12, #111318, #1a1f2e) !important;
    background-size: 400% 400% !important;
    color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important;
}}
[data-testid="stHeader"] {{ background: transparent !important; visibility: visible !important; }}
h1, h2, h3, p, label, .stMarkdown {{ color: #e8eaf0 !important; }}
#MainMenu, footer {{ visibility: hidden; }}

.lyra-card {{
    background: {ACCENT}12;
    border: 1px solid {ACCENT}33;
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 18px;
}}
.lyra-step-num {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: {ACCENT};
    color: #fff;
    font-weight: 600;
    font-size: 0.85rem;
    margin-right: 10px;
}}
.lyra-tag {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    background: {ACCENT}22;
    border: 1px solid {ACCENT}55;
    color: {ACCENT};
    margin: 2px 4px 2px 0;
}}
</style>
""", unsafe_allow_html=True)

def img_to_base64(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    ext  = path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"

# ── LYRA logo header stamp ────────────────────────────────────────────────
logo_path = "assets/lyra_logo.png"
_logo_b64 = img_to_base64(logo_path)
if _logo_b64:
    st.markdown(
        f"<div style='text-align:center; padding:0px 0 0px 0; margin-top:-120px;'>"
        f"<img src='{_logo_b64}' style='width:200px; opacity:0.92;'/>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center; padding: 20px 0 10px 0;'>
    <span style='font-family:"DM Serif Display",serif; font-size:2.6rem;
                 letter-spacing:-1px;'>What is LYRA?</span>
    <p style='font-size:1.05rem; opacity:0.65; margin-top:6px; font-weight:300;'>
        A quick look under the hood
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ── Intro ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='lyra-card'>
<p style='font-size:1rem; line-height:1.7; margin:0;'>
LYRA is a music recommendation system that actually reads how you're feeling —
not just what you've listened to before. Most music apps look at your history
and call it personalization. LYRA looks at what you <i>type</i>, figures out
the emotion underneath it, and builds a playlist that actually matches where
your head's at right now.
</p>
</div>
""", unsafe_allow_html=True)

# ── How it works — steps ────────────────────────────────────────────────────
st.markdown(f"""
<h2 style='font-family:"DM Serif Display",serif; font-size:1.6rem;
           margin-top:30px;'>How it actually works</h2>
""", unsafe_allow_html=True)

steps = [
    ("You type how you feel", 
     "No dropdowns, no mood emojis to pick from. Just type naturally — "
     "\"stress gila, exam tomorrow\" works just as well as \"I'm feeling anxious.\" "
     "LYRA's built to understand slang, idioms, and the way people actually talk, "
     "not just textbook emotion words."),
    
    ("LYRA reads the emotion underneath", 
     "Behind the scenes, a transformer-based language model (a DistilBERT variant "
     "trained on the GoEmotions dataset) analyzes your text alongside a custom "
     "rule-based layer built specifically for this project — covering idioms "
     "like \"heart is heavy,\" activities like \"going for a long drive,\" "
     "and Malaysian-English phrasing like \"penat gila.\" The two systems "
     "blend their results so LYRA catches both natural language nuance and "
     "informal expression."),
    
    ("Your emotion gets mapped to actual audio features", 
     "Every emotion LYRA detects — calm, stressed, romance, motivated, and more — "
     "is mapped to a specific range of musical qualities: valence (how positive "
     "a song sounds), energy, tempo, and danceability. These aren't guesses — "
     "they're based on validated Music Emotion Recognition research connecting "
     "audio characteristics to how songs actually feel."),
    
    ("LYRA builds your playlist", 
     "From a library of over 150,000 unique tracks, LYRA filters down to songs "
     "matching your emotional profile, then ranks them by how closely they fit. "
     "It also balances familiar songs with discovery — about 60% recent tracks, "
     "40% older ones — so you're not stuck hearing the same five years of music "
     "every time."),
    
    ("If you mention an artist, LYRA listens — carefully", 
     "Say \"play some Taylor Swift\" and LYRA will check her catalog — but only "
     "includes her songs if they actually match your detected mood. Emotional "
     "accuracy always wins over artist preference. If none of her songs fit, "
     "none get forced in."),
]

for i, (title, desc) in enumerate(steps, start=1):
    st.markdown(f"""
    <div class='lyra-card'>
        <div style='display:flex; align-items:flex-start;'>
            <span class='lyra-step-num'>{i}</span>
            <div>
                <div style='font-weight:600; font-size:1.05rem; margin-bottom:6px;'>
                    {title}
                </div>
                <div style='font-size:0.92rem; line-height:1.65; opacity:0.85;'>
                    {desc}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Safety note ──────────────────────────────────────────────────────────────
st.markdown(f"""
<h2 style='font-family:"DM Serif Display",serif; font-size:1.6rem;
           margin-top:30px;'>A quick word on safety 💙</h2>
<div class='lyra-card' style='border-left: 4px solid #D7392A;'>
<p style='font-size:0.95rem; line-height:1.7; margin:0;'>
LYRA isn't a therapist, and it's not trying to be one. But if something you
type signals that you might be going through something serious — like
thoughts of self-harm — LYRA won't just hand you a playlist and move on.
It'll pause, show you real support resources (like Befrienders Malaysia),
and gently let you know it's there when you're ready for music again.
Some things matter more than a good song.
</p>
</div>
""", unsafe_allow_html=True)

# ── Privacy note ─────────────────────────────────────────────────────────────
st.markdown(f"""
<h2 style='font-family:"DM Serif Display",serif; font-size:1.6rem;
           margin-top:30px;'>What LYRA remembers (and what it doesn't)</h2>
<div class='lyra-card'>
<p style='font-size:0.95rem; line-height:1.7; margin-bottom:10px;'>
LYRA doesn't create accounts, doesn't track you across visits, and doesn't
store what you typed anywhere permanent. Everything happens within your
current session — close the tab, and it's gone. The only thing saved is
optional, anonymous feedback (a rating and an optional comment) used purely
to evaluate and improve the system.
</p>
<p style='font-size:0.95rem; line-height:1.7; margin:0;'>
This was a deliberate design choice — emotional honesty works better when
people don't feel watched or logged.
</p>
</div>
""", unsafe_allow_html=True)

# ── Tech stack tags ──────────────────────────────────────────────────────────
st.markdown(f"""
<h2 style='font-family:"DM Serif Display",serif; font-size:1.6rem;
           margin-top:30px;'>Built with</h2>
""", unsafe_allow_html=True)

tags = [
    "Python", "Streamlit", "HuggingFace Transformers", "DistilBERT (GoEmotions)",
    "Pandas", "Plotly", "Spotify Web Embeds",
]
tags_html = "".join(f"<span class='lyra-tag'>{t}</span>" for t in tags)
st.markdown(f"<div style='margin-bottom:20px;'>{tags_html}</div>", unsafe_allow_html=True)

st.write("")
st.markdown(
    "<div style='text-align:center; opacity:0.45; font-size:0.82rem; "
    "padding:20px 0;'>LYRA — built as part of a Final Year Project, "
    "exploring emotion-aware music recommendation.</div>",
    unsafe_allow_html=True,
)