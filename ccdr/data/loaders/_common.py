"""Common loader helpers (sha256, manifest lookup).

This module is framework-blind by design: it knows nothing about derivations
or framework parameters. The framework-blind lint test enforces this.
"""
import hashlib
import json
import pathlib
from typing import Tuple

MANIFEST_DIR = pathlib.Path(__file__).resolve().parent.parent / "manifests"
CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(name: str) -> dict:
    """Load a SHA256 manifest by name (without extension). Returns {} if absent."""
    path = MANIFEST_DIR / f"{name}.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def manifest_sha(name: str, file_key: str = "primary") -> str:
    return load_manifest(name).get(file_key, "")


__all__ = ["sha256_bytes", "sha256_file", "load_manifest", "manifest_sha",
           "MANIFEST_DIR", "CACHE_DIR"]
