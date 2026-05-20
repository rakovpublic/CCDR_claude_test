"""Wilson-coefficient fitter (P-A10 b→sμμ)."""
from typing import Iterable, Tuple


def wilson_coefficient_fitter(observables) -> Tuple[float, float, int]:
    """Extract δC_9 from LHCb b→sμμ observables.

    Payload contract: iterable of (observable_name, value, sigma).
    Returns (mean δC_9, uncertainty, n_observables).
    """
    pts = [(name, float(v), float(s)) for name, v, s in observables]
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0)
    weights = [1.0 / max(s * s, 1e-30) for _, _, s in pts]
    norm = sum(weights)
    val = sum(v * w for (_, v, _), w in zip(pts, weights)) / norm
    return (val, (1.0 / norm) ** 0.5, n)
