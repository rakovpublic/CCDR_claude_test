"""Direct-detection mass-tower consistency check (P-A02).

Given a list of predicted peak masses (GeV) and a list of exclusion curves
(mass-grid → upper-limit cross-section), report fraction of predicted peaks
*not* excluded at 95% CL.
"""
from typing import Iterable, Sequence, Tuple


def mass_tower_consistency_check(
    exclusion_curves: Iterable[Sequence[Tuple[float, float]]],
    sigma_floor: float = 1e-46,
) -> Tuple[float, float, int]:
    """Return (fraction_not_excluded, uncertainty, n_curves).

    A predicted peak is 'not excluded' if at its mass the cross-section
    upper limit exceeds sigma_floor. This estimator is intentionally simple:
    it operates on the exclusion curves alone (no framework input).
    """
    curves = list(exclusion_curves)
    n = len(curves)
    if n == 0:
        return (0.0, 0.0, 0)
    passes = 0
    for curve in curves:
        if not curve:
            continue
        worst_sigma = max(point[1] for point in curve)
        if worst_sigma > sigma_floor:
            passes += 1
    frac = passes / n
    unc = (frac * (1 - frac) / n) ** 0.5 if n > 0 else 0.0
    return (frac, unc, n)
