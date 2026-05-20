"""Harmonic peak detector (P-A06 sub-BAO Lyα)."""
from typing import Iterable, Tuple


def harmonic_peak_detector(spectrum) -> Tuple[float, float, int]:
    """Identify dominant harmonic peak in (k, P) spectrum.

    Returns (k_peak, uncertainty, n_bins).
    """
    pts = [(float(k), float(p)) for k, p in spectrum]
    n = len(pts)
    if n < 4:
        return (0.0, 0.0, n)
    k_peak, p_peak = max(pts, key=lambda kp: kp[1])
    dk = pts[1][0] - pts[0][0] if n > 1 else 0.0
    return (k_peak, abs(dk), n)
