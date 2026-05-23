"""Exhaustive coverage of the synthesis decision tree (CLAUDE_op11_nu.md §11 #5).

classify(...) is total: every input combination maps to exactly one
OP11Classification, never None and never an exception. Fixtures below hit each
branch classify can produce; AUDIT_NOT_RUN / AUDIT_INCOMPLETE are lifecycle
states owned by run_audit, not classify.
"""
import itertools

import pytest

from ccdr.audits.op11_nu.classification import OP11Classification as C
from ccdr.audits.op11_nu.results import (
    HierarchicalResult, PerDatasetChi2Result, ProfileLikelihoodResult,
)
from ccdr.audits.op11_nu.synthesis import classify


def chi2_row(name, label, accepts, dof=1):
    return PerDatasetChi2Result(
        dataset_name=name, nu_value=1.0, nu_label=label,
        chi2=1.0, dof=dof, p_value=(0.5 if accepts else 0.001),
        accepts_at_95=accepts,
    )


def path1(spec):
    """spec: {dataset: (joint_accepts, standalone_accepts)}."""
    rows = []
    for name, (j, s) in spec.items():
        rows.append(chi2_row(name, "joint", j))
        rows.append(chi2_row(name, "standalone", s))
    return rows


def prof(name, mle, unc):
    return ProfileLikelihoodResult(
        dataset_name=name, nu_grid=(mle,), log_likelihood=(0.0,),
        nu_mle=mle, nu_mle_uncertainty=unc,
    )


def hier(assessment):
    return HierarchicalResult(
        nu_global_mean=5e-3, nu_global_std=1e-3, tau_mean=1e-4,
        tau_95_upper=2e-4, universality_assessment=assessment,
        per_dataset_nu={},
    )


def test_insufficient_data_empty():
    assert classify([], [], [], None, False, False) == C.INSUFFICIENT_DATA


def test_insufficient_data_dof_zero():
    rows = [chi2_row("A", "joint", True, dof=0),
            chi2_row("A", "standalone", True, dof=0)]
    assert classify(rows, [], [], None, False, False) == C.INSUFFICIENT_DATA


def test_resolved_joint():
    p1 = path1({"A": (True, True), "B": (True, False)})
    assert classify(p1, [], [], None, False, False) == C.RESOLVED_JOINT


def test_resolved_standalone():
    p1 = path1({"A": (True, True), "B": (False, True)})
    assert classify(p1, [], [], None, False, False) == C.RESOLVED_STANDALONE


def test_resolved_third_value_overlap():
    p1 = path1({"A": (False, False), "B": (False, False)})
    p2 = [prof("A", 1.0e-3, 5.0e-4), prof("B", 1.2e-3, 5.0e-4)]
    assert classify(p1, p2, [], None, False, False) == C.RESOLVED_THIRD_VALUE


def test_model_misspecified_no_overlap():
    p1 = path1({"A": (False, False), "B": (False, False)})
    p2 = [prof("A", 1.0e-3, 1.0e-5), prof("B", 4.0e-2, 1.0e-5)]
    assert classify(p1, p2, [], None, False, False) == C.MODEL_MISSPECIFIED


def test_partial_universal_promotes_to_joint():
    # both extractors accepted everywhere -> falls to the hierarchical branch
    p1 = path1({"A": (True, True), "B": (True, True)})
    assert classify(p1, [], [], hier("UNIVERSAL"), False, False) == C.RESOLVED_JOINT


def test_partial_documented_with_valid_rationale():
    p1 = path1({"A": (True, False), "B": (False, True)})  # crossed: neither clean
    out = classify(p1, [], [], hier("DATASET_DEPENDENT"), True, True)
    assert out == C.DATASET_DEPENDENT_DOCUMENTED


def test_partial_unresolved_without_rationale():
    p1 = path1({"A": (True, False), "B": (False, True)})
    out = classify(p1, [], [], hier("DATASET_DEPENDENT"), False, False)
    assert out == C.DATASET_DEPENDENT_UNRESOLVED


def test_partial_unresolved_rationale_present_but_invalid():
    p1 = path1({"A": (True, False), "B": (False, True)})
    out = classify(p1, [], [], None, True, False)
    assert out == C.DATASET_DEPENDENT_UNRESOLVED


def test_classify_is_total():
    """No input combination yields None or raises."""
    reachable = {
        C.INSUFFICIENT_DATA, C.RESOLVED_JOINT, C.RESOLVED_STANDALONE,
        C.RESOLVED_THIRD_VALUE, C.MODEL_MISSPECIFIED,
        C.DATASET_DEPENDENT_DOCUMENTED, C.DATASET_DEPENDENT_UNRESOLVED,
    }
    specs = [
        {"A": (j, s)} for j, s in itertools.product([True, False], repeat=2)
    ] + [
        {"A": (ja, sa), "B": (jb, sb)}
        for ja, sa, jb, sb in itertools.product([True, False], repeat=4)
    ]
    p2_variants = [[], [prof("A", 1e-3, 5e-4), prof("B", 1.1e-3, 5e-4)],
                   [prof("A", 1e-3, 1e-6), prof("B", 4e-2, 1e-6)]]
    p4_variants = [None, hier("UNIVERSAL"), hier("DATASET_DEPENDENT"), hier("MARGINAL")]
    for spec in specs:
        for p2 in p2_variants:
            for p4 in p4_variants:
                for rp, rv in [(False, False), (True, False), (True, True)]:
                    out = classify(path1(spec), p2, [], p4, rp, rv)
                    assert isinstance(out, C)
                    assert out in reachable
