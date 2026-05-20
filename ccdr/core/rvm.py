"""Running Vacuum Model (RVM) primitives: ρ_vac(H), C₀(t), Λ(t).

Pure math. No data, no I/O.
"""
from typing import Optional


def rho_vac(H: float, nu: Optional[float], rho_vac_0: float = 1.0) -> Optional[float]:
    """ρ_vac(H) = ρ_vac_0 + ν · H² (leading-order RVM ansatz)."""
    if nu is None:
        return None
    return rho_vac_0 + nu * H * H


def C_0(t: float, beta: Optional[float] = None) -> Optional[float]:
    """Cascade cooling coefficient C₀(t) ~ t^(-beta)."""
    if beta is None or t <= 0:
        return None
    return t ** (-beta)


def Lambda_t(t: float, nu: Optional[float], beta: Optional[float],
             Lambda_0: float = 1.0) -> Optional[float]:
    """Λ(t) = Λ_0 · (1 + ν · C₀(t))."""
    if nu is None or beta is None:
        return None
    c0 = C_0(t, beta)
    if c0 is None:
        return None
    return Lambda_0 * (1.0 + nu * c0)


__all__ = ["rho_vac", "C_0", "Lambda_t"]
