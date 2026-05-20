"""Joint posterior composition (P-A19)."""
from typing import Iterable, Tuple


def joint_posterior(component_measurements) -> Tuple[float, float, int]:
    """Combine component (value, uncertainty) pairs into a joint test statistic.

    Returns (geometric mean of |value|, quadrature-summed uncertainty, n_components).
    """
    pts = [(float(v), float(u)) for v, u in component_measurements]
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0)
    prod = 1.0
    for v, _ in pts:
        prod *= abs(v) if v != 0 else 1e-30
    mean = prod ** (1.0 / n)
    unc = (sum(u * u for _, u in pts)) ** 0.5
    return (mean, unc, n)
