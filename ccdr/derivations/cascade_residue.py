"""Cascade-residue derivations: mass tower, ν-dependent amplitudes, sub-BAO harmonics.

P-A02 (mass tower), P-A06 (sub-BAO harmonics), P-B06 (frozen-vs-live DM).
"""
import math
from typing import Optional

from ccdr.core.status import DerivationResult, DerivationStatus
from ccdr.derivations.base import pending, derived

_PROV_TOWER = "CCDR §4.5 + §7 (cascade mass tower)"
_PROV_SUBBAO = "CCDR §13 (sub-BAO cascade harmonics)"


def mass_tower(
    m_0: Optional[float] = None,
    rho: Optional[float] = None,
    n_total: Optional[int] = None,
) -> DerivationResult:
    """Geometric mass tower {m_k = m_0 · rho**k}.

    Value field contains the lightest predicted mass (k=1). Full list is in
    parameters_used['tower_gev']. This is sufficient for the measurement
    counterpart (P-A02 consistency check against current XENONnT/LZ/PandaX
    exclusions, which compare each peak).
    """
    fn_id = "cascade_residue.mass_tower@v1"
    missing = []
    if m_0 is None:
        missing.append("M_0_DM_GEV")
    if rho is None:
        missing.append("RHO_CASCADE")
    if n_total is None:
        missing.append("N_CASCADE")
    if missing:
        return pending(missing, fn_id, _PROV_TOWER)

    tower = [m_0 * (rho ** k) for k in range(max(1, n_total - 3))]
    return derived(
        value=tower[0],
        uncertainty=tower[0] * 0.2,
        fn_id=fn_id,
        provenance=_PROV_TOWER,
        parameters_used={"M_0_DM_GEV": m_0, "RHO_CASCADE": rho,
                         "N_CASCADE": n_total, "tower_gev": tower},
    )


def subbao_harmonics(
    rho: Optional[float] = None,
    k_star: Optional[float] = None,
) -> DerivationResult:
    """Predicted sub-BAO harmonic peak position k_h = k_star · rho.

    P-A06 BOSS Lyα measurement.
    """
    fn_id = "cascade_residue.subbao_harmonics@v1"
    missing = []
    if rho is None:
        missing.append("RHO_CASCADE")
    if k_star is None:
        missing.append("K_STAR")
    if missing:
        return pending(missing, fn_id, _PROV_SUBBAO)
    k_h = k_star * rho
    return derived(
        value=k_h,
        uncertainty=k_h * 0.15,
        fn_id=fn_id,
        provenance=_PROV_SUBBAO,
        parameters_used={"RHO_CASCADE": rho, "K_STAR": k_star},
    )


def frozen_live_fraction(
    rho: Optional[float] = None,
    n_total: Optional[int] = None,
) -> DerivationResult:
    """Predicted f_live (live cascade-DM fraction) from cascade retention.

    f_live = ρ^(n_total - 1) (geometric retention fraction).
    """
    fn_id = "cascade_residue.frozen_live_fraction@v1"
    missing = []
    if rho is None:
        missing.append("RHO_CASCADE")
    if n_total is None:
        missing.append("N_CASCADE")
    if missing:
        return pending(missing, fn_id, "CCDR §13 cascade retention")
    f_live = rho ** max(0, n_total - 1)
    return derived(
        value=f_live,
        uncertainty=f_live * 0.3,
        fn_id=fn_id,
        provenance="CCDR §13 cascade retention",
        parameters_used={"RHO_CASCADE": rho, "N_CASCADE": n_total},
    )


def fsigma8_modification(
    f_live: Optional[float] = None,
    alpha_growth: Optional[float] = None,
    z: float = 0.5,
) -> DerivationResult:
    """Predicted multiplicative modification to fσ_8(z) (P-B06).

    fσ_8(z) / fσ_8_ΛCDM(z) = 1 + alpha_growth · f_live · (1+z)
    """
    fn_id = "cascade_residue.fsigma8_modification@v1"
    missing = []
    if f_live is None:
        missing.append("F_LIVE")
    if alpha_growth is None:
        missing.append("ALPHA_GROWTH")
    if missing:
        return pending(missing, fn_id, "CCDR §13 frozen-vs-live fσ_8 deficit")
    val = 1.0 + alpha_growth * f_live * (1.0 + z)
    return derived(
        value=val,
        uncertainty=abs(alpha_growth * f_live) * 0.4,
        fn_id=fn_id,
        provenance="CCDR §13 frozen-vs-live growth modification",
        parameters_used={"F_LIVE": f_live, "ALPHA_GROWTH": alpha_growth, "z_eval": z},
    )


def delta_kappa_density(
    c_kappa: Optional[float] = None,
    nu: Optional[float] = None,
) -> DerivationResult:
    """Density-correlated Δκ amplitude Δκ = c_κ · ν (P-B07)."""
    fn_id = "cascade_residue.delta_kappa_density@v1"
    missing = []
    if c_kappa is None:
        missing.append("C_KAPPA")
    if nu is None:
        missing.append("NU")
    if missing:
        return pending(missing, fn_id, "CCDR §13 density-stratified κ")
    val = c_kappa * nu
    return derived(
        value=val,
        uncertainty=abs(val) * 0.3,
        fn_id=fn_id,
        provenance="CCDR §13 density-stratified Δκ",
        parameters_used={"C_KAPPA": c_kappa, "NU": nu},
    )


def mu_y_per_stage(
    per_stage_energy_injection: Optional[float] = None,
    n_total: Optional[int] = None,
) -> DerivationResult:
    """Predicted total μ spectral distortion from cascade stages (P-B08).

    Toy model: μ = N · ΔE_k (sums over all cascade stages above z=10⁶).
    Returns μ as the scalar value; y has the same scale within a factor.
    """
    fn_id = "cascade_residue.mu_y_per_stage@v1"
    missing = []
    if per_stage_energy_injection is None:
        missing.append("PER_STAGE_ENERGY_INJECTION")
    if n_total is None:
        missing.append("N_CASCADE")
    if missing:
        return pending(missing, fn_id, "CCDR §6 μ, y from cascade-stage injection")
    mu = n_total * per_stage_energy_injection
    return derived(
        value=mu,
        uncertainty=mu * 0.5,
        fn_id=fn_id,
        provenance="CCDR §6 μ from staged energy injection",
        parameters_used={"PER_STAGE_ENERGY_INJECTION": per_stage_energy_injection,
                         "N_CASCADE": n_total},
    )


def dm_phase_space_zscore(
    z_score_amplitude: Optional[float] = None,
) -> DerivationResult:
    """Predicted DM phase-space drift z-score amplitude (P-B10)."""
    fn_id = "cascade_residue.dm_phase_space_zscore@v1"
    if z_score_amplitude is None:
        return pending(["Z_SCORE_AMPLITUDE"], fn_id,
                       "P-B10 live-DM phase-space response")
    return derived(
        value=z_score_amplitude,
        uncertainty=abs(z_score_amplitude) * 0.3,
        fn_id=fn_id,
        provenance="CCDR §13 live-DM phase-space response",
        parameters_used={"Z_SCORE_AMPLITUDE": z_score_amplitude},
    )
