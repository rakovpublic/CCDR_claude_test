"""Common loader helpers (sha256, manifest lookup, JSON reader).

This module is framework-blind by design: it knows nothing about
derivations or framework parameters. The framework-blind lint test
enforces this.
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


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
    with open(path) as f:
        return json.load(f), sha


__all__ = [
    "sha256_bytes", "sha256_file", "load_manifest", "manifest_sha",
    "read_cached_json", "DataQualityFailed", "DataUnavailable",
    "MANIFEST_DIR", "CACHE_DIR",
]
