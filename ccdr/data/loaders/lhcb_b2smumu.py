"""LHCb b→sμμ Run-3 loader.

Payload contract for `wilson_coefficient_fitter`: iterable of
(observable_name, delta_C9, sigma) triples — every row is already mapped
to its implied δC_9 contribution (SM = 0).
"""
from ccdr.data.loaders._common import read_cached_json


def load_run3():
    data, sha = read_cached_json("lhcb_b2smumu_run3")
    payload = [(name, float(v), float(s)) for name, v, s in data["rows"]]
    return payload, sha
