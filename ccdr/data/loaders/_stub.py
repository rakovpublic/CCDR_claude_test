"""Stub loader helper.

Every loader follows the same shape: return (payload, sha256) where payload
is whatever the estimator expects (a dict, a numpy array, a list of records).
Until real data is wired in, loaders raise FileNotFoundError with a clear
manifest-name reference. Callers must catch and return
`MeasurementStatus.DATA_UNAVAILABLE`.
"""


class DataUnavailable(FileNotFoundError):
    """Raised by stub loaders when no cached data file is present."""


def stub(manifest_name: str, data_source_label: str):
    """Build a no-op loader that raises DataUnavailable."""
    def _load():
        raise DataUnavailable(
            f"No cached data for '{data_source_label}'. "
            f"Populate manifests/{manifest_name}.json and place the file under data/cache/."
        )
    _load.manifest_name = manifest_name
    _load.data_source_label = data_source_label
    return _load
