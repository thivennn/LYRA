# src/recommendation/emotion_to_music.py

EMOTION_FEATURE_RULES = {
    "calm": {"valence": (0.40, 0.75), "energy": (0.15, 0.45), "tempo": (60, 105), "danceability": (0.20, 0.60)},
    "sad": {"valence": (0.05, 0.40), "energy": (0.05, 0.35), "tempo": (55, 95), "danceability": (0.10, 0.45)},
    "happy": {"valence": (0.65, 1.00), "energy": (0.45, 0.85), "tempo": (95, 160), "danceability": (0.45, 0.90)},
    "angry": {"valence": (0.05, 0.45), "energy": (0.65, 1.00), "tempo": (110, 180), "danceability": (0.35, 0.85)},
    "anxious": {"valence": (0.25, 0.60), "energy": (0.10, 0.45), "tempo": (55, 100), "danceability": (0.15, 0.55)},
    "stressed": {"valence": (0.30, 0.65), "energy": (0.15, 0.50), "tempo": (60, 110), "danceability": (0.15, 0.55)},
    "excited": {"valence": (0.60, 1.00), "energy": (0.70, 1.00), "tempo": (115, 190), "danceability": (0.55, 1.00)},
    "neutral": {"valence": (0.35, 0.70), "energy": (0.30, 0.70), "tempo": (80, 140), "danceability": (0.30, 0.75)},
}

def filter_songs_by_emotion(df, emotion: str):
    rules = EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])
    filtered = df.copy()

    for feature, (low, high) in rules.items():
        if feature in filtered.columns:
            filtered = filtered[(filtered[feature] >= low) & (filtered[feature] <= high)]

    return filtered

def rank_songs(df, emotion: str):
    rules = EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])
    ranked = df.copy()

    score = 0
    for feature, (low, high) in rules.items():
        if feature in ranked.columns:
            target = (low + high) / 2
            score += (ranked[feature] - target) ** 2

    ranked["match_score"] = score
    return ranked.sort_values("match_score", ascending=True)

def relax_filter(df, emotion: str, relax_factor: float = 0.15):
    """
    If strict filtering yields too few songs, expand ranges slightly.
    """
    rules = EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])
    filtered = df.copy()

    for feature, (low, high) in rules.items():
        if feature not in filtered.columns:
            continue
        span = (high - low)
        low2 = low - span * relax_factor
        high2 = high + span * relax_factor
        filtered = filtered[(filtered[feature] >= low2) & (filtered[feature] <= high2)]

    return filtered
