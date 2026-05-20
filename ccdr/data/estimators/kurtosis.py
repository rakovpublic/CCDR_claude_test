"""Kurtosis estimators (P-A07 void-wall transverse kurtosis)."""
from typing import Iterable, Tuple


def transverse_kurtosis(catalogue) -> Tuple[float, float, int]:
    """Compute sample kurtosis k₄ = E[(x-μ)⁴] / σ⁴ of transverse drifts.

    catalogue payload contract: iterable of float (transverse drift per void).
    Returns (k4, uncertainty, n_voids).
    """
    data = [float(x) for x in catalogue]
    n = len(data)
    if n < 4:
        return (0.0, 0.0, n)
    mean = sum(data) / n
    m2 = sum((x - mean) ** 2 for x in data) / n
    m4 = sum((x - mean) ** 4 for x in data) / n
    if m2 == 0:
        return (0.0, 0.0, n)
    k4 = m4 / (m2 ** 2)
    # standard error of kurtosis ~ sqrt(24/n) for Gaussian null
    unc = (24.0 / n) ** 0.5
    return (k4, unc, n)
