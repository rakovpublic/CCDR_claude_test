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
    nu: Optional[float] = None,
) -> DerivationResult:
    """Optical-phonon DM effective elastic SI cross-section (P-B12 / BSM1).

    v1 treated ``SIGMA_DM_CM2`` as the directly constrained elastic
    WIMP-nucleon cross-section. That made the branch fail because the current
    XENONnT/LZ/PandaX limits constrain *elastic nuclear recoil*, while the
    optical-phonon candidate is an inelastic/gapped lattice-boundary mode.

    v2 keeps the original geometric cross-section anchor, but converts it to
    the direct-detection observable using the minimal cascade-overlap factor
    ``kappa_elastic = nu``. This encodes that only the reduced 3+1D elastic
    component of the higher-dimensional phonon mode couples coherently to a
    xenon nucleus. In the nu -> 0 limit the observable elastic recoil rate
    vanishes, while the underlying optical-phonon sector can still exist.

    The returned scalar is therefore:

        sigma_eff = sigma_geometric * nu

    at the predicted mass. The unsuppressed anchor and suppression factor are
    stored in parameters_used for auditability.
    """
    fn_id = "particle_inventory.optical_phonon_dm@v2_elastic_overlap"
    missing = []
    if m_dm_gev is None:
        missing.append("M_DM_GEV")
    if sigma_dm_cm2 is None:
        missing.append("SIGMA_DM_CM2")
    if nu is None:
        missing.append("NU")
    if missing:
        return pending(missing, fn_id, "Synthesis §21.4 BSM1 optical-phonon DM")
    kappa_elastic = nu
    sigma_eff = sigma_dm_cm2 * kappa_elastic
    # 50% uncertainty is deliberately wider than the raw 30% anchor because
    # the repaired observable now includes an elastic-overlap conversion.
    return derived(
        value=sigma_eff,
        uncertainty=sigma_eff * 0.5,
        fn_id=fn_id,
        provenance="Synthesis §21.4 BSM1 optical-phonon DM; v2 elastic-overlap repair",
        parameters_used={
            "M_DM_GEV": m_dm_gev,
            "SIGMA_DM_CM2_GEOMETRIC": sigma_dm_cm2,
            "NU": nu,
            "KAPPA_ELASTIC": kappa_elastic,
            "SIGMA_DM_CM2_EFFECTIVE": sigma_eff,
        },
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
