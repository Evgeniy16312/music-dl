from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent

DEFAULT_OUTPUT = Path.home() / "Music" / "YandexMusic"
DEFAULT_TOKEN_FILE = PROJECT_ROOT / ".token"
DEFAULT_FILENAME_TEMPLATE = "{n:02d} - {artist} - {title}"
DEFAULT_WORKERS = 3
FAILED_LOG_NAME = ".ym_download_failed.json"

KNOWN_COMMANDS = frozenset({"auth", "download", "list-playlists", "pick", "init-config"})

BITRATES = (320, 256, 192, 128, 64)
ARTIST_SCOPES = ("discography", "direct", "also", "all")
ARTIST_ALBUM_PAGE_SIZE = 50
ARTIST_TRACK_PAGE_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY_SEC = 2
