"""Path 4: hierarchical Bayesian model, per-dataset nu_i with a global hyperprior.

Model:
    nu_i ~ Normal(mu, tau^2)                       (global mean mu, spread tau)
    dataset i gives a Gaussian likelihood summary (m_i, s_i) on nu_i (Path 2)

Marginalising nu_i analytically, dataset i contributes Normal(m_i | mu, s_i^2 + tau^2).
The joint posterior over (mu, tau) is evaluated on a fixed 2-D grid with flat
priors (mu over the nu grid range, tau over [0, grid span]). No MCMC: the grid
makes the result bit-identical on re-run (CLAUDE_op11_nu.md §11 #2, §14).

The key output is `universality_assessment`: whether the between-dataset spread
tau is consistent with zero (UNIVERSAL), bounded away from zero
(DATASET_DEPENDENT), or in between (MARGINAL). Synthesis only consults Path 4 in
the ambiguous partial-agreement branch.
"""
import math
from typing import List, Optional

from ..candidates import NU_GRID_HI, NU_GRID_LO
from ..results import HierarchicalResult, ProfileLikelihoodResult

DIAGNOSTIC_FN_ID = "path4_hierarchical@v1"

_MU_N = 200
_TAU_N = 200
_TAU_MAX = NU_GRID_HI - NU_GRID_LO

# universality thresholds, expressed relative to the global mean
_UNIVERSAL_RATIO = 0.10        # tau_95_upper / |mu| below this -> spread is negligible
_DEPENDENT_RATIO = 0.30        # tau_mean / |mu| above this -> spread is real


def _linspace(lo: float, hi: float, n: int) -> list:
    if n == 1:
        return [lo]
    step = (hi - lo) / (n - 1)
    return [lo + i * step for i in range(n)]


def _marginal_stats(grid: list, weights: list):
    total = sum(weights)
    if total <= 0.0:
        return grid[0], 0.0
    mean = sum(g * w for g, w in zip(grid, weights)) / total
    var = sum((g - mean) ** 2 * w for g, w in zip(grid, weights)) / total
    return mean, math.sqrt(max(var, 0.0))


def _quantile(grid: list, weights: list, q: float) -> float:
    total = sum(weights)
    if total <= 0.0:
        return grid[-1]
    cum = 0.0
    for g, w in zip(grid, weights):
        cum += w
        if cum / total >= q:
            return g
    return grid[-1]


def run_path4(path2: List[ProfileLikelihoodResult]) -> Optional[HierarchicalResult]:
    summaries = [(r.dataset_name, r.nu_mle, r.nu_mle_uncertainty) for r in path2]
    if len(summaries) < 2:
        return None

    mu_grid = _linspace(NU_GRID_LO, NU_GRID_HI, _MU_N)
    tau_grid = _linspace(0.0, _TAU_MAX, _TAU_N)

    # log-posterior on the (mu, tau) grid, flat priors.
    log_post = [[0.0] * _TAU_N for _ in range(_MU_N)]
    log_max = float("-inf")
    for i, mu in enumerate(mu_grid):
        for j, tau in enumerate(tau_grid):
            lp = 0.0
            for _, m, s in summaries:
                var = s * s + tau * tau
                lp += -0.5 * (math.log(2.0 * math.pi * var) + (m - mu) ** 2 / var)
            log_post[i][j] = lp
            if lp > log_max:
                log_max = lp

    post = [[math.exp(log_post[i][j] - log_max) for j in range(_TAU_N)]
            for i in range(_MU_N)]

    mu_marg = [sum(post[i][j] for j in range(_TAU_N)) for i in range(_MU_N)]
    tau_marg = [sum(post[i][j] for i in range(_MU_N)) for j in range(_TAU_N)]

    nu_global_mean, nu_global_std = _marginal_stats(mu_grid, mu_marg)
    tau_mean, _ = _marginal_stats(tau_grid, tau_marg)
    tau_95_upper = _quantile(tau_grid, tau_marg, 0.95)

    denom = abs(nu_global_mean) if nu_global_mean != 0 else 1.0
    if tau_95_upper / denom < _UNIVERSAL_RATIO:
        assessment = "UNIVERSAL"
    elif tau_mean / denom > _DEPENDENT_RATIO:
        assessment = "DATASET_DEPENDENT"
    else:
        assessment = "MARGINAL"

    tau_eff = max(tau_mean, 1e-12)
    per_dataset = {}
    for name, m, s in summaries:
        prec = 1.0 / (s * s) + 1.0 / (tau_eff * tau_eff)
        post_var = 1.0 / prec
        post_mean = (m / (s * s) + nu_global_mean / (tau_eff * tau_eff)) * post_var
        per_dataset[name] = (post_mean, math.sqrt(post_var))

    return HierarchicalResult(
        nu_global_mean=nu_global_mean,
        nu_global_std=nu_global_std,
        tau_mean=tau_mean,
        tau_95_upper=tau_95_upper,
        universality_assessment=assessment,
        per_dataset_nu=per_dataset,
    )


__all__ = ["run_path4", "DIAGNOSTIC_FN_ID"]
