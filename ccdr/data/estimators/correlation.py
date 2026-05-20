"""Correlation-function estimators (P-A01 filament texture)."""
from typing import Iterable, Tuple


def exponential_correlation_fit(catalogue) -> Tuple[float, float, int]:
    """Fit C(r) = A · exp(-r / r_texture) to a filament catalogue.

    Returns (r_texture, uncertainty, n_pairs).

    Catalogue payload contract: iterable of (r_value, C_value, sigma) triples.
    """
    points = list(catalogue)
    n = len(points)
    if n < 3:
        return (0.0, 0.0, n)
    # crude linear fit in log space: log C = log A - r / r_tex
    import math
    rs = [p[0] for p in points]
    cs = [max(p[1], 1e-300) for p in points]
    log_cs = [math.log(c) for c in cs]
    mean_r = sum(rs) / n
    mean_log_c = sum(log_cs) / n
    num = sum((rs[i] - mean_r) * (log_cs[i] - mean_log_c) for i in range(n))
    den = sum((rs[i] - mean_r) ** 2 for i in range(n))
    if den == 0:
        return (0.0, 0.0, n)
    slope = num / den
    if slope >= 0:
        return (0.0, 0.0, n)
    r_tex = -1.0 / slope
    resid = [log_cs[i] - (mean_log_c + slope * (rs[i] - mean_r)) for i in range(n)]
    var = sum(r * r for r in resid) / max(1, n - 2)
    unc = (var / max(1e-30, den)) ** 0.5 * r_tex ** 2
    return (r_tex, unc, n)
