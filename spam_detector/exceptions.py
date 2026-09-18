"""
exceptions.py
-------------
Custom exceptions for bad user input.
Caught in app.py and shown as friendly warnings — never raw tracebacks.
"""


class EmptyMessageError(Exception):
    """Raised when the user submits an empty or whitespace-only message."""

    def __init__(self, message: str = "Message cannot be empty.") -> None:
        super().__init__(message)


class MessageTooLongError(Exception):
    """Raised when the message exceeds the maximum allowed length."""

    def __init__(self, message: str = "Message is too long (maximum 2000 characters).") -> None:
        super().__init__(message)
