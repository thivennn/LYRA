# pages/1_Analytics.py
# ─────────────────────────────────────────────────────────────────────────────
# LYRA Analytics Dashboard
# Accessible via sidebar when running: python -m streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────────

import os
import base64
import sys
import ast
from datetime import datetime

# Path fix — resolve project root from this file's location
# pages/ sits at project root, so one level up is FYP2 DRAFT/
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px

from src.analytics.feedback_analyzer import get_full_report

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LYRA – Analytics",
    page_icon="📊",
    layout="wide",
)

# ── Minimal dark theme to match main app ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
    background-color: #111318 !important;
    color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"] { background-color: #111318 !important; }
h1,h2,h3,h4,h5,h6,p,label,.stMarkdown { color: #e8eaf0 !important; }
[data-testid="stMetric"] {
    background-color: #1e2128 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    border: 1px solid #3a3f50 !important;
}
[data-testid="stMetricValue"] { color: #93C9E2 !important; }
hr { border-color: #2a2f3a !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { visibility: visible !important; }
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
        f"<div style='text-align:center; padding:0px 0 0px 0; margin-top:-90px;'>"
        f"<img src='{_logo_b64}' style='width:180px; opacity:0.92;'/>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-family:"DM Serif Display",serif; font-size:2rem;
           letter-spacing:-0.5px; margin-bottom:4px;'>
    📊 LYRA Analytics
</h1>
<p style='opacity:0.5; font-size:0.85rem; margin-bottom:0;'>
    Anonymous system-level insights — no individual user data stored.
</p>
""", unsafe_allow_html=True)
st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
report = get_full_report()

if report is None:
    st.info(
        "📭 No feedback data yet. Once users start rating playlists on the "
        "main app, analytics will appear here automatically."
    )
    st.stop()

# ── Unpack ────────────────────────────────────────────────────────────────────
overall     = report["overall"]
by_emotion  = report["by_emotion"]
by_context  = report["by_context"]
emo_freq    = report["emotion_frequency"]
ctx_freq    = report["context_frequency"]
rating_dist = report["rating_distribution"]

# ─────────────────────────────────────────────────────────────────────────────
# ROW 1 — KPIs
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Overview")
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("🎧 Total Sessions", overall["total_sessions"])
with k2:
    st.metric("⭐ Avg Rating", f"{overall['overall_avg_rating']} / 5")
with k3:
    st.metric(
        "🏆 Best Emotion",
        overall["best_emotion"].title(),
        help="Highest average playlist rating",
    )
with k4:
    st.metric(
        "📉 Needs Work",
        overall["worst_emotion"].title(),
        help="Lowest average playlist rating",
    )
with k5:
    st.metric(
        "💬 Most Common Mood",
        overall["most_common_emotion"].title(),
        help="Emotion users arrive with most often",
    )

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ROW 2 — Emotion insights
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Emotion Insights")
col_l, col_r = st.columns(2)

with col_l:
    st.markdown("**How often each emotion is detected**")
    if not emo_freq.empty:
        fig = px.bar(
            emo_freq, x="emotion", y="sessions",
            color="emotion",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"emotion": "Emotion", "sessions": "Sessions"},
            text_auto=True,
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
            margin=dict(t=20, b=20),
            xaxis_title=None,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No emotion frequency data yet.")

with col_r:
    st.markdown("**Average playlist rating per emotion**")
    if not by_emotion.empty:
        fig2 = px.bar(
            by_emotion, x="detected_emotion", y="avg_rating",
            color="avg_rating",
            color_continuous_scale="RdYlGn",
            range_color=[1, 5],
            labels={"detected_emotion": "Emotion", "avg_rating": "Avg Rating"},
            text_auto=True,
        )
        fig2.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
            margin=dict(t=20, b=20),
            xaxis_title=None,
            yaxis=dict(range=[0, 5]),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No rating data per emotion yet.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ROW 3 — Context insights
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Context Insights")
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("**Context distribution**")
    if not ctx_freq.empty:
        fig3 = px.pie(
            ctx_freq, names="context", values="sessions",
            color_discrete_sequence=px.colors.qualitative.Pastel2,
            hole=0.4,
        )
        fig3.update_layout(
            margin=dict(t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
        )
        fig3.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No context data yet.")

with col_c2:
    st.markdown("**Average rating per context**")
    if not by_context.empty:
        fig4 = px.bar(
            by_context, x="context", y="avg_rating",
            color="avg_rating",
            color_continuous_scale="Blues",
            range_color=[1, 5],
            labels={"context": "Context", "avg_rating": "Avg Rating"},
            text_auto=True,
        )
        fig4.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
            margin=dict(t=20, b=20),
            xaxis_title=None,
            yaxis=dict(range=[0, 5]),
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No context rating data yet.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ROW 4 — Rating distribution
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Overall Rating Distribution")
col_rd1, col_rd2 = st.columns([1.5, 1])

with col_rd1:
    if not rating_dist.empty:
        fig5 = px.bar(
            rating_dist, x="stars", y="count",
            color="stars",
            color_continuous_scale="RdYlGn",
            range_color=[1, 5],
            labels={"stars": "Star Rating", "count": "Number of Ratings"},
            text_auto=True,
        )
        fig5.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
            margin=dict(t=20, b=20),
            xaxis=dict(tickmode="linear", dtick=1),
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No rating data yet.")

with col_rd2:
    st.markdown("**Rating breakdown**")
    if not rating_dist.empty:
        total = rating_dist["count"].sum()
        for _, row in rating_dist.sort_values("stars", ascending=False).iterrows():
            stars = int(row["stars"])
            count = int(row["count"])
            pct   = round((count / total) * 100, 1) if total > 0 else 0
            st.markdown(
                f"{'⭐' * stars} &nbsp; **{count}** ratings ({pct}%)",
                unsafe_allow_html=True,
            )
    else:
        st.info("No data yet.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ROW 5 — Emotion Blend Insight
# Does multi-emotion detection correlate with better satisfaction?
# ─────────────────────────────────────────────────────────────────────────────

st.divider()
st.subheader("Emotion Blend Insight")
st.caption(
    "LYRA can detect a single dominant emotion or a blend of 2-3 emotions "
    "together. This checks whether blended detections lead to better or "
    "worse playlist satisfaction."
)

raw = report["raw"]

if "emotion_blend" in raw.columns and "rating" in raw.columns:
    def _blend_size(val):
        try:
            parsed = ast.literal_eval(val) if isinstance(val, str) else val
            return len(parsed) if isinstance(parsed, list) else 1
        except (ValueError, SyntaxError):
            return 1

    blend_df = raw.copy()
    blend_df["blend_size"] = blend_df["emotion_blend"].apply(_blend_size)
    blend_df["blend_type"] = blend_df["blend_size"].apply(
        lambda n: "Single Emotion" if n == 1 else
                  "Two Emotions" if n == 2 else "Three Emotions"
    )

    blend_summary = (
        blend_df.groupby("blend_type")["rating"]
        .agg(avg_rating="mean", sessions="count")
        .reset_index()
    )
    blend_summary["avg_rating"] = blend_summary["avg_rating"].round(2)

    bl_col1, bl_col2 = st.columns([1.3, 1])

    with bl_col1:
        if not blend_summary.empty:
            fig_blend = px.bar(
                blend_summary, x="blend_type", y="avg_rating",
                color="avg_rating",
                color_continuous_scale="RdYlGn",
                range_color=[1, 5],
                text_auto=True,
                labels={"blend_type": "Detection Type", "avg_rating": "Avg Rating"},
            )
            fig_blend.update_layout(
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e8eaf0",
                margin=dict(t=20, b=20),
                xaxis_title=None,
                yaxis=dict(range=[0, 5]),
            )
            st.plotly_chart(fig_blend, use_container_width=True)
        else:
            st.info("Not enough data to compare blend types yet.")

    with bl_col2:
        st.markdown("**Sessions per blend type**")
        if not blend_summary.empty:
            for _, row in blend_summary.iterrows():
                st.markdown(
                    f"**{row['blend_type']}** — {int(row['sessions'])} sessions, "
                    f"{row['avg_rating']}/5 avg"
                )
        else:
            st.info("No data yet.")
else:
    st.info("Emotion blend data not available yet.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ROW 6 — Candidate Pool Size vs Rating
# Does a thin candidate pool correlate with lower satisfaction?
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Candidate Pool Size vs Satisfaction")
st.caption(
    "Each playlist is built from a pool of emotionally-matched candidate "
    "songs. This checks whether smaller candidate pools (fewer matching "
    "songs found) tend to produce lower-rated playlists — a useful signal "
    "for identifying where the system's matching logic may need tuning."
)

if "num_candidates" in raw.columns and "rating" in raw.columns:
    scatter_df = raw.dropna(subset=["num_candidates", "rating"]).copy()
    scatter_df["num_candidates"] = pd.to_numeric(
        scatter_df["num_candidates"], errors="coerce"
    )
    scatter_df = scatter_df.dropna(subset=["num_candidates"])

    if not scatter_df.empty:
        fig_scatter = px.scatter(
            scatter_df, x="num_candidates", y="rating",
            color="detected_emotion" if "detected_emotion" in scatter_df.columns else None,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"num_candidates": "Candidate Songs Found", "rating": "Rating Given"},
            trendline="ols" if len(scatter_df) >= 4 else None,
        )
        fig_scatter.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
            margin=dict(t=20, b=20),
            yaxis=dict(range=[0, 5.5], dtick=1),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Not enough numeric candidate data yet.")
else:
    st.info("Candidate pool data not available yet.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ROW 7 — Ratings Over Time
# Tracks whether iterative system improvements moved satisfaction over time.
# Note: only sessions logged AFTER timestamp tracking was added will appear.
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("Ratings Over Time")

if "timestamp" in raw.columns:
    time_df = raw.dropna(subset=["timestamp"]).copy()
    time_df["timestamp"] = pd.to_datetime(time_df["timestamp"], errors="coerce")
    time_df = time_df.dropna(subset=["timestamp"]).sort_values("timestamp")

    if len(time_df) >= 2:
        fig_time = px.line(
            time_df, x="timestamp", y="rating",
            markers=True,
            labels={"timestamp": "Time", "rating": "Rating Given"},
        )
        fig_time.update_traces(line_color="#93C9E2")
        fig_time.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eaf0",
            margin=dict(t=20, b=20),
            yaxis=dict(range=[0, 5.5], dtick=1),
        )
        st.plotly_chart(fig_time, use_container_width=True)
        st.caption(
            f"Showing {len(time_df)} timestamped sessions. Older feedback "
            "collected before timestamp tracking was added won't appear here."
        )
    else:
        st.info(
            "Not enough timestamped sessions yet to show a trend. "
            "This will fill in as more feedback is collected going forward."
        )
else:
    st.info(
        "Timestamp tracking was added recently — this chart will populate "
        "as new feedback comes in."
    )

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ROW 8 — Raw data
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🗃️ Raw Feedback Data", expanded=False):
    st.caption("Anonymised feedback log — no usernames or identifying info stored.")
    raw          = report["raw"]
    display_cols = [c for c in raw.columns if c != "Unnamed: 0"]
    st.dataframe(raw[display_cols], use_container_width=True)
    csv_data = raw[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_data,
        file_name="lyra_feedback_export.csv",
        mime="text/csv",
    )