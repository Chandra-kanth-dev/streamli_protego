"""
safety_rules.py
================
Rule-based safety enforcement module for PROTEGO.

FINAL authority in risk decisions.
Deterministically overrides ML outputs when safety is at risk.

Enhanced:
- Safer emergency keyword handling
- Stronger persistence logic
- Explicit no-downgrade guarantees
- Fully backward compatible
"""

from typing import Dict

from protego.nlp.keywords import (
    EMERGENCY_KEYWORDS,
    PHYSICAL_ABUSE_KEYWORDS,
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
# Safety rule engine (FINAL AUTHORITY)
# -------------------------------------------------
def apply_safety_rules(
    text: str,
    current_risk: str,
    context_summary: Dict[str, object]
) -> Dict[str, object]:
    """
    Apply deterministic, priority-ordered safety rules.

    Guarantees:
    - Risk is NEVER downgraded
    - Emergency signals override all other logic
    - Rules are explainable and auditable
    """

    text_lower = text.lower()

    result = {
        "final_risk": current_risk,
        "rule_triggered": False,
        "rule_reason": None,
        "rule_priority": None
    }

    # -------------------------------------------------
    # RULE 1 (Priority 1): Explicit emergency language
    # -------------------------------------------------
    if keyword_hits(text_lower, EMERGENCY_KEYWORDS) >= 1:
        result.update({
            "final_risk": "emergency",
            "rule_triggered": True,
            "rule_reason": "Explicit emergency keyword detected",
            "rule_priority": 1
        })
        return result

    # -------------------------------------------------
    # RULE 2 (Priority 2): Sustained or repeated high risk
    # -------------------------------------------------
    if context_summary.get("repeated_high_risk"):
        result.update({
            "final_risk": "emergency",
            "rule_triggered": True,
            "rule_reason": "Sustained high or emergency risk pattern detected",
            "rule_priority": 2
        })
        return result

    # -------------------------------------------------
    # RULE 3 (Priority 3): Physical abuse indicators
    # -------------------------------------------------
    if keyword_hits(text_lower, PHYSICAL_ABUSE_KEYWORDS) >= 1:
        if RISK_ORDER.get(current_risk, 1) < RISK_ORDER["high"]:
            result.update({
                "final_risk": "high",
                "rule_triggered": True,
                "rule_reason": "Physical abuse indicator detected",
                "rule_priority": 3
            })
            return result

    # -------------------------------------------------
    # RULE 4 (Priority 4): Escalating trend
    # -------------------------------------------------
    if context_summary.get("is_escalating"):
        if current_risk == "medium":
            result.update({
                "final_risk": "high",
                "rule_triggered": True,
                "rule_reason": "Escalating risk trend detected",
                "rule_priority": 4
            })
            return result

    # -------------------------------------------------
    # RULE 5 (Priority 5): Recent emergency persistence
    # -------------------------------------------------
    recent_risks = context_summary.get("recent_risks", [])
    if recent_risks[-2:].count("emergency") >= 1:
        result.update({
            "final_risk": "emergency",
            "rule_triggered": True,
            "rule_reason": "Recent emergency risk persists in conversation",
            "rule_priority": 5
        })
        return result

    # -------------------------------------------------
    # No override → keep current risk
    # -------------------------------------------------
    return result
