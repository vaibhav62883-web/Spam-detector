"""
advisor.py
----------
Maps each message type to a short list of practical safety tips.
Keeping advice separate from detection makes both easier to maintain.
"""

from __future__ import annotations


class SafetyAdvisor:
    """
    Returns safety advice based on the detected message type.

    Usage
    -----
    >>> advisor = SafetyAdvisor()
    >>> advisor.get_advice("Spam")
    ['Do not click any links in this message', ...]
    """

    # Internal lookup: message type → list of advice strings.
    _ADVICE: dict[str, list[str]] = {
        "Safe": [],

        "Spam": [
            "Do not click any links in this message.",
            "Mark the message as spam in your email or messaging app.",
            "Do not reply or click 'unsubscribe' — it confirms your address is active.",
            "Block the sender if the messages persist.",
        ],

        "Suspicious/Fake": [
            "Do NOT enter your password, OTP, or personal details via any link in this message.",
            "Go directly to the official website by typing the address yourself — do not click links.",
            "Contact the real organisation through their official phone number or website to verify.",
            "Legitimate companies never ask you to 'confirm' sensitive details by email or SMS.",
            "Check the sender's email address carefully for slight misspellings.",
        ],

        "Potential Scam": [
            "Never send money, gift cards, or cryptocurrency to someone you haven't met in person.",
            "Do NOT share your bank details, card numbers, CVV, PIN, or OTP with anyone.",
            "No legitimate lottery, government body, or business asks for an upfront fee.",
            "If someone threatens legal action or arrest over a message, it is almost certainly a scam.",
            "Report this message to your local consumer protection authority or cybercrime helpline.",
            "If in doubt, talk to a trusted friend, family member, or your bank before acting.",
        ],
    }

    def get_advice(self, message_type: str) -> list[str]:
        """
        Return safety tips for the given message type.

        Parameters
        ----------
        message_type : str
            One of "Safe", "Spam", "Suspicious/Fake", or "Potential Scam".

        Returns
        -------
        list[str]
            A list of advice strings, or an empty list if the type is unknown.
        """
        return self._ADVICE.get(message_type, [])
