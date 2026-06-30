from __future__ import annotations

from yandex_music import Client

from music_dl.core.models import DownloadOptions, DownloadStats, ParsedTarget, TrackCollection
from music_dl.providers.yandex.artist import download_artist_albums, require_all_albums_flag
from music_dl.providers.yandex.loaders import (
    load_album,
    load_artist_tracks,
    load_likes,
    load_playlist,
    load_playlist_uuid,
    load_track,
)
from music_dl.providers.yandex.metadata import create_client
from music_dl.providers.yandex.targets import can_parse_yandex, parse_yandex_target
from music_dl.pipeline.runner import download_collection


class YandexMusicProvider:
    name = "yandex"

    def can_parse(self, url: str) -> bool:
        return can_parse_yandex(url)

    def parse(self, url: str) -> ParsedTarget:
        return parse_yandex_target(url)

    def create_client(self, token: str) -> Client:
        return create_client(token)

    def load(self, client: Client, target: ParsedTarget) -> TrackCollection:
        kind = target.kind
        params = target.params
        if kind == "album":
            return load_album(client, params["album_id"])
        if kind == "playlist":
            return load_playlist(client, params["user"], params["kind"])
        if kind == "playlist_uuid":
            return load_playlist_uuid(client, params["uuid"])
        if kind == "track":
            return load_track(client, params["track_id"])
        if kind == "artist_tracks":
            return load_artist_tracks(client, params["artist_id"])
        if kind == "likes":
            return load_likes(client)
        raise SystemExit(f"Неизвестный тип цели: {kind}")

    def download_collection(
        self,
        client: Client,
        token: str,
        collection: TrackCollection,
        opts: DownloadOptions,
    ) -> DownloadStats:
        return download_collection(client, token, collection, opts)

    def download_target(
        self,
        client: Client,
        token: str,
        target: ParsedTarget,
        opts: DownloadOptions,
    ) -> DownloadStats:
        if target.kind == "artist":
            require_all_albums_flag(target.params["artist_id"], opts.all_albums)
            return download_artist_albums(client, token, target.params["artist_id"], opts)
        collection = self.load(client, target)
        return self.download_collection(client, token, collection, opts)
