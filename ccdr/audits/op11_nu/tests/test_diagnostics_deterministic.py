"""Determinism + sanity for the diagnostics (CLAUDE_op11_nu.md §7, §11 #2).

Each diagnostic returns identical output on the same inputs across runs. chi2 is
finite and non-negative, p-values lie in [0, 1], and evaluate_chi2(nu) is
bowl-shaped (unimodal) in nu for every dataset.
"""
import math

from ccdr.audits.op11_nu.candidates import THIRD_VALUE_GRID
from ccdr.audits.op11_nu.datasets import iter_datasets
from ccdr.audits.op11_nu.diagnostics import (
    run_path1, run_path2, run_path3, run_path4,
)


def test_path1_deterministic_and_valid():
    a = run_path1()
    b = run_path1()
    assert a == b
    for r in a:
        assert math.isfinite(r.chi2) and r.chi2 >= 0.0
        assert 0.0 <= r.p_value <= 1.0
        assert r.dof >= 1


def test_path2_deterministic():
    assert run_path2() == run_path2()


def test_path3_deterministic():
    p2 = run_path2()
    assert run_path3(p2) == run_path3(p2)


def test_path4_deterministic():
    p2 = run_path2()
    assert run_path4(p2) == run_path4(p2)


def test_full_chain_deterministic():
    ds = iter_datasets()
    p2a = run_path2(ds)
    p2b = run_path2(ds)
    assert run_path4(p2a) == run_path4(p2b)


def test_evaluate_chi2_is_unimodal_in_nu():
    for ds in iter_datasets():
        vals = [ds.evaluate_chi2(nu) for nu in THIRD_VALUE_GRID]
        assert all(math.isfinite(v) and v >= 0.0 for v in vals)
        argmin = min(range(len(vals)), key=lambda i: vals[i])
        tol = 1e-9
        for i in range(1, argmin + 1):
            assert vals[i] <= vals[i - 1] + tol, f"{ds.name} not non-increasing before min"
        for i in range(argmin + 1, len(vals)):
            assert vals[i] >= vals[i - 1] - tol, f"{ds.name} not non-decreasing after min"
