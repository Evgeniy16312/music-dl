from __future__ import annotations

import os
import signal
import sys
import threading

_cancel_requested = threading.Event()


def install_cancel_handlers() -> None:
    def on_cancel(signum, frame) -> None:
        if _cancel_requested.is_set():
            sys.stderr.write("\nПринудительный выход.\n")
            os._exit(130)
        _cancel_requested.set()
        sys.stderr.write(
            "\nОстановка... (Ctrl+C ещё раз — выйти сразу, без ожидания)\n"
        )

    signal.signal(signal.SIGINT, on_cancel)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, on_cancel)


def is_cancel_requested() -> bool:
    return _cancel_requested.is_set()


def raise_if_cancelled() -> None:
    if _cancel_requested.is_set():
        raise KeyboardInterrupt
