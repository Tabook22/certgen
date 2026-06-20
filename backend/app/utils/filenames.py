import re
import secrets
from pathlib import Path


_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name.strip().replace(" ", "_")
    sanitized = _SAFE_FILENAME_RE.sub("", name)
    return sanitized or f"upload-{secrets.token_hex(8)}"


def file_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def unique_storage_name(filename: str) -> str:
    safe_name = sanitize_filename(filename)
    return f"{secrets.token_hex(8)}-{safe_name}"
