"""Exclusion-curve consistency checks (P-A13, P-A17).

Returns fraction of predicted parameter point that survives the union of
exclusion curves.
"""
from typing import Iterable, Sequence, Tuple


def exclusion_consistency_check(curves) -> Tuple[float, float, int]:
    """Each curve is a sequence of (param_value, allowed_upper_limit).
    Returns (mean allowed limit at the curve midpoint, uncertainty, n_curves).
    """
    curves = [list(c) for c in curves]
    n = len(curves)
    if n == 0:
        return (0.0, 0.0, 0)
    mids = []
    for c in curves:
        if not c:
            continue
        c.sort(key=lambda p: p[0])
        mid = c[len(c) // 2][1]
        mids.append(mid)
    if not mids:
        return (0.0, 0.0, n)
    mean = sum(mids) / len(mids)
    if len(mids) > 1:
        var = sum((m - mean) ** 2 for m in mids) / (len(mids) - 1)
        unc = (var / len(mids)) ** 0.5
    else:
        unc = mean * 0.5
    return (mean, unc, n)
