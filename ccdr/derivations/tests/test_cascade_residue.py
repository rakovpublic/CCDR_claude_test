from ccdr.derivations.cascade_residue import (
    mass_tower, subbao_harmonics, frozen_live_fraction,
)
from ccdr.core.status import DerivationStatus


def test_mass_tower_pending():
    assert mass_tower().status == DerivationStatus.PARAMETER_PENDING


def test_mass_tower_geometric():
    r = mass_tower(m_0=100.0, rho=0.5, n_total=8)
    assert r.status == DerivationStatus.DERIVED
    tower = r.parameters_used["tower_gev"]
    for i in range(1, len(tower)):
        assert abs(tower[i] / tower[i - 1] - 0.5) < 1e-12


def test_subbao_pending():
    assert subbao_harmonics().status == DerivationStatus.PARAMETER_PENDING


def test_subbao_derived():
    r = subbao_harmonics(rho=0.4, k_star=0.1)
    assert r.status == DerivationStatus.DERIVED
    assert abs(r.value - 0.04) < 1e-12


def test_frozen_live_fraction_decreases_with_n():
    r1 = frozen_live_fraction(rho=0.6, n_total=4)
    r2 = frozen_live_fraction(rho=0.6, n_total=8)
    assert r2.value < r1.value
