"""
schemas.py
==========
Pydantic data models for PROTEGO API.

This version is:
✅ Strictly validated
✅ Safety-aware
✅ Interview & production ready
"""

from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# -----------------------------
# Request schema
# -----------------------------
class ChatRequest(BaseModel):
    """
    Incoming chat message from user.
    """

    message: str = Field(
        ...,
        min_length=1,
        examples=["I feel scared to go home tonight"],
        description="User input message"
    )

    country: Optional[str] = Field(
        default="India",
        examples=["India", "USA", "UK"],
        description="User country for emergency contacts"
    )

    model_config = ConfigDict(
        extra="forbid"
    )


# -----------------------------
# Emergency contact schema (NEW)
# -----------------------------
class EmergencyContact(BaseModel):
    """
    Structured emergency contact information.
    """

    number: str = Field(
        ...,
        description="Emergency phone number"
    )

    description: str = Field(
        ...,
        description="What this helpline is for"
    )

    available: str = Field(
        ...,
        description="Availability (e.g., 24/7)"
    )


# -----------------------------
# Base response schema
# -----------------------------
class ChatResponse(BaseModel):
    """
    AI-generated response returned to frontend.
    """

    reply: str = Field(
        ...,
        description="Chatbot reply message"
    )

    risk_level: Literal[
        "low",
        "medium",
        "high",
        "emergency",
        "unknown"
    ] = Field(
        ...,
        description="Final assessed risk level"
    )

    emotion: Optional[str] = Field(
        default=None,
        description="Detected emotional state"
    )

    sentiment: Optional[str] = Field(
        default=None,
        description="Detected sentiment polarity"
    )

    show_emergency: bool = Field(
        ...,
        description="Whether emergency UI should be shown"
    )

    emergency_contacts: Optional[Dict[str, EmergencyContact]] = Field(
        default=None,
        description="Emergency contacts relevant to the user"
    )

    tone: Optional[str] = Field(
        default="neutral",
        description="Suggested UI tone"
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "reply": "I’m really glad you reached out. You’re not alone.",
                "risk_level": "high",
                "emotion": "fear",
                "sentiment": "negative",
                "show_emergency": True,
                "emergency_contacts": {
                    "police": {
                        "number": "112",
                        "description": "Police emergency assistance",
                        "available": "24/7"
                    },
                    "women_helpline": {
                        "number": "181",
                        "description": "Women in distress helpline",
                        "available": "24/7"
                    }
                },
                "tone": "serious"
            }
        }
    )


# -----------------------------
# Debug / explainability schema
# -----------------------------
class DebugInfo(BaseModel):
    """
    Internal AI decision details (debug only).
    """

    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Numerical risk score"
    )

    rule_triggered: bool = Field(
        ...,
        description="Whether a safety rule overrode ML output"
    )

    rule_reason: Optional[str] = Field(
        default=None,
        description="Reason for rule trigger"
    )

    context_summary: Dict[str, str] = Field(
        ...,
        description="Short summary of recent conversation context"
    )


class ChatResponseWithDebug(ChatResponse):
    """
    Extended response including debug information.
    """

    debug: Optional[DebugInfo] = Field(
        default=None,
        description="Explainability data (debug endpoint only)"
    )
