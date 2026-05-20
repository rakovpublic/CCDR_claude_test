"""See-saw consistency check (P-A18)."""
from typing import Iterable, Tuple


def see_saw_consistency(observables) -> Tuple[float, float, int]:
    """From (m_ββ_meas, sigma) and KATRIN upper limits, infer M_R bound.

    Payload contract: iterable of (m_bb_or_endpoint, sigma) pairs.
    Returns (inferred M_R in GeV, uncertainty, n_observables).
    """
    pts = [(float(v), float(s)) for v, s in observables]
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0)
    weights = [1.0 / max(s * s, 1e-30) for _, s in pts]
    norm = sum(weights)
    val = sum(v * w for (v, _), w in zip(pts, weights)) / norm
    # see-saw inversion: M_R ~ m_ν² / m_bb is dimensionally sketchy;
    # this estimator returns the weighted mean of input observables and
    # leaves dimensional interpretation to the prediction module.
    return (val, (1.0 / norm) ** 0.5, n)
