from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from music_dl.constants import DEFAULT_FILENAME_TEMPLATE, DEFAULT_OUTPUT, DEFAULT_WORKERS


@dataclass(frozen=True)
class ParsedTarget:
    provider: str
    kind: str
    params: dict[str, Any]


@dataclass(frozen=True)
class TrackCollection:
    provider: str
    label: str
    items: Sequence[Any]


@dataclass
class DownloadOptions:
    output: Path = DEFAULT_OUTPUT
    codec: str = "mp3"
    bitrate: int = 320
    skip_existing: bool = True
    flat: bool = False
    dry_run: bool = False
    workers: int = DEFAULT_WORKERS
    filename_template: str = DEFAULT_FILENAME_TEMPLATE
    embed_tags: bool = True
    track_from: int | None = None
    track_to: int | None = None
    artist_scope: str = "all"
    all_albums: bool = False


@dataclass
class TrackJob:
    number: int
    total: int
    item: Any
    dest: Path


@dataclass
class DownloadStats:
    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    failed_entries: list[dict[str, Any]] = field(default_factory=list)

    def merge(self, other: DownloadStats) -> None:
        self.downloaded += other.downloaded
        self.skipped += other.skipped
        self.failed += other.failed
        self.failed_entries.extend(other.failed_entries)
