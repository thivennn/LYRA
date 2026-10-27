# src/safety/crisis_detector.py
#
# LYRA Crisis Safety Module
# Detects self-harm, suicidal ideation, and severe distress signals
# in user text before any emotion detection or playlist generation runs.
#
# When triggered:
#   - No playlist is generated
#   - A compassionate message + crisis hotlines are shown instead
#   - The interaction is logged anonymously for system awareness
#
# This is a moral responsibility, not just a feature.
# Users in genuine distress deserve care, not a playlist.

from __future__ import annotations
import re

# ─────────────────────────────────────────────────────────────────────────────
# Crisis signal keywords and phrases
# Deliberately broad — better to trigger unnecessarily than to miss a real case
# ─────────────────────────────────────────────────────────────────────────────
CRISIS_PHRASES = [
    # Direct suicidal ideation
    "plan to suicide", "going to suicide", "want to suicide",
    "planning to kill myself", "going to kill myself", "want to kill myself",
    "thinking of killing myself", "thinking about killing myself",
    "i will kill myself", "ill kill myself", "i will end my life",
    "going to end my life", "want to end my life", "planning to end my life",
    "end it all", "end it tonight", "ending it all", "ending my life",
    "taking my life", "take my life", "take my own life",
    "no reason to live", "no reason to be alive", "don't want to be alive",
    "dont want to be alive", "don't want to exist", "dont want to exist",
    "wish i was dead", "wish i were dead", "want to be dead",
    "better off dead", "better off without me", "world better without me",
    "everyone better without me", "nobody would miss me", "suicide", "wan to kill my self", "rasa macam nak mati la",
    "nak bunuh", 

    # Self harm
    "want to hurt myself", "going to hurt myself", "thinking of hurting myself",
    "cut myself", "cutting myself", "harm myself", "harming myself",
    "self harm", "self-harm",

    # Severe hopelessness combined with finality
    "last time", "last night alive", "last day alive", "goodbye forever",
    "final goodbye", "this is goodbye", "won't be here tomorrow",
    "wont be here tomorrow", "not going to be here anymore",

    # Informal / slang expressions
    "kms", "kms fr", "i wanna kms", "gonna kms",
    "unalive myself", "want to unalive", "going to unalive",
    "i want to die", "i wanna die", "wanna die",
    "just let me die", "let me die", "i should die",
    "i deserve to die", "i need to die",
]

# Softer distress signals — these don't trigger full crisis mode
# but flag that the user needs extra care in the response
DISTRESS_PHRASES = [
    "i give up", "given up on everything", "given up on life",
    "can't go on", "cant go on", "can't do this anymore",
    "too tired to continue", "exhausted from living",
    "what's the point", "whats the point", "nothing matters",
    "nobody cares about me", "no one cares if i disappear",
    "feel like disappearing", "want to disappear",
    "don't want to wake up", "dont want to wake up",
    "wish i could sleep forever",
]


def check_crisis(text: str) -> dict:
    """
    Checks user text for crisis signals before any processing.

    Returns:
        {
            "is_crisis"  : bool  — True if immediate crisis support needed
            "is_distress": bool  — True if softer distress detected
            "matched"    : str   — which phrase triggered (for logging)
        }
    """
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)

    # Check crisis phrases first
    for phrase in CRISIS_PHRASES:
        if phrase in t:
            return {
                "is_crisis":   True,
                "is_distress": False,
                "matched":     phrase,
            }

    # Check softer distress
    for phrase in DISTRESS_PHRASES:
        if phrase in t:
            return {
                "is_crisis":   False,
                "is_distress": True,
                "matched":     phrase,
            }

    return {
        "is_crisis":   False,
        "is_distress": False,
        "matched":     None,
    }