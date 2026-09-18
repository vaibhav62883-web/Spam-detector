"""
detector.py
-----------
Core analysis engine.  MessageDetector.analyze() is the single public entry
point.  It checks the message against three independent rule sets (spam, fake,
scam), combines the findings, and returns a fully-populated AnalysisResult.

No Streamlit, no file I/O, no safety advice — those live in other modules.
"""

from __future__ import annotations

import re
from datetime import datetime

from models import AnalysisResult
import rules


class MessageDetector:
    """
    Analyses a text message and returns an AnalysisResult.

    Usage
    -----
    >>> result = MessageDetector().analyze("Congratulations! You have won $1,000!")
    >>> print(result.risk_level, result.message_type)
    High Spam
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, message: str) -> AnalysisResult:
        """
        Run all checks on *message* and return a complete AnalysisResult.

        Parameters
        ----------
        message : str
            The raw text submitted by the user.

        Returns
        -------
        AnalysisResult
            Fully populated result object (advice list is left empty here;
            SafetyAdvisor fills it in app.py).
        """
        normalised = message.lower()

        spam_reasons  = self._check_spam(normalised, message)
        fake_reasons  = self._check_fake(normalised)
        scam_reasons  = self._check_scam(normalised, message)  # pass original for pattern matching

        all_reasons   = spam_reasons + fake_reasons + scam_reasons
        risk_level    = self._calculate_risk(all_reasons)
        message_type  = self._determine_type(spam_reasons, fake_reasons, scam_reasons)
        timestamp     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return AnalysisResult(
            original_message=message,
            risk_level=risk_level,
            message_type=message_type,
            reasons=all_reasons,
            advice=[],          # populated later by SafetyAdvisor
            timestamp=timestamp,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_spam(self, normalised: str, original: str) -> list[str]:
        """
        Check for spam keywords and formatting patterns.

        Parameters
        ----------
        normalised : str
            Lowercase version of the original message (used for keyword matching).
        original : str
            Raw original message (used for case-sensitive pattern matching).

        Returns
        -------
        list[str]
            Human-readable reasons describing what was found.
        """
        found: list[str] = []

        for keyword in rules.SPAM_KEYWORDS:
            if keyword in normalised:
                found.append(f"Spam keyword detected: '{keyword}'")

        for pattern in rules.SPAM_PATTERNS:
            # Run patterns on the original (not lowercased) string so that
            # the ALL-CAPS pattern only triggers on genuinely capitalised words,
            # and currency / punctuation patterns match correctly.
            match = re.search(pattern, original)
            if match:
                matched_text = match.group(0)[:30]   # truncate long matches
                found.append(f"Spam formatting pattern: '{matched_text}'")

        return found

    def _check_fake(self, normalised: str) -> list[str]:
        """
        Check for fake / impersonation indicators.

        Parameters
        ----------
        normalised : str
            Lowercase version of the original message.

        Returns
        -------
        list[str]
            Human-readable reasons describing what was found.
        """
        found: list[str] = []

        for keyword in rules.FAKE_KEYWORDS:
            if keyword in normalised:
                found.append(f"Impersonation phrase detected: '{keyword}'")

        for pattern in rules.FAKE_PATTERNS:
            match = re.search(pattern, normalised, re.IGNORECASE)
            if match:
                matched_text = match.group(0)[:30]
                found.append(f"Suspicious lookalike name detected: '{matched_text}'")

        return found

    def _check_scam(self, normalised: str, original: str) -> list[str]:
        """
        Check for scam keywords, patterns, and suspicious URLs.

        Parameters
        ----------
        normalised : str
            Lowercase version of the original message (for keyword matching).
        original : str
            The raw original message (for case-sensitive pattern matching).

        Returns
        -------
        list[str]
            Human-readable reasons describing what was found.
        """
        found: list[str] = []

        for keyword in rules.SCAM_KEYWORDS:
            if keyword in normalised:
                found.append(f"Scam keyword detected: '{keyword}'")

        for pattern in rules.SCAM_PATTERNS:
            match = re.search(pattern, original, re.IGNORECASE)
            if match:
                matched_text = match.group(0)[:40]
                found.append(f"Scam pattern detected: '{matched_text}'")

        # Check for any URL (generic suspicious link)
        url_matches = re.findall(rules.SUSPICIOUS_URL_PATTERN, original)
        for url in url_matches:
            found.append(f"Suspicious link found: '{url[:50]}'")

        return found

    def _calculate_risk(self, all_reasons: list[str]) -> str:
        """
        Map the total number of detected indicators to a risk level.

        0 indicators  → "Low"
        1–2 indicators → "Medium"
        3+  indicators → "High"

        Parameters
        ----------
        all_reasons : list[str]
            Combined list of reasons from all three checks.

        Returns
        -------
        str
            "Low", "Medium", or "High".
        """
        count = len(all_reasons)
        if count == 0:
            return "Low"
        if count <= 2:
            return "Medium"
        return "High"

    def _determine_type(
        self,
        spam_reasons: list[str],
        fake_reasons: list[str],
        scam_reasons: list[str],
    ) -> str:
        """
        Pick the message type label based on which category has the most hits.

        If all lists are empty → "Safe".
        On a tie, scam takes priority over fake, which takes priority over spam.

        Parameters
        ----------
        spam_reasons, fake_reasons, scam_reasons : list[str]
            Reasons from each individual check.

        Returns
        -------
        str
            "Safe", "Spam", "Suspicious/Fake", or "Potential Scam".
        """
        counts = {
            "Potential Scam":  len(scam_reasons),
            "Suspicious/Fake": len(fake_reasons),
            "Spam":            len(spam_reasons),
        }

        if all(v == 0 for v in counts.values()):
            return "Safe"

        # Return the type with the highest count (scam wins ties due to dict order)
        return max(counts, key=lambda k: counts[k])
