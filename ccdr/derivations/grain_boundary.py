"""Grain-boundary phonon-scattering derivations.

Shared mechanism across P-A01 (filament texture), P-A03 (a₀ evolution),
P-A07 (void k₄), P-A12 (joint density-sign), P-B03 (η/s).

Provenance: CCDR §8.2 (filaments), §8.3 (voids), §6.1 (Milgrom a₀).
"""
import math
from typing import Optional

from ccdr.core.status import DerivationResult, DerivationStatus
from ccdr.derivations.base import pending, derived

_PROV_VOID = "CCDR §8.3 eq 8.17 (grain-boundary scattering kernel)"
_PROV_FILA = "CCDR §8.2 (filament texture correlation)"
_PROV_A0 = "CCDR §6.1 (Milgrom a₀ z-evolution)"


def predict_void_kurtosis(
    nu: Optional[float] = None,
    r_grain_mpc_h: Optional[float] = None,
) -> DerivationResult:
    """Predicted transverse kurtosis k₄ of void-wall radial-drift distribution.

    δk₄ = c_4(ν) · (r_grain / r_void_wall)²,  c_4(ν) = ν · π² / 6
    """
    fn_id = "grain_boundary.predict_void_kurtosis@v1"
    missing = []
    if nu is None:
        missing.append("NU")
    if r_grain_mpc_h is None:
        missing.append("R_GRAIN_MPC_H")
    if missing:
        return pending(missing, fn_id, _PROV_VOID)

    r_void_wall_mpc_h = 30.0  # typical void-wall scale; treated as fixed prior
    c4 = nu * math.pi ** 2 / 6.0
    delta_k4 = c4 * (r_grain_mpc_h / r_void_wall_mpc_h) ** 2
    k4 = 3.0 + delta_k4
    rel_unc_sq = (0.10) ** 2 + (2 * 0.30) ** 2
    uncertainty = abs(delta_k4) * rel_unc_sq ** 0.5
    return derived(
        value=k4,
        uncertainty=uncertainty,
        fn_id=fn_id,
        provenance=_PROV_VOID,
        parameters_used={"NU": nu, "R_GRAIN_MPC_H": r_grain_mpc_h},
    )


def predict_filament_texture(
    nu: Optional[float] = None,
    r_grain_mpc_h: Optional[float] = None,
    r_star_bao: Optional[float] = None,
) -> DerivationResult:
    """Predicted filament orientational correlation length r_texture (Mpc/h).

    Heuristic form: r_texture = r* · (1 + ν · (r_grain / r*)) (CCDR §8.2).
    Returns the correlation length itself; amplitude A is a free
    normalisation absorbed by the estimator.
    """
    fn_id = "grain_boundary.predict_filament_texture@v1"
    missing = []
    if nu is None:
        missing.append("NU")
    if r_grain_mpc_h is None:
        missing.append("R_GRAIN_MPC_H")
    if r_star_bao is None:
        missing.append("R_STAR_BAO")
    if missing:
        return pending(missing, fn_id, _PROV_FILA)

    r_tex = r_star_bao * (1.0 + nu * (r_grain_mpc_h / r_star_bao))
    rel_unc = (0.15 ** 2 + 0.25 ** 2) ** 0.5
    return derived(
        value=r_tex,
        uncertainty=r_tex * rel_unc,
        fn_id=fn_id,
        provenance=_PROV_FILA,
        parameters_used={"NU": nu, "R_GRAIN_MPC_H": r_grain_mpc_h,
                         "R_STAR_BAO": r_star_bao},
    )


def a0_z_evolution(
    nu: Optional[float] = None,
    z_star: Optional[float] = None,
    z: float = 1.0,
) -> DerivationResult:
    """Predicted a₀(z)/a₀(0) at redshift z, with α_a derived from cascade ν.

    For z > z_star: a₀(z) = a₀(0) · (1 + α_a (z - z_star)), α_a = ν · π.
    """
    fn_id = "grain_boundary.a0_z_evolution@v1"
    missing = []
    if nu is None:
        missing.append("NU")
    if z_star is None:
        missing.append("Z_TRANSITION")
    if missing:
        return pending(missing, fn_id, _PROV_A0)

    alpha_a = nu * math.pi
    if z <= z_star:
        ratio = 1.0
    else:
        ratio = 1.0 + alpha_a * (z - z_star)
    return derived(
        value=ratio,
        uncertainty=abs(alpha_a) * 0.3 * max(0.0, z - z_star),
        fn_id=fn_id,
        provenance=_PROV_A0,
        parameters_used={"NU": nu, "Z_TRANSITION": z_star, "z_eval": z},
    )


def joint_density_sign(
    nu: Optional[float] = None,
) -> DerivationResult:
    """Predicted SIGN of joint density-stratified excess for P-A12 (CL4 composition).

    Returns +1 if ν > 0 (same-sign excess in high/low subsets), 0 if ν == 0.
    """
    fn_id = "grain_boundary.joint_density_sign@v1"
    if nu is None:
        return pending(["NU"], fn_id, "CL4 composition of P-A01 + P-A07")
    sign = 1.0 if nu > 0 else (-1.0 if nu < 0 else 0.0)
    return derived(
        value=sign,
        uncertainty=0.0,
        fn_id=fn_id,
        provenance="CL4 joint density-sign (composition)",
        parameters_used={"NU": nu},
    )


def eta_over_s_enhancement(
    nu: Optional[float] = None,
    c_eta_s: Optional[float] = None,
) -> DerivationResult:
    """η/s = (1/4π)(1 + c_η/s · ν). P-B03."""
    fn_id = "grain_boundary.eta_over_s_enhancement@v1"
    missing = []
    if nu is None:
        missing.append("NU")
    if c_eta_s is None:
        missing.append("C_ETA_S")
    if missing:
        return pending(missing, fn_id, "CCDR §6.x phase-boundary scattering")
    kss = 1.0 / (4.0 * math.pi)
    value = kss * (1.0 + c_eta_s * nu)
    return derived(
        value=value,
        uncertainty=abs(value - kss) * 0.3,
        fn_id=fn_id,
        provenance="KSS bound + phase-boundary scattering",
        parameters_used={"NU": nu, "C_ETA_S": c_eta_s},
    )
