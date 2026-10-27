# src/context/context_detector.py
#
# Detects activity/situation context (study, workout, heartbreak, etc.)
# from user text, separately from emotion detection.
#
# IMPORTANT DESIGN NOTE:
# Context and emotion answer different questions -- context answers
# "what situation is the user in", emotion answers "how do they feel".
# They are meant to be complementary. The fix here specifically targets
# the case where an "emotion-flavoured" context (anger/anxious) wins off
# a weak signal that CONTRADICTS a clearly different dominant emotion
# (e.g. "Anger" context showing next to a Sad-dominant result, when the
# word "angry" was only one word among several emotions mentioned).
# It does NOT suppress context just because it's a single matched word --
# specific situational words like "exam" or "gym" are trusted on their
# own. It also does NOT suppress an emotion-flavoured context when it
# actually AGREES with the dominant emotion (e.g. "Anger" context next to
# an Angry-dominant result is correct and should show).

import re

# -----------------------------------------------------------------------------
# Keywords and phrases per context.
# Multi-word phrases score higher (weight 2) vs single words (weight 1).
# -----------------------------------------------------------------------------
CONTEXT_KEYWORDS = {

    "study": {
        "phrases": ["can't focus", "cant focus", "need to focus", "study session",
                    "final exam", "assignment due", "deadline tonight", "revision mode"],
        "words":   ["exam", "study", "studying", "assignment", "deadline", "university",
                    "focus", "finals", "test", "lecture", "revision", "thesis", "fyp",
                    "homework", "research", "paper", "submit"],
    },

    "sleep": {
        "phrases": ["can't sleep", "cant sleep", "trying to sleep", "going to bed",
                    "falling asleep", "wide awake", "late night"],
        "words":   ["sleep", "insomnia", "sleepy", "night", "rest", "tired",
                    "bed", "drowsy", "nap", "restless", "bedtime"],
    },

    "workout": {
        "phrases": ["hitting the gym", "working out", "training session",
                    "leg day", "push day", "morning run"],
        "words":   ["gym", "workout", "exercise", "training", "run", "running",
                    "football", "badminton", "basketball", "lifting", "cardio",
                    "fitness", "jog", "jogging", "sprint", "weights"],
    },

    "heartbreak": {
        "phrases": ["miss her", "miss him", "broke up", "broke my heart",
                    "she left", "he left", "can't move on", "cant move on",
                    "still think about", "lost her", "lost him"],
        "words":   ["breakup", "heartbroken", "lonely", "ex", "rejected",
                    "crying over", "alone", "left me", "moved on"],
    },

    "relaxation": {
        "phrases": ["wind down", "winding down", "clear my head",
                    "need a break", "taking it easy", "chill out"],
        "words":   ["meditate", "meditation", "peace", "peaceful", "relax",
                    "relaxing", "quiet", "spiritual", "breathe", "chill",
                    "unwind", "decompress", "slow down"],
    },

    "motivation": {
        "phrases": ["get back on track", "push through", "need a boost",
                    "feeling motivated", "make it happen", "grind time"],
        "words":   ["motivate", "motivated", "productive",
                    "power", "confidence", "success", "rebuild", "grind",
                    "hustle", "achieve", "goal", "ambitious", "conquer"],
    },

    "anxious": {
        "phrases": ["kinda freaking out", "feeling off", "not sitting right with me",
                    "mind won't chill", "spiraling a bit", "feeling tense about it",
                    "something feels wrong but I can't explain it",
                    "silence that feels too loud"],
        "words":   ["nervous", "worried", "uneasy", "apprehensive",
                    "tense", "stressed", "jittery", "on edge", "troubled",
                    "fearful", "mentally buzzing"],
    },

    "anger": {
        "phrases": ["seeing red", "about to snap", "boiling inside",
                    "trying not to lose it", "fed up with this",
                    "holding back a storm", "this really gets under my skin",
                    "one more thing and I'm done",
                    "carrying a grudge", "rage simmering beneath the surface"],
        "words":   ["angry", "mad", "furious", "irritated",
                    "annoyed", "frustrated", "enraged", "resentful",
                    "bitter", "outraged", "hostile", "agitated",
                    "fuming", "livid", "seething", "wrathful",
                    "heated", "indignant", "triggered", "vengeful"],
    },
}

# Contexts that are emotion-flavoured rather than situational. These are
# the only ones subject to the emotion-contradiction check below, since
# situational contexts like "study" or "workout" don't conflict with an
# emotion label the way "anger context + sad emotion" visually does.
EMOTION_FLAVORED_CONTEXTS = {"anxious", "anger"}


def detect_context(text: str, dominant_emotion: str | None = None) -> tuple[str, dict]:
    """
    Detects activity/situation context from user text.

    Args:
        text             : raw user input
        dominant_emotion : optional, the emotion already determined by
                            predict_emotion(). Used only as a targeted
                            sanity check: if an emotion-flavoured context
                            (anger/anxious) wins but DISAGREES with a
                            clearly different dominant emotion, AND the
                            winning score is weak (just one stray word
                            among other emotion words), we prefer
                            "general" to avoid a visibly contradictory
                            pairing. If the context AGREES with the
                            dominant emotion, it is always trusted.

    Returns:
        context (str)  : best matched context label, or "general"
        scores  (dict) : raw scores per context (useful for debugging/display)
    """
    normalized = text.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)

    scores = {ctx: 0 for ctx in CONTEXT_KEYWORDS}

    for context, keyword_sets in CONTEXT_KEYWORDS.items():
        for phrase in keyword_sets.get("phrases", []):
            if phrase in normalized:
                scores[context] += 2

        for word in keyword_sets.get("words", []):
            if re.search(rf"\b{re.escape(word)}\b", normalized):
                scores[context] += 1

    best       = max(scores, key=scores.get)
    best_score = scores[best]

    # Nothing matched at all -> general
    if best_score == 0:
        return "general", scores

    # Targeted contradiction check, ONLY for emotion-flavoured contexts,
    # ONLY when they disagree with a confidently different dominant
    # emotion, AND only when the match was a single weak word (score 1).
    # A context score of 2+ (a real phrase match, or two separate words)
    # is trusted even if it nominally disagrees, since that's a strong
    # enough signal to not be incidental.
    if (
        dominant_emotion is not None
        and best in EMOTION_FLAVORED_CONTEXTS
        and best != dominant_emotion
        and best_score == 1
    ):
        # Drop this context from contention and re-pick from the rest,
        # rather than blanket-falling to general -- there may be a
        # genuinely good second-place context (e.g. "study") that
        # deserves to win instead.
        remaining = {k: v for k, v in scores.items() if k != best}
        if remaining and max(remaining.values()) > 0:
            best       = max(remaining, key=remaining.get)
            best_score = remaining[best]
        else:
            return "general", scores

    return best, scores