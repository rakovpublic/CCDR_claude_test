"""EHT M87* / Sgr A* loader.

Payload contract for `boundary_deformation_residual`: iterable of
(target_name, fractional_residual_vs_kerr, sigma) triples.
"""
from ccdr.data.loaders._common import read_cached_json


def load_m87_sgrA():
    data, sha = read_cached_json("eht_m87_sgrA")
    payload = [(f"eht.{name}", float(r), float(s)) for name, r, s in data["rows"]]
    return payload, sha
