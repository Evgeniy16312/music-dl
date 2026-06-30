from __future__ import annotations

from dataclasses import replace

from yandex_music import Client

from music_dl.constants import ARTIST_ALBUM_PAGE_SIZE, ARTIST_SCOPES
from music_dl.console import console
from music_dl.core.cancel import raise_if_cancelled
from music_dl.core.filenames import sanitize_filename
from music_dl.core.models import DownloadOptions, DownloadStats
from music_dl.providers.yandex.loaders import load_album, resolve_artist_name
from music_dl.pipeline.runner import download_collection


def artist_url_help(artist_id: int) -> str:
    return (
        f"Ссылка https://music.yandex.ru/artist/{artist_id} — страница исполнителя.\n\n"
        "Скачать треки со вкладки «Треки»:\n"
        f'  python ym_download.py "https://music.yandex.ru/artist/{artist_id}/tracks"\n\n'
        "Скачать один альбом — открой альбом, скопируй URL с /album/:\n"
        '  python ym_download.py "https://music.yandex.ru/album/42432434"\n\n'
        "Скачать ВСЕ альбомы исполнителя:\n"
        f'  python ym_download.py "https://music.yandex.ru/artist/{artist_id}" --all-albums'
    )


def require_all_albums_flag(artist_id: int, all_albums: bool) -> None:
    if not all_albums:
        raise SystemExit(artist_url_help(artist_id))


def _album_fetcher(client: Client, scope: str):
    fetchers = {
        "discography": client.artists_discography_albums,
        "direct": client.artists_direct_albums,
        "also": client.artists_also_albums,
    }
    if scope not in fetchers:
        raise SystemExit(f"Неизвестный artist-scope: {scope}")
    return fetchers[scope]


def fetch_artist_album_ids(client: Client, artist_id: int, scope: str) -> list[int]:
    scopes = ("discography", "direct", "also") if scope == "all" else (scope,)
    album_ids: list[int] = []
    seen: set[int] = set()

    for current_scope in scopes:
        if current_scope not in ARTIST_SCOPES and current_scope != "all":
            continue
        fetcher = _album_fetcher(client, current_scope)
        page = 0
        while True:
            result = fetcher(artist_id, page=page, page_size=ARTIST_ALBUM_PAGE_SIZE)
            if result is None or not result.albums:
                break
            for album in result.albums:
                if album.id is not None and album.id not in seen:
                    seen.add(album.id)
                    album_ids.append(album.id)
            pager = result.pager
            if pager is None or (pager.page + 1) * pager.per_page >= pager.total:
                break
            page += 1

    return album_ids


def download_artist_albums(
    client: Client,
    token: str,
    artist_id: int,
    opts: DownloadOptions,
) -> DownloadStats:
    name = resolve_artist_name(client, artist_id)
    album_ids = fetch_artist_album_ids(client, artist_id, opts.artist_scope)

    if not album_ids and opts.artist_scope != "all":
        console.print(f"[yellow]scope={opts.artist_scope} пуст, пробую all[/yellow]")
        album_ids = fetch_artist_album_ids(client, artist_id, "all")
        opts = replace(opts, artist_scope="all")

    if not album_ids:
        raise SystemExit(f"У артиста «{name}» нет альбомов (scope={opts.artist_scope})")

    console.print(
        f"[bold]Артист {name}[/bold]: {len(album_ids)} альбом(ов), scope={opts.artist_scope}"
    )

    artist_opts = opts
    if not opts.flat:
        artist_opts = replace(opts, output=opts.output / sanitize_filename(name))

    if opts.dry_run:
        stats = DownloadStats()
        for album_id in album_ids:
            source = load_album(client, album_id)
            console.print(f"  [dim]album[/dim]  {source.label} ({len(source.items)} трек.)")
        return stats

    total = DownloadStats()
    for index, album_id in enumerate(album_ids, start=1):
        raise_if_cancelled()
        console.print(f"[bold]Альбом {index}/{len(album_ids)}[/bold]")
        collection = load_album(client, album_id)
        stats = download_collection(client, token, collection, artist_opts)
        total.merge(stats)

    return total
