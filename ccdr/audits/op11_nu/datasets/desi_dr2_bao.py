"""DESI DR2 BAO sound-horizon-shift likelihood.

The RVM running shifts the BAO scale at leading order by

    delta_r_star / r_star = nu / 2        (CCDR §15.2, P-B01)

The cached datum is the mean fractional shift over 0 < z < 2 with its
uncertainty. One observable, no fitted nuisance, so dof = 1.

This is the highest-leverage dataset for OP11: the joint extractor predicts a
shift of order 1e-3 (well inside the measured band) while the standalone
extractor (~1e-5) predicts essentially zero shift, which the data exclude.
"""
from ccdr.data.loaders._common import read_cached_json

_CACHE_NAME = "desi_dr2_bao"


class DesiDr2Bao:
    name = "desi_dr2_bao"
    degrees_of_freedom = 1

    def __init__(self):
        data, sha = read_cached_json(_CACHE_NAME)
        self.data_sha256 = sha
        row = data["rows"][0]
        self._delta_obs = float(row[1])
        self._sigma = float(row[2])

    def evaluate_chi2(self, nu: float) -> float:
        delta_pred = nu / 2.0
        resid = (self._delta_obs - delta_pred) / self._sigma
        return resid * resid


def load() -> DesiDr2Bao:
    return DesiDr2Bao()


__all__ = ["DesiDr2Bao", "load"]
