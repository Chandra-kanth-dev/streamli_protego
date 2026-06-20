"""
risk_scoring.py
================
Advanced risk decision engine for PROTEGO.

Enhanced:
- Capped linguistic inflation
- Clearer keyword severity weighting
- More sensitive context escalation
- Explicit emergency explanations
- Fully backward compatible
"""

from typing import Dict, List, Optional

from protego.nlp.features import extract_features
from protego.nlp.keywords import (
    EMERGENCY_KEYWORDS,
    PHYSICAL_ABUSE_KEYWORDS,
    FEAR_KEYWORDS,
    SELF_HARM_KEYWORDS,
    keyword_hits
)

# -------------------------------------------------
# Risk hierarchy (authoritative)
# -------------------------------------------------
RISK_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "emergency": 4
}

# -------------------------------------------------
# Component weights (safety-biased)
# -------------------------------------------------
EMOTION_WEIGHTS = {
    "fear": 3.0,
    "sadness": 2.0,
    "anger": 1.5,
    "neutral": 0.5
}

SENTIMENT_WEIGHTS = {
    "negative": 1.5,
    "neutral": 0.5,
    "positive": 0.0
}

ML_RISK_WEIGHTS = {
    "low": 1.0,
    "medium": 3.0,
    "high": 6.0,
    "emergency": 9.0
}

# -------------------------------------------------
# Risk thresholds (monotonic & interpretable)
# -------------------------------------------------
RISK_THRESHOLDS = {
    "medium": 4.0,
    "high": 8.0,
    "emergency": 12.0
}

# -------------------------------------------------
# Emergency type detection
# -------------------------------------------------
def detect_emergency_type(text: str) -> Optional[str]:
    text = text.lower()

    if keyword_hits(text, SELF_HARM_KEYWORDS) >= 1:
        return "self_harm"

    if (
        keyword_hits(text, EMERGENCY_KEYWORDS) >= 1
        or keyword_hits(text, PHYSICAL_ABUSE_KEYWORDS) >= 1
    ):
        return "external_threat"

    return None


# -------------------------------------------------
# Core scoring function
# -------------------------------------------------
def compute_risk(
    text: str,
    emotion: str,
    sentiment: str,
    ml_risk: str,
    previous_risks: List[str] | None = None
) -> Dict[str, object]:

    if previous_risks is None:
        previous_risks = []

    score = 0.0
    explanations = []

    # -----------------------------
    # 1️⃣ ML & affective baseline
    # -----------------------------
    score += EMOTION_WEIGHTS.get(emotion, 0.5)
    score += SENTIMENT_WEIGHTS.get(sentiment, 0.5)
    score += ML_RISK_WEIGHTS.get(ml_risk, 1.0)

    explanations.append("baseline_ml_emotion_sentiment")

    # -----------------------------
    # 2️⃣ Linguistic intensity (CAPPED)
    # -----------------------------
    features = extract_features(text)

    linguistic_score = 0.0
    linguistic_score += min(features.get("urgency_count", 0), 3) * 2.0
    linguistic_score += min(features.get("intensity", 1.0), 1.0) * 2.0
    linguistic_score += min(features.get("repetition_score", 0), 3) * 0.5

    score += min(linguistic_score, 5.0)  # cap inflation
    explanations.append("linguistic_intensity")

    # -----------------------------
    # 3️⃣ Keyword escalation (severity-aware)
    # -----------------------------
    score += min(keyword_hits(text, PHYSICAL_ABUSE_KEYWORDS), 3) * 3.0
    score += min(keyword_hits(text, FEAR_KEYWORDS), 4) * 1.2
    score += min(keyword_hits(text, SELF_HARM_KEYWORDS), 2) * 4.5

    explanations.append("keyword_escalation")

    # -----------------------------
    # 4️⃣ Context escalation (trend-aware)
    # -----------------------------
    if previous_risks:
        recent = previous_risks[-3:]
        numeric = [RISK_ORDER.get(r, 1) for r in recent]

        if max(numeric) >= RISK_ORDER["high"]:
            score += 1.5
            explanations.append("context_high_risk_history")

        elif numeric.count(RISK_ORDER["medium"]) >= 2:
            score += 0.8
            explanations.append("context_sustained_medium")

    # -----------------------------
    # 5️⃣ Emergency override (absolute)
    # -----------------------------
    emergency_type = detect_emergency_type(text)
    emergency_override = emergency_type is not None

    if emergency_override:
        explanations.append(f"emergency_override:{emergency_type}")

    # -----------------------------
    # 6️⃣ Final risk mapping
    # -----------------------------
    final_risk = _map_score_to_risk(score, emergency_override)

    return {
        "risk_score": round(score, 2),
        "final_risk": final_risk,
        "emergency_override": emergency_override,
        "emergency_type": emergency_type,
        "explanations": explanations,
        "debug": {
            "emotion": emotion,
            "sentiment": sentiment,
            "ml_risk": ml_risk,
            "features": features,
            "previous_risks": previous_risks
        }
    }


# -------------------------------------------------
# Score → risk mapping
# -------------------------------------------------
def _map_score_to_risk(score: float, emergency_override: bool) -> str:
    if emergency_override or score >= RISK_THRESHOLDS["emergency"]:
        return "emergency"
    if score >= RISK_THRESHOLDS["high"]:
        return "high"
    if score >= RISK_THRESHOLDS["medium"]:
        return "medium"
    return "low"
