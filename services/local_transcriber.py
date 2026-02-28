"""Local Whisper transcription service (offline, no cloud API)."""

from __future__ import annotations

from pathlib import Path
from threading import Lock

import whisper


class LocalTranscriberError(Exception):
    """Raised when local Whisper transcription fails."""


# Global singleton state: keep one base model in memory for faster repeated usage.
_MODEL = None
_MODEL_LOCK = Lock()


def _get_model():
    """Load Whisper base model lazily on first use."""
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                # base model is a good balance for laptop CPU usage.
                _MODEL = whisper.load_model("base")
    return _MODEL


def transcribe(path: Path) -> str:
    """Transcribe a WAV file with local Whisper and return text."""
    try:
        model = _get_model()
        result = model.transcribe(str(path), language="zh", fp16=False)
        return str(result.get("text", "")).strip()
    except Exception as exc:
        raise LocalTranscriberError("Local Whisper transcription failed.") from exc
