from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from music_dl.core.models import DownloadOptions, DownloadStats, ParsedTarget, TrackCollection


@runtime_checkable
class MusicProvider(Protocol):
    name: str

    def can_parse(self, url: str) -> bool: ...

    def parse(self, url: str) -> ParsedTarget: ...

    def create_client(self, token: str) -> Any: ...

    def load(self, client: Any, target: ParsedTarget) -> TrackCollection: ...

    def download_collection(
        self,
        client: Any,
        token: str,
        collection: TrackCollection,
        opts: DownloadOptions,
    ) -> DownloadStats: ...

    def download_target(
        self,
        client: Any,
        token: str,
        target: ParsedTarget,
        opts: DownloadOptions,
    ) -> DownloadStats: ...
