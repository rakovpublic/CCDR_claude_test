"""Synthetic-data tests for estimators. No framework imports allowed here either."""
import random

from ccdr.data.estimators.kurtosis import transverse_kurtosis
from ccdr.data.estimators.correlation import exponential_correlation_fit
from ccdr.data.estimators.mass_tower import mass_tower_consistency_check
from ccdr.data.estimators.bound_check import consistency_check_N_le_11


def test_kurtosis_gaussian_close_to_3():
    random.seed(0)
    data = [random.gauss(0, 1) for _ in range(5000)]
    k4, unc, n = transverse_kurtosis(data)
    assert n == 5000
    assert abs(k4 - 3.0) < 0.5


def test_kurtosis_short_returns_zero():
    k4, unc, n = transverse_kurtosis([1.0, 2.0])
    assert n == 2 and k4 == 0.0


def test_correlation_fit_recovers_scale():
    import math
    r_tex_true = 100.0
    pts = [(r, math.exp(-r / r_tex_true), 0.01) for r in range(10, 200, 10)]
    r_tex_fit, unc, n = exponential_correlation_fit(pts)
    assert n == len(pts)
    assert abs(r_tex_fit - r_tex_true) / r_tex_true < 0.05


def test_mass_tower_consistency():
    curves = [[(1.0, 1e-44)], [(1.0, 1e-50)]]
    frac, unc, n = mass_tower_consistency_check(curves, sigma_floor=1e-46)
    assert n == 2
    assert frac == 0.5


def test_bound_check_le_11():
    val, _, _ = consistency_check_N_le_11(N=11)
    assert val == 1.0
    val, _, _ = consistency_check_N_le_11(N=12)
    assert val == 0.0
