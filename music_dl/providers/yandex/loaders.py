from __future__ import annotations

from yandex_music import Client
from yandex_music.track.track import Track

from music_dl.core.models import TrackCollection
from music_dl.providers.yandex.metadata import artist_names


def load_album(client: Client, album_id: int) -> TrackCollection:
    album = client.albums_with_tracks(album_id)
    if album is None:
        raise SystemExit(f"Альбом {album_id} не найден")

    tracks: list[Track] = []
    for volume in album.volumes or []:
        tracks.extend(volume)

    artists = ", ".join(a.name for a in album.artists or [] if a.name)
    label = album.title or f"album_{album_id}"
    if artists:
        label = f"{label} — {artists}"
    if album.year:
        label = f"{label} ({album.year})"

    return TrackCollection("yandex", label, tracks)


def load_playlist(client: Client, user: str, kind: int) -> TrackCollection:
    playlist = client.users_playlists(kind, user_id=user)
    if playlist is None:
        raise SystemExit(f"Плейлист {user}/{kind} не найден")
    tracks = playlist.tracks or playlist.fetch_tracks()
    title = playlist.title or f"playlist_{kind}"
    return TrackCollection("yandex", title, tracks)


def load_playlist_uuid(client: Client, uuid: str) -> TrackCollection:
    playlist = client.playlist(uuid)
    if playlist is None:
        raise SystemExit(f"Плейлист {uuid} не найден")
    tracks = playlist.tracks or playlist.fetch_tracks()
    title = playlist.title or f"playlist_{uuid[:8]}"
    return TrackCollection("yandex", title, tracks)


def load_track(client: Client, track_id: int) -> TrackCollection:
    tracks = client.tracks(track_id)
    if not tracks:
        raise SystemExit(f"Трек {track_id} не найден")
    track = tracks[0]
    label = f"{track.title or track_id} — {artist_names(track)}"
    return TrackCollection("yandex", label, [track])


def load_likes(client: Client) -> TrackCollection:
    likes = client.users_likes_tracks()
    if likes is None or not likes.tracks:
        raise SystemExit("Список «Мне нравится» пуст")
    return TrackCollection("yandex", "Мне нравится", likes.tracks)


def resolve_artist_name(client: Client, artist_id: int) -> str:
    artists = client.artists(artist_id)
    if artists and artists[0].name:
        return artists[0].name
    return f"artist_{artist_id}"


def fetch_artist_tracks(client: Client, artist_id: int) -> list[Track]:
    from music_dl.constants import ARTIST_TRACK_PAGE_SIZE

    tracks: list[Track] = []
    page = 0
    while True:
        result = client.artists_tracks(artist_id, page=page, page_size=ARTIST_TRACK_PAGE_SIZE)
        if result is None or not result.tracks:
            break
        tracks.extend(result.tracks)
        pager = result.pager
        if pager is None or (pager.page + 1) * pager.per_page >= pager.total:
            break
        page += 1
    return tracks


def load_artist_tracks(client: Client, artist_id: int) -> TrackCollection:
    name = resolve_artist_name(client, artist_id)
    tracks = fetch_artist_tracks(client, artist_id)
    if not tracks:
        raise SystemExit(f"У артиста «{name}» нет треков")
    return TrackCollection("yandex", f"{name} — треки", tracks)
