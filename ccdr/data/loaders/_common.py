"""Common loader helpers (sha256, manifest lookup, JSON reader).

This module is framework-blind by design: it knows nothing about
derivations or framework parameters. The framework-blind lint test
enforces this.

SHA256 is computed over the *line-ending-normalised* file content
(CRLF → LF). This keeps the manifest SHA stable across Linux, macOS,
and Windows checkouts even when git normalises line endings. The
.gitattributes file also pins cache and manifest files to LF, so on
a clean checkout normalised and raw SHA agree.
"""
import hashlib
import json
import pathlib
from typing import Tuple, Any

MANIFEST_DIR = pathlib.Path(__file__).resolve().parent.parent / "manifests"
CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache"


class DataUnavailable(FileNotFoundError):
    """Raised when a cached data file is absent."""


class DataQualityFailed(Exception):
    """Raised when a cached file's SHA256 mismatches the manifest."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalise_line_endings(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256_file(path: pathlib.Path) -> str:
    """SHA256 of a file's content with line endings normalised to LF."""
    data = pathlib.Path(path).read_bytes()
    return hashlib.sha256(_normalise_line_endings(data)).hexdigest()


def load_manifest(name: str) -> dict:
    path = MANIFEST_DIR / f"{name}.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def manifest_sha(name: str, file_key: str = "primary") -> str:
    return load_manifest(name).get(file_key, "")


def read_cached_json(name: str) -> Tuple[Any, str]:
    """Read ccdr/data/cache/<name>.json, verify SHA256 against manifest if
    present, and return (decoded_json, sha256_hex)."""
    path = CACHE_DIR / f"{name}.json"
    if not path.exists():
        raise DataUnavailable(f"cache miss: {path}")
    sha = sha256_file(path)
    expected = manifest_sha(name)
    if expected and expected != sha:
        raise DataQualityFailed(
            f"SHA256 mismatch for {name}: expected {expected}, got {sha}"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f), sha


__all__ = [
    "sha256_bytes", "sha256_file", "load_manifest", "manifest_sha",
    "read_cached_json", "DataQualityFailed", "DataUnavailable",
    "MANIFEST_DIR", "CACHE_DIR",
]
