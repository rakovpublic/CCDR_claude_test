"""Frozen result dataclasses for the OP11 audit (CLAUDE_op11_nu.md §5).

All diagnostic outputs are immutable (frozen=True) so a computed result cannot
be mutated between diagnosis and synthesis. Tuples are used in place of lists
for the same reason.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

from .classification import OP11Classification


@dataclass(frozen=True)
class PerDatasetChi2Result:
    dataset_name: str
    nu_value: float
    nu_label: str               # "joint" | "standalone" | "third_value_grid_<i>"
    chi2: float
    dof: int
    p_value: float
    accepts_at_95: bool         # p_value > 0.05


@dataclass(frozen=True)
class ProfileLikelihoodResult:
    dataset_name: str
    nu_grid: tuple              # immutable; sorted ascending
    log_likelihood: tuple
    nu_mle: float
    nu_mle_uncertainty: float


@dataclass(frozen=True)
class TensionMetricsResult:
    dataset_pair: tuple         # ("pantheon_plus_sn", "desi_dr2_bao")
    log_R: float
    log_I: float
    log_suspiciousness: float
    tension_sigma: float


@dataclass(frozen=True)
class HierarchicalResult:
    nu_global_mean: float
    nu_global_std: float
    tau_mean: float             # between-dataset spread (posterior mean)
    tau_95_upper: float
    universality_assessment: str   # "UNIVERSAL" | "DATASET_DEPENDENT" | "MARGINAL"
    per_dataset_nu: Dict[str, tuple]  # name -> (mean, std)


@dataclass(frozen=True)
class OP11Report:
    classification: OP11Classification
    committed_nu: Optional[float]
    committed_nu_uncertainty: Optional[float]
    provenance: str
    audit_revision: str         # git SHA at audit time
    data_revision: Dict[str, str]  # per-dataset sha256
    diagnostics: dict           # path1, path2, path3, path4 results
    rationale_sha256: Optional[str]  # only if DOCUMENTED
    timestamp: datetime
    framework_revision_flag: bool   # True only if MODEL_MISSPECIFIED
    notes: str = ""


__all__ = [
    "PerDatasetChi2Result",
    "ProfileLikelihoodResult",
    "TensionMetricsResult",
    "HierarchicalResult",
    "OP11Report",
]
