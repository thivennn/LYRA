# src/evaluation/evaluator.py
#
# Phase D — Evaluation Module
# Measures LYRA's technical performance across 5 key metrics.
#
# Metrics:
#   1. Response Time      — how fast the playlist generates (ms)
#   2. Candidate Coverage — how many songs passed the filter
#   3. Playlist Diversity — unique artists ratio in the playlist
#   4. Emotion Consistency — how well songs match the target audio profile
#   5. User Satisfaction  — average rating from feedback.csv
#
# Used by:
#   - Analytics dashboard (Phase E)
#   - FYP2 evaluation chapter (report evidence)
#
# Does NOT modify any existing pipeline files.
# generate_playlist.py already returns num_candidates and adjusted_rules —
# we just use what's already there.

from __future__ import annotations
import time
import os
import pandas as pd
import numpy as np

FEEDBACK_PATH = os.path.join("outputs", "feedback", "feedback.csv")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Response Time
# ─────────────────────────────────────────────────────────────────────────────

def measure_response_time(generate_fn, *args, **kwargs) -> tuple[dict, float]:
    """
    Wraps any function call and measures how long it takes in milliseconds.

    Usage:
        result, elapsed_ms = measure_response_time(generate_playlist, user_text, songs_path)

    Returns:
        result     : whatever generate_fn returned
        elapsed_ms : float, time taken in milliseconds
    """
    start  = time.perf_counter()
    result = generate_fn(*args, **kwargs)
    end    = time.perf_counter()

    elapsed_ms = round((end - start) * 1000, 2)
    return result, elapsed_ms


# ─────────────────────────────────────────────────────────────────────────────
# 2. Candidate Coverage
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_candidate_coverage(
    num_candidates: int,
    total_songs: int,
    top_n: int = 40,
) -> dict:
    """
    Measures how much of the dataset survived the emotional filter.

    Args:
        num_candidates : songs that passed the filter (from result["num_candidates"])
        total_songs    : total songs in the dataset
        top_n          : target playlist size

    Returns dict with:
        num_candidates     : int
        total_songs        : int
        coverage_pct       : float  — % of dataset that matched the profile
        sufficient         : bool   — True if enough candidates for a full playlist
        verdict            : str    — human-readable assessment
    """
    coverage_pct = round((num_candidates / total_songs) * 100, 2) if total_songs > 0 else 0.0
    sufficient   = num_candidates >= top_n

    if coverage_pct >= 10:
        verdict = "Excellent — rich candidate pool"
    elif coverage_pct >= 3:
        verdict = "Good — adequate candidate pool"
    elif coverage_pct >= 1:
        verdict = "Moderate — filter is quite strict"
    else:
        verdict = "Low — consider relaxing audio feature ranges"

    return {
        "num_candidates": num_candidates,
        "total_songs":    total_songs,
        "coverage_pct":   coverage_pct,
        "sufficient":     sufficient,
        "verdict":        verdict,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. Playlist Diversity
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_playlist_diversity(tracks: list[dict]) -> dict:
    """
    Measures artist diversity in the generated playlist.
    A good playlist avoids recommending the same artist too many times.

    Args:
        tracks : list of track dicts from result["tracks"]

    Returns dict with:
        total_tracks      : int
        unique_artists    : int
        diversity_ratio   : float  — unique_artists / total_tracks (0–1)
        avg_songs_per_artist : float
        verdict           : str
    """
    if not tracks:
        return {
            "total_tracks": 0,
            "unique_artists": 0,
            "diversity_ratio": 0.0,
            "avg_songs_per_artist": 0.0,
            "verdict": "No tracks to evaluate",
        }

    artists = [t.get("artist_main", "Unknown") for t in tracks]
    total   = len(artists)
    unique  = len(set(artists))
    ratio   = round(unique / total, 3)
    avg     = round(total / unique, 2) if unique > 0 else 0.0

    if ratio >= 0.80:
        verdict = "Excellent diversity — mostly unique artists"
    elif ratio >= 0.60:
        verdict = "Good diversity — some artist repetition"
    elif ratio >= 0.40:
        verdict = "Moderate diversity — noticeable repetition"
    else:
        verdict = "Low diversity — few artists dominate the playlist"

    return {
        "total_tracks":         total,
        "unique_artists":       unique,
        "diversity_ratio":      ratio,
        "avg_songs_per_artist": avg,
        "verdict":              verdict,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. Emotion Consistency
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_emotion_consistency(
    tracks: list[dict],
    adjusted_rules: dict,
) -> dict:
    """
    Measures how well the recommended songs actually match the target audio profile.

    For each audio feature (valence, energy, tempo, danceability), checks what
    percentage of songs fall within the target range. A high score means the
    recommendation engine is correctly selecting emotionally aligned songs.

    Args:
        tracks         : list of track dicts (must have valence, energy, tempo, danceability)
        adjusted_rules : the post-context audio feature ranges from generate_playlist

    Returns dict with:
        per_feature     : dict — { feature: { in_range_pct, mean_val, target_midpoint } }
        overall_score   : float — average in-range % across all features (0–100)
        verdict         : str
    """
    if not tracks or not adjusted_rules:
        return {
            "per_feature":   {},
            "overall_score": 0.0,
            "verdict":       "No data to evaluate",
        }

    df = pd.DataFrame(tracks)

    features    = ["valence", "energy", "tempo", "danceability"]
    per_feature = {}
    scores      = []

    for feature in features:
        if feature not in df.columns or feature not in adjusted_rules:
            continue

        low, high  = adjusted_rules[feature]
        target_mid = round((low + high) / 2, 3)

        # Buffer: same as filter_songs_by_blended_profile (35% of span)
        span    = high - low
        buf     = span * 0.35
        f_low   = low  - buf
        f_high  = high + buf

        col         = pd.to_numeric(df[feature], errors="coerce").dropna()
        in_range    = col[(col >= f_low) & (col <= f_high)]
        in_range_pct = round(len(in_range) / len(col) * 100, 1) if len(col) > 0 else 0.0
        mean_val    = round(col.mean(), 3)

        per_feature[feature] = {
            "target_range":   (round(low, 3), round(high, 3)),
            "target_midpoint": target_mid,
            "mean_val":       mean_val,
            "in_range_pct":   in_range_pct,
        }
        scores.append(in_range_pct)

    overall_score = round(np.mean(scores), 1) if scores else 0.0

    if overall_score >= 80:
        verdict = "Excellent — songs closely match the emotional profile"
    elif overall_score >= 60:
        verdict = "Good — most songs align with the target mood"
    elif overall_score >= 40:
        verdict = "Moderate — partial emotional alignment"
    else:
        verdict = "Low — songs may feel emotionally mismatched"

    return {
        "per_feature":   per_feature,
        "overall_score": overall_score,
        "verdict":       verdict,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. User Satisfaction (from feedback.csv)
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_user_satisfaction() -> dict:
    """
    Reads feedback.csv and computes satisfaction metrics.

    Returns dict with:
        total_ratings     : int
        avg_rating        : float
        rating_dist       : dict  { 1: n, 2: n, 3: n, 4: n, 5: n }
        pct_positive      : float — % of ratings 4 or 5
        verdict           : str
    """
    if not os.path.exists(FEEDBACK_PATH):
        return {
            "total_ratings": 0,
            "avg_rating":    None,
            "rating_dist":   {},
            "pct_positive":  None,
            "verdict":       "No feedback data collected yet",
        }

    try:
        df = pd.read_csv(FEEDBACK_PATH)
        if df.empty or "rating" not in df.columns:
            return {
                "total_ratings": 0,
                "avg_rating":    None,
                "rating_dist":   {},
                "pct_positive":  None,
                "verdict":       "Feedback file exists but has no rating data",
            }
    except Exception as e:
        return {
            "total_ratings": 0,
            "avg_rating":    None,
            "rating_dist":   {},
            "pct_positive":  None,
            "verdict":       f"Could not read feedback file: {e}",
        }

    ratings      = df["rating"].dropna()
    total        = len(ratings)
    avg          = round(ratings.mean(), 2)
    dist         = ratings.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0).to_dict()
    pct_positive = round(((dist.get(4, 0) + dist.get(5, 0)) / total) * 100, 1) if total > 0 else 0.0

    if avg >= 4.0:
        verdict = "Excellent user satisfaction"
    elif avg >= 3.0:
        verdict = "Good — users generally happy"
    elif avg >= 2.0:
        verdict = "Moderate — room for improvement"
    else:
        verdict = "Low — recommendations need significant improvement"

    return {
        "total_ratings": total,
        "avg_rating":    avg,
        "rating_dist":   dist,
        "pct_positive":  pct_positive,
        "verdict":       verdict,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Full evaluation report (all 5 metrics in one call)
# ─────────────────────────────────────────────────────────────────────────────

def get_full_evaluation(
    result: dict,
    total_songs: int,
    elapsed_ms: float,
    top_n: int = 40,
) -> dict:
    """
    Convenience function — runs all 4 post-generation metrics + satisfaction.

    Args:
        result      : dict returned by generate_playlist()
        total_songs : total rows in songs_clean_final.csv
        elapsed_ms  : from measure_response_time()
        top_n       : target playlist size

    Returns full evaluation dict with keys:
        response_time, candidate_coverage, diversity,
        emotion_consistency, user_satisfaction
    """
    return {
        "response_time": {
            "elapsed_ms": elapsed_ms,
            "verdict": (
                "Fast" if elapsed_ms < 1000 else
                "Acceptable" if elapsed_ms < 3000 else
                "Slow — consider optimising dataset loading"
            ),
        },
        "candidate_coverage": evaluate_candidate_coverage(
            num_candidates=result["num_candidates"],
            total_songs=total_songs,
            top_n=top_n,
        ),
        "diversity": evaluate_playlist_diversity(
            tracks=result["tracks"],
        ),
        "emotion_consistency": evaluate_emotion_consistency(
            tracks=result["tracks"],
            adjusted_rules=result["adjusted_rules"],
        ),
        "user_satisfaction": evaluate_user_satisfaction(),
    }