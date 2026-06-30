from __future__ import annotations

import argparse
from pathlib import Path

from music_dl.constants import (
    ARTIST_SCOPES,
    BITRATES,
    DEFAULT_TOKEN_FILE,
    FAILED_LOG_NAME,
    KNOWN_COMMANDS,
)
from music_dl.core.config import load_config, options_from_config
from music_dl.core.models import DownloadOptions


def add_download_args(parser: argparse.ArgumentParser) -> None:
    cfg = load_config()
    default_opts = options_from_config(cfg, DownloadOptions)

    parser.add_argument(
        "targets",
        nargs="*",
        help="URL, album/artist id, user/kind, likes (несколько целей подряд)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=default_opts.output,
        help=f"папка назначения (по умолчанию {default_opts.output})",
    )
    parser.add_argument("--token", help="OAuth access_token или путь к файлу с токеном")
    parser.add_argument(
        "--bitrate",
        type=int,
        default=default_opts.bitrate,
        choices=BITRATES,
        help="желаемый битрейт MP3",
    )
    parser.add_argument(
        "--codec",
        default=default_opts.codec,
        choices=("mp3", "aac"),
        help="кодек",
    )
    force = parser.add_mutually_exclusive_group()
    force.add_argument(
        "--skip-existing",
        action="store_true",
        default=None,
        help="не перекачивать существующие файлы (по умолчанию)",
    )
    force.add_argument(
        "--force",
        action="store_true",
        help="перекачать даже если файл уже есть",
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        default=default_opts.flat,
        help="не создавать подпапку с названием альбома/плейлиста",
    )
    parser.add_argument("--dry-run", action="store_true", help="показать план без скачивания")
    parser.add_argument(
        "--workers",
        type=int,
        default=default_opts.workers,
        help=f"параллельных загрузок (по умолчанию {default_opts.workers})",
    )
    parser.add_argument(
        "--template",
        default=default_opts.filename_template,
        help="шаблон имени: {n}, {artist}, {title}, {album}, {year}",
    )
    parser.add_argument("--no-tags", action="store_true", help="не записывать ID3-теги")
    parser.add_argument("--from", dest="track_from", type=int, metavar="N")
    parser.add_argument("--to", dest="track_to", type=int, metavar="N")
    parser.add_argument(
        "--retry-failed",
        type=Path,
        metavar="LOG",
        help=f"повторить из {FAILED_LOG_NAME}",
    )
    parser.add_argument("--targets-file", type=Path, metavar="FILE")
    parser.add_argument(
        "--all-albums",
        action="store_true",
        help="скачать все альбомы по ссылке /artist/",
    )
    parser.add_argument(
        "--artist-scope",
        choices=ARTIST_SCOPES,
        default="all",
        help="с --all-albums: all, discography, direct, also",
    )


def build_download_options(args: argparse.Namespace) -> DownloadOptions:
    cfg = load_config()
    opts = options_from_config(cfg, DownloadOptions)
    opts.output = args.output
    opts.codec = args.codec
    opts.bitrate = args.bitrate
    opts.flat = args.flat
    opts.dry_run = args.dry_run
    opts.workers = max(1, args.workers)
    opts.filename_template = args.template
    opts.embed_tags = not args.no_tags
    opts.track_from = args.track_from
    opts.track_to = args.track_to
    opts.artist_scope = args.artist_scope
    opts.all_albums = args.all_albums

    if args.force:
        opts.skip_existing = False
    elif args.skip_existing is True:
        opts.skip_existing = True
    elif args.skip_existing is None and "skip_existing" not in load_config():
        opts.skip_existing = True

    return opts


def collect_targets(args: argparse.Namespace) -> list[str]:
    targets = list(args.targets or [])
    if args.targets_file:
        if not args.targets_file.is_file():
            raise SystemExit(f"Файл не найден: {args.targets_file}")
        for line in args.targets_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                targets.append(line)
    if not targets and not args.retry_failed:
        raise SystemExit("Укажите цель: URL, album id, likes или --targets-file")
    return targets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Скачать музыку из поддерживаемых стриминговых сервисов",
    )
    sub = parser.add_subparsers(dest="command")

    auth = sub.add_parser("auth", help="получить OAuth-токен (Яндекс.Музыка)")
    auth.add_argument("--token-file", type=Path, default=DEFAULT_TOKEN_FILE)

    sub.add_parser("init-config", help="создать пример config.json")

    dl = sub.add_parser("download", help="скачать альбом/плейлист/треки")
    add_download_args(dl)

    pick = sub.add_parser("pick", help="выбрать плейлист и скачать")
    add_download_args(pick)

    lst = sub.add_parser("list-playlists", help="показать плейлисты (Яндекс)")
    lst.add_argument("--token", help="OAuth access_token или путь к файлу")

    return parser


def inject_shorthand(argv: list[str]) -> list[str]:
    if len(argv) <= 1:
        return argv
    first = argv[1]
    if first in KNOWN_COMMANDS or first.startswith("-"):
        return argv
    return [argv[0], "download", *argv[1:]]
