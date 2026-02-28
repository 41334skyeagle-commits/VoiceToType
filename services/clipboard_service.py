"""Clipboard helper wrapper."""

from __future__ import annotations

import pyperclip


class ClipboardService:
    """Copy text to system clipboard."""

    @staticmethod
    def copy_text(text: str) -> None:
        pyperclip.copy(text)
