"""Particle inventory derivations: axion mass (P-A17), νR mass (P-A18)."""
from typing import Optional

from ccdr.core.status import DerivationResult
from ccdr.derivations.base import pending, derived


def axion_mass(f_pq: Optional[float] = None) -> DerivationResult:
    """Predicted QCD-axion mass m_a from PQ scale f_PQ.

    Standard relation: m_a ≈ 5.7 μeV · (10¹² GeV / f_PQ).
    """
    fn_id = "particle_inventory.axion_mass@v1"
    if f_pq is None:
        return pending(["F_PQ"], fn_id, "Synthesis §21.4 BSM2")
    m_a_uev = 5.7 * (1.0e12 / f_pq)
    return derived(
        value=m_a_uev,
        uncertainty=m_a_uev * 0.05,
        fn_id=fn_id,
        provenance="Synthesis §21.4 BSM2 axion mass-PQ relation",
        parameters_used={"F_PQ": f_pq},
    )


def optical_phonon_dm(
    m_dm_gev: Optional[float] = None,
    sigma_dm_cm2: Optional[float] = None,
) -> DerivationResult:
    """Optical-phonon DM mass and cross-section (P-B12 / BSM1).

    Returns the predicted SI cross-section at the predicted mass as the
    scalar value; the predicted mass is recorded in parameters_used.
    """
    fn_id = "particle_inventory.optical_phonon_dm@v1"
    missing = []
    if m_dm_gev is None:
        missing.append("M_DM_GEV")
    if sigma_dm_cm2 is None:
        missing.append("SIGMA_DM_CM2")
    if missing:
        return pending(missing, fn_id, "Synthesis §21.4 BSM1 optical-phonon DM")
    return derived(
        value=sigma_dm_cm2,
        uncertainty=sigma_dm_cm2 * 0.3,
        fn_id=fn_id,
        provenance="Synthesis §21.4 BSM1 optical-phonon DM",
        parameters_used={"M_DM_GEV": m_dm_gev, "SIGMA_DM_CM2": sigma_dm_cm2},
    )


def koide_q() -> DerivationResult:
    """Koide Q = 2/3 theorem (P-D01, asserted from C₆ᵥ symmetry)."""
    fn_id = "particle_inventory.koide_q@v1"
    return derived(
        value=2.0 / 3.0,
        uncertainty=1.0e-6,
        fn_id=fn_id,
        provenance="SM-D5 / §21 C₆ᵥ symmetry on Hermitian mass matrix",
        parameters_used={},
    )


def right_handed_nu_mass(crystal_boundary_energy: Optional[float] = None) -> DerivationResult:
    """Predicted right-handed neutrino mass M_R from crystal boundary energy.

    Heuristic: M_R = crystal_boundary_energy (GeV).
    """
    fn_id = "particle_inventory.right_handed_nu_mass@v1"
    if crystal_boundary_energy is None:
        return pending(
            ["CRYSTAL_BOUNDARY_ENERGY"], fn_id,
            "Synthesis §21.4 BSM4 νR see-saw",
        )
    return derived(
        value=crystal_boundary_energy,
        uncertainty=crystal_boundary_energy * 0.3,
        fn_id=fn_id,
        provenance="Synthesis §21.4 BSM4 νR mass from crystal boundary",
        parameters_used={"CRYSTAL_BOUNDARY_ENERGY": crystal_boundary_energy},
    )
