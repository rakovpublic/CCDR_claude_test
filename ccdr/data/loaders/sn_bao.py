"""Pantheon+ SNe Ia and DESI DR2 BAO loaders.

Payload contract for `w_z_reconstruction`: iterable of (z, w_eff, sigma_w).
"""
from ccdr.data.loaders._common import read_cached_json


def _load_rows(name):
    data, sha = read_cached_json(name)
    payload = [tuple(row) for row in data["rows"]]
    return payload, sha


def load_pantheon_plus():
    return _load_rows("pantheon_plus")


def load_desi_dr2():
    return _load_rows("desi_dr2")
