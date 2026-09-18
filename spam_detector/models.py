"""
models.py
---------
Data shapes used across the entire application.
Both dataclasses support to_dict() / from_dict() for JSON persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnalysisResult:
    """Holds the full result of a single message analysis."""

    original_message: str
    risk_level: str          # "Low", "Medium", or "High"
    message_type: str        # "Safe", "Spam", "Suspicious/Fake", or "Potential Scam"
    reasons: list[str]       # Plain-English list of detected warning signs
    advice: list[str]        # Safety tips (empty when risk is Low / Safe)
    timestamp: str           # Formatted string, e.g. "2024-06-01 14:30:00"

    def to_dict(self) -> dict:
        """Convert this result to a plain dictionary (for JSON storage)."""
        return {
            "original_message": self.original_message,
            "risk_level": self.risk_level,
            "message_type": self.message_type,
            "reasons": self.reasons,
            "advice": self.advice,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult":
        """Rebuild an AnalysisResult from a plain dictionary."""
        return cls(
            original_message=data["original_message"],
            risk_level=data["risk_level"],
            message_type=data["message_type"],
            reasons=data.get("reasons", []),
            advice=data.get("advice", []),
            timestamp=data["timestamp"],
        )


@dataclass
class HistoryEntry:
    """
    A lightweight summary stored in history.json.
    Does NOT store the full original message to keep the file small.
    """

    message_preview: str   # First 60 characters of the original message
    risk_level: str
    message_type: str
    timestamp: str

    def to_dict(self) -> dict:
        """Convert to a plain dictionary (for JSON storage)."""
        return {
            "message_preview": self.message_preview,
            "risk_level": self.risk_level,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Rebuild a HistoryEntry from a plain dictionary."""
        return cls(
            message_preview=data["message_preview"],
            risk_level=data["risk_level"],
            message_type=data["message_type"],
            timestamp=data["timestamp"],
        )
