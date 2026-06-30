from __future__ import annotations

import sys

from music_dl.console import console
from music_dl.core.cancel import install_cancel_handlers
from music_dl.cli.parser import build_parser, inject_shorthand
from music_dl.cli.commands.auth import run_auth, run_init_config, run_list_playlists
from music_dl.cli.commands.download import run_download
from music_dl.cli.commands.pick import run_pick


def main() -> None:
    install_cancel_handlers()
    sys.argv = inject_shorthand(sys.argv)
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "auth":
        run_auth(args)
        return
    if args.command == "init-config":
        run_init_config(args)
        return
    if args.command == "list-playlists":
        run_list_playlists(args)
        return
    if args.command == "pick":
        run_pick(args)
        return
    if args.command == "download":
        run_download(args)
        return

    parser.print_help()
    console.print("\nПримеры:")
    console.print("  python ym_download.py auth")
    console.print("  python ym_download.py init-config")
    console.print('  python ym_download.py "https://music.yandex.ru/album/2832563"')
    console.print('  python ym_download.py download likes -o D:\\Music\\Likes')
    console.print("  python ym_download.py pick")


if __name__ == "__main__":
    main()
