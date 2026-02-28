"""Runtime environment patching for packaged EXE execution."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import imageio_ffmpeg


def get_resource_base_dir() -> Path:
    """Return resource base for source run and PyInstaller (_MEIPASS) run."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def get_whisper_model_dir() -> Path:
    """Resolve whisper_model folder and ensure it exists."""
    model_dir = get_resource_base_dir() / "whisper_model"
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir


def patch_runtime_environment() -> Path:
    """Patch PATH and env vars so EXE can locate ffmpeg and local Whisper model."""
    model_dir = get_whisper_model_dir()
    os.environ["WHISPER_MODEL_DIR"] = str(model_dir)

    # Ensure FFmpeg binary from imageio-ffmpeg is available in PATH.
    ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    ffmpeg_dir = str(ffmpeg_exe.parent)
    current_path = os.environ.get("PATH", "")
    if ffmpeg_dir not in current_path.split(os.pathsep):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path

    return model_dir
