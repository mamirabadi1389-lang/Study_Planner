"""Desktop entry point: Flask running inside a native window."""
from __future__ import annotations

import ctypes
import logging
import os
import socket
import sys
import threading
import time
import urllib.request
from ctypes import wintypes
from pathlib import Path

# A windowed (no console) build has no stdout/stderr: give them a sink.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import webview  # noqa: E402
from flask import Flask  # noqa: E402

from app import create_app  # noqa: E402

HOST = "127.0.0.1"
TITLE = "پلنر"
APP_ID = "StudyPlanner.App"

WM_SETICON = 0x0080
ICON_SMALL, ICON_BIG = 0, 1
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x0010
SM_CXICON, SM_CXSMICON = 11, 49


def _free_port() -> int:
    """Ask the OS for an unused local port."""
    with socket.socket() as sock:
        sock.bind((HOST, 0))
        return sock.getsockname()[1]


def _serve(app: Flask, port: int) -> None:
    app.run(host=HOST, port=port, debug=False, use_reloader=False)


def _wait_until_up(url: str, timeout: float = 10.0) -> None:
    """Block until the server answers (or the timeout passes)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except OSError:
            time.sleep(0.1)


def _set_app_id() -> None:
    """Make Windows group the taskbar button under our own icon."""
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)


def _apply_icon(icon: Path, timeout: float = 10.0) -> None:
    """Put the logo on the window title bar and the taskbar (Windows)."""
    if sys.platform != "win32" or not icon.exists():
        return
    user32 = ctypes.windll.user32
    user32.FindWindowW.restype = wintypes.HWND
    user32.FindWindowW.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR)
    user32.LoadImageW.restype = wintypes.HANDLE
    user32.LoadImageW.argtypes = (
        wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
        ctypes.c_int, ctypes.c_int, wintypes.UINT,
    )
    user32.SendMessageW.restype = wintypes.LPARAM
    user32.SendMessageW.argtypes = (
        wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
    )

    hwnd = None
    deadline = time.time() + timeout
    while time.time() < deadline:
        hwnd = user32.FindWindowW(None, TITLE)
        if hwnd:
            break
        time.sleep(0.1)
    if not hwnd:
        return

    sizes = (
        (ICON_SMALL, user32.GetSystemMetrics(SM_CXSMICON)),
        (ICON_BIG, user32.GetSystemMetrics(SM_CXICON)),
    )
    for kind, size in sizes:
        handle = user32.LoadImageW(
            None, str(icon), IMAGE_ICON, size, size, LR_LOADFROMFILE
        )
        if handle:
            user32.SendMessageW(hwnd, WM_SETICON, kind, handle)


def main() -> None:
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    flask_app = create_app()
    icon = Path(flask_app.root_path) / "static" / "img" / "logo.ico"

    port = _free_port()
    url = f"http://{HOST}:{port}"
    threading.Thread(target=_serve, args=(flask_app, port), daemon=True).start()
    _wait_until_up(url)

    _set_app_id()
    webview.create_window(
        TITLE, url, width=1280, height=800, min_size=(960, 640)
    )
    webview.start(_apply_icon, (icon,))


if __name__ == "__main__":
    main()