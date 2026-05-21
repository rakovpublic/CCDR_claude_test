"""Regenerate SHA256 manifests for every file in ccdr/data/cache/.

Usage: python scripts/refresh_manifests.py
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "ccdr" / "data" / "cache"
MANIFESTS = ROOT / "ccdr" / "data" / "manifests"


def _normalised_sha(path: pathlib.Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def main():
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    for p in sorted(CACHE.glob("*.json")):
        sha = _normalised_sha(p)
        name = p.stem
        try:
            with open(p, encoding="utf-8") as f:
                meta = json.load(f)
        except json.JSONDecodeError:
            meta = {}
        manifest = {
            "source": meta.get("source", name),
            "url": meta.get("url", ""),
            "primary": sha,
            "notes": "auto-generated; rerun scripts/refresh_manifests.py after editing the cached file",
        }
        (MANIFESTS / f"{name}.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{name}: {sha}")


if __name__ == "__main__":
    main()
