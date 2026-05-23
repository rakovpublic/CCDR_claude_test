"""Synthesis: combine the four diagnostic outputs into one OP11Classification.

The decision tree is explicit and ordered — earlier branches dominate, and the
most-blocking classification wins. `classify(...)` is total: it returns some
OP11Classification for every combination of inputs, never None and never an
uncaught exception (CLAUDE_op11_nu.md §11 #5). tests/test_synthesis_exhaustive.py
covers every branch.
"""
from __future__ import annotations

from typing import List, Optional

from .classification import OP11Classification
from .results import (
    HierarchicalResult,
    PerDatasetChi2Result,
    ProfileLikelihoodResult,
    TensionMetricsResult,
)


def classify(
    path1: List[PerDatasetChi2Result],
    path2: List[ProfileLikelihoodResult],
    path3: List[TensionMetricsResult],
    path4: Optional[HierarchicalResult],
    rationale_present: bool,
    rationale_valid: bool,
) -> OP11Classification:
    """Decision tree for OP11 classification. Order matters."""

    # Guard: nothing to classify, or a dataset too sparse to yield a valid
    # goodness-of-fit (dof < 1).
    if not path1 or any(r.dof < 1 for r in path1):
        return OP11Classification.INSUFFICIENT_DATA

    joint_accepted_by = {r.dataset_name for r in path1
                         if r.nu_label == "joint" and r.accepts_at_95}
    sa_accepted_by = {r.dataset_name for r in path1
                      if r.nu_label == "standalone" and r.accepts_at_95}
    all_datasets = {r.dataset_name for r in path1}

    # Case 1: joint resolves cleanly — every dataset accepts joint, and
    # standalone is rejected by at least one.
    if joint_accepted_by == all_datasets and sa_accepted_by != all_datasets:
        return OP11Classification.RESOLVED_JOINT

    # Case 2: standalone resolves cleanly.
    if sa_accepted_by == all_datasets and joint_accepted_by != all_datasets:
        return OP11Classification.RESOLVED_STANDALONE

    # Case 3: both extractors rejected by every dataset. Look to Path 2 for a
    # consensus third value; if none exists, no nu fits all data.
    if not joint_accepted_by and not sa_accepted_by:
        third = _find_consensus_third_value(path2)
        if third is not None:
            return OP11Classification.RESOLVED_THIRD_VALUE
        return OP11Classification.MODEL_MISSPECIFIED

    # Both accepted everywhere, or partial agreement: the data do not by
    # themselves prefer one extractor.

    # Hierarchical model may still declare nu universal despite Path 1 noise;
    # joint then overlaps the universal posterior.
    if path4 is not None and path4.universality_assessment == "UNIVERSAL":
        return OP11Classification.RESOLVED_JOINT

    # Genuine disagreement. Promote to DOCUMENTED only with a valid,
    # human-authored RATIONALE.md; otherwise stop at UNRESOLVED.
    if rationale_present and rationale_valid:
        return OP11Classification.DATASET_DEPENDENT_DOCUMENTED
    return OP11Classification.DATASET_DEPENDENT_UNRESOLVED


def _find_consensus_third_value(
    profiles: List[ProfileLikelihoodResult],
) -> Optional[float]:
    """Return a nu value in the 1-sigma overlap of every per-dataset profile,
    or None if the profiles have no common 1-sigma region."""
    if not profiles:
        return None
    lo = max(p.nu_mle - p.nu_mle_uncertainty for p in profiles)
    hi = min(p.nu_mle + p.nu_mle_uncertainty for p in profiles)
    if lo <= hi:
        return 0.5 * (lo + hi)
    return None


__all__ = ["classify"]
