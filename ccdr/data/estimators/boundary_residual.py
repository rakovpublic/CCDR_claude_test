"""Boundary-deformation residual estimator (P-A11)."""
from typing import Iterable, Tuple


def boundary_deformation_residual(joint) -> Tuple[float, float, int]:
    """Residual from EHT shadow + GWTC-3 ringdowns combined into a slope.

    Payload contract: iterable of (ell_or_mode_id, residual, sigma).
    """
    pts = [(name, float(r), float(s)) for name, r, s in joint]
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0)
    weights = [1.0 / max(s * s, 1e-30) for _, _, s in pts]
    norm = sum(weights)
    val = sum(r * w for (_, r, _), w in zip(pts, weights)) / norm
    return (val, (1.0 / norm) ** 0.5, n)
