from __future__ import annotations

import re

from music_dl.core.models import ParsedTarget
from music_dl.providers.yandex.auth import normalize_target
from music_dl.providers.yandex.patterns import (
    URL_ALBUM,
    URL_ARTIST,
    URL_ARTIST_TRACKS,
    URL_LIKES,
    URL_PLAYLIST_USER,
    URL_PLAYLIST_UUID,
    URL_TRACK,
    YANDEX_HOST,
)


def can_parse_yandex(url: str) -> bool:
    value = normalize_target(url)
    if re.search(YANDEX_HOST, value, re.IGNORECASE):
        return True
    if value.isdigit():
        return True
    lowered = value.lower()
    return lowered in {"likes", "лайки", "мне нравится"} or bool(
        re.fullmatch(r"(?P<user>[^/]+)/(?P<kind>\d+)", value)
        or re.fullmatch(r"track[:/](?P<id>\d+)", value, re.IGNORECASE)
        or re.fullmatch(r"artist[:/](?P<id>\d+)", value, re.IGNORECASE)
    )


def parse_yandex_target(value: str) -> ParsedTarget:
    value = normalize_target(value)

    if m := URL_TRACK.search(value):
        return ParsedTarget("yandex", "track", {"track_id": int(m.group("id"))})
    if m := URL_ARTIST_TRACKS.search(value):
        return ParsedTarget("yandex", "artist_tracks", {"artist_id": int(m.group("id"))})
    if m := URL_ARTIST.search(value):
        return ParsedTarget("yandex", "artist", {"artist_id": int(m.group("id"))})
    if value.isdigit():
        return ParsedTarget("yandex", "album", {"album_id": int(value)})
    if m := URL_ALBUM.search(value):
        return ParsedTarget("yandex", "album", {"album_id": int(m.group("id"))})
    if m := URL_PLAYLIST_USER.search(value):
        return ParsedTarget(
            "yandex",
            "playlist",
            {"user": m.group("user"), "kind": int(m.group("kind"))},
        )
    if m := URL_PLAYLIST_UUID.search(value):
        return ParsedTarget("yandex", "playlist_uuid", {"uuid": m.group("uuid")})
    if URL_LIKES.search(value) or value.lower() in {"likes", "лайки", "мне нравится"}:
        return ParsedTarget("yandex", "likes", {})
    if m := re.fullmatch(r"(?P<user>[^/]+)/(?P<kind>\d+)", value):
        return ParsedTarget(
            "yandex",
            "playlist",
            {"user": m.group("user"), "kind": int(m.group("kind"))},
        )
    if m := re.fullmatch(r"track[:/](?P<id>\d+)", value, re.IGNORECASE):
        return ParsedTarget("yandex", "track", {"track_id": int(m.group("id"))})
    if m := re.fullmatch(r"artist[:/](?P<id>\d+)", value, re.IGNORECASE):
        return ParsedTarget("yandex", "artist", {"artist_id": int(m.group("id"))})

    raise ValueError(f"Не удалось разобрать цель Яндекс.Музыки: {value}")
