from __future__ import annotations

from typing import TYPE_CHECKING

from yandex_music import Client
from yandex_music.track.track import Track
from yandex_music.track_short import TrackShort

if TYPE_CHECKING:
    from yandex_music import Client as YandexClient


def create_client(token: str) -> YandexClient:
    return Client(token, report_unknown_fields=False).init()


def artist_names(track: Track) -> str:
    if not track.artists:
        return "Unknown Artist"
    return ", ".join(a.name for a in track.artists if a.name)


def album_info(track: Track) -> tuple[str, int | None]:
    if not track.albums:
        return "", None
    album = track.albums[0]
    return album.title or "", album.year


def resolve_track(item: Track | TrackShort) -> Track:
    if isinstance(item, Track):
        return item
    if item.track:
        return item.track
    return item.fetch_track()
