"""Tkinter UI for VoiceToType desktop app."""

from __future__ import annotations

import threading
from enum import Enum
from pathlib import Path
from tkinter import END, LEFT, RIGHT, Button, Entry, Frame, Label, Listbox, Scrollbar, StringVar, Text, Tk, messagebox

from audio.recorder import AudioRecorder, AudioRecorderError
from services.clipboard_service import ClipboardService
from services.history_service import HistoryService
from services.hotkey_manager import HotkeyError, HotkeyManager
from services.openai_service import OpenAIService, OpenAIServiceError


class AppStatus(str, Enum):
    IDLE = "待機"
    RECORDING = "錄音中"
    PROCESSING = "處理中"
    DONE = "完成"
    ERROR = "錯誤"


class VoiceToTypeApp:
    """Main application composition root."""

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("VoiceToType - 語音轉文字")
        self.root.geometry("760x520")

        self.status_var = StringVar(value=AppStatus.IDLE.value)
        self.hotkey_var = StringVar(value="right alt")

        self.recorder = AudioRecorder()
        self.history_service = HistoryService()

        try:
            self.openai_service = OpenAIService()
        except OpenAIServiceError as exc:
            self.openai_service = None
            self.status_var.set(AppStatus.ERROR.value)
            messagebox.showerror("API Key 設定錯誤", str(exc))

        self.hotkey_manager = HotkeyManager(on_toggle=self.on_hotkey_toggle)
        self.hotkey_manager.start()

        self._build_layout()
        self._load_history()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_layout(self) -> None:
        top_bar = Frame(self.root)
        top_bar.pack(fill="x", padx=12, pady=8)

        Label(top_bar, text="目前狀態：").pack(side=LEFT)
        Label(top_bar, textvariable=self.status_var, fg="#0f4c81").pack(side=LEFT)

        controls = Frame(self.root)
        controls.pack(fill="x", padx=12, pady=6)

        Label(controls, text="全域快捷鍵：").pack(side=LEFT)
        self.hotkey_entry = Entry(controls, textvariable=self.hotkey_var, width=14)
        self.hotkey_entry.pack(side=LEFT, padx=4)
        Button(controls, text="套用快捷鍵", command=self.apply_hotkey).pack(side=LEFT, padx=4)
        Button(controls, text="開始 / 停止錄音", command=self.on_hotkey_toggle).pack(side=LEFT, padx=4)

        result_panel = Frame(self.root)
        result_panel.pack(fill="both", expand=True, padx=12, pady=8)

        Label(result_panel, text="最新結果（已自動複製到剪貼簿）").pack(anchor="w")
        self.result_text = Text(result_panel, height=10, wrap="word")
        self.result_text.pack(fill="both", expand=False, pady=4)

        history_row = Frame(result_panel)
        history_row.pack(fill="both", expand=True, pady=6)

        Label(history_row, text="歷史紀錄").pack(anchor="w")
        list_frame = Frame(history_row)
        list_frame.pack(fill="both", expand=True)

        self.history_list = Listbox(list_frame)
        self.history_list.pack(side=LEFT, fill="both", expand=True)

        scrollbar = Scrollbar(list_frame, orient="vertical", command=self.history_list.yview)
        scrollbar.pack(side=RIGHT, fill="y")
        self.history_list.config(yscrollcommand=scrollbar.set)

    def _load_history(self) -> None:
        self.history_list.delete(0, END)
        for entry in self.history_service.load_history():
            self.history_list.insert(END, f"[{entry.timestamp}] {entry.text}")

    def apply_hotkey(self) -> None:
        try:
            self.hotkey_manager.set_hotkey(self.hotkey_var.get())
            messagebox.showinfo("快捷鍵更新", "新的全域快捷鍵已套用。")
        except HotkeyError as exc:
            messagebox.showerror("快捷鍵格式錯誤", str(exc))

    def on_hotkey_toggle(self) -> None:
        """Start recording on first press, stop and process on second press."""
        if self.recorder.is_recording:
            self._stop_recording_and_process()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        if self.status_var.get() == AppStatus.PROCESSING.value:
            return

        try:
            self.recorder.start()
            self.status_var.set(AppStatus.RECORDING.value)
        except AudioRecorderError as exc:
            self.status_var.set(AppStatus.ERROR.value)
            messagebox.showerror("錄音錯誤", f"無法開始錄音：{exc}")

    def _stop_recording_and_process(self) -> None:
        try:
            audio_path = self.recorder.stop_and_save()
        except AudioRecorderError as exc:
            self.status_var.set(AppStatus.ERROR.value)
            messagebox.showerror("錄音錯誤", f"無法停止錄音：{exc}")
            return

        self.status_var.set(AppStatus.PROCESSING.value)
        worker = threading.Thread(target=self._process_audio_worker, args=(audio_path,), daemon=True)
        worker.start()

    def _process_audio_worker(self, audio_path: Path) -> None:
        try:
            if not self.openai_service:
                raise OpenAIServiceError("OpenAI service is not initialized.")

            raw_text = self.openai_service.transcribe_audio(audio_path)
            polished_text = self.openai_service.polish_text(raw_text)
            ClipboardService.copy_text(polished_text)
            self.history_service.add_entry(polished_text)

            self.root.after(0, lambda: self._update_result(polished_text, AppStatus.DONE))
        except OpenAIServiceError as exc:
            self.root.after(0, lambda: self._show_processing_error(f"API 呼叫失敗：{exc}"))
        except Exception as exc:  # pragma: no cover - broad fallback for runtime safety
            self.root.after(0, lambda: self._show_processing_error(f"處理失敗：{exc}"))
        finally:
            if audio_path.exists():
                audio_path.unlink(missing_ok=True)

    def _update_result(self, text: str, status: AppStatus) -> None:
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", text)
        self._load_history()
        self.status_var.set(status.value)

    def _show_processing_error(self, error_message: str) -> None:
        self.status_var.set(AppStatus.ERROR.value)
        messagebox.showerror("語音處理錯誤", error_message)

    def on_close(self) -> None:
        self.hotkey_manager.stop()
        self.root.destroy()
