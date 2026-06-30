from __future__ import annotations

from pathlib import Path

from yandex_music.exceptions import YandexMusicError
from yandex_music.track.track import Track

from music_dl.console import console, print_lock
from music_dl.providers.yandex.metadata import album_info, artist_names


def embed_yandex_tags(path: Path, track: Track, track_number: int) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        return

    album, year = album_info(track)
    title = track.title or f"track_{track.id}"
    artist = artist_names(track)
    cover_bytes: bytes | None = None

    try:
        cover_bytes = track.download_cover_bytes(size="400x400")
    except (YandexMusicError, OSError):
        pass

    suffix = path.suffix.lower()
    try:
        if suffix == ".mp3":
            from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TALB, TDRC, TIT2, TPE1, TRCK

            try:
                tags = ID3(path)
            except ID3NoHeaderError:
                tags = ID3()
            tags.delall("TIT2")
            tags.delall("TPE1")
            tags.add(TIT2(encoding=3, text=title))
            tags.add(TPE1(encoding=3, text=artist))
            if album:
                tags.delall("TALB")
                tags.add(TALB(encoding=3, text=album))
            if year:
                tags.delall("TDRC")
                tags.add(TDRC(encoding=3, text=str(year)))
            tags.delall("TRCK")
            tags.add(TRCK(encoding=3, text=str(track_number)))
            if cover_bytes:
                tags.delall("APIC")
                tags.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=cover_bytes,
                    )
                )
            tags.save(path)
        elif suffix == ".m4a":
            from mutagen.mp4 import MP4, MP4Cover

            audio = MP4(path)
            audio["\xa9nam"] = title
            audio["\xa9ART"] = artist
            if album:
                audio["\xa9alb"] = album
            if year:
                audio["\xa9day"] = str(year)
            audio["trkn"] = [(track_number, 0)]
            if cover_bytes:
                audio["covr"] = [MP4Cover(cover_bytes, imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()
    except Exception as error:
        with print_lock:
            console.print(f"  [yellow]tags  не удалось записать теги: {error}[/yellow]")
