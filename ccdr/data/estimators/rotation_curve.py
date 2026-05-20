"""Rotation-curve a₀ extractor (P-A03)."""
from typing import Iterable, Tuple


def rotation_curve_a0_extractor(curves) -> Tuple[float, float, int]:
    """Estimate effective MOND acceleration scale a₀ from rotation curves.

    Payload contract: iterable of (radius_kpc, v_circ_km_s) curves
    (one curve = list of (r, v) tuples).
    Returns (a0_eff_m_s2, uncertainty, n_curves).
    """
    curves = list(curves)
    n = len(curves)
    if n == 0:
        return (0.0, 0.0, 0)
    KPC_M = 3.0857e19
    KM_M = 1.0e3
    a0_per_curve = []
    for curve in curves:
        pts = list(curve)
        if len(pts) < 3:
            continue
        # transition acceleration: v²/r at outer point
        r_kpc, v_kms = pts[-1]
        r_m = r_kpc * KPC_M
        v_ms = v_kms * KM_M
        if r_m > 0:
            a0_per_curve.append(v_ms ** 2 / r_m)
    n_used = len(a0_per_curve)
    if n_used == 0:
        return (0.0, 0.0, 0)
    mean = sum(a0_per_curve) / n_used
    if n_used > 1:
        var = sum((x - mean) ** 2 for x in a0_per_curve) / (n_used - 1)
        unc = (var / n_used) ** 0.5
    else:
        unc = mean * 0.5
    return (mean, unc, n_used)
