"""Pantheon+ SN late-time expansion-history likelihood.

nu enters through the RVM running of the vacuum energy density, which tilts the
effective dark-energy equation of state away from -1:

    w(z; nu) = -1 + nu * (1 + z) ** (-BETA_RVM)        (CCDR §15.2, P-A08)

The cooling exponent BETA_RVM is the framework's *functional form*, not the
quantity OP11 is deciding, so it is inlined as a fixed constant with a citation
rather than imported — keeping this loader framework-blind (§11 #3).

`evaluate_chi2(nu)` is a pure goodness-of-fit of the binned w_eff(z) data
against w(z; nu) with no free parameters, so dof = number of redshift bins.
"""
from ccdr.data.loaders._common import read_cached_json

# Leading-order RVM cooling exponent (CCDR §15.2). Fixed; not an OP11 unknown.
BETA_RVM = 1.0

_CACHE_NAME = "pantheon_plus"


class PantheonPlusSN:
    name = "pantheon_plus_sn"

    def __init__(self):
        data, sha = read_cached_json(_CACHE_NAME)
        self.data_sha256 = sha
        self._z = tuple(row[0] for row in data["rows"])
        self._w = tuple(row[1] for row in data["rows"])
        self._sigma = tuple(row[2] for row in data["rows"])
        self.degrees_of_freedom = len(self._z)

    def _w_pred(self, z: float, nu: float) -> float:
        return -1.0 + nu * (1.0 + z) ** (-BETA_RVM)

    def evaluate_chi2(self, nu: float) -> float:
        total = 0.0
        for z, w, sigma in zip(self._z, self._w, self._sigma):
            resid = (w - self._w_pred(z, nu)) / sigma
            total += resid * resid
        return total


def load() -> PantheonPlusSN:
    return PantheonPlusSN()


__all__ = ["PantheonPlusSN", "load"]
