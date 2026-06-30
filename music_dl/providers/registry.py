from __future__ import annotations

from music_dl.core.models import ParsedTarget
from music_dl.providers.base import MusicProvider
from music_dl.providers.yandex.provider import YandexMusicProvider

_PROVIDERS: list[MusicProvider] = [YandexMusicProvider()]


def all_providers() -> list[MusicProvider]:
    return list(_PROVIDERS)


def register_provider(provider: MusicProvider) -> None:
    _PROVIDERS.append(provider)


def parse_url(url: str) -> ParsedTarget:
    for provider in _PROVIDERS:
        if provider.can_parse(url):
            try:
                return provider.parse(url)
            except ValueError:
                continue
    raise SystemExit(
        "Не удалось разобрать цель. Примеры:\n"
        "  https://music.yandex.ru/album/12345\n"
        "  https://music.yandex.ru/album/12345/track/67890\n"
        "  https://music.yandex.ru/artist/3379147/tracks\n"
        "  https://music.yandex.ru/artist/3379147  (нужен --all-albums)\n"
        "  https://music.yandex.ru/users/login/playlists/3\n"
        "  likes"
    )


def get_provider(name: str) -> MusicProvider:
    for provider in _PROVIDERS:
        if provider.name == name:
            return provider
    raise SystemExit(f"Неизвестный провайдер: {name}")
