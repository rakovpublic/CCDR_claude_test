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
