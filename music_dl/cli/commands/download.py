from __future__ import annotations

import argparse

from music_dl.console import console
from music_dl.core.cancel import raise_if_cancelled
from music_dl.core.models import DownloadStats
from music_dl.cli.parser import build_download_options, collect_targets
from music_dl.pipeline.runner import retry_failed
from music_dl.providers.registry import get_provider, parse_url
from music_dl.providers.yandex.auth import read_token


def run_download(args: argparse.Namespace) -> None:
    token = read_token(args.token)
    provider = get_provider("yandex")
    client = provider.create_client(token)
    opts = build_download_options(args)

    total = DownloadStats()

    try:
        if args.retry_failed:
            stats = retry_failed(token, args.retry_failed, opts)
            total.merge(stats)
        else:
            for target in collect_targets(args):
                raise_if_cancelled()
                parsed = parse_url(target)
                prov = get_provider(parsed.provider)
                stats = prov.download_target(client, token, parsed, opts)
                total.merge(stats)
    except KeyboardInterrupt:
        console.print("[yellow]Скачивание прервано (Ctrl+C)[/yellow]")
        raise SystemExit(130) from None

    console.print(
        f"[bold]Готово:[/bold] скачано {total.downloaded}, "
        f"пропущено {total.skipped}, ошибок {total.failed}"
    )
    if total.failed:
        raise SystemExit(1)
