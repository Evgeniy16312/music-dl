from __future__ import annotations

import os
import re
from pathlib import Path

from music_dl.constants import DEFAULT_TOKEN_FILE
from music_dl.console import console
from music_dl.providers.yandex.patterns import YANDEX_HOST


def read_token(raw: str | None) -> str:
    if raw:
        path = Path(raw)
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
        return raw.strip()

    from music_dl.providers.yandex.patterns import TOKEN_ENV

    env = os.environ.get(TOKEN_ENV)
    if env:
        return env.strip()

    if DEFAULT_TOKEN_FILE.is_file():
        return DEFAULT_TOKEN_FILE.read_text(encoding="utf-8").strip()

    raise SystemExit(
        "Нужен токен: --token, переменная YANDEX_MUSIC_TOKEN "
        f"или файл {DEFAULT_TOKEN_FILE}"
    )


def save_token(token: str, path: Path = DEFAULT_TOKEN_FILE) -> None:
    path.write_text(token.strip(), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    console.print(f"Токен сохранён: {path}")


def normalize_target(value: str) -> str:
    value = value.strip().strip('"\'')
    if m := re.search(rf"https?://{YANDEX_HOST}/[^\s<>\"']+", value, re.IGNORECASE):
        return m.group(0).rstrip(".,;)")
    if m := re.search(rf"{YANDEX_HOST}/[^\s<>\"']+", value, re.IGNORECASE):
        return "https://" + m.group(0).rstrip(".,;)")
    return value


def device_auth(token_file: Path = DEFAULT_TOKEN_FILE) -> None:
    from yandex_music import Client

    from music_dl.providers.yandex.metadata import create_client

    def on_code(code) -> None:
        console.print(f"Откройте: {code.verification_url}")
        console.print(f"Код: {code.user_code}")
        console.print()
        console.print("1) Введите код на сайте и подтвердите вход.")
        console.print("2) НЕ закрывайте терминал — ждите сообщение «Авторизация OK».")
        console.print("   (обычно 5–30 секунд после подтверждения в браузере)")
        console.print()

    console.print("Ожидание подтверждения в браузере...")
    client = Client()
    token = client.device_auth(on_code=on_code)
    save_token(token.access_token, token_file)
    client = create_client(token.access_token)
    name = client.me.account.first_name or "пользователь"
    console.print(f"[green]Авторизация OK, {name}[/green]")
