from ccdr.derivations.grain_boundary import (
    predict_void_kurtosis,
    predict_filament_texture,
    a0_z_evolution,
    joint_density_sign,
)
from ccdr.core.status import DerivationStatus


def test_void_pending_when_nu_missing():
    r = predict_void_kurtosis(nu=None, r_grain_mpc_h=10.0, n_cascade=8)
    assert r.status == DerivationStatus.PARAMETER_PENDING
    assert "NU" in r.missing_parameters


def test_void_lambda_cdm_limit():
    r = predict_void_kurtosis(nu=0.0, r_grain_mpc_h=10.0, n_cascade=8)
    assert r.status == DerivationStatus.DERIVED
    assert abs(r.value - 3.0) < 1e-10


def test_void_monotonic_in_nu():
    r1 = predict_void_kurtosis(nu=1e-3, r_grain_mpc_h=10.0, n_cascade=8)
    r2 = predict_void_kurtosis(nu=5e-3, r_grain_mpc_h=10.0, n_cascade=8)
    assert r2.value > r1.value


def test_void_scales_as_inverse_r_grain_squared_after_repair():
    r1 = predict_void_kurtosis(nu=5e-3, r_grain_mpc_h=10.0, n_cascade=8)
    r2 = predict_void_kurtosis(nu=5e-3, r_grain_mpc_h=20.0, n_cascade=8)
    ratio = (r2.value - 3.0) / (r1.value - 3.0)
    assert abs(ratio - 0.25) < 0.01


def test_void_claim_k4_above_four_for_frozen_like_parameters():
    r = predict_void_kurtosis(nu=5.08e-3, r_grain_mpc_h=10.0, n_cascade=8)
    assert r.status == DerivationStatus.DERIVED
    assert r.value > 4.0
    assert r.derivation_function_id.endswith("@v2")


def test_filament_texture_pending():
    r = predict_filament_texture()
    assert r.status == DerivationStatus.PARAMETER_PENDING


def test_filament_texture_derived():
    r = predict_filament_texture(nu=5e-3, r_grain_mpc_h=10.0, r_star_bao=147.0)
    assert r.status == DerivationStatus.DERIVED
    assert r.value > 147.0  # bigger than the BAO scale


def test_a0_pending():
    assert a0_z_evolution().status == DerivationStatus.PARAMETER_PENDING


def test_a0_below_transition_unchanged():
    r = a0_z_evolution(nu=5e-3, z_star=0.3, z=0.1)
    assert abs(r.value - 1.0) < 1e-12


def test_a0_above_transition_increases():
    r = a0_z_evolution(nu=5e-3, z_star=0.3, z=1.5)
    assert r.value > 1.0


def test_joint_density_sign_positive_when_nu_positive():
    assert joint_density_sign(nu=1e-3).value == 1.0
