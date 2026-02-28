"""History storage manager for transcript records."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class HistoryEntry:
    """Single history record."""

    timestamp: str
    text: str


class HistoryManager:
    """Manage JSON-based history with CRUD-style helpers."""

    def __init__(self, history_file: Path | None = None, max_entries: int = 100) -> None:
        default_path = Path.home() / ".voicetotype" / "history.json"
        self.history_file = history_file or default_path
        self.max_entries = max_entries
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> list[HistoryEntry]:
        """Load all entries from history.json."""
        if not self.history_file.exists():
            return []

        try:
            raw_data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return [HistoryEntry(**item) for item in raw_data]
        except Exception:
            return []

    def save_history(self, entries: list[HistoryEntry]) -> None:
        """Persist all entries back to history.json."""
        self.history_file.write_text(
            json.dumps([asdict(item) for item in entries], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_entry(self, text: str) -> HistoryEntry:
        """Insert a new entry at the top of history."""
        entries = self.load_history()
        entry = HistoryEntry(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text=text)
        entries.insert(0, entry)
        self.save_history(entries[: self.max_entries])
        return entry

    def delete_history_item(self, index: int) -> None:
        """Delete one entry by index in current list order."""
        entries = self.load_history()
        if index < 0 or index >= len(entries):
            raise IndexError("History index out of range.")
        del entries[index]
        self.save_history(entries)

    def delete_all_history(self) -> None:
        """Clear all history entries."""
        self.save_history([])
