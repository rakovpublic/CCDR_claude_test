"""w(z) reconstruction estimator (P-A08)."""
from typing import Iterable, Tuple


def w_z_reconstruction(joint_data) -> Tuple[float, float, int]:
    """Estimate w(z) - (-1) at z ≈ 0.5 from (z, w_meas, sigma_w) triples.

    Returns (mean Δw, uncertainty, n).
    """
    pts = [(float(z), float(w), float(s)) for z, w, s in joint_data]
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0)
    deltas = [(w + 1.0, s) for _, w, s in pts]
    inv_var = [1.0 / max(s * s, 1e-30) for _, s in deltas]
    norm = sum(inv_var)
    mean = sum(d * w for (d, _), w in zip(deltas, inv_var)) / norm
    unc = (1.0 / norm) ** 0.5
    return (mean, unc, n)
