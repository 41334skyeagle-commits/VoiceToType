"""Single-instance coordination and wake-up signaling."""

from __future__ import annotations

import socket
import threading
from typing import Callable


class SingleInstanceManager:
    """Ensure only one app instance; notify running instance to show window."""

    def __init__(self, host: str = "127.0.0.1", port: int = 47653) -> None:
        self.host = host
        self.port = port
        self._server_socket: socket.socket | None = None
        self._thread: threading.Thread | None = None

    def try_acquire(self) -> bool:
        """Try to become primary process. Returns True when lock acquired."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
            sock.listen(5)
            self._server_socket = sock
            return True
        except OSError:
            sock.close()
            return False

    def notify_existing_instance(self) -> None:
        """Send wake-up message to existing app instance."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(1.0)
            client.connect((self.host, self.port))
            client.sendall(b"SHOW_WINDOW")

    def start_listener(self, on_show_window: Callable[[], None]) -> None:
        """Start listener thread to receive wake-up signal."""
        if self._server_socket is None:
            return

        def _worker() -> None:
            while self._server_socket is not None:
                try:
                    conn, _ = self._server_socket.accept()
                except OSError:
                    break
                with conn:
                    try:
                        data = conn.recv(1024)
                    except OSError:
                        continue
                    if data == b"SHOW_WINDOW":
                        on_show_window()

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def close(self) -> None:
        """Release socket resources."""
        if self._server_socket is not None:
            self._server_socket.close()
            self._server_socket = None
