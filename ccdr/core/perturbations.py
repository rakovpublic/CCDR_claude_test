"""Cascade-modified linear perturbation theory primitives.

Pure-math helpers used by rvm_cosmology and bulk_weyl derivations.
"""
from typing import Optional


def growth_modification(z: float, nu: Optional[float], beta: Optional[float]) -> Optional[float]:
    """Multiplicative modification to ΛCDM growth factor D(z):
        D_CCDR(z) = D_ΛCDM(z) · (1 + nu · (1+z)^(-beta))
    Returns the multiplicative factor (not D itself)."""
    if nu is None or beta is None:
        return None
    return 1.0 + nu * (1.0 + z) ** (-beta)


def bao_shift_fraction(nu: Optional[float]) -> Optional[float]:
    """δr*/r* = ν / 2 (RVM leading order)."""
    if nu is None:
        return None
    return nu / 2.0


__all__ = ["growth_modification", "bao_shift_fraction"]
