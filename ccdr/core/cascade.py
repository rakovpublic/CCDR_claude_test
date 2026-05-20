"""Cascade primitives: χ_k geometry function, ν algebra, mass-tower helper.

Pure-math module. No I/O. May be imported by derivations.
"""
import math
from typing import Optional


def chi_geom(k: int, n_total: int) -> float:
    """Geometric χ_k factor for cascade stage k of n_total.

    Convention: χ_k is dimensionless, χ_0 = 1, monotonically decreasing.
    Concrete form here: χ_k = ((n_total - k) / n_total)**0.5
    """
    if n_total <= 0 or k < 0 or k > n_total:
        raise ValueError(f"invalid cascade indices k={k} n_total={n_total}")
    return ((n_total - k) / n_total) ** 0.5


def mass_tower(m_0: float, rho: float, n_total: int) -> list:
    """Geometric mass tower m_k = m_0 · rho**k for k = 0 .. n_total - 4."""
    if rho <= 0:
        raise ValueError("rho must be positive")
    return [m_0 * (rho ** k) for k in range(max(0, n_total - 4) + 1)]


def nu_algebra_residue(nu: float, k: int) -> float:
    """Cascade-residue amplitude at stage k as power of ν."""
    return nu ** max(1, k)


def cascade_propagator(nu: Optional[float], k: int, n_total: int) -> Optional[float]:
    """Combined geometry × residue propagator. Returns None if nu is None."""
    if nu is None:
        return None
    return chi_geom(k, n_total) * nu_algebra_residue(nu, k)


__all__ = [
    "chi_geom",
    "mass_tower",
    "nu_algebra_residue",
    "cascade_propagator",
]
