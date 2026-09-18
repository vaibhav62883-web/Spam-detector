"""
tests/test_advisor.py
---------------------
Tests for SafetyAdvisor.get_advice().
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from advisor import SafetyAdvisor


@pytest.fixture()
def advisor() -> SafetyAdvisor:
    return SafetyAdvisor()


def test_safe_advice_is_empty(advisor):
    assert advisor.get_advice("Safe") == []


def test_spam_advice_is_non_empty(advisor):
    advice = advisor.get_advice("Spam")
    assert isinstance(advice, list)
    assert len(advice) > 0


def test_suspicious_fake_advice_is_non_empty(advisor):
    advice = advisor.get_advice("Suspicious/Fake")
    assert isinstance(advice, list)
    assert len(advice) > 0


def test_potential_scam_advice_is_non_empty(advisor):
    advice = advisor.get_advice("Potential Scam")
    assert isinstance(advice, list)
    assert len(advice) > 0


def test_unknown_type_returns_empty_list(advisor):
    """An unrecognised message type must not raise an exception."""
    advice = advisor.get_advice("UNKNOWN_TYPE_XYZ")
    assert advice == []


def test_all_advice_items_are_strings(advisor):
    for msg_type in ("Spam", "Suspicious/Fake", "Potential Scam"):
        for item in advisor.get_advice(msg_type):
            assert isinstance(item, str), f"Non-string advice item for '{msg_type}': {item!r}"
