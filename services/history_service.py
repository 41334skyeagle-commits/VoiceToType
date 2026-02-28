"""Local history persistence for transcription results."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass
class HistoryEntry:
    """A single conversion record shown in the UI and saved locally."""

    timestamp: str
    text: str


class HistoryService:
    """Manages JSON-based history stored in the user's home folder."""

    def __init__(self, history_file: Path | None = None, max_entries: int = 100) -> None:
        default_path = Path.home() / ".voicetotype" / "history.json"
        self.history_file = history_file or default_path
        self.max_entries = max_entries
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> List[HistoryEntry]:
        if not self.history_file.exists():
            return []

        try:
            raw_data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return [HistoryEntry(**item) for item in raw_data]
        except Exception:
            return []

    def add_entry(self, text: str) -> HistoryEntry:
        entries = self.load_history()
        entry = HistoryEntry(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text=text)
        entries.insert(0, entry)
        entries = entries[: self.max_entries]
        self.history_file.write_text(
            json.dumps([asdict(item) for item in entries], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return entry
