"""Path 2: per-dataset profile likelihood over the nu grid.

For each dataset, scan log-likelihood = -chi2(nu)/2 over THIRD_VALUE_GRID and
locate the maximum-likelihood nu and its 1-sigma width. The scan runs in
log10(nu) space (the grid is log-spaced); the MLE and curvature come from a
parabolic refinement around the grid minimum of chi2.

Output feeds:
  - the third-value search in synthesis (overlap of per-dataset 1-sigma bands)
  - Path 3 tension metrics (per-dataset Gaussian summary)
  - Path 4 hierarchical model (per-dataset likelihood location/scale)

Deterministic: a fixed grid, no sampling.
"""
import math
from typing import List

from ..candidates import THIRD_VALUE_GRID
from ..datasets import iter_datasets
from ..results import ProfileLikelihoodResult

DIAGNOSTIC_FN_ID = "path2_profile_likelihood@v1"

_LN10 = math.log(10.0)


def _refine_minimum(u: list, chi2: list):
    """Parabolic refinement of the chi2 minimum in log10(nu) space.

    Returns (u_mle, sigma_u) where sigma_u is the 1-sigma half-width in u
    (Delta chi2 = 1). If the minimum is at a grid edge or the local curvature
    is non-convex, nu is treated as unconstrained and sigma_u is the full grid
    span."""
    n = len(u)
    imin = min(range(n), key=lambda i: chi2[i])
    full_span = u[-1] - u[0]
    if imin == 0 or imin == n - 1:
        return u[imin], full_span
    y0, y1, y2 = chi2[imin - 1], chi2[imin], chi2[imin + 1]
    curv = y0 - 2.0 * y1 + y2
    h = u[imin + 1] - u[imin]
    if curv <= 0.0:
        return u[imin], full_span
    u_mle = u[imin] - 0.5 * h * (y2 - y0) / curv
    a = curv / (2.0 * h * h)               # chi2 ~ a (u - u_mle)^2 + const
    sigma_u = 1.0 / math.sqrt(a)
    return u_mle, sigma_u


def run_path2(datasets=None) -> List[ProfileLikelihoodResult]:
    if datasets is None:
        datasets = iter_datasets()
    grid = THIRD_VALUE_GRID
    u = [math.log10(g) for g in grid]
    results: List[ProfileLikelihoodResult] = []
    for ds in datasets:
        chi2 = [float(ds.evaluate_chi2(g)) for g in grid]
        loglike = tuple(-0.5 * c for c in chi2)
        u_mle, sigma_u = _refine_minimum(u, chi2)
        u_mle = max(u[0], min(u[-1], u_mle))
        nu_mle = 10.0 ** u_mle
        # Delta method: sigma_nu = nu * ln(10) * sigma_u, capped at grid span.
        nu_span = grid[-1] - grid[0]
        nu_unc = min(nu_mle * _LN10 * sigma_u, nu_span)
        results.append(ProfileLikelihoodResult(
            dataset_name=ds.name,
            nu_grid=grid,
            log_likelihood=loglike,
            nu_mle=nu_mle,
            nu_mle_uncertainty=nu_unc,
        ))
    return results


__all__ = ["run_path2", "DIAGNOSTIC_FN_ID"]
