"""
tests/test_detector.py
----------------------
Tests for MessageDetector — classification accuracy, risk levels, edge cases.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from detector import MessageDetector
from models import AnalysisResult


@pytest.fixture()
def detector() -> MessageDetector:
    return MessageDetector()


# ---------------------------------------------------------------------------
# Safe / clean messages
# ---------------------------------------------------------------------------

def test_clean_message_is_safe(detector):
    result = detector.analyze("Hi, how are you today? Hope you're having a great day!")
    assert result.risk_level == "Low"
    assert result.message_type == "Safe"
    assert result.reasons == []


def test_emoji_only_message_is_safe(detector):
    """A message containing only emojis should not trigger any rules."""
    result = detector.analyze("😊🎉👍✨🌟")
    assert result.risk_level == "Low"
    assert result.message_type == "Safe"


def test_short_greeting_is_safe(detector):
    result = detector.analyze("Hello, thank you for your message.")
    assert result.risk_level == "Low"
    assert result.message_type == "Safe"


# ---------------------------------------------------------------------------
# Spam detection
# ---------------------------------------------------------------------------

def test_single_spam_keyword_is_medium_spam(detector):
    result = detector.analyze("Congratulations! You have been selected for a free offer!")
    # "congratulations" and "free offer" are both spam keywords → Medium or High
    assert result.message_type == "Spam"
    assert result.risk_level in ("Medium", "High")


def test_spam_keyword_winner(detector):
    result = detector.analyze("You are a winner! Click here to claim your prize.")
    assert result.message_type == "Spam"
    assert len(result.reasons) > 0


def test_excessive_exclamation_marks_flagged(detector):
    result = detector.analyze("BUY NOW!!! Limited time offer!!!")
    assert result.message_type == "Spam"
    assert any("!" in r for r in result.reasons)


def test_all_caps_word_flagged(detector):
    """A standalone ALL-CAPS word (5+ letters) should trigger the spam pattern."""
    result = detector.analyze("This is URGENT please act now")
    # "URGENT" is 6 caps letters → spam pattern, "act now" is spam keyword
    assert result.message_type in ("Spam", "Potential Scam")
    assert len(result.reasons) > 0


def test_reasons_list_non_empty_for_spam(detector):
    result = detector.analyze("Buy now and earn money fast! Click here.")
    assert len(result.reasons) > 0


# ---------------------------------------------------------------------------
# Fake / impersonation detection
# ---------------------------------------------------------------------------

def test_fake_impersonation_message(detector):
    result = detector.analyze(
        "Dear Customer, your account has been suspended due to unusual activity. "
        "Please verify your identity immediately."
    )
    assert result.message_type == "Suspicious/Fake"
    assert result.risk_level in ("Medium", "High")


def test_security_alert_is_fake(detector):
    result = detector.analyze("Security alert: we noticed unusual activity on your account. Confirm your details now.")
    assert result.message_type == "Suspicious/Fake"


def test_dear_valued_customer_is_flagged(detector):
    result = detector.analyze("Dear valued customer, please update your information to avoid suspension.")
    assert result.message_type == "Suspicious/Fake"
    assert len(result.reasons) > 0


# ---------------------------------------------------------------------------
# Scam detection
# ---------------------------------------------------------------------------

def test_scam_message_high_risk(detector):
    result = detector.analyze(
        "URGENT: You have won the lottery! Send your bank details and OTP to claim your prize. "
        "Wire transfer required. This is confidential."
    )
    assert result.message_type == "Potential Scam"
    assert result.risk_level == "High"


def test_otp_request_is_scam(detector):
    result = detector.analyze("Please share your OTP to complete the transaction.")
    assert result.message_type == "Potential Scam"


def test_gift_card_request_is_scam(detector):
    result = detector.analyze("You owe back taxes. Buy iTunes gift cards and call us immediately.")
    assert result.message_type == "Potential Scam"


def test_suspicious_shortlink_is_detected(detector):
    result = detector.analyze("Click here to claim your reward: https://bit.ly/abc123")
    assert any("bit.ly" in r for r in result.reasons)


def test_generic_url_is_flagged(detector):
    result = detector.analyze("Please click https://verify-now.example.com/login to confirm.")
    assert any("http" in r for r in result.reasons)


# ---------------------------------------------------------------------------
# Risk level thresholds
# ---------------------------------------------------------------------------

def test_zero_indicators_is_low_risk(detector):
    result = detector.analyze("The weather is nice today.")
    assert result.risk_level == "Low"


def test_one_indicator_is_medium_risk(detector):
    """One spam keyword should give Medium risk."""
    result = detector.analyze("You can earn money with our program.")
    # "earn money" is 1 keyword → Medium
    assert result.risk_level in ("Medium", "High")


def test_three_plus_indicators_is_high_risk(detector):
    """Multiple scam + spam keywords should give High risk."""
    result = detector.analyze(
        "Urgent! You have won a lottery. Send your credit card number and OTP. "
        "Western Union wire transfer required. Gift card payment accepted."
    )
    assert result.risk_level == "High"


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

def test_analyze_returns_analysis_result(detector):
    result = detector.analyze("Test message.")
    assert isinstance(result, AnalysisResult)


def test_timestamp_is_set(detector):
    result = detector.analyze("Test message.")
    assert result.timestamp != ""
    assert len(result.timestamp) == len("2024-06-01 12:00:00")
