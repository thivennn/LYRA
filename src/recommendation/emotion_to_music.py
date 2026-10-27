# src/recommendation/emotion_to_music.py

EMOTION_FEATURE_RULES = {
    "calm":     {"valence": (0.40, 0.75), "energy": (0.15, 0.45), "tempo": (60, 105),  "danceability": (0.20, 0.60)},
    "sad":      {"valence": (0.05, 0.40), "energy": (0.05, 0.35), "tempo": (55, 95),   "danceability": (0.10, 0.45)},
    "happy":    {"valence": (0.65, 1.00), "energy": (0.45, 0.85), "tempo": (95, 160),  "danceability": (0.45, 0.90)},
    "angry":    {"valence": (0.05, 0.45), "energy": (0.65, 1.00), "tempo": (110, 180), "danceability": (0.35, 0.85)},
    "anxious":  {"valence": (0.25, 0.60), "energy": (0.10, 0.45), "tempo": (55, 100),  "danceability": (0.15, 0.55)},
    "stressed": {"valence": (0.30, 0.65), "energy": (0.15, 0.50), "tempo": (60, 110),  "danceability": (0.15, 0.55)},
    "excited":  {"valence": (0.60, 1.00), "energy": (0.70, 1.00), "tempo": (115, 190), "danceability": (0.55, 1.00)},
    "neutral":  {"valence": (0.35, 0.70), "energy": (0.30, 0.70), "tempo": (80, 140),  "danceability": (0.30, 0.75)},
    "romance":  {"valence": (0.55, 0.90), "energy": (0.20, 0.55), "tempo": (60, 110),  "danceability": (0.35, 0.70)},
    "motivated": {"valence": (0.55, 0.95), "energy": (0.60, 0.95), "tempo": (100, 180), "danceability": (0.45, 0.85)},
}

# ─────────────────────────────────────────────────────────────────────────────
# Context modifiers
# Each key maps to delta adjustments applied on top of the blended profile.
# Format: { feature: (low_shift, high_shift) }
# Positive = push range higher, Negative = push range lower.
# ─────────────────────────────────────────────────────────────────────────────
CONTEXT_MODIFIERS = {
    "study": {
        # Lower energy + danceability (focus music), moderate tempo
        "energy":       (-0.15, -0.15),
        "danceability": (-0.15, -0.15),
        "tempo":        (-15,   -15),
        "valence":      (0.00,  0.00),
    },
    "workout": {
        # Push energy and tempo up significantly
        "energy":       (+0.20, +0.20),
        "tempo":        (+20,   +20),
        "danceability": (+0.10, +0.10),
        "valence":      (+0.05, +0.05),
    },
    "sleep": {
        # Very low energy, very slow tempo, no danceability
        "energy":       (-0.25, -0.25),
        "tempo":        (-25,   -25),
        "danceability": (-0.20, -0.20),
        "valence":      (-0.05, -0.05),
    },
    "heartbreak": {
        # Softer emotional profile — lower energy, slightly lower valence
        "energy":       (-0.10, -0.10),
        "valence":      (-0.10, -0.10),
        "tempo":        (-10,   -10),
        "danceability": (-0.10, -0.10),
    },
    "motivated": {
        # High valence, high energy, strong tempo
        "energy":       (+0.15, +0.15),
        "valence":      (+0.10, +0.10),
        "tempo":        (+10,   +10),
        "danceability": (+0.05, +0.05),
    },
    "relaxation": {
        # Similar to calm — low energy, slow tempo, peaceful
        "energy":       (-0.10, -0.10),
        "tempo":        (-10,   -10),
        "danceability": (-0.10, -0.10),
        "valence":      (+0.05, +0.05),
    },
     "anxious": {
        "energy":       (-0.18, -0.18),
        "tempo":        (-18, -18),
        "danceability": (-0.15, -0.15),
        "valence":      (+0.05, +0.05),
    },
    "general": {
        # No modification — pure emotion-based
        "energy":       (0, 0),
        "tempo":        (0, 0),
        "danceability": (0, 0),
        "valence":      (0, 0),
    },
    "anger": {
        # Intense, aggressive, high-drive music
        "energy":       (+0.20, +0.20),
        "tempo":        (+15, +15),
        "danceability": (+0.05, +0.05),
        "valence":      (-0.15, -0.15),
    },
    "romance": {
        "energy":       (-0.05, -0.05),
        "tempo":        (-8,    -8),
        "danceability": (+0.05, +0.05),
        "valence":      (+0.05, +0.05),
    },
}

# Feature absolute clamp bounds (so we don't go out of [0,1] or crazy tempos)
FEATURE_CLAMPS = {
    "valence":      (0.0, 1.0),
    "energy":       (0.0, 1.0),
    "danceability": (0.0, 1.0),
    "tempo":        (40.0, 210.0),
}


def blend_emotion_features(selected_emotions: list[tuple[str, float]]) -> dict:
    """
    Creates a blended emotional audio profile from multiple weighted emotions.
    selected_emotions: [("sad", 0.5), ("stressed", 0.3), ("anxious", 0.2)]
    Returns: { feature: (low, high) }
    """
    blended = {}
    features = ["valence", "energy", "tempo", "danceability"]

    for feature in features:
        low_sum = 0.0
        high_sum = 0.0
        for emotion, weight in selected_emotions:
            rules = EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])
            low, high = rules[feature]
            low_sum += low * weight
            high_sum += high * weight
        blended[feature] = (low_sum, high_sum)

    return blended


def apply_context_modifier(blended_rules: dict, context: str) -> dict:
    """
    Applies context-based delta shifts on top of the blended emotion profile.
    This is where context ACTUALLY changes what songs get recommended.

    E.g. study context lowers energy + danceability.
         workout context pushes energy + tempo up.
         sleep context drops everything to very low.
    """
    modifiers = CONTEXT_MODIFIERS.get(context, CONTEXT_MODIFIERS["general"])
    adjusted = {}

    for feature, (low, high) in blended_rules.items():
        d_low, d_high = modifiers.get(feature, (0, 0))
        new_low  = low  + d_low
        new_high = high + d_high

        # Clamp to valid range
        clamp_low, clamp_high = FEATURE_CLAMPS.get(feature, (0.0, 1.0))
        new_low  = max(clamp_low,  min(clamp_high, new_low))
        new_high = max(clamp_low,  min(clamp_high, new_high))

        # Ensure low <= high after clamping
        if new_low > new_high:
            new_low, new_high = new_high, new_low

        adjusted[feature] = (new_low, new_high)

    return adjusted


def filter_songs_by_blended_profile(df, blended_rules: dict, buffer_factor: float = 0.35):
    """
    Filters songs using dynamically blended (and context-adjusted) feature ranges.
    Applies a small buffer so the filter isn't overly strict.
    """
    filtered = df.copy()

    for feature, (low, high) in blended_rules.items():
        if feature not in filtered.columns:
            continue
        span   = high - low
        buffer = span * buffer_factor
        filtered = filtered[
            (filtered[feature] >= (low  - buffer)) &
            (filtered[feature] <= (high + buffer))
        ]

    return filtered


def rank_songs_by_blended_profile(df, blended_rules: dict):
    """
    Ranks songs by emotional feature match + recency boost.
    Recent songs get a small score reduction (improvement) so they
    surface more often without overriding emotional accuracy.
    """
    ranked = df.copy()
    score  = 0

    # ── Emotional feature matching ────────────────────────────────────────────
    for feature, (low, high) in blended_rules.items():
        if feature not in ranked.columns:
            continue
        target = (low + high) / 2
        score += (ranked[feature] - target) ** 2

    ranked["match_score"] = score

    # ── Recency boost ─────────────────────────────────────────────────────────
    # Songs from RECENCY_PEAK_YEAR onwards get a bonus (score reduction).
    # The boost scales linearly — newer = stronger boost.
    # RECENCY_WEIGHT controls how much recency influences ranking.
    # 0.0 = no recency effect (pure emotion match)
    # 0.3 = moderate boost (recommended)
    # 1.0 = strong boost (recency dominates)
    RECENCY_PEAK_YEAR = 2010
    RECENCY_WEIGHT    = 0.25

    if "year" in ranked.columns:
        max_year   = ranked["year"].max()  # 2020 in your dataset
        year_range = max(max_year - RECENCY_PEAK_YEAR, 1)

        # Recency score: 0.0 for old songs, 1.0 for newest songs
        recency = ((ranked["year"] - RECENCY_PEAK_YEAR) / year_range).clip(0, 1)

        # Subtract from match_score — lower score = better rank
        # Multiply by match_score range to keep it proportional
        score_range = ranked["match_score"].max() - ranked["match_score"].min()
        score_range = max(score_range, 0.001)  # avoid divide by zero

        ranked["match_score"] = (
            ranked["match_score"] - (recency * score_range * RECENCY_WEIGHT)
        )

    return ranked.sort_values("match_score", ascending=True)


def filter_songs_by_emotion(df, emotion: str):
    """Single-emotion strict filter (used as fallback)."""
    rules    = EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])
    filtered = df.copy()

    for feature, (low, high) in rules.items():
        if feature in filtered.columns:
            filtered = filtered[(filtered[feature] >= low) & (filtered[feature] <= high)]

    return filtered


def rank_songs(df, emotion: str):
    """Single-emotion ranking with recency boost (fallback)."""
    rules  = EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])
    ranked = df.copy()
    score  = 0

    for feature, (low, high) in rules.items():
        if feature in ranked.columns:
            target        = (low + high) / 2
            feature_range = max(high - low, 0.01)
            score        += ((ranked[feature] - target) / feature_range) ** 2

    ranked["match_score"] = score

    # Recency boost — same logic as blended ranker
    RECENCY_PEAK_YEAR = 2010
    RECENCY_WEIGHT    = 0.15

    if "year" in ranked.columns:
        max_year   = ranked["year"].max()
        year_range = max(max_year - RECENCY_PEAK_YEAR, 1)
        recency = ((ranked["year"] - RECENCY_PEAK_YEAR) / year_range).clip(0, 1)

        # Cap recency influence — it can only nudge within a tolerance band,
        # never let a poor emotional match beat a strong one.
        # We sort by match_score first to find the "good enough" tolerance,
        # then only apply recency boost within that band.
        match_min = ranked["match_score"].min()
        tolerance_band = match_min + (
            (ranked["match_score"].max() - match_min) * 0.35
        )

        is_good_match = ranked["match_score"] <= tolerance_band

        score_range = ranked["match_score"].max() - ranked["match_score"].min()
        score_range = max(score_range, 0.001)

        # Only apply recency boost to songs that are already good matches
        recency_adjustment = recency * score_range * RECENCY_WEIGHT
        recency_adjustment = recency_adjustment.where(is_good_match, 0)

        ranked["match_score"] = ranked["match_score"] - recency_adjustment

    return ranked.sort_values("match_score", ascending=True)


def relax_filter(df, emotion: str, relax_factor: float = 0.15):
    """
    Fallback: if strict filtering yields too few songs, expand ranges slightly.
    """
    rules    = EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])
    filtered = df.copy()

    for feature, (low, high) in rules.items():
        if feature not in filtered.columns:
            continue
        span  = high - low
        low2  = low  - span * relax_factor
        high2 = high + span * relax_factor
        filtered = filtered[(filtered[feature] >= low2) & (filtered[feature] <= high2)]

    return filtered