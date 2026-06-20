"""
keywords.py
============
Enhanced domain-specific keyword banks for PROTEGO.

Upgrades:
- Better implicit danger coverage
- Stronger coercive control detection
- Panic & escalation language
- Fully backward compatible
"""

import re
from typing import Iterable, Dict


# -------------------------------------------------
# Emergency / life-threatening
# -------------------------------------------------
EMERGENCY_KEYWORDS = {
    # Explicit violence
    "kill", "killing", "knife", "gun", "weapon", "blood",
    "strangle", "strangling", "choking",
    "attack", "attacking",
    "dying", "death",

    # Threat escalation
    "threatening", "threat",
    "finish me", "end me",
    "won't survive", "will die",

    # Immediate urgency
    "help now", "right now", "immediately",
    "call police", "call ambulance"
}


# -------------------------------------------------
# Physical abuse indicators
# -------------------------------------------------
PHYSICAL_ABUSE_KEYWORDS = {
    "hit", "hitting", "beat", "beating",
    "slap", "slapped", "punch", "punched",
    "kick", "kicked", "push", "pushed",
    "bruise", "injury", "hurt",

    # Restraint & force
    "grab", "grabbed",
    "hold me", "holding me",
    "block", "blocked",
    "lock", "locked",
    "throw", "threw"
}


# -------------------------------------------------
# Emotional / psychological abuse
# -------------------------------------------------
EMOTIONAL_ABUSE_KEYWORDS = {
    "insult", "insulting", "shout", "shouting",
    "control", "controlling",
    "humiliate", "humiliated",
    "threaten", "threatening",
    "manipulate", "manipulating",

    # Coercive control
    "monitor", "monitoring",
    "track", "tracking",
    "isolate", "isolating",
    "doesn't let me",
    "won't let me",
    "checks my phone"
}


# -------------------------------------------------
# Fear & panic indicators
# -------------------------------------------------
FEAR_KEYWORDS = {
    "scared", "afraid", "fear",
    "unsafe", "danger", "terrified",
    "panic", "panicking",

    # Panic symptoms
    "shaking",
    "heart racing",
    "can't breathe",
    "cant breathe",
    "frozen"
}


# -------------------------------------------------
# Self-harm / hopelessness (PHRASES ONLY)
# -------------------------------------------------
SELF_HARM_KEYWORDS = {
    "i will die",
    "i want to die",
    "i am going to die",
    "kill myself",
    "end my life",
    "no reason to live",
    "i can't go on",
    "i cant go on",
    "i give up",
    "i want everything to stop",
    "i don't want to live",
    "i dont want to live",
    "nothing matters anymore",
    "i am done"
}


# -------------------------------------------------
# Keyword matching engine
# -------------------------------------------------
def keyword_hits(text: str, keywords: Iterable[str]) -> int:
    """
    Count keyword/phrase hits in text.

    - Single words use word-boundary matching
    - Phrases use substring matching
    """

    if not isinstance(text, str) or not text.strip():
        return 0

    text_lower = text.lower()
    hits = 0

    for kw in keywords:
        kw = kw.lower().strip()

        if " " in kw:
            if kw in text_lower:
                hits += 1
        else:
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                hits += 1

    return hits


# -------------------------------------------------
# Explainable keyword scan (audit/debug)
# -------------------------------------------------
def keyword_explain(text: str, keywords: Iterable[str]) -> Dict[str, int]:
    """
    Return which keywords were matched and how many times.
    Useful for debugging and audits.
    """

    if not isinstance(text, str) or not text.strip():
        return {}

    text_lower = text.lower()
    result = {}

    for kw in keywords:
        kw = kw.lower().strip()

        if " " in kw:
            count = text_lower.count(kw)
        else:
            count = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))

        if count > 0:
            result[kw] = count

    return result
