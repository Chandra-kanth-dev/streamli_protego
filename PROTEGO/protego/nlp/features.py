"""
features.py
============
Enhanced linguistic and behavioral feature extraction for PROTEGO.

Upgrades:
- Stronger urgency & distress detection
- Better rumination signals
- Short-message intensity handling
- Fully backward compatible
"""

import re
from typing import Dict


# -------------------------------------------------
# Domain-specific signal vocabularies
# -------------------------------------------------

URGENCY_WORDS = {
    "now", "today", "immediately", "urgent", "asap",
    "right", "help", "quick", "fast"
}

THREAT_WORDS = {
    "hurt", "kill", "hit", "beat", "threat", "attack",
    "force", "abuse", "harm"
}

FIRST_PERSON_WORDS = {
    "i", "me", "my", "mine", "myself"
}

NEGATION_WORDS = {
    "not", "no", "never", "dont", "can't", "cant",
    "won't", "wont", "nothing"
}

DISTRESS_PHRASES = {
    "help me",
    "please help",
    "i can't",
    "i cant",
    "i am scared",
    "i feel unsafe",
    "i am afraid",
    "i am trapped",
    "i need help",
    "i don't feel safe"
}

HOPELESSNESS_PHRASES = {
    "no way out",
    "nothing will change",
    "i give up",
    "i am tired of this",
    "i can't take it anymore"
}


# -------------------------------------------------
# Feature extraction
# -------------------------------------------------
def extract_features(text: str) -> Dict[str, float]:
    """
    Extract linguistic and psychological features from raw text.

    Returns normalized, safety-oriented signals.
    """

    if not isinstance(text, str) or not text.strip():
        return _empty_features()

    raw_text = text.strip()
    text_lower = raw_text.lower()

    tokens = re.findall(r"\b[a-z']+\b", text_lower)
    word_count = len(tokens)
    unique_word_count = len(set(tokens))

    # -----------------------------
    # Lexical features
    # -----------------------------
    urgency_count = sum(1 for w in tokens if w in URGENCY_WORDS)
    threat_count = sum(1 for w in tokens if w in THREAT_WORDS)
    first_person_count = sum(1 for w in tokens if w in FIRST_PERSON_WORDS)
    negation_count = sum(1 for w in tokens if w in NEGATION_WORDS)

    # -----------------------------
    # Phrase-level distress
    # -----------------------------
    distress_phrase_hits = sum(
        1 for phrase in DISTRESS_PHRASES if phrase in text_lower
    )

    hopelessness_hits = sum(
        1 for phrase in HOPELESSNESS_PHRASES if phrase in text_lower
    )

    # -----------------------------
    # Rumination (repeated self-focus)
    # -----------------------------
    repetition_score = max(
        (word_count - unique_word_count) / max(word_count, 1),
        0
    )

    # -----------------------------
    # Punctuation & casing intensity
    # -----------------------------
    exclamation_count = raw_text.count("!")
    question_count = raw_text.count("?")

    uppercase_ratio = (
        sum(1 for c in raw_text if c.isupper()) / max(len(raw_text), 1)
    )

    # -----------------------------
    # Intensity estimation
    # -----------------------------
    short_message_urgency = 1.0 if word_count <= 4 and urgency_count > 0 else 0.0

    punctuation_intensity = min(
        (exclamation_count + question_count) / 4.0,
        1.0
    )

    length_intensity = min(word_count / 20.0, 1.0)

    combined_intensity = min(
        length_intensity
        + punctuation_intensity
        + short_message_urgency,
        1.0
    )

    # -----------------------------
    # Final feature vector
    # -----------------------------
    return {
        "word_count": float(word_count),
        "urgency_count": float(urgency_count),
        "threat_count": float(threat_count),
        "first_person_ratio": round(first_person_count / max(word_count, 1), 2),
        "negation_count": float(negation_count),
        "repetition_score": round(repetition_score, 2),
        "distress_phrase_hits": float(distress_phrase_hits),
        "hopelessness_hits": float(hopelessness_hits),
        "uppercase_ratio": round(uppercase_ratio, 2),
        "punctuation_intensity": round(punctuation_intensity, 2),
        "intensity": round(combined_intensity, 2)
    }


# -------------------------------------------------
# Empty feature fallback
# -------------------------------------------------
def _empty_features() -> Dict[str, float]:
    """
    Default feature values for empty or invalid input.
    """
    return {
        "word_count": 0.0,
        "urgency_count": 0.0,
        "threat_count": 0.0,
        "first_person_ratio": 0.0,
        "negation_count": 0.0,
        "repetition_score": 0.0,
        "distress_phrase_hits": 0.0,
        "hopelessness_hits": 0.0,
        "uppercase_ratio": 0.0,
        "punctuation_intensity": 0.0,
        "intensity": 0.0
    }
