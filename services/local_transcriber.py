"""Local Whisper transcription service (offline, no cloud API)."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock

import whisper


class LocalTranscriberError(Exception):
    """Raised when local Whisper transcription fails."""


# Global singleton state: keep one base model in memory for faster repeated usage.
_MODEL = None
_MODEL_LOCK = Lock()
_MODEL_NAME = "base"


def _resolve_model_dir() -> Path:
    """Read model directory from runtime env set by runtime_patch."""
    configured = os.getenv("WHISPER_MODEL_DIR", "whisper_model")
    return Path(configured)


def _get_model():
    """Load Whisper base model lazily on first use from bundled model directory."""
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                model_dir = _resolve_model_dir()
                model_dir.mkdir(parents=True, exist_ok=True)
                # Use local model directory (whisper_model/) so EXE is self-contained.
                _MODEL = whisper.load_model(_MODEL_NAME, download_root=str(model_dir))
    return _MODEL


def preload_model(model_dir: Path | None = None) -> None:
    """Warm up model loading at app startup to fail fast on packaging issues."""
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is not None:
            return
        resolved = model_dir or _resolve_model_dir()
        resolved.mkdir(parents=True, exist_ok=True)
        _MODEL = whisper.load_model(_MODEL_NAME, download_root=str(resolved))


def transcribe(path: Path) -> str:
    """Transcribe a WAV file with local Whisper and return text."""
    try:
        model = _get_model()
        result = model.transcribe(str(path), language="zh", fp16=False)
        return str(result.get("text", "")).strip()
    except Exception as exc:
        raise LocalTranscriberError("Local Whisper transcription failed.") from exc
