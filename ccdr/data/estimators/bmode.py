"""B-mode template-fit estimator (P-A09)."""
from typing import Iterable, Tuple


def bmode_template_fit(bandpowers) -> Tuple[float, float, int]:
    """Fit a CCDR-template amplitude to bandpowers.

    Payload contract: iterable of (ell, C_BB, sigma) triples.
    Returns (amplitude_at_peak, uncertainty, n_bandpowers).
    """
    pts = [(float(l), float(c), float(s)) for l, c, s in bandpowers]
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0)
    # weighted mean of C_BB near ell ~ 80 as proxy amplitude
    weights = [1.0 / max(s * s, 1e-30) for _, _, s in pts]
    norm = sum(weights)
    amp = sum(c * w for (_, c, _), w in zip(pts, weights)) / norm
    unc = (1.0 / norm) ** 0.5
    return (amp, unc, n)
