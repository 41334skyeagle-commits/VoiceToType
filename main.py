"""Entry point for the VoiceToType desktop application."""

from tkinter import Tk

from dotenv import load_dotenv

from ui.main_window import VoiceToTypeApp


def main() -> None:
    load_dotenv()
    root = Tk()
    VoiceToTypeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
