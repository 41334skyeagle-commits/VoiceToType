"""Entry point for the VoiceToType desktop application."""

from tkinter import Tk

from ui.main_window import VoiceToTypeApp


def main() -> None:
    root = Tk()
    VoiceToTypeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
