# src/emotion_detection/hybrid_detector.py
#
# The brain of LYRA's emotion detection system.
# Combines transformer (Layer 1) + rule-based (Layer 2) + negation (Layer 3)
#
# Decision logic:
#   - Always run transformer first
#   - If transformer confidence >= threshold → trust transformer (primary)
#     and blend with baseline for richness
#   - If transformer confidence < threshold → trust baseline (primary)
#     transformer used as weak signal only
#   - Final scores: weighted merge of both systems
#
# This gives us:
#   Accurate detection for natural language (transformer)
#   Handles slang and informal text (baseline lexicon)
#   Handles negations ("not happy", "don't feel calm") (baseline)
#   Graceful fallback if model fails or is slow (baseline always runs)

from __future__ import annotations
import traceback

from src.emotion_detection.baseline_detector import predict_emotion as baseline_predict
from src.emotion_detection.transformer_detector import (
    predict_emotion_transformer,
    TRANSFORMER_CONFIDENCE_THRESHOLD,
    LYRA_EMOTIONS,
)

# How much to weight transformer vs baseline in the final blend
# When transformer is confident: 70% transformer, 30% baseline
# When transformer is uncertain: 30% transformer, 70% baseline
TRANSFORMER_WEIGHT_HIGH = 0.70
TRANSFORMER_WEIGHT_LOW  = 0.30

# Minimum score to appear in final output
FINAL_THRESHOLD = 0.06


def predict_emotion(text: str) -> tuple[str, dict[str, float]]:
    """
    Hybrid emotion detection — main entry point.
    Drop-in replacement for baseline_detector.predict_emotion().

    Returns:
        dominant_emotion : str   — one of LYRA's 8 emotions
        probabilities    : dict  — emotion → score, filtered + normalized
    """

    # ── Layer 1: Transformer ──────────────────────────────────────────────────
    transformer_ok         = False
    transformer_dominant   = "neutral"
    transformer_scores     = {}
    transformer_confidence = 0.0

    try:
        transformer_dominant, transformer_scores, transformer_confidence = \
            predict_emotion_transformer(text)
        transformer_ok = True
    except Exception:
        # If transformer fails for any reason (network, model load error, etc.)
        # silently fall back to baseline only — never crash the app
        transformer_ok = False

    # ── Layer 2: Baseline (rule-based + negation) ─────────────────────────────
    baseline_dominant, baseline_scores = baseline_predict(text)

    # ── Layer 3: Merge ────────────────────────────────────────────────────────
    if not transformer_ok:
        # Transformer failed — use baseline only
        return baseline_dominant, baseline_scores

    # Determine blend weights based on transformer confidence
    if transformer_confidence >= TRANSFORMER_CONFIDENCE_THRESHOLD:
        t_weight = TRANSFORMER_WEIGHT_HIGH
        b_weight = 1.0 - TRANSFORMER_WEIGHT_HIGH
    else:
        # Transformer is uncertain — baseline takes lead
        t_weight = TRANSFORMER_WEIGHT_LOW
        b_weight = 1.0 - TRANSFORMER_WEIGHT_LOW

    # Blend scores across all LYRA emotions
    merged = {}
    all_emotions = set(list(transformer_scores.keys()) +
                       list(baseline_scores.keys()) +
                       LYRA_EMOTIONS)

    for emo in all_emotions:
        t_score = transformer_scores.get(emo, 0.0)
        b_score = baseline_scores.get(emo, 0.0)
        merged[emo] = (t_weight * t_score) + (b_weight * b_score)

    # ── Filter noise ──────────────────────────────────────────────────────────
    filtered = {e: s for e, s in merged.items() if s >= FINAL_THRESHOLD}

    # ── Renormalize ───────────────────────────────────────────────────────────
    total = sum(filtered.values())
    if total > 0:
        filtered = {e: s / total for e, s in filtered.items()}
    else:
        filtered = {"neutral": 1.0}

    # ── Pick dominant ─────────────────────────────────────────────────────────
    # Tie-breaker: prefer emotionally meaningful over neutral
    tie_priority = [
        "sad", "anxious", "stressed", "angry",
        "calm", "happy", "excited", "neutral", "motivated", "romance"
    ]

    dominant = max(
        filtered,
        key=lambda e: (
            filtered[e],
            # Secondary sort: lower tie_priority index = higher priority
            -tie_priority.index(e) if e in tie_priority else -99
        )
    )

    return dominant, filtered