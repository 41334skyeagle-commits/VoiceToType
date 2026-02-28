"""Audio recording utilities for the VoiceToType desktop app."""

from __future__ import annotations

import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import List

import numpy as np
import sounddevice as sd


class AudioRecorderError(Exception):
    """Raised when audio recording cannot continue."""


@dataclass(frozen=True)
class RecordingConfig:
    """Simple audio settings used by the recorder."""

    sample_rate: int = 16000
    channels: int = 1
    dtype: str = "int16"


class AudioRecorder:
    """Stream-based recorder that writes microphone input to a WAV temp file."""

    def __init__(self, config: RecordingConfig | None = None) -> None:
        self.config = config or RecordingConfig()
        self._frames: List[np.ndarray] = []
        self._lock = Lock()
        self._stream: sd.InputStream | None = None
        self._is_recording = False

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start(self) -> None:
        """Start capturing microphone frames."""
        if self._is_recording:
            raise AudioRecorderError("Recorder is already running.")

        self._frames = []

        try:
            self._stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=self.config.dtype,
                callback=self._on_audio_callback,
            )
            self._stream.start()
            self._is_recording = True
        except Exception as exc:  # pragma: no cover - hardware dependent
            self._stream = None
            self._is_recording = False
            raise AudioRecorderError("Unable to access microphone.") from exc

    def stop_and_save(self) -> Path:
        """Stop recording and save the captured audio into a temp WAV file."""
        if not self._is_recording or self._stream is None:
            raise AudioRecorderError("Recorder is not running.")

        self._stream.stop()
        self._stream.close()
        self._stream = None
        self._is_recording = False

        with self._lock:
            if not self._frames:
                raise AudioRecorderError("No audio data was captured.")
            audio_data = np.concatenate(self._frames, axis=0)

        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = Path(temp_file.name)
        temp_file.close()

        with wave.open(str(temp_path), "wb") as wav_file:
            wav_file.setnchannels(self.config.channels)
            wav_file.setsampwidth(np.dtype(self.config.dtype).itemsize)
            wav_file.setframerate(self.config.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        return temp_path

    def _on_audio_callback(self, indata, frames, time, status) -> None:  # noqa: ANN001
        """Collect each audio chunk from the sounddevice callback."""
        if status:  # pragma: no cover - depends on audio hardware behavior
            return
        with self._lock:
            self._frames.append(indata.copy())
