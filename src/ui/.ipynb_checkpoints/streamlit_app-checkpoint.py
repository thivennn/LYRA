# src/ui/streamlit_app.py

import os
import pandas as pd
import streamlit as st

from src.pipeline.generate_playlist import generate_playlist

st.set_page_config(page_title="Lyra - Emotion Music Recommender", layout="wide")

st.title("LYRA 🎧")
st.caption("Share your mood, let LYRA's music follow...")

# Path to songs dataset (adjust if your file name differs)
SONGS_PATH = os.path.join("data", "processed", "songs_clean_recheck.csv")

user_text = st.text_area("How are you feeling right now?", height=120, placeholder="e.g., I'm overwhelmed and need something calm...")

col1, col2 = st.columns([1, 1])

if st.button("Generate Playlist"):
    if not user_text.strip():
        st.warning("Do share how you feel first.")
    else:
        result = generate_playlist(user_text=user_text, songs_csv_path=SONGS_PATH, top_n=15)

        # Apply theme color (simple visual proof)
        st.markdown(
            f"""
            <div style="padding:14px;border-radius:16px;background:{result['theme_color']};">
            <b>Detected emotion:</b> {result['dominant_emotion']} <br/>
            <b>Playlist:</b> {result['playlist_title']} <br/>
            <b>Candidate songs found:</b> {result['num_candidates']}
            </div>
            """,
            unsafe_allow_html=True
        )

        col1.subheader("Emotion scores (baseline)")
        col1.write(result["emotion_scores"])

        col2.subheader("Recommended songs")
        tracks_df = pd.DataFrame(result["tracks"])
        st.dataframe(tracks_df, use_container_width=True)

        st.divider()
        st.subheader("Quick feedback (for UAT)")
        rating = st.slider("How well did this playlist match your mood?", 1, 5, 3)
        comment = st.text_input("Any comment (optional)?")

        if st.button("Submit feedback"):
            os.makedirs(os.path.join("outputs", "feedback"), exist_ok=True)
            fb_path = os.path.join("outputs", "feedback", "feedback.csv")
            new_row = pd.DataFrame([{
                "text": user_text,
                "detected_emotion": result["dominant_emotion"],
                "rating": rating,
                "comment": comment
            }])
            if os.path.exists(fb_path):
                old = pd.read_csv(fb_path)
                pd.concat([old, new_row], ignore_index=True).to_csv(fb_path, index=False)
            else:
                new_row.to_csv(fb_path, index=False)

            st.success("Feedback saved")
