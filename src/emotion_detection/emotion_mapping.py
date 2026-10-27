
EMOTION_MAP = {
    # happy
    "joy":"happy","love":"happy","gratitude":"happy","optimism":"happy",
    "amusement":"happy","admiration":"happy","approval":"happy","pride":"happy",

    # sad
    "sadness":"sad","grief":"sad","disappointment":"sad",
    "remorse":"sad","embarrassment":"sad",

    # angry
    "anger":"angry","annoyance":"angry","disapproval":"angry","disgust":"angry",

    # anxious
    "fear":"anxious","nervousness":"anxious",

    # stressed
    "confusion":"stressed","realization":"stressed",
    "curiosity":"stressed","desire":"stressed",

    # excited
    "excitement":"excited","surprise":"excited",

    # calm
    "relief":"calm","caring":"calm",

    # neutral
    "neutral":"neutral"
}

def map_emotion(dominant_emotion: str) -> str:
    """
    Maps GoEmotions fine-grained emotion to application-level emotion.
    """
    return EMOTION_MAP.get(dominant_emotion, "neutral")
