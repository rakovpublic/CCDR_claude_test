"""BOSS Lyα flux power spectrum loader.

Payload contract for `harmonic_peak_detector`: iterable of (k, P) pairs.
"""
from ccdr.data.loaders._common import read_cached_json


def load_pf_k():
    data, sha = read_cached_json("boss_lyalpha_pf_k")
    payload = [tuple(row) for row in data["rows"]]
    return payload, sha
