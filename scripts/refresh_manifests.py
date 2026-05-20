"""Regenerate SHA256 manifests for every file in ccdr/data/cache/.

Usage: python scripts/refresh_manifests.py
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "ccdr" / "data" / "cache"
MANIFESTS = ROOT / "ccdr" / "data" / "manifests"


def main():
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    for p in sorted(CACHE.glob("*.json")):
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        name = p.stem
        try:
            with open(p) as f:
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
