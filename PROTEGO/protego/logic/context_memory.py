"""
context_memory.py
=================
Conversation context and risk memory manager for PROTEGO.

Enhanced:
- More robust escalation detection
- Stronger sustained-risk logic
- Dominant emotion summarization
- Fully backward compatible
"""

from collections import deque, Counter
from typing import List, Dict


class ContextMemory:
    """
    Maintains short-term conversational context for a single user session.
    """

    # Risk hierarchy (authoritative)
    RISK_ORDER = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "emergency": 4
    }

    def __init__(self, max_history: int = 5):
        self.max_history = max_history
        self.risk_history: deque[str] = deque(maxlen=max_history)
        self.emotion_history: deque[str] = deque(maxlen=max_history)

    # -----------------------------
    # Update context
    # -----------------------------
    def update(self, risk: str, emotion: str) -> None:
        if risk in self.RISK_ORDER:
            self.risk_history.append(risk)

        if isinstance(emotion, str) and emotion:
            self.emotion_history.append(emotion)

    # -----------------------------
    # Accessors
    # -----------------------------
    def get_recent_risks(self) -> List[str]:
        return list(self.risk_history)

    def get_recent_emotions(self) -> List[str]:
        return list(self.emotion_history)

    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _numeric_risks(self) -> List[int]:
        return [self.RISK_ORDER[r] for r in self.risk_history]

    # -----------------------------
    # Trend analysis
    # -----------------------------
    def is_escalating(self) -> bool:
        """
        Detect whether risk is generally trending upward,
        allowing for plateaus (e.g., high → high).
        """
        nums = self._numeric_risks()
        if len(nums) < 3:
            return False

        return nums[-1] >= nums[-2] and nums[-1] > min(nums)

    def escalation_strength(self) -> float:
        """
        Normalized escalation score [0.0, 1.0].
        """
        nums = self._numeric_risks()
        if len(nums) < 2:
            return 0.0

        delta = max(nums) - min(nums)
        max_delta = self.RISK_ORDER["emergency"] - self.RISK_ORDER["low"]

        return round(max(delta / max_delta, 0.0), 2)

    def repeated_high_risk(self) -> bool:
        """
        Detect sustained high or emergency risk patterns.
        """
        if not self.risk_history:
            return False

        recent = list(self.risk_history)[-3:]

        if "emergency" in recent:
            return True

        # sustained high risk (not intermittent)
        return recent.count("high") == len(recent)

    # -----------------------------
    # Emotion insights
    # -----------------------------
    def dominant_emotion(self) -> str:
        """
        Most frequent recent emotion (if available).
        """
        if not self.emotion_history:
            return "unknown"

        return Counter(self.emotion_history).most_common(1)[0][0]

    # -----------------------------
    # Explainable summary
    # -----------------------------
    def summary(self) -> Dict[str, object]:
        return {
            "recent_risks": self.get_recent_risks(),
            "recent_emotions": self.get_recent_emotions(),
            "dominant_emotion": self.dominant_emotion(),
            "is_escalating": self.is_escalating(),
            "escalation_strength": self.escalation_strength(),
            "repeated_high_risk": self.repeated_high_risk()
        }

    # -----------------------------
    # Reset memory
    # -----------------------------
    def reset(self) -> None:
        self.risk_history.clear()
        self.emotion_history.clear()
