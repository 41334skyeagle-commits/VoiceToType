"""Rule-based local text cleaner for Mandarin speech-to-text output."""

from __future__ import annotations

import re

# Common filler/discourse words often produced in conversational speech.
FILLER_PATTERNS = [
    r"\b嗯+\b",
    r"\b呃+\b",
    r"\b啊+\b",
    r"\b喔+\b",
    r"\b齁+\b",
    r"\b就是\b",
    r"\b那個\b",
    r"\b然後\b",
    r"\b這個\b",
]


def clean_text(text: str) -> str:
    """Clean filler words and extra spaces while preserving the original meaning."""
    cleaned = text

    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned)

    # Collapse repeated punctuation created after filler removal.
    cleaned = re.sub(r"([，。！？；：,.!?;:])\1+", r"\1", cleaned)

    # Normalize all whitespace/newlines/tabs to single spaces.
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Remove leading/trailing punctuation-like separators and spaces.
    cleaned = cleaned.strip(" ，。！？；：,.!?;:\t\n\r")

    return cleaned
