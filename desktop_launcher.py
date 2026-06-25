import os
import socket
import sys
import threading
import time
from pathlib import Path

import webview
from waitress import serve


HOST = "localhost"
PORT = 8000


def wait_for_port(host: str, port: int, timeout: float = 20.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket() as sock:
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.1)
    return False

 
def start_server() -> None:
    serve(application, host=HOST, port=PORT)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    if getattr(sys, "frozen", False):
        base_dir = Path(getattr(sys, "_MEIPASS", base_dir))

    sys.path.insert(0, str(base_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

    from myproject.wsgi import application

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    if not wait_for_port(HOST, PORT):
        raise RuntimeError("Django server failed to start.")

    webview.create_window("KICCD", f"http://{HOST}:{PORT}")
    webview.start()
