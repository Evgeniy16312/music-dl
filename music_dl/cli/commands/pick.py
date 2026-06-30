from __future__ import annotations

import argparse
import re

from music_dl.console import console
from music_dl.cli.commands.download import run_download
from music_dl.providers.yandex.auth import read_token
from music_dl.providers.yandex.metadata import create_client


def run_pick(args: argparse.Namespace) -> None:
    token = read_token(args.token)
    client = create_client(token)
    playlists = client.users_playlists_list() or []

    if not playlists:
        raise SystemExit("Плейлисты не найдены")

    console.print(f"Плейлисты ({client.me.account.login}):")
    for index, playlist in enumerate(playlists, start=1):
        owner = playlist.owner.login if playlist.owner else client.me.account.login
        console.print(
            f"  [{index:2d}] {playlist.title!r} "
            f"({playlist.track_count} трек., {owner}/{playlist.kind})"
        )

    console.print()
    console.print("Дополнительно: [bold]likes[/bold] — «Мне нравится»")
    console.print("Введите номера через запятую, all или likes:")
    try:
        selection = input("> ").strip()
    except EOFError:
        raise SystemExit("Отменено") from None

    if not selection:
        raise SystemExit("Ничего не выбрано")

    targets: list[str] = []
    if selection.lower() in {"all", "*"}:
        for playlist in playlists:
            owner = playlist.owner.login if playlist.owner else client.me.account.login
            targets.append(f"{owner}/{playlist.kind}")
    elif selection.lower() in {"likes", "лайки"}:
        targets.append("likes")
    else:
        for part in re.split(r"[,;\s]+", selection):
            part = part.strip()
            if not part:
                continue
            if part.lower() in {"likes", "лайки"}:
                targets.append("likes")
                continue
            if not part.isdigit():
                raise SystemExit(f"Некорректный номер: {part!r}")
            index = int(part)
            if index < 1 or index > len(playlists):
                raise SystemExit(f"Номер вне диапазона: {index}")
            playlist = playlists[index - 1]
            owner = playlist.owner.login if playlist.owner else client.me.account.login
            targets.append(f"{owner}/{playlist.kind}")

    args.targets = targets
    run_download(args)
