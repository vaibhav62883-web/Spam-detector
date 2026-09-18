"""
tests/test_history.py
---------------------
Tests for HistoryManager — file creation, ordering, cap, and clear.

Uses pytest's tmp_path fixture so no real files are written during testing.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from history import HistoryManager, MAX_ENTRIES
from models import AnalysisResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_result(message: str = "Test message", risk: str = "Low", msg_type: str = "Safe") -> AnalysisResult:
    return AnalysisResult(
        original_message=message,
        risk_level=risk,
        message_type=msg_type,
        reasons=[],
        advice=[],
        timestamp="2024-06-01 12:00:00",
    )


def make_manager(tmp_path) -> HistoryManager:
    """Return a HistoryManager backed by a temp file path."""
    hm = HistoryManager(filepath=str(tmp_path / "history.json"))
    return hm


# ---------------------------------------------------------------------------
# File creation
# ---------------------------------------------------------------------------

def test_add_entry_creates_file(tmp_path):
    hm = make_manager(tmp_path)
    assert not os.path.exists(hm.filepath)
    hm.add_entry(make_result())
    assert os.path.exists(hm.filepath)


def test_get_history_on_missing_file_returns_empty(tmp_path):
    hm = make_manager(tmp_path)
    assert hm.get_history() == []


# ---------------------------------------------------------------------------
# Add and retrieve
# ---------------------------------------------------------------------------

def test_single_entry_is_stored_and_retrieved(tmp_path):
    hm = make_manager(tmp_path)
    hm.add_entry(make_result("Hello world", risk="Low", msg_type="Safe"))
    entries = hm.get_history()
    assert len(entries) == 1
    assert entries[0].message_preview == "Hello world"
    assert entries[0].risk_level == "Low"
    assert entries[0].message_type == "Safe"


def test_multiple_entries_newest_first(tmp_path):
    hm = make_manager(tmp_path)
    hm.add_entry(make_result("First message"))
    hm.add_entry(make_result("Second message"))
    hm.add_entry(make_result("Third message"))

    entries = hm.get_history()
    assert entries[0].message_preview == "Third message"
    assert entries[1].message_preview == "Second message"
    assert entries[2].message_preview == "First message"


# ---------------------------------------------------------------------------
# Cap enforcement
# ---------------------------------------------------------------------------

def test_history_capped_at_max_entries(tmp_path):
    hm = make_manager(tmp_path)
    for i in range(MAX_ENTRIES + 1):
        hm.add_entry(make_result(f"Message number {i}"))

    entries = hm.get_history()
    assert len(entries) == MAX_ENTRIES


def test_oldest_entry_is_dropped_when_cap_exceeded(tmp_path):
    hm = make_manager(tmp_path)
    hm.add_entry(make_result("oldest"))
    for i in range(MAX_ENTRIES):
        hm.add_entry(make_result(f"newer {i}"))

    entries = hm.get_history()
    previews = [e.message_preview for e in entries]
    assert "oldest" not in previews


# ---------------------------------------------------------------------------
# Clear
# ---------------------------------------------------------------------------

def test_clear_history_empties_list(tmp_path):
    hm = make_manager(tmp_path)
    hm.add_entry(make_result("Something"))
    hm.clear_history()
    assert hm.get_history() == []


def test_clear_on_empty_history_does_not_raise(tmp_path):
    hm = make_manager(tmp_path)
    hm.clear_history()       # no file exists yet — should not raise
    assert hm.get_history() == []


# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------

def test_malformed_json_returns_empty_history(tmp_path):
    filepath = str(tmp_path / "history.json")
    with open(filepath, "w") as fh:
        fh.write("this is not valid json {{{{")
    hm = HistoryManager(filepath=filepath)
    assert hm.get_history() == []


def test_message_preview_truncated_to_60_chars(tmp_path):
    hm = make_manager(tmp_path)
    long_message = "A" * 120
    hm.add_entry(make_result(long_message))
    entry = hm.get_history()[0]
    assert len(entry.message_preview) == 60
