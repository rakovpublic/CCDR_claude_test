"""Path 3: pairwise tension metrics between datasets.

For each pair of datasets we summarise each Path-2 profile as a Gaussian on nu
(mean = nu_mle, sigma = nu_mle_uncertainty) and compute the standard tension
statistics that anesthetic computes from nested-sampling chains, in their
closed Gaussian form (deterministic, no sampler):

  tension_sigma : |mu1 - mu2| / sqrt(sigma1^2 + sigma2^2)
  log_R         : Bayes ratio R = Z_12 / (Z_1 Z_2), flat prior of width Delta
                  (Marshall et al. 2006)
  log_I         : information / prior-shrinkage term, log(Delta / posterior width)
  log_S         : suspiciousness, log_R - log_I (prior-volume independent;
                  Handley & Lemos 2019)

Path 3 is reported for transparency; the classification decision tree in
synthesis.py keys off Path 1/2/4, not these scalars.
"""
import math
from itertools import combinations
from typing import List

from ..candidates import NU_GRID_HI, NU_GRID_LO
from ..results import ProfileLikelihoodResult, TensionMetricsResult

DIAGNOSTIC_FN_ID = "path3_tension_metrics@v1"

_PRIOR_WIDTH = NU_GRID_HI - NU_GRID_LO
_LOG_2PI = math.log(2.0 * math.pi)


def _pair_metrics(a: ProfileLikelihoodResult, b: ProfileLikelihoodResult) -> TensionMetricsResult:
    mu1, s1 = a.nu_mle, a.nu_mle_uncertainty
    mu2, s2 = b.nu_mle, b.nu_mle_uncertainty
    sigma_quad = s1 * s1 + s2 * s2
    if sigma_quad <= 0.0:
        tension = float("inf")
        log_R = float("-inf")
        log_I = 0.0
        log_S = float("-inf")
    else:
        d2 = (mu1 - mu2) ** 2
        tension = math.sqrt(d2 / sigma_quad)
        log_R = (math.log(_PRIOR_WIDTH) - 0.5 * (_LOG_2PI + math.log(sigma_quad))
                 - 0.5 * d2 / sigma_quad)
        sigma_post_sq = (s1 * s1 * s2 * s2) / sigma_quad
        log_I = math.log(_PRIOR_WIDTH) - 0.5 * (_LOG_2PI + math.log(sigma_post_sq))
        log_S = log_R - log_I
    pair = tuple(sorted((a.dataset_name, b.dataset_name)))
    return TensionMetricsResult(
        dataset_pair=pair,
        log_R=log_R,
        log_I=log_I,
        log_suspiciousness=log_S,
        tension_sigma=tension,
    )


def run_path3(path2: List[ProfileLikelihoodResult]) -> List[TensionMetricsResult]:
    ordered = sorted(path2, key=lambda r: r.dataset_name)
    return [_pair_metrics(a, b) for a, b in combinations(ordered, 2)]


__all__ = ["run_path3", "DIAGNOSTIC_FN_ID"]
