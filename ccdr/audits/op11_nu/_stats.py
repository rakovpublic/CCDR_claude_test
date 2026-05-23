"""Pure-stdlib statistics for the OP11 audit.

The parent project declares zero runtime dependencies and computes everything
with `math`. The audit follows the same rule: no numpy, no scipy, no MCMC
samplers. This keeps the audit deterministic by construction (CLAUDE.md §11
constraint 2) — there are no random seeds whose change could flip a
classification, and no heavyweight optional dependency that CI might lack.

Functions here are validated against scipy in development; see
tests/test_diagnostics_deterministic.py for the determinism contract.
"""
import math

_SQRT2 = math.sqrt(2.0)


def _gamma_p_series(s: float, x: float) -> float:
    """Lower regularized incomplete gamma P(s, x) via series (x < s + 1)."""
    if x <= 0.0:
        return 0.0
    term = 1.0 / s
    total = term
    n = s
    for _ in range(10000):
        n += 1.0
        term *= x / n
        total += term
        if abs(term) < abs(total) * 1e-15:
            break
    return total * math.exp(-x + s * math.log(x) - math.lgamma(s))


def _gamma_q_cf(s: float, x: float) -> float:
    """Upper regularized incomplete gamma Q(s, x) via continued fraction
    (x >= s + 1), Lentz's algorithm."""
    tiny = 1e-300
    b = x + 1.0 - s
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - s)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return math.exp(-x + s * math.log(x) - math.lgamma(s)) * h


def regularized_gamma_q(s: float, x: float) -> float:
    """Upper regularized incomplete gamma function Q(s, x) = 1 - P(s, x)."""
    if x < 0.0 or s <= 0.0:
        raise ValueError("regularized_gamma_q requires s > 0 and x >= 0")
    if x == 0.0:
        return 1.0
    if x < s + 1.0:
        return 1.0 - _gamma_p_series(s, x)
    return _gamma_q_cf(s, x)


def chi2_sf(x: float, df: int) -> float:
    """Survival function (upper tail, the p-value) of the chi-square
    distribution with `df` degrees of freedom: P(X > x)."""
    if df < 1:
        raise ValueError("chi2_sf requires df >= 1")
    if x <= 0.0:
        return 1.0
    return regularized_gamma_q(df / 2.0, x / 2.0)


def normal_cdf(z: float) -> float:
    """Standard-normal CDF Φ(z)."""
    return 0.5 * math.erfc(-z / _SQRT2)


def normal_sf(z: float) -> float:
    """Standard-normal survival function 1 - Φ(z)."""
    return 0.5 * math.erfc(z / _SQRT2)


def sigma_from_two_sided_p(p: float) -> float:
    """Number of standard deviations whose two-tailed probability is `p`.

    Inverse of p = 2(1 - Φ(σ)). Used to express a discrepancy probability as a
    Gaussian-sigma tension. Bisection — deterministic, no scipy.ppf."""
    if p <= 0.0:
        return float("inf")
    if p >= 1.0:
        return 0.0
    lo, hi = 0.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 2.0 * normal_sf(mid) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


__all__ = [
    "regularized_gamma_q",
    "chi2_sf",
    "normal_cdf",
    "normal_sf",
    "sigma_from_two_sided_p",
]
