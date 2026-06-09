"""
chatbot_service.py
==================
Central orchestration service for PROTEGO chatbot.
"""

from __future__ import annotations

import json
import threading
import re
from pathlib import Path
from typing import Dict, Optional

import joblib

from protego.nlp.preprocess import clean_text
from protego.logic.context_memory import ContextMemory
from protego.logic.risk_scoring import compute_risk
from protego.logic.safety_rules import apply_safety_rules
from protego.logic.response_engine import generate_response

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

# -----------------------------
# Globals
# -----------------------------
_model_lock = threading.Lock()

_emotion_model = None
_sentiment_model = None
_risk_model = None

_emotion_vectorizer = None
_sentiment_vectorizer = None
_risk_vectorizer = None

_EMERGENCY_CONTACTS = None

_context_memory = ContextMemory(max_history=5)


# -----------------------------
# 🔥 CLEAN RESPONSE TEXT (FIX)
# -----------------------------
def clean_response_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # Add space after punctuation
    text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', text)

    # Fix joined lowercase-uppercase words
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)

    # Add paragraph spacing
    text = re.sub(r'([.!?])\s*', r'\1\n\n', text)

    return text.strip()


# -----------------------------
# Load resources (once)
# -----------------------------
def _load_resources() -> None:
    global _emotion_model, _sentiment_model, _risk_model
    global _emotion_vectorizer, _sentiment_vectorizer, _risk_vectorizer
    global _EMERGENCY_CONTACTS

    if _emotion_model is not None:
        return

    with _model_lock:
        if _emotion_model is not None:
            return

        try:
            _emotion_model = joblib.load(MODEL_DIR / "emotion_model.pkl")
            _sentiment_model = joblib.load(MODEL_DIR / "sentiment_model.pkl")
            _risk_model = joblib.load(MODEL_DIR / "risk_model.pkl")

            _emotion_vectorizer = joblib.load(MODEL_DIR / "emotion_vectorizer.pkl")
            _sentiment_vectorizer = joblib.load(MODEL_DIR / "sentiment_vectorizer.pkl")
            _risk_vectorizer = joblib.load(MODEL_DIR / "risk_vectorizer.pkl")

        except Exception as e:
            raise RuntimeError(f"❌ Model/vectorizer loading failed: {e}")

        try:
            with open(KNOWLEDGE_DIR / "emergency_contacts.json", "r", encoding="utf-8") as f:
                _EMERGENCY_CONTACTS = json.load(f)
        except Exception as e:
            raise RuntimeError(f"❌ Emergency contacts load failed: {e}")


# -----------------------------
# Get emergency contacts
# -----------------------------
def get_contacts(country: str) -> Dict:
    if _EMERGENCY_CONTACTS:
        return _EMERGENCY_CONTACTS.get(country, _EMERGENCY_CONTACTS.get("Global"))
    return None


# -----------------------------
# Main handler
# -----------------------------
def handle_message(
    message: str,
    country: str = "India",
    debug: bool = False
) -> Dict[str, object]:

    if not message or not message.strip():
        return {
            "reply": "I’m here with you 🤍 Tell me what’s going on.",
            "risk_level": "low",
            "emotion": "neutral",
            "sentiment": "neutral",
            "show_emergency": False,
            "emergency_contacts": None,
            "tone": "gentle"
        }

    _load_resources()

    # -----------------------------
    # 1. Preprocess
    # -----------------------------
    cleaned_text = clean_text(message)

    # -----------------------------
    # 2. Vectorize
    # -----------------------------
    X_emotion = _emotion_vectorizer.transform([cleaned_text])
    X_sentiment = _sentiment_vectorizer.transform([cleaned_text])
    X_risk = _risk_vectorizer.transform([cleaned_text])

    # -----------------------------
    # 3. Predictions
    # -----------------------------
    emotion = _emotion_model.predict(X_emotion)[0]
    sentiment = _sentiment_model.predict(X_sentiment)[0]
    ml_risk = _risk_model.predict(X_risk)[0]

    # -----------------------------
    # 4. Risk fusion
    # -----------------------------
    risk_result = compute_risk(
        text=message,
        emotion=emotion,
        sentiment=sentiment,
        ml_risk=ml_risk,
        previous_risks=_context_memory.get_recent_risks()
    )

    # -----------------------------
    # 5. Safety rules
    # -----------------------------
    safety = apply_safety_rules(
        text=message,
        current_risk=risk_result["final_risk"],
        context_summary=_context_memory.summary()
    )

    final_risk = safety["final_risk"]

    # -----------------------------
    # 6. Update context
    # -----------------------------
    _context_memory.update(risk=final_risk, emotion=emotion)

    # -----------------------------
    # 7. Emergency contacts
    # -----------------------------
    emergency_contacts: Optional[dict] = None
    if final_risk in {"high", "emergency"}:
        emergency_contacts = get_contacts(country)

    # -----------------------------
    # 8. Generate response
    # -----------------------------
    response_payload = generate_response(
        emotion=emotion,
        final_risk=final_risk,
        emergency_contacts=emergency_contacts
    )

    # -----------------------------
    # 9. FINAL RESPONSE (🔥 FIXED)
    # -----------------------------
    reply_text = clean_response_text(response_payload["message"])

    response = {
        "reply": reply_text,
        "risk_level": final_risk,
        "emotion": emotion,
        "sentiment": sentiment,
        "show_emergency": response_payload["show_emergency"],
        "emergency_contacts": emergency_contacts,
        "tone": response_payload["tone"]
    }

    if debug:
        response["debug"] = {
            "ml_risk": ml_risk,
            "risk_score": risk_result.get("risk_score"),
            "rule_triggered": safety.get("rule_triggered"),
            "rule_reason": safety.get("rule_reason"),
            "context_summary": _context_memory.summary()
        }

    return response