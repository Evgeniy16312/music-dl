from __future__ import annotations

import time
from pathlib import Path

from yandex_music import Client
from yandex_music.exceptions import InvalidBitrateError, YandexMusicError
from yandex_music.track.track import Track

from music_dl.constants import BITRATES, MAX_RETRIES, RETRY_DELAY_SEC
from music_dl.console import console, print_lock
from music_dl.core.cancel import raise_if_cancelled
from music_dl.core.filenames import sanitize_filename
from music_dl.core.models import DownloadOptions, TrackJob
from music_dl.pipeline.tags import embed_yandex_tags
from music_dl.providers.yandex.metadata import (
    album_info,
    artist_names,
    create_client,
    resolve_track,
)


def pick_bitrate(track: Track, codec: str, preferred: int) -> int:
    infos = track.get_download_info()
    available = sorted(
        {info.bitrate_in_kbps for info in infos if info.codec == codec},
        reverse=True,
    )
    if not available:
        raise InvalidBitrateError(f"No {codec} download info for track {track.title}")
    if preferred in available:
        return preferred
    for bitrate in BITRATES:
        if bitrate in available:
            return bitrate
    return available[0]


def build_track_filename(template: str, number: int, track: Track) -> str:
    album, year = album_info(track)
    try:
        raw = template.format(
            n=number,
            artist=artist_names(track),
            title=track.title or f"track_{track.id}",
            album=album,
            year=year or "",
        )
    except KeyError as error:
        raise SystemExit(f"Неизвестное поле в шаблоне имени: {error}") from error
    return sanitize_filename(raw)


def download_yandex_track(
    track: Track,
    dest: Path,
    codec: str,
    bitrate: int,
    skip_existing: bool,
    embed: bool,
    track_number: int,
) -> str:
    if skip_existing and dest.exists() and dest.stat().st_size > 0:
        return "skipped"

    dest.parent.mkdir(parents=True, exist_ok=True)
    actual_bitrate = pick_bitrate(track, codec, bitrate)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            track.download(str(dest), codec=codec, bitrate_in_kbps=actual_bitrate)
            if embed:
                embed_yandex_tags(dest, track, track_number)
            return "downloaded"
        except (YandexMusicError, OSError) as error:
            if attempt == MAX_RETRIES:
                raise
            with print_lock:
                console.print(f"  [yellow]retry {attempt}/{MAX_RETRIES}: {error}[/yellow]")
            time.sleep(RETRY_DELAY_SEC)

    return "skipped"


def run_yandex_worker(
    token: str,
    job: TrackJob,
    opts: DownloadOptions,
) -> tuple[str, dict | None]:
    raise_if_cancelled()
    client = create_client(token)
    track = resolve_track(job.item)
    track.client = client
    try:
        result = download_yandex_track(
            track,
            job.dest,
            opts.codec,
            opts.bitrate,
            opts.skip_existing,
            opts.embed_tags,
            job.number,
        )
        return result, None
    except (YandexMusicError, OSError) as error:
        return "failed", {
            "track_id": str(track.id),
            "dest": str(job.dest),
            "title": track.title,
            "artist": artist_names(track),
            "error": str(error),
        }
