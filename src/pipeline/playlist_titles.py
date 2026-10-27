# ─────────────────────────────────────────────────────────────────────────────
# PLAYLIST TITLES — combined context + emotion, randomized for variety
#
# BUG FIXED: previously, playlist_title was built purely from context
# (study, workout, sleep, etc). When no specific context was detected,
# it always fell back to "general", which then showed the same flat
# "Your Mood Mix" title regardless of which emotion was actually detected
# (e.g. "stressed" with no context still showed only general titles).
#
# FIX: context titles are now only used when a SPECIFIC context is
# detected (not "general"). When context is "general", the title is
# drawn from the EMOTION instead, so the dominant feeling is always
# reflected in the title rather than being hidden behind a generic label.
# Both dictionaries are now lists, randomly picked each time, to avoid
# the same exact title appearing every single session.
# ─────────────────────────────────────────────────────────────────────────────
import random

PLAYLIST_TITLES_BY_CONTEXT = {
    "study":      ["Deep Focus", "Quiet Mode", "Headspace", "Study Flow"],
    "workout":    ["Power Up", "Full Throttle", "Pump Mode", "Push Harder"],
    "sleep":      ["Drift Away", "Wind Down", "Night Mode", "Slow Fade"],
    "heartbreak": ["Feel It Out", "Sit With It", "Letting Go", "After the Fall"],
    "motivation": ["Rise Up", "Onward", "Next Chapter", "Built for This"],
    "relaxation": ["Unwind", "Soft Landing", "Easy Hours", "Still Air"],
    "anxious":    ["Breathe Easy", "Steady Now", "Settle In", "Quiet the Noise"],
    "anger":      ["Unfiltered Fury", "Burn It Off", "No Filter", "Loud and Clear"],
    "romance":    ["Love in the Air", "Slow Burn", "Close to You", "Heart First"],
    # NOTE: "general" deliberately excluded here — handled by emotion below
}

PLAYLIST_TITLES_BY_EMOTION = {
    "happy":     ["Light & Easy", "Good Day Energy", "Sunshine State", "Your Mood Mix"],
    "sad":       ["Sit With It", "Quiet Heart", "Soft Static", "Your Mood Mix"],
    "angry":     ["Out Loud", "No Holding Back", "Static & Sparks", "Your Mood Mix"],
    "anxious":   ["Steady Hands", "One Breath at a Time", "Quiet the Static", "Your Mood Mix"],
    "stressed":  ["Pressure Valve", "Slow the Spiral", "Catch Your Breath", "Your Mood Mix"],
    "excited":   ["Buzzing", "Wide Awake", "On the Edge of Something", "Your Mood Mix"],
    "calm":      ["Still Water", "Soft Focus", "Even Ground", "Your Mood Mix"],
    "romance":   ["Heart First", "Slow Burn", "Close Enough to Hear", "Your Mood Mix"],
    "motivated": ["No Days Off", "Built Different", "Keep Moving", "Rise & Conquer"],
    "neutral":   ["Just Today", "Plain Sailing", "Nothing Forced", "Your Mood Mix"],
}


def get_playlist_title_prefix(context: str, dominant_emotion: str) -> str:
    """
    Returns the title prefix (before the " — Emotion + Emotion" suffix).

    Priority:
    1. If a SPECIFIC context was detected (not "general"), use a random
       title from that context's list — situational context is the more
       specific signal when present.
    2. Otherwise (context is "general"), use a random title drawn from
       the dominant EMOTION's list instead, so the title still reflects
       how the user feels rather than defaulting to a flat generic label.
    3. If the emotion itself isn't recognised for some reason, fall back
       to "Your Mood Mix" as the final safety net.
    """
    if context != "general" and context in PLAYLIST_TITLES_BY_CONTEXT:
        return random.choice(PLAYLIST_TITLES_BY_CONTEXT[context])

    if dominant_emotion in PLAYLIST_TITLES_BY_EMOTION:
        return random.choice(PLAYLIST_TITLES_BY_EMOTION[dominant_emotion])

    return "Your Mood Mix"