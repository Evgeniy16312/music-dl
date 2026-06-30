from __future__ import annotations

import argparse

from music_dl.constants import DEFAULT_TOKEN_FILE
from music_dl.core.config import save_config_example
from music_dl.providers.yandex.auth import device_auth, read_token


def run_auth(args: argparse.Namespace) -> None:
    device_auth(args.token_file)


def run_init_config(_args: argparse.Namespace) -> None:
    save_config_example()


def run_list_playlists(args: argparse.Namespace) -> None:
    from music_dl.console import console
    from music_dl.providers.yandex.metadata import create_client

    token = read_token(getattr(args, "token", None))
    client = create_client(token)
    playlists = client.users_playlists_list() or []

    console.print(f"Плейлисты ({client.me.account.login}):")
    for index, playlist in enumerate(playlists, start=1):
        owner = playlist.owner.login if playlist.owner else client.me.account.login
        console.print(
            f"  [{index:2d}] {playlist.title!r}: kind={playlist.kind}, "
            f"tracks={playlist.track_count}, user={owner}"
        )
    console.print()
    console.print("Скачать интерактивно: python ym_download.py pick")
