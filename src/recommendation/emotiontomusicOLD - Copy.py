
EMOTION_FEATURE_RULES = {
    "calm": {
        "valence": (0.40, 0.75),
        "energy": (0.15, 0.45),
        "tempo": (60, 105),
        "danceability": (0.20, 0.60),
        "acousticness": (0.35, 1.00),
        "speechiness": (0.00, 0.12),
    },
    "stressed": {
        "valence": (0.30, 0.65),
        "energy": (0.15, 0.50),
        "tempo": (60, 110),
        "danceability": (0.15, 0.55),
        "acousticness": (0.30, 1.00),
        "instrumentalness": (0.10, 1.00),
    },
    "anxious": {
        "valence": (0.25, 0.60),
        "energy": (0.10, 0.45),
        "tempo": (55, 100),
        "danceability": (0.15, 0.55),
        "speechiness": (0.00, 0.10),
    },
    "sad": {
        "valence": (0.05, 0.40),
        "energy": (0.05, 0.35),
        "tempo": (55, 95),
        "danceability": (0.10, 0.45),
        "acousticness": (0.25, 1.00),
    },
    "angry": {
        "valence": (0.05, 0.45),
        "energy": (0.65, 1.00),
        "tempo": (110, 180),
        "danceability": (0.35, 0.85),
        # optional: loudness is negative numbers, so keep it if you want
        "loudness": (-8.0, 0.0),
    },
    "excited": {
        "valence": (0.60, 1.00),
        "energy": (0.70, 1.00),
        "tempo": (115, 190),
        "danceability": (0.55, 1.00),
    },
    "happy": {
        "valence": (0.65, 1.00),
        "energy": (0.45, 0.85),
        "tempo": (95, 160),
        "danceability": (0.45, 0.90),
    },
    "neutral": {
        "valence": (0.35, 0.70),
        "energy": (0.30, 0.70),
        "tempo": (80, 140),
        "danceability": (0.30, 0.75),
    },
}

#------
# Filtering Function:
#------

def get_rules(emotion: str) -> dict:
    return EMOTION_FEATURE_RULES.get(emotion, EMOTION_FEATURE_RULES["neutral"])


def filter_songs_by_emotion(df, emotion):
    rules = EMOTION_FEATURE_RULES[emotion]
    filtered = df.copy()

    for feature, (low, high) in rules.items():
        filtered = filtered[
            (filtered[feature] >= low) & (filtered[feature] <= high)
        ]

    return filtered

#------
# Ranking function:
#------

def rank_songs(df, emotion):
    rules = EMOTION_FEATURE_RULES[emotion]
    ranked = df.copy()

    score = 0
    for feature, (low, high) in rules.items():
        target = (low + high) / 2
        score += (ranked[feature] - target) ** 2

    ranked["match_score"] = score
    return ranked.sort_values("match_score")
