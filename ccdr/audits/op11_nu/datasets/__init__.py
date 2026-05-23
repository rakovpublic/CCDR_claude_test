"""Per-dataset likelihood loaders for the OP11 audit.

`iter_datasets()` returns the fixed, ordered tuple of NuDataset instances the
diagnostics run over. Order is fixed so diagnostic output (and therefore the
report) is deterministic.
"""
from .base import NuDataset
from . import pantheon_plus_sn, desi_dr2_bao, planck_growth, nanograv_15yr

_LOADERS = (
    pantheon_plus_sn.load,
    desi_dr2_bao.load,
    planck_growth.load,
    nanograv_15yr.load,
)


def iter_datasets() -> tuple:
    """Construct each dataset once, in fixed order."""
    return tuple(load() for load in _LOADERS)


__all__ = ["NuDataset", "iter_datasets"]
