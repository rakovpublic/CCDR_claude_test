"""Filament catalogue loader (DisPerSE/Bisous on SDSS DR16 / DESI DR2).

Payload contract for `exponential_correlation_fit`: iterable of
(r_mpc_h, C_fil, sigma_C) triples.
"""
from ccdr.data.loaders._common import read_cached_json


def load_disperse_or_bisous():
    data, sha = read_cached_json("filament_catalogues")
    payload = [tuple(row) for row in data["rows"]]
    return payload, sha
