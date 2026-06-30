from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from music_dl.console import console
from music_dl.constants import (
    DEFAULT_FILENAME_TEMPLATE,
    DEFAULT_OUTPUT,
    DEFAULT_WORKERS,
)


def config_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path.home() / ".config"
    return base / "ym_download"


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        console.print(f"[yellow]Не удалось прочитать {path}: {error}[/yellow]")
        return {}


def save_config_example() -> None:
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = config_path()
    if path.is_file():
        console.print(f"Конфиг уже существует: {path}")
        return

    example = {
        "output": str(DEFAULT_OUTPUT),
        "bitrate": 320,
        "codec": "mp3",
        "skip_existing": True,
        "workers": DEFAULT_WORKERS,
        "filename_template": DEFAULT_FILENAME_TEMPLATE,
        "embed_tags": True,
        "flat": False,
    }
    path.write_text(json.dumps(example, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    console.print(f"Пример конфига создан: {path}")


def options_from_config(cfg: dict[str, Any], options_cls: type):
    opts = options_cls()
    if "output" in cfg:
        opts.output = Path(cfg["output"])
    if "codec" in cfg:
        opts.codec = str(cfg["codec"])
    if "bitrate" in cfg:
        opts.bitrate = int(cfg["bitrate"])
    if "skip_existing" in cfg:
        opts.skip_existing = bool(cfg["skip_existing"])
    if "flat" in cfg:
        opts.flat = bool(cfg["flat"])
    if "workers" in cfg:
        opts.workers = max(1, int(cfg["workers"]))
    if "filename_template" in cfg:
        opts.filename_template = str(cfg["filename_template"])
    if "embed_tags" in cfg:
        opts.embed_tags = bool(cfg["embed_tags"])
    return opts
