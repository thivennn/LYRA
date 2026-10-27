# src/analytics/feedback_analyzer.py
#
# Reads feedback.csv and computes anonymous system-level metrics.
# No individual user data — purely aggregated signals.
#
# Used by:
#   - Analytics dashboard (Phase E)
#   - Evaluation module (Phase D)

from __future__ import annotations
import os
import pandas as pd

FEEDBACK_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # src/analytics/
    "..", "..",                                   # up to FYP2 DRAFT/
    "outputs", "feedback", "feedback.csv"
)


def load_feedback() -> pd.DataFrame | None:
    """
    Load feedback CSV. Returns None if file doesn't exist or is empty.
    """
    if not os.path.exists(FEEDBACK_PATH):
        return None
    try:
        df = pd.read_csv(FEEDBACK_PATH)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def avg_rating_by_emotion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Average rating per detected emotion.
    Returns a DataFrame sorted by avg_rating descending.

    Example output:
        emotion   avg_rating   count
        calm      4.6          12
        sad       4.1          8
        anxious   3.2          5
    """
    return (
        df.groupby("detected_emotion")["rating"]
        .agg(avg_rating="mean", count="count")
        .reset_index()
        .sort_values("avg_rating", ascending=False)
        .round({"avg_rating": 2})
    )


def avg_rating_by_context(df: pd.DataFrame) -> pd.DataFrame:
    """
    Average rating per detected context.
    Returns a DataFrame sorted by avg_rating descending.
    """
    if "context" not in df.columns:
        return pd.DataFrame(columns=["context", "avg_rating", "count"])
    return (
        df.groupby("context")["rating"]
        .agg(avg_rating="mean", count="count")
        .reset_index()
        .sort_values("avg_rating", ascending=False)
        .round({"avg_rating": 2})
    )


def emotion_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    How often each emotion is detected across all sessions.
    Useful for: 'What emotion do users come to LYRA with most?'
    """
    return (
        df["detected_emotion"]
        .value_counts()
        .reset_index()
        .rename(columns={"detected_emotion": "emotion", "count": "sessions"})
    )


def context_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    How often each context is detected across all sessions.
    """
    if "context" not in df.columns:
        return pd.DataFrame(columns=["context", "sessions"])
    return (
        df["context"]
        .value_counts()
        .reset_index()
        .rename(columns={"context": "context", "count": "sessions"})
    )


def overall_stats(df: pd.DataFrame) -> dict:
    """
    Top-level KPIs for the analytics dashboard.

    Returns:
        total_sessions    : int
        overall_avg       : float
        best_emotion      : str   (highest avg rating)
        worst_emotion     : str   (lowest avg rating)
        best_context      : str   (highest avg rating)
        most_common_emotion : str
    """
    total       = len(df)
    overall_avg = round(df["rating"].mean(), 2)

    by_emo      = avg_rating_by_emotion(df)
    best_emo    = by_emo.iloc[0]["detected_emotion"]  if not by_emo.empty  else "N/A"
    worst_emo   = by_emo.iloc[-1]["detected_emotion"] if len(by_emo) > 1   else "N/A"

    by_ctx      = avg_rating_by_context(df)
    best_ctx    = by_ctx.iloc[0]["context"] if not by_ctx.empty else "N/A"

    most_common = df["detected_emotion"].mode()[0] if not df.empty else "N/A"

    return {
        "total_sessions":      total,
        "overall_avg_rating":  overall_avg,
        "best_emotion":        best_emo,
        "worst_emotion":       worst_emo,
        "best_context":        best_ctx,
        "most_common_emotion": most_common,
    }


def rating_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count of each star rating (1–5).
    Useful for a bar chart showing how satisfied users generally are.
    """
    dist = (
        df["rating"]
        .value_counts()
        .reindex([1, 2, 3, 4, 5], fill_value=0)
        .reset_index()
        .rename(columns={"rating": "stars", "count": "count"})
    )
    return dist


def get_full_report() -> dict | None:
    """
    Convenience function — loads feedback and returns all metrics in one call.
    Returns None if no feedback data exists yet.

    Used by the analytics dashboard and evaluation module.
    """
    df = load_feedback()
    if df is None:
        return None

    return {
        "overall":             overall_stats(df),
        "by_emotion":          avg_rating_by_emotion(df),
        "by_context":          avg_rating_by_context(df),
        "emotion_frequency":   emotion_frequency(df),
        "context_frequency":   context_frequency(df),
        "rating_distribution": rating_distribution(df),
        "raw":                 df,
    }