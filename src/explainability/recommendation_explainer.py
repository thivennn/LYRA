# src/explainability/recommendation_explainer.py

# Human-readable descriptions of what each context actually does to the music
CONTEXT_EFFECT_DESCRIPTIONS = {
    "study": (
        "For studying, LYRA reduced energy and danceability and slowed the tempo "
        "so the music stays in the background without breaking your focus."
    ),
    "workout": (
        "For your workout, LYRA boosted energy and tempo significantly — "
        "these tracks are built to keep you moving."
    ),
    "sleep": (
        "For winding down, LYRA pulled energy and tempo way down — "
        "slow, soft, and drift-worthy."
    ),
    "heartbreak": (
        "For heartbreak, LYRA softened the emotional profile — "
        "lower energy, gentler tempo, music that feels like it understands."
    ),
    "motivation": (
        "For motivation, LYRA pushed valence and energy up — "
        "uplifting, forward-moving tracks to get you back on your feet."
    ),
    "relaxation": (
        "For relaxation, LYRA eased energy and tempo down — "
        "calm, peaceful music to help you unwind."
    ),
    "general": None,  # No context description needed
}

# Descriptions of what each emotion contributes to the audio profile
EMOTION_AUDIO_DESCRIPTIONS = {
    "happy":    "higher valence and energy",
    "sad":      "lower valence and softer energy",
    "calm":     "moderate valence with low energy",
    "angry":    "high energy and intense tempo",
    "anxious":  "lower energy and gentler tempo",
    "stressed": "moderate valence with calming energy",
    "excited":  "high energy, high valence and fast tempo",
    "neutral":  "balanced audio characteristics",
}


def generate_explanation(
    selected_emotions: list[tuple[str, float]],
    context: str = "general",
) -> str:
    """
    Generates a human-readable explanation of why LYRA chose these songs.
    Covers: detected emotion blend + audio profile + context shift.
    """

    # ── Part 1: Emotion blend ─────────────────────────────────────────────────
    emotion_parts = []
    for emotion, weight in selected_emotions:
        pct  = round(weight * 100, 1)
        desc = EMOTION_AUDIO_DESCRIPTIONS.get(emotion, "mixed characteristics")
        emotion_parts.append(f"{emotion.title()} ({pct}% → {desc})")

    blend_line = "LYRA detected a blend of: " + ", ".join(emotion_parts) + "."

    # ── Part 2: Audio selection rationale ─────────────────────────────────────
    audio_line = (
        "Songs were selected by matching emotional audio characteristics — "
        "valence, energy, tempo and danceability — to your detected mood blend."
    )

    # ── Part 3: Context effect (only if context was applied) ──────────────────
    context_line = CONTEXT_EFFECT_DESCRIPTIONS.get(context)

    # ── Part 4: Closing ───────────────────────────────────────────────────────
    closing = (
        "Hope these tracks feel right. Drop a feedback when you're done — "
        "it helps LYRA learn 🎧"
    )

    parts = [blend_line, audio_line]
    if context_line:
        parts.append(context_line)
    parts.append(closing)

    return " ".join(parts)