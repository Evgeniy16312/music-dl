from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Any

from music_dl.core.models import DownloadOptions, TrackCollection, TrackJob
from music_dl.providers.yandex.metadata import resolve_track
from music_dl.providers.yandex.track_download import build_track_filename


def iter_numbered(
    items: Iterable[Any],
    track_from: int | None = None,
    track_to: int | None = None,
) -> Iterator[tuple[int, Any]]:
    index = 0
    for item in items:
        index += 1
        if track_from is not None and index < track_from:
            continue
        if track_to is not None and index > track_to:
            break
        yield index, item


def build_jobs(
    collection: TrackCollection,
    out_dir,
    opts: DownloadOptions,
) -> list[TrackJob]:
    if collection.provider != "yandex":
        raise SystemExit(f"Провайдер {collection.provider!r} пока не поддерживается в pipeline")

    ext = "mp3" if opts.codec == "mp3" else "m4a"
    items = list(collection.items)
    total = len(items)
    if opts.track_from or opts.track_to:
        total = sum(
            1
            for i in range(1, len(items) + 1)
            if (opts.track_from is None or i >= opts.track_from)
            and (opts.track_to is None or i <= opts.track_to)
        )

    jobs: list[TrackJob] = []
    for number, item in iter_numbered(items, opts.track_from, opts.track_to):
        track = resolve_track(item)
        filename = build_track_filename(opts.filename_template, number, track)
        dest = out_dir / f"{filename}.{ext}"
        jobs.append(TrackJob(number=number, total=total, item=item, dest=dest))
    return jobs
