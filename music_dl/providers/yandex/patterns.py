import re

TOKEN_ENV = "YANDEX_MUSIC_TOKEN"
YANDEX_HOST = r"music\.yandex\.(?:ru|com|by|kz|ua)"

URL_ARTIST_TRACKS = re.compile(
    rf"{YANDEX_HOST}/artist/(?P<id>\d+)/tracks",
    re.IGNORECASE,
)
URL_ARTIST = re.compile(
    rf"{YANDEX_HOST}/artist/(?P<id>\d+)(?:[/?#]|$)",
    re.IGNORECASE,
)
URL_ALBUM = re.compile(rf"{YANDEX_HOST}/album/(?P<id>\d+)", re.IGNORECASE)
URL_TRACK = re.compile(
    rf"{YANDEX_HOST}/(?:album/\d+/)?track/(?P<id>\d+)",
    re.IGNORECASE,
)
URL_PLAYLIST_USER = re.compile(
    rf"{YANDEX_HOST}/users/(?P<user>[^/?#]+)/playlists/(?P<kind>\d+)",
    re.IGNORECASE,
)
URL_PLAYLIST_UUID = re.compile(
    rf"{YANDEX_HOST}/playlist(?:s)?/(?P<uuid>(?:lk\.)?[0-9a-f-]{{36}})",
    re.IGNORECASE,
)
URL_LIKES = re.compile(rf"{YANDEX_HOST}/users/[^/?#]+/likes", re.IGNORECASE)
