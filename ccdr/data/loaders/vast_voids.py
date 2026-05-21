"""VAST VoidFinder catalogue loader.

Payload contract for `transverse_kurtosis`: iterable of float transverse
drifts (one entry per void).
"""
from ccdr.data.loaders._common import read_cached_json


def load_vast_catalogue():
    data, sha = read_cached_json("vast_voids")
    payload = [float(x) for x in data["rows"]]
    return payload, sha


load_catalogue = load_vast_catalogue
