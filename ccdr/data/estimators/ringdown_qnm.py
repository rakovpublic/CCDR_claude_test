"""Ringdown QNM population estimator (P-A05)."""
from typing import Iterable, Tuple


def population_deviation(events) -> Tuple[float, float, int]:
    """Return (mean fractional deviation δω/ω from Kerr, uncertainty, n_events).

    Payload contract: iterable of (omega_meas, omega_kerr) pairs.
    """
    pts = [(a, b) for a, b in events if b]
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0)
    deltas = [(a - b) / b for a, b in pts]
    mean = sum(deltas) / n
    if n > 1:
        var = sum((d - mean) ** 2 for d in deltas) / (n - 1)
        unc = (var / n) ** 0.5
    else:
        unc = abs(mean) * 0.5 + 0.01
    return (mean, unc, n)
