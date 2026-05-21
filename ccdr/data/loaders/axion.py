"""ADMX and HAYSTAC axion-haloscope exclusion loaders.

Payload contract for `exclusion_consistency_check`: each loader returns
ONE curve, a sequence of (m_a_ueV, g_a_gamma_ul) pairs.
"""
from ccdr.data.loaders._common import read_cached_json


def _load_curve(name):
    data, sha = read_cached_json(name)
    payload = [tuple(row) for row in data["rows"]]
    return payload, sha


def load_admx():
    return _load_curve("admx")


def load_haystac():
    return _load_curve("haystac")
