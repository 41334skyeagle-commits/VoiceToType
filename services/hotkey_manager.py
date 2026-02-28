"""Global hotkey listener using pynput."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Callable

from pynput import keyboard


class HotkeyError(Exception):
    """Raised when the provided hotkey is invalid."""


@dataclass
class HotkeyConfig:
    """Current hotkey metadata."""

    raw_value: str = "right alt"


class HotkeyManager:
    """Monitors global key presses and triggers callback on single key-down events."""

    KEY_ALIASES = {
        "right alt": keyboard.Key.alt_gr,
        "alt gr": keyboard.Key.alt_gr,
        "altgr": keyboard.Key.alt_gr,
        "alt_r": keyboard.Key.alt_gr,
        "f8": keyboard.Key.f8,
        "f9": keyboard.Key.f9,
        "f10": keyboard.Key.f10,
        "f11": keyboard.Key.f11,
        "f12": keyboard.Key.f12,
    }

    def __init__(self, on_toggle: Callable[[], None], config: HotkeyConfig | None = None) -> None:
        self.on_toggle = on_toggle
        self.config = config or HotkeyConfig()
        self._target_key = self._resolve_key(self.config.raw_value)
        self._listener: keyboard.Listener | None = None
        self._is_pressed = False
        self._lock = Lock()

    def start(self) -> None:
        """Start the global key listener."""
        if self._listener is not None:
            return
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def stop(self) -> None:
        """Stop the global key listener."""
        if self._listener is None:
            return
        self._listener.stop()
        self._listener = None

    def set_hotkey(self, hotkey_text: str) -> None:
        """Update hotkey definition at runtime."""
        key = self._resolve_key(hotkey_text)
        with self._lock:
            self._target_key = key
            self.config.raw_value = hotkey_text.strip().lower()
            self._is_pressed = False

    def _resolve_key(self, hotkey_text: str):
        normalized = hotkey_text.strip().lower()
        if normalized in self.KEY_ALIASES:
            return self.KEY_ALIASES[normalized]

        if len(normalized) == 1:
            return keyboard.KeyCode.from_char(normalized)

        raise HotkeyError(
            "Unsupported hotkey. Try: right alt, f8-f12, or a single keyboard character."
        )

    def _on_press(self, key) -> None:  # noqa: ANN001
        with self._lock:
            if key == self._target_key and not self._is_pressed:
                self._is_pressed = True
                self.on_toggle()

    def _on_release(self, key) -> None:  # noqa: ANN001
        with self._lock:
            if key == self._target_key:
                self._is_pressed = False
