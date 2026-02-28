"""OpenAI API integration for transcription and text polishing."""

from __future__ import annotations

import os
from pathlib import Path

from openai import OpenAI


class OpenAIServiceError(Exception):
    """Raised when OpenAI operations fail."""


class OpenAIService:
    """Handles Whisper transcription and GPT text optimization."""

    def __init__(self, api_key: str | None = None) -> None:
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured in environment variables.")
        self.client = OpenAI(api_key=resolved_key)

    def transcribe_audio(self, audio_path: Path) -> str:
        """Send WAV audio to whisper-1 and return plain text."""
        try:
            with audio_path.open("rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh",
                )
            return response.text.strip()
        except Exception as exc:
            raise OpenAIServiceError("Whisper API transcription failed.") from exc

    def polish_text(self, raw_text: str) -> str:
        """Use GPT-4o-mini to remove filler words while keeping meaning."""
        if not raw_text.strip():
            return ""

        system_prompt = (
            "你是中文文本整理助手。\n"
            "請將使用者提供的語音轉文字結果整理成自然、精簡、可直接貼上的繁體中文。\n"
            "規則：\n"
            "1) 移除口語贅詞與重複語句。\n"
            "2) 保留原始語意，不得新增新資訊。\n"
            "3) 若原文已清楚，僅做最小必要修飾。\n"
        )

        try:
            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_text},
                ],
            )
            return response.output_text.strip()
        except Exception as exc:
            raise OpenAIServiceError("GPT text optimization failed.") from exc
