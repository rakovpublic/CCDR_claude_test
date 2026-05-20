"""Direct-detection loaders: XENONnT 2025, LZ 2024, PandaX-4T 2024.

Each loader returns (curve, sha) where curve is a list of
(m_dm_gev, sigma_si_cm2_ul) tuples.
"""
from ccdr.data.loaders._common import read_cached_json


def _load_exclusion_curve(name):
    data, sha = read_cached_json(name)
    payload = [tuple(row) for row in data["rows"]]
    return payload, sha


def load_xenonnt_2025():
    return _load_exclusion_curve("xenonnt_2025")


def load_lz_2024():
    return _load_exclusion_curve("lz_2024")


def load_pandax_2024():
    return _load_exclusion_curve("pandax_2024")
