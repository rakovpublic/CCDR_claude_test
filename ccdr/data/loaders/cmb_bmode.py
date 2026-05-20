"""BICEP/Keck 18 and Planck PR4 B-mode bandpower loaders.

Payload contract for `bmode_template_fit`: iterable of
(ell, C_BB_uK2, sigma_uK2) triples.
"""
from ccdr.data.loaders._common import read_cached_json


def _load_bandpowers(name):
    data, sha = read_cached_json(name)
    payload = [tuple(row) for row in data["rows"]]
    return payload, sha


def load_bk18_bandpowers():
    return _load_bandpowers("bk18")


def load_planck_pr4_bmode():
    return _load_bandpowers("planck_pr4_bmode")
