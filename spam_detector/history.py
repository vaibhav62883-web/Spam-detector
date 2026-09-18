"""
history.py
----------
Persists analysis history to a local JSON file.
History is capped at 20 entries (most recent kept).

No Streamlit imports — pure Python file I/O.
"""

from __future__ import annotations

import json
import os

from models import AnalysisResult, HistoryEntry

MAX_ENTRIES: int = 20


class HistoryManager:
    """
    Reads and writes analysis history to a JSON file on disk.

    Usage
    -----
    >>> hm = HistoryManager()
    >>> hm.add_entry(result)
    >>> entries = hm.get_history()   # newest first
    >>> hm.clear_history()
    """

    def __init__(self, filepath: str = "history.json") -> None:
        """
        Parameters
        ----------
        filepath : str
            Path to the JSON file.  Defaults to "history.json" next to app.py.
            Override in tests to use a temporary path.
        """
        self.filepath = filepath

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_entry(self, result: AnalysisResult) -> None:
        """
        Append a new history entry derived from *result*, then trim to the
        most recent MAX_ENTRIES and save.

        Parameters
        ----------
        result : AnalysisResult
            The result object returned by MessageDetector.analyze().
        """
        entry = HistoryEntry(
            message_preview=result.original_message[:60],
            risk_level=result.risk_level,
            message_type=result.message_type,
            timestamp=result.timestamp,
        )

        entries = self._load()
        entries.append(entry.to_dict())

        # Keep only the most recent MAX_ENTRIES
        if len(entries) > MAX_ENTRIES:
            entries = entries[-MAX_ENTRIES:]

        self._save(entries)

    def get_history(self) -> list[HistoryEntry]:
        """
        Return history entries with the newest first.

        Returns
        -------
        list[HistoryEntry]
            May be empty if no entries have been saved yet.
        """
        raw = self._load()
        entries = [HistoryEntry.from_dict(d) for d in raw]
        return list(reversed(entries))   # newest first

    def clear_history(self) -> None:
        """Delete all saved history entries."""
        self._save([])

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> list[dict]:
        """
        Read the JSON file and return its contents as a list of dicts.
        Returns an empty list when the file does not exist or is malformed.
        """
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            # Malformed file or permission error — start fresh silently.
            return []

    def _save(self, entries: list[dict]) -> None:
        """
        Write *entries* to the JSON file, creating it if necessary.

        Parameters
        ----------
        entries : list[dict]
            The full list to persist (already trimmed to MAX_ENTRIES).
        """
        try:
            with open(self.filepath, "w", encoding="utf-8") as fh:
                json.dump(entries, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            # Surface the error as a plain Python exception so app.py can
            # catch it and show a friendly warning instead of crashing.
            raise OSError(f"Could not save history: {exc}") from exc
