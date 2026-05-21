"""Generic scalar weighted-mean estimator.

Used by Tier B predictions whose measurement is a small set of
(value, sigma) pairs already on the comparison units of the derivation.
"""
from typing import Iterable, Tuple


def weighted_mean(rows) -> Tuple[float, float, int]:
    """Inverse-variance weighted mean of (value, sigma) pairs."""
    rows = [(float(v), float(s)) for v, s in rows]
    if not rows:
        return (0.0, 0.0, 0)
    inv = [1.0 / max(s * s, 1e-60) for _v, s in rows]
    norm = sum(inv)
    mean = sum(v * w for (v, _), w in zip(rows, inv)) / norm
    return (mean, (1.0 / norm) ** 0.5, len(rows))


def select_observable(rows, name) -> Tuple[float, float, int]:
    """Pick a named (name, value, sigma) row; return (value, sigma, 1)."""
    for n, v, s in rows:
        if n == name:
            return (float(v), float(s), 1)
    return (0.0, 0.0, 0)
