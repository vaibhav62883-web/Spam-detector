"""
tests/test_models.py
--------------------
Tests for AnalysisResult and HistoryEntry dataclasses.
"""

import pytest
import sys
import os

# Make the spam_detector package importable when running pytest from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import AnalysisResult, HistoryEntry


# ---------------------------------------------------------------------------
# AnalysisResult
# ---------------------------------------------------------------------------

def make_result(**overrides) -> AnalysisResult:
    defaults = dict(
        original_message="Hello, this is a test.",
        risk_level="Low",
        message_type="Safe",
        reasons=[],
        advice=[],
        timestamp="2024-06-01 12:00:00",
    )
    defaults.update(overrides)
    return AnalysisResult(**defaults)


def test_analysis_result_to_dict_has_correct_keys():
    result = make_result()
    d = result.to_dict()
    assert set(d.keys()) == {
        "original_message", "risk_level", "message_type",
        "reasons", "advice", "timestamp",
    }


def test_analysis_result_to_dict_values_match():
    result = make_result(risk_level="High", message_type="Spam", reasons=["Spam keyword detected: 'winner'"])
    d = result.to_dict()
    assert d["risk_level"] == "High"
    assert d["message_type"] == "Spam"
    assert d["reasons"] == ["Spam keyword detected: 'winner'"]


def test_analysis_result_round_trip():
    original = make_result(
        risk_level="Medium",
        message_type="Potential Scam",
        reasons=["Scam keyword detected: 'otp'"],
        advice=["Never share your OTP."],
    )
    restored = AnalysisResult.from_dict(original.to_dict())
    assert restored.original_message == original.original_message
    assert restored.risk_level == original.risk_level
    assert restored.message_type == original.message_type
    assert restored.reasons == original.reasons
    assert restored.advice == original.advice
    assert restored.timestamp == original.timestamp


def test_analysis_result_from_dict_missing_optional_fields():
    """from_dict() should handle missing 'reasons' and 'advice' gracefully."""
    d = {
        "original_message": "test",
        "risk_level": "Low",
        "message_type": "Safe",
        "timestamp": "2024-01-01 00:00:00",
    }
    result = AnalysisResult.from_dict(d)
    assert result.reasons == []
    assert result.advice == []


# ---------------------------------------------------------------------------
# HistoryEntry
# ---------------------------------------------------------------------------

def make_entry(**overrides) -> HistoryEntry:
    defaults = dict(
        message_preview="First 60 chars...",
        risk_level="Low",
        message_type="Safe",
        timestamp="2024-06-01 12:00:00",
    )
    defaults.update(overrides)
    return HistoryEntry(**defaults)


def test_history_entry_to_dict_has_correct_keys():
    entry = make_entry()
    d = entry.to_dict()
    assert set(d.keys()) == {"message_preview", "risk_level", "message_type", "timestamp"}


def test_history_entry_round_trip():
    original = make_entry(risk_level="High", message_type="Potential Scam")
    restored = HistoryEntry.from_dict(original.to_dict())
    assert restored.message_preview == original.message_preview
    assert restored.risk_level == original.risk_level
    assert restored.message_type == original.message_type
    assert restored.timestamp == original.timestamp
