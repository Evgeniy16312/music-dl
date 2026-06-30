from __future__ import annotations

import re

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WHITESPACE = re.compile(r"\s+")


def sanitize_filename(name: str, max_len: int = 180) -> str:
    cleaned = INVALID_FILENAME_CHARS.sub("_", name)
    cleaned = WHITESPACE.sub(" ", cleaned).strip(" .")
    if not cleaned:
        return "untitled"
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip(" .")
    return cleaned
