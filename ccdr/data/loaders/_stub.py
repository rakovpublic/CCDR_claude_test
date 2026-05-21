"""Stub loader helper (legacy).

Real loaders raise `DataUnavailable` from `_common` directly. This module
remains for the small set of sources that have no public-data loader
(P-A15 CDT-plusplus output).
"""
from ccdr.data.loaders._common import DataUnavailable


def stub(manifest_name: str, data_source_label: str):
    """Build a no-op loader that raises DataUnavailable."""
    def _load():
        raise DataUnavailable(
            f"No cached data for '{data_source_label}'. "
            f"Populate manifests/{manifest_name}.json and place the file "
            f"under data/cache/."
        )
    _load.manifest_name = manifest_name
    _load.data_source_label = data_source_label
    return _load


__all__ = ["DataUnavailable", "stub"]
