# src/pipeline/generate_playlist.py

from __future__ import annotations
import random
import pandas as pd

from src.emotion_detection.hybrid_detector import predict_emotion
from src.context.context_detector import detect_context
from src.explainability.recommendation_explainer import generate_explanation
from src.recommendation.emotion_to_music import (
    blend_emotion_features,
    apply_context_modifier,
    filter_songs_by_blended_profile,
    rank_songs_by_blended_profile,
    relax_filter,
)
from src.pipeline.playlist_titles import get_playlist_title_prefix
from src.personalization.user_profile import apply_session_nudge


def detect_mentioned_artist(user_text: str, df) -> str | None:
    """
    Checks if the user mentioned a specific artist by name in their text.
    Uses whole-word matching so "selena gomez" matches "Selena Gomez" but
    short/fragmented artist names (e.g. single-letter words) can't falsely
    match against unrelated text.
    """
    import re
    text_lower = user_text.lower()
    text_words = set(re.findall(r"\b[\w']+\b", text_lower))

    unique_artists = df["artist_main"].dropna().unique()

    best_match = None
    best_match_word_count = 0

    for artist in unique_artists:
        artist_lower = artist.lower()
        artist_words = re.findall(r"\b[\w']+\b", artist_lower)

        # Skip if any word is too short to be meaningful (avoids "A R I Z O N A"
        # style false positives, and single-letter junk matches)
        if any(len(w) <= 1 for w in artist_words):
            continue

        # Skip single-word artist names that are very short/common
        if len(artist_words) == 1 and len(artist_words[0]) <= 3:
            continue

        # Require ALL artist words to exist as WHOLE WORDS in the text
        # (not substrings) — this is the real fix
        if all(word in text_words for word in artist_words):
            if len(artist_words) > best_match_word_count:
                best_match = artist
                best_match_word_count = len(artist_words)

    return best_match


THEME_COLORS = {
    "calm":     "#93C9E2",
    "sad":      "#4154BD",
    "happy":    "#EAC559",
    "angry":    "#D7392A",
    "anxious":  "#917BBB",
    "stressed": "#78B1A0",
    "excited":  "#BA3B6E",
    "neutral":  "#596B0A",
    "romance":  "#E8749A",
    "motivated": "#7BC67E",
}


# ── Artist inclusion rules ───────────────────────────────────────────────────
# Artist songs are ONLY included if they pass the same emotional audio
# feature filter as everything else. This is a ceiling, not a quota —
# LYRA never forces in a poor emotional match just to satisfy an artist
# mention. Emotion accuracy always comes first.
ARTIST_MAX_SONGS      = 8   # ceiling — never more than this even if more match
ARTIST_MIN_TO_INCLUDE = 3   # below this, skip artist inclusion entirely


def _select_emotions(scores: dict) -> list[tuple[str, float]]:
    """
    Adaptive multi-emotion selection from filtered probability dict.
    - Always pick top 1
    - Add 2nd if it is above 10% weight (meaningful, not noise)
    - Add 3rd if it is close enough to top-1 (within 0.15) and above 8%
    - Normalize weights to sum to 1.0
    """
    sorted_emotions = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    selected = [sorted_emotions[0]]

    if len(sorted_emotions) >= 2 and sorted_emotions[1][1] >= 0.10:
        selected.append(sorted_emotions[1])

    if len(sorted_emotions) >= 3:
        e1_score = sorted_emotions[0][1]
        e3_score = sorted_emotions[2][1]
        if (e1_score - e3_score) <= 0.30 and e3_score >= 0.08:
            selected.append(sorted_emotions[2])

    total    = sum(w for _, w in selected)
    selected = [(emo, w / total) for emo, w in selected]

    return selected


def _sample_pool(df, n, pool_mult=3):
    """Randomize within top pool for freshness, then take n."""
    if n <= 0 or len(df) == 0:
        return df.head(0)
    pool_size = min(len(df), max(n * pool_mult, n + 20))
    pool      = df.head(pool_size).copy()
    pool      = pool.sample(frac=1, random_state=None).reset_index(drop=True)
    return pool.head(n)


def generate_playlist(
    user_text: str,
    songs_csv_path: str,
    top_n: int = 40,
    min_candidates: int = 50,
    session_rating: int | None = None,   # from previous rating this session
) -> dict:
    """
    Full pipeline: text → emotion → context → blended + context-adjusted
    audio profile → filtered + ranked songs → playlist dict.

    If the user mentions a specific artist, up to ARTIST_MAX_SONGS of their
    tracks are included — but ONLY if those tracks pass the same emotional
    audio feature filter as everything else. Emotion accuracy is never
    compromised to fit an artist mention.

    Returns:
        dominant_emotion    : str
        emotion_scores      : dict[str, float]
        selected_emotions   : list[tuple[str, float]]
        context             : str
        context_adjusted    : bool
        theme_color         : str
        playlist_title      : str
        explanation         : str
        tracks              : list[dict]
        num_candidates      : int
        blended_rules       : dict
        adjusted_rules      : dict
        mentioned_artist     : str | None
        artist_songs_included: int
    """

    # ── 1. Emotion detection ──────────────────────────────────────────────────
    emotion, scores = predict_emotion(user_text)

    # ── 2. Context detection ──────────────────────────────────────────────────
    context, _context_scores = detect_context(user_text, dominant_emotion=emotion)

    # ── 3. Multi-emotion selection & weighting ────────────────────────────────
    selected = _select_emotions(scores)

    # ── 4. Blend emotion audio features ───────────────────────────────────────
    blended_rules = blend_emotion_features(selected)

    # ── 5. Apply context modifier ─────────────────────────────────────────────
    adjusted_rules   = apply_context_modifier(blended_rules, context)
    context_adjusted = (context != "general")

    # ── 5b. Apply session nudge (if user rated a previous playlist) ───────────
    if session_rating is not None:
        adjusted_rules = apply_session_nudge(adjusted_rules, session_rating)

    # ── 6. Load songs dataset ─────────────────────────────────────────────────
    songs = pd.read_csv(songs_csv_path)

    # ── 7. Filter using context-adjusted blended profile ─────────────────────
    candidates = filter_songs_by_blended_profile(songs, adjusted_rules)

    if len(candidates) < min_candidates:
        candidates = filter_songs_by_blended_profile(
            songs, adjusted_rules, buffer_factor=0.55
        )

    if len(candidates) < min_candidates:
        candidates = relax_filter(songs, emotion, relax_factor=0.25)

    # ── 7b. Artist mention detection — checked against EMOTIONALLY
    #         MATCHED candidates only, never the raw dataset ─────────────────
    mentioned_artist      = detect_mentioned_artist(user_text, songs)
    artist_picked         = pd.DataFrame()
    artist_songs_included = 0

    if mentioned_artist:
        artist_candidates = candidates[
            candidates["artist_main"] == mentioned_artist
        ].copy()

        if len(artist_candidates) >= ARTIST_MIN_TO_INCLUDE:
            artist_ranked = rank_songs_by_blended_profile(
                artist_candidates, adjusted_rules
            )
            artist_final_count = min(len(artist_ranked), ARTIST_MAX_SONGS)
            artist_picked       = artist_ranked.head(artist_final_count)
            artist_songs_included = len(artist_picked)
        # else: fewer than ARTIST_MIN_TO_INCLUDE good matches found —
        # skip artist inclusion entirely, fall through to normal pipeline

    # ── 8. Rank general pool (excluding artist's own songs to avoid dupes) ───
    if artist_songs_included > 0:
        general_candidates = candidates[
            candidates["artist_main"] != mentioned_artist
        ].copy()
    else:
        general_candidates = candidates

    ranked = rank_songs_by_blended_profile(general_candidates, adjusted_rules)

    # ── 9. Split remaining slots into recent + older buckets ─────────────────
    # Total playlist = artist_songs_included + recent + older = top_n
    remaining_slots = top_n - artist_songs_included

    RECENT_YEAR  = 2000
    RECENT_RATIO = 25 / 40   # keep same proportion as original 25/15 split

    RECENT_COUNT = round(remaining_slots * RECENT_RATIO)
    OLDER_COUNT  = remaining_slots - RECENT_COUNT

    cols = [c for c in ["name", "artist_main", "valence", "energy",
                         "tempo", "danceability", "id", "year"]
            if c in ranked.columns]

    if "year" in ranked.columns and remaining_slots > 0:
        recent_pool = ranked[ranked["year"] >= RECENT_YEAR].copy()
        older_pool  = ranked[ranked["year"] <  RECENT_YEAR].copy()

        recent_tracks = _sample_pool(recent_pool, RECENT_COUNT)
        older_tracks  = _sample_pool(older_pool,  OLDER_COUNT)

        if len(recent_tracks) < RECENT_COUNT:
            shortfall    = RECENT_COUNT - len(recent_tracks)
            older_tracks = _sample_pool(older_pool, OLDER_COUNT + shortfall)

        if len(older_tracks) < OLDER_COUNT:
            shortfall     = OLDER_COUNT - len(older_tracks)
            recent_tracks = _sample_pool(recent_pool, RECENT_COUNT + shortfall)

        top = pd.concat([recent_tracks, older_tracks], ignore_index=True)
        top = top.sample(frac=1, random_state=None).reset_index(drop=True)

    elif remaining_slots > 0:
        pool_size = min(len(ranked), max(remaining_slots * 3, 150))
        pool      = ranked.head(pool_size).copy()
        pool      = pool.sample(frac=1, random_state=None).reset_index(drop=True)
        top       = pool.head(remaining_slots)
    else:
        top = ranked.head(0)

    top = top[[c for c in cols if c in top.columns]].copy()

    # ── 9b. Merge in artist picks ──────────────────────────────────────────
    if artist_songs_included > 0:
        artist_cols = [c for c in cols if c in artist_picked.columns]
        top = pd.concat([top, artist_picked[artist_cols]], ignore_index=True)
        top = top.sample(frac=1, random_state=None).reset_index(drop=True)

    tracks = top.to_dict(orient="records")

    # ── 10. Add Spotify links ─────────────────────────────────────────────────
    for t in tracks:
        track_id = t.get("id")
        if isinstance(track_id, str) and track_id.strip():
            t["spotify_url"]   = f"https://open.spotify.com/track/{track_id}"
            t["spotify_embed"] = f"https://open.spotify.com/embed/track/{track_id}"
        else:
            t["spotify_url"]   = None
            t["spotify_embed"] = None

    # ── 11. Build explanation ─────────────────────────────────────────────────
    explanation = generate_explanation(selected, context)
    if artist_songs_included > 0:
        explanation += (
            f" Since you mentioned {mentioned_artist}, we included "
            f"{artist_songs_included} of their tracks that matched your "
            f"current mood."
        )

 # ── 12. Playlist title ────────────────────────────────────────────────────
    context_title = get_playlist_title_prefix(context, emotion)
    blend_names   = " + ".join(emo.title() for emo, _ in selected)
    playlist_title = f"{context_title} — {blend_names}"

    return {
        "dominant_emotion":      emotion,
        "emotion_scores":        scores,
        "selected_emotions":     selected,
        "context":               context,
        "context_adjusted":      context_adjusted,
        "theme_color":           THEME_COLORS.get(emotion, THEME_COLORS["neutral"]),
        "playlist_title":        playlist_title,
        "explanation":           explanation,
        "tracks":                tracks,
        "num_candidates":        int(len(candidates)),
        "blended_rules":         blended_rules,
        "adjusted_rules":        adjusted_rules,
        "total_songs":           len(songs),
        "mentioned_artist":      mentioned_artist,
        "artist_songs_included": artist_songs_included,
    }