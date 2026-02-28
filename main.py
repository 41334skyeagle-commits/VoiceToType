"""Entry point for the VoiceToType desktop application."""

from __future__ import annotations

from tkinter import messagebox, Tk

from runtime_patch import patch_runtime_environment
from services.local_transcriber import LocalTranscriberError, preload_model
from services.single_instance import SingleInstanceManager
from ui.main_window import VoiceToTypeApp


def main() -> None:
    model_dir = patch_runtime_environment()

    instance_manager = SingleInstanceManager()
    if not instance_manager.try_acquire():
        # Already running: ask existing process to show window, then exit.
        try:
            instance_manager.notify_existing_instance()
        except OSError:
            pass
        return

    root = Tk()

    # Load model from local whisper_model folder at startup.
    try:
        preload_model(model_dir)
    except LocalTranscriberError:
        pass
    except Exception as exc:
        messagebox.showerror(
            "Whisper 模型載入失敗",
            "無法從本機 whisper_model 載入 base 模型。\n"
            "請確認打包時已包含 whisper_model/base.pt 與 ffmpeg 資源。\n"
            f"詳細錯誤：{exc}",
        )

    app = VoiceToTypeApp(root)

    # When another process instance starts, wake this window.
    instance_manager.start_listener(lambda: root.after(0, app.show_window))

    def _on_exit() -> None:
        instance_manager.close()
        app.on_close()

    root.protocol("WM_DELETE_WINDOW", _on_exit)
    root.mainloop()


if __name__ == "__main__":
    main()
