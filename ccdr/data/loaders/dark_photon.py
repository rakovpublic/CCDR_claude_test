"""BaBar / LHCb dark-photon exclusion loaders.

Payload contract for `exclusion_consistency_check`: each loader returns
ONE curve, a sequence of (m_Aprime_gev, epsilon2_ul) pairs.
"""
from ccdr.data.loaders._common import read_cached_json


def _load_curve(name):
    data, sha = read_cached_json(name)
    payload = [tuple(row) for row in data["rows"]]
    return payload, sha


def load_babar_limits():
    return _load_curve("babar_dark_photon")


def load_lhcb_dp():
    return _load_curve("lhcb_dark_photon")
