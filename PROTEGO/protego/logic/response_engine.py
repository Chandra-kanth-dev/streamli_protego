"""
response_engine.py
==================
Generates safe, empathetic, layered, HUMAN responses
for the PROTEGO chatbot.

Priority:
1. Keyword-based deep responses (most human)
2. Risk-based layered guidance (fallback)
"""

import json
import random
from pathlib import Path
from typing import Dict, Optional

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
GUIDANCE_PATH = BASE_DIR / "knowledge" / "guidance_templates.json"
KEYWORD_RESPONSE_PATH = BASE_DIR / "knowledge" / "keyword_responses.json"

# -------------------------------------------------
# Load resources once
# -------------------------------------------------
with open(GUIDANCE_PATH, "r", encoding="utf-8") as f:
    GUIDANCE = json.load(f)

with open(KEYWORD_RESPONSE_PATH, "r", encoding="utf-8") as f:
    KEYWORD_RESPONSES = json.load(f)


# -------------------------------------------------
# Empathetic openers (fallback use)
# -------------------------------------------------
OPENERS = {
    "low": [
        "I’m really glad you reached out 🤍",
        "Thank you for telling me how you’re feeling.",
        "I’m here with you, and I’m listening."
    ],
    "medium": [
        "I’m really sorry you’re feeling this way 🤍",
        "That sounds emotionally heavy, and I’m glad you spoke up.",
        "What you’re feeling matters, and you’re not alone."
    ],
    "high": [
        "I’m really concerned about you 🤍",
        "What you’re describing sounds serious, and I care about your safety.",
        "I’m worried about what you’re going through."
    ],
    "emergency": [
        "I’m really glad you reached out 🤍",
        "I care about your safety, and I’m concerned right now."
    ]
}


# -------------------------------------------------
# Public API (UNCHANGED)
# -------------------------------------------------
def generate_response(
    emotion: str,
    final_risk: str,
    emergency_contacts: Optional[Dict[str, str]] = None
) -> Dict[str, object]:
    """
    Generate final chatbot response based on FINAL risk
    and keyword-based deep responses.
    """

    # -------------------------------------------------
    # 1️⃣ KEYWORD-BASED BIG RESPONSES (TOP PRIORITY)
    # -------------------------------------------------
    text_probe = f"{emotion} {final_risk}".lower()

    for keyword, data in KEYWORD_RESPONSES.items():
        if keyword in text_probe:
            return {
                "message": data["response"],
                "show_emergency": data["risk"] in {"high", "emergency"},
                "tone": data["risk"]
            }

    # -------------------------------------------------
    # 2️⃣ RISK-BASED LAYERED RESPONSE (FALLBACK)
    # -------------------------------------------------
    risk_block = GUIDANCE.get(final_risk, {})
    guidance_list = risk_block.get("guidance", [])
    next_prompt = risk_block.get("next_step_prompt", "")

    opener = random.choice(OPENERS.get(final_risk, ["I’m here with you 🤍"]))

    # Pick up to 2 guidance lines (avoid overload)
    guidance_lines = random.sample(
        guidance_list,
        k=min(2, len(guidance_list))
    )

    message_parts = [
        opener,
        "",
        *guidance_lines
    ]

    if next_prompt:
        message_parts.extend(["", next_prompt])

    message = "\n".join(message_parts)

    return {
        "message": message,
        "show_emergency": final_risk in {"high", "emergency"},
        "tone": risk_block.get("tone", "gentle")
    }
