"""NANOGrav 15-yr PTA spectral-index likelihood.

The RVM running tilts the stochastic GW background spectral index relative to
the standard supermassive-black-hole-binary expectation:

    delta_n_GW = -nu / 3        (CCDR §15.4, P-B04)

The cached datum is the measured spectral-index offset relative to SMBHB with
its posterior width. One observable, dof = 1.
"""
from ccdr.data.loaders._common import read_cached_json

_CACHE_NAME = "nanograv_spectral_index"


class NanoGrav15yr:
    name = "nanograv_15yr"
    degrees_of_freedom = 1

    def __init__(self):
        data, sha = read_cached_json(_CACHE_NAME)
        self.data_sha256 = sha
        row = data["rows"][0]
        self._delta_n_obs = float(row[1])
        self._sigma = float(row[2])

    def evaluate_chi2(self, nu: float) -> float:
        delta_n_pred = -nu / 3.0
        resid = (self._delta_n_obs - delta_n_pred) / self._sigma
        return resid * resid


def load() -> NanoGrav15yr:
    return NanoGrav15yr()


__all__ = ["NanoGrav15yr", "load"]
