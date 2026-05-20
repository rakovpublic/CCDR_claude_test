from ccdr.core.status import DerivationStatus
from ccdr.derivations.algebra_bounds import dao_max_N
from ccdr.derivations.theory_consistency import as_eprl_gamma
from ccdr.derivations.lattice_count import cdt_chirality
from ccdr.derivations.rvm_cosmology import w_z_drift, bao_shift, pta_spectral_shift
from ccdr.derivations.photon_dispersion import dark_photon_epsilon, cosmic_string_tension
from ccdr.derivations.boundary_deformation import qnm_deviation, epsilon_spectrum
from ccdr.derivations.bulk_weyl import bmode_template, bmode_shape
from ccdr.derivations.flavour_wilson import b_to_smumu_pattern
from ccdr.derivations.particle_inventory import axion_mass, right_handed_nu_mass
from ccdr.derivations.joint_inference import posterior


def test_dao_bound_is_eleven():
    r = dao_max_N()
    assert r.status == DerivationStatus.DERIVED
    assert r.value == 11.0


def test_as_eprl_consistency_zero():
    r = as_eprl_gamma()
    assert r.status == DerivationStatus.DERIVED
    assert r.value == 0.0


def test_cdt_chirality_incomplete_without_N4():
    assert cdt_chirality().status == DerivationStatus.DERIVATION_INCOMPLETE


def test_cdt_chirality_analytic_limit():
    r = cdt_chirality(N_4=400)
    assert r.value == 200.0


def test_rvm_w_drift_pending():
    assert w_z_drift().status == DerivationStatus.PARAMETER_PENDING


def test_bao_shift_value():
    r = bao_shift(nu=0.005)
    assert abs(r.value - 0.0025) < 1e-12


def test_pta_shift_sign():
    r = pta_spectral_shift(nu=0.005)
    assert r.value < 0


def test_dark_photon_pending():
    assert dark_photon_epsilon().status == DerivationStatus.PARAMETER_PENDING


def test_cosmic_string_pending():
    assert cosmic_string_tension().status == DerivationStatus.PARAMETER_PENDING


def test_qnm_deviation_pending():
    assert qnm_deviation().status == DerivationStatus.PARAMETER_PENDING


def test_epsilon_spectrum_pending():
    assert epsilon_spectrum().status == DerivationStatus.PARAMETER_PENDING


def test_bmode_template_pending():
    assert bmode_template().status == DerivationStatus.PARAMETER_PENDING


def test_bmode_shape_derived():
    assert bmode_shape().status == DerivationStatus.DERIVED


def test_b2smumu_pending():
    assert b_to_smumu_pattern().status == DerivationStatus.PARAMETER_PENDING


def test_axion_pending():
    assert axion_mass().status == DerivationStatus.PARAMETER_PENDING


def test_axion_scales_inverse_f():
    r1 = axion_mass(f_pq=1e12)
    r2 = axion_mass(f_pq=2e12)
    assert abs(r2.value * 2 - r1.value) < 1e-9


def test_nuR_pending():
    assert right_handed_nu_mass().status == DerivationStatus.PARAMETER_PENDING


def test_posterior_no_components_pending():
    assert posterior().status == DerivationStatus.PARAMETER_PENDING
