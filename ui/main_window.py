"""Tkinter UI for VoiceToType desktop app."""

from __future__ import annotations

import threading
from enum import Enum
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, VERTICAL, Button, Canvas, Entry, Frame, Label, Scrollbar, StringVar, Text, Tk, messagebox

from pynput import keyboard

from audio.recorder import AudioRecorder, AudioRecorderError
from services.clipboard_service import ClipboardService
from services.history_manager import HistoryManager
from services.hotkey_manager import HotkeyError, HotkeyManager
from services.local_transcriber import LocalTranscriberError, transcribe
from services.text_cleaner import clean_text


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
        self.root.geometry("820x580")

        self.status_var = StringVar(value=AppStatus.IDLE.value)
        self.hotkey_var = StringVar(value="right alt")

        self.recorder = AudioRecorder()
        self.history_manager = HistoryManager()

        self.hotkey_manager = HotkeyManager(on_toggle=self.on_hotkey_toggle)
        self.hotkey_manager.start()

        # Global hotkey for quickly showing the app window.
        self.wake_hotkey = keyboard.GlobalHotKeys({"<ctrl>+<alt>+w": self._handle_wake_hotkey})
        self.wake_hotkey.start()

        self._build_layout()
        self._load_history()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start minimized to taskbar as requested.
        self.root.after(200, self.minimize_window)

    def _build_layout(self) -> None:
        top_bar = Frame(self.root)
        top_bar.pack(fill="x", padx=12, pady=8)

        Label(top_bar, text="目前狀態：").pack(side=LEFT)
        Label(top_bar, textvariable=self.status_var, fg="#0f4c81").pack(side=LEFT)

        controls = Frame(self.root)
        controls.pack(fill="x", padx=12, pady=6)

        Label(controls, text="錄音快捷鍵：").pack(side=LEFT)
        self.hotkey_entry = Entry(controls, textvariable=self.hotkey_var, width=14)
        self.hotkey_entry.pack(side=LEFT, padx=4)
        Button(controls, text="套用快捷鍵", command=self.apply_hotkey).pack(side=LEFT, padx=4)
        Button(controls, text="開始 / 停止錄音", command=self.on_hotkey_toggle).pack(side=LEFT, padx=4)
        Button(controls, text="最小化", command=self.minimize_window).pack(side=LEFT, padx=4)
        Button(controls, text="喚醒視窗", command=self.show_window).pack(side=LEFT, padx=4)

        result_panel = Frame(self.root)
        result_panel.pack(fill=BOTH, expand=True, padx=12, pady=8)

        Label(result_panel, text="最新結果（已自動複製到剪貼簿）").pack(anchor="w")
        self.result_text = Text(result_panel, height=10, wrap="word")
        self.result_text.pack(fill=BOTH, expand=False, pady=4)

        history_row = Frame(result_panel)
        history_row.pack(fill=BOTH, expand=True, pady=6)

        header = Frame(history_row)
        header.pack(fill="x")
        Label(header, text="歷史紀錄").pack(side=LEFT)
        Button(header, text="清空歷史", command=self.clear_all_history).pack(side=RIGHT)

        # Scrollable history rows: each row contains text + delete button.
        list_frame = Frame(history_row)
        list_frame.pack(fill=BOTH, expand=True)

        self.history_canvas = Canvas(list_frame, borderwidth=0)
        self.history_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.history_canvas.yview)
        scrollbar.pack(side=RIGHT, fill="y")
        self.history_canvas.configure(yscrollcommand=scrollbar.set)

        self.history_rows_frame = Frame(self.history_canvas)
        self.history_window = self.history_canvas.create_window((0, 0), window=self.history_rows_frame, anchor="nw")

        self.history_rows_frame.bind("<Configure>", self._on_history_frame_configure)
        self.history_canvas.bind("<Configure>", self._on_history_canvas_configure)

    def _on_history_frame_configure(self, _event) -> None:  # noqa: ANN001
        self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))

    def _on_history_canvas_configure(self, event) -> None:  # noqa: ANN001
        self.history_canvas.itemconfigure(self.history_window, width=event.width)

    def _load_history(self) -> None:
        for child in self.history_rows_frame.winfo_children():
            child.destroy()

        entries = self.history_manager.load_history()
        if not entries:
            Label(self.history_rows_frame, text="（目前尚無歷史紀錄）", fg="#666").pack(anchor="w", padx=4, pady=4)
            return

        for index, entry in enumerate(entries):
            row = Frame(self.history_rows_frame)
            row.pack(fill="x", padx=2, pady=2)

            text_preview = f"[{entry.timestamp}] {entry.text}"
            Label(row, text=text_preview, anchor="w", justify="left", wraplength=640).pack(side=LEFT, fill="x", expand=True)
            Button(row, text="刪除", command=lambda i=index: self.delete_history_item(i)).pack(side=RIGHT, padx=4)

    def apply_hotkey(self) -> None:
        try:
            self.hotkey_manager.set_hotkey(self.hotkey_var.get())
            messagebox.showinfo("快捷鍵更新", "新的錄音全域快捷鍵已套用。")
        except HotkeyError as exc:
            messagebox.showerror("快捷鍵格式錯誤", str(exc))

    def _handle_wake_hotkey(self) -> None:
        # Callback runs in listener thread; marshal back into Tk event loop.
        self.root.after(0, self.show_window)

    def show_window(self) -> None:
        """Show and focus app window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def minimize_window(self) -> None:
        """Minimize app window to taskbar."""
        self.root.iconify()

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
            raw_text = transcribe(audio_path)
            polished_text = clean_text(raw_text)
            ClipboardService.copy_text(polished_text)
            self.history_manager.add_entry(polished_text)
            self.root.after(0, lambda: self._update_result(polished_text, AppStatus.DONE))
        except LocalTranscriberError as exc:
            self.root.after(0, lambda: self._show_processing_error(f"本機語音辨識失敗：{exc}"))
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

    def delete_history_item(self, index: int) -> None:
        """Delete one history item and refresh list."""
        try:
            self.history_manager.delete_history_item(index)
            self._load_history()
            messagebox.showinfo("歷史紀錄", "已刪除該筆歷史紀錄。")
        except IndexError:
            messagebox.showerror("歷史紀錄", "刪除失敗：找不到該筆歷史紀錄。")

    def clear_all_history(self) -> None:
        """Clear all history after user confirmation."""
        confirmed = messagebox.askyesno("清空歷史", "確定要清空全部歷史紀錄嗎？此動作無法復原。")
        if not confirmed:
            return

        self.history_manager.delete_all_history()
        self._load_history()
        messagebox.showinfo("歷史紀錄", "已清空全部歷史紀錄。")

    def _show_processing_error(self, error_message: str) -> None:
        self.status_var.set(AppStatus.ERROR.value)
        messagebox.showerror("語音處理錯誤", error_message)

    def on_close(self) -> None:
        self.hotkey_manager.stop()
        self.wake_hotkey.stop()
        self.root.destroy()
