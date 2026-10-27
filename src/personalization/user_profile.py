# src/personalization/user_profile.py
#
# Session-scoped preference nudge — anonymous, nothing persisted to disk.
# LYRA gets smarter within your session, then forgets. Clean slate every time.
#
# How it works:
# - User rates a playlist (1-5)
# - If rating >= 4: tighten audio ranges (you liked this, stay close)
# - If rating <= 2: widen audio ranges (explore more variety)
# - Rating 3: no change
# - All of this lives in st.session_state, gone when session ends

NUDGE_STRENGTH = 0.10   # 10% shift on feature ranges — gentle but noticeable

FEATURE_CLAMPS = {
    "valence":      (0.0, 1.0),
    "energy":       (0.0, 1.0),
    "danceability": (0.0, 1.0),
    "tempo":        (40.0, 210.0),
}


def apply_session_nudge(adjusted_rules: dict, session_rating: int) -> dict:
    """
    Nudges audio feature ranges based on the rating given this session.

    Args:
        adjusted_rules : dict of { feature: (low, high) } — post-context rules
        session_rating : int 1–5 from the feedback slider

    Returns:
        nudged rules dict (same structure, slightly shifted ranges)
    """
    if session_rating == 3:
        return adjusted_rules   # Neutral — no change

    nudged = {}

    for feature, (low, high) in adjusted_rules.items():
        span   = high - low
        shift  = span * NUDGE_STRENGTH
        cl, ch = FEATURE_CLAMPS.get(feature, (0.0, 1.0))

        if session_rating >= 4:
            # Liked it — tighten toward centre (more of the same)
            new_low  = min(low  + shift, high)
            new_high = max(high - shift, low)
        else:
            # Didn't like it — widen to explore more variety
            new_low  = max(cl, low  - shift)
            new_high = min(ch, high + shift)

        nudged[feature] = (new_low, new_high)

    return nudged