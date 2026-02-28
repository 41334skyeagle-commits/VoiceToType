"""Entry point for the VoiceToType desktop application."""

from __future__ import annotations

from tkinter import Tk

from services.single_instance import SingleInstanceManager
from ui.main_window import VoiceToTypeApp


def main() -> None:
    instance_manager = SingleInstanceManager()
    if not instance_manager.try_acquire():
        # Already running: ask existing process to show window, then exit.
        try:
            instance_manager.notify_existing_instance()
        except OSError:
            pass
        return

    root = Tk()
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
