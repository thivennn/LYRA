# src/emotion_detection/transformer_detector.py
#
# Layer 1 — Transformer-based emotion detection
# Model: bhadresh-savani/distilbert-base-uncased-go-emotion
# Trained on GoEmotions dataset (28 fine-grained emotion labels)
#
# First run: downloads ~1GB model to HuggingFace cache (~3-5 min)
# Every run after: loads from cache instantly
#
# Returns scores mapped to LYRA's 8 app-level emotions via emotion_mapping.py

from __future__ import annotations
import re
from collections import defaultdict

# Lazy import — only load when first called, not at module import time
_pipeline = None
MODEL_NAME = "bhadresh-savani/distilbert-base-uncased-go-emotion"

# GoEmotions 28-label → LYRA 8-label mapping
# Based on your existing emotion_mapping.py, extended for all 28 GoEmotions labels
GOEMOTIONS_TO_LYRA = {
    # happy
    "joy":          "happy",
    "love":         "happy",
    "gratitude":    "happy",
    "optimism":     "happy",
    "amusement":    "happy",
    "admiration":   "happy",
    "approval":     "happy",
    "pride":        "happy",
    "excitement":   "excited",   # maps to excited not happy

    # sad
    "sadness":      "sad",
    "grief":        "sad",
    "disappointment": "sad",
    "remorse":      "sad",
    "embarrassment": "sad",

    # angry
    "anger":        "angry",
    "annoyance":    "angry",
    "disapproval":  "angry",
    "disgust":      "angry",

    # anxious
    "fear":         "anxious",
    "nervousness":  "anxious",

    # stressed
    "confusion":    "stressed",
    "realization":  "stressed",

    # excited
    "surprise":     "excited",

    # calm
    "relief":       "calm",
    "caring":       "calm",

    # neutral
    "neutral":      "neutral",
    "curiosity":    "neutral",
    "desire":       "neutral",
    
    # romance
    "love":    "romance",
    "caring":  "romance",
    "desire":  "romance",
    
    # motivated
    "pride":        "motivated",
    "optimism":     "motivated",
    "admiration":   "motivated",
}

# LYRA's 10 app emotions
LYRA_EMOTIONS = ["happy", "sad", "angry", "anxious",
                 "stressed", "excited", "calm", "romance", "motivated", "neutral"]

# Minimum confidence threshold for transformer to be trusted
TRANSFORMER_CONFIDENCE_THRESHOLD = 0.15


def _load_pipeline():
    """
    Loads the HuggingFace pipeline once and caches it in module-level variable.
    Thread-safe for Streamlit's execution model.
    """
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline
        _pipeline = pipeline(
            "text-classification",
            model=MODEL_NAME,
            return_all_scores=True,
            # Use CPU — safe default for all machines
            # If user has GPU, transformers will use it automatically
        )
    return _pipeline


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def predict_emotion_transformer(
    text: str,
) -> tuple[str, dict[str, float], float]:
    """
    Runs the GoEmotions DistilBERT model on the input text.

    Returns:
        dominant_emotion : str  — LYRA-level emotion (one of 8)
        lyra_scores      : dict — aggregated scores per LYRA emotion
        confidence       : float — top GoEmotions score (model certainty)
    """
    clf = _load_pipeline()
    t   = _normalize(text)

    # Get all 28 GoEmotions scores
    raw_results = clf(t, truncation=True, max_length=512)[0]
    # raw_results: [{"label": "joy", "score": 0.92}, ...]

    # Aggregate into LYRA's 8 emotions
    lyra_scores: dict[str, float] = defaultdict(float)
    top_raw_score = 0.0

    for item in raw_results:
        label = item["label"]
        score = item["score"]

        # Track highest raw score for confidence
        if score > top_raw_score:
            top_raw_score = score

        # Map to LYRA emotion
        lyra_label = GOEMOTIONS_TO_LYRA.get(label, "neutral")
        lyra_scores[lyra_label] += score

    # Fill in any missing LYRA emotions with 0
    for emo in LYRA_EMOTIONS:
        if emo not in lyra_scores:
            lyra_scores[emo] = 0.0

    # Normalize so scores sum to 1.0
    total = sum(lyra_scores.values())
    if total > 0:
        lyra_scores = {e: s / total for e, s in lyra_scores.items()}

    # Remove near-zero scores (below 5% — noise)
    lyra_scores = {
        e: s for e, s in lyra_scores.items()
        if s >= 0.05
    }

    # Renormalize after filtering
    total2 = sum(lyra_scores.values())
    if total2 > 0:
        lyra_scores = {e: s / total2 for e, s in lyra_scores.items()}

    # Pick dominant
    if lyra_scores:
        dominant = max(lyra_scores, key=lyra_scores.get)
    else:
        dominant  = "neutral"
        lyra_scores = {"neutral": 1.0}

    return dominant, dict(lyra_scores), top_raw_score