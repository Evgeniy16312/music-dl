from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from music_dl.constants import FAILED_LOG_NAME


def failed_log_path(out_dir: Path) -> Path:
    return out_dir / FAILED_LOG_NAME


def load_failed_log(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise SystemExit(f"Файл ошибок не найден: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"Некорректный JSON в {path}: {error}") from error
    if not isinstance(data, list):
        raise SystemExit(f"Ожидался список записей в {path}")
    return data


def save_failed_log(path: Path, entries: list[dict[str, Any]]) -> None:
    if not entries:
        if path.is_file():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
