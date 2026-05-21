"""RVM cosmology derivations: w(z) drift, BAO shift, growth deficit.

P-A08 (w drift), P-B01 (BAO shift), P-B04 (PTA spectral index), P-B06 (fσ_8).
"""
from typing import Optional

from ccdr.core.status import DerivationResult, DerivationStatus
from ccdr.derivations.base import pending, derived
from ccdr.core.perturbations import bao_shift_fraction


def w_z_drift(
    nu_bulk: Optional[float] = None,
    beta: Optional[float] = None,
    z: float = 0.5,
) -> DerivationResult:
    """Secular drift of dark-energy equation of state w(z).

    w(z) = -1 + ν_bulk · (1 + z) ** (-β)  (P-A08 leading order).
    Returns w(z=z) - (-1) = ν_bulk · (1+z)^(-β).
    """
    fn_id = "rvm_cosmology.w_z_drift@v1"
    missing = []
    if nu_bulk is None:
        missing.append("NU_BULK")
    if beta is None:
        missing.append("BETA_COOLING")
    if missing:
        return pending(missing, fn_id, "CCDR §15.2 RVM w(z)")

    dw = nu_bulk * (1.0 + z) ** (-beta)
    return derived(
        value=dw,
        uncertainty=abs(dw) * 0.25,
        fn_id=fn_id,
        provenance="CCDR §15.2 w(z) RVM drift",
        parameters_used={"NU_BULK": nu_bulk, "BETA_COOLING": beta, "z_eval": z},
    )


def bao_shift(nu: Optional[float] = None) -> DerivationResult:
    """δr*/r* = ν/2 (P-B01 RVM leading order)."""
    fn_id = "rvm_cosmology.bao_shift@v1"
    if nu is None:
        return pending(["NU"], fn_id, "CCDR §15.2 / RVM δr*/r* = ν/2")
    val = bao_shift_fraction(nu)
    return derived(
        value=val,
        uncertainty=abs(val) * 0.3,
        fn_id=fn_id,
        provenance="RVM δr*/r* = ν/2",
        parameters_used={"NU": nu},
    )


def pta_spectral_shift(nu: Optional[float] = None) -> DerivationResult:
    """PTA GW spectral index shift δn_GW = -ν/3 relative to SMBHB -2/3."""
    fn_id = "rvm_cosmology.pta_spectral_shift@v1"
    if nu is None:
        return pending(["NU"], fn_id, "P-B04 NANOGrav δn_GW")
    val = -nu / 3.0
    return derived(
        value=val,
        uncertainty=abs(val) * 0.3 if val != 0 else 0.1,
        fn_id=fn_id,
        provenance="P-B04 NG15 spectral index shift",
        parameters_used={"NU": nu},
    )


def pta_kappa_correlation(r_predicted: Optional[float] = None) -> DerivationResult:
    """Predicted PTA × cosmic-web κ Pearson correlation amplitude (P-B05)."""
    fn_id = "rvm_cosmology.pta_kappa_correlation@v1"
    if r_predicted is None:
        return pending(["R_PREDICTED"], fn_id,
                       "P-B05 reducing-volume PTA × κ correlation amplitude")
    return derived(
        value=r_predicted,
        uncertainty=abs(r_predicted) * 0.4,
        fn_id=fn_id,
        provenance="P-B05 reducing-volume mechanism",
        parameters_used={"R_PREDICTED": r_predicted},
    )


def delta_rd(
    c_r: Optional[float] = None,
    sign: Optional[int] = None,
    nu: Optional[float] = None,
    delta_8: float = 1.0,
) -> DerivationResult:
    """Density-correlated BAO sound horizon shift δr_d/r_d = c_r · ν · (1 + δ_8).

    Sign is committed by SIGN_DELTA_R_D (OP12) (P-B09).
    """
    fn_id = "rvm_cosmology.delta_rd@v1"
    missing = []
    if c_r is None:
        missing.append("C_R")
    if sign is None:
        missing.append("SIGN_DELTA_R_D")
    if nu is None:
        missing.append("NU")
    if missing:
        return pending(missing, fn_id, "CCDR §13 + OP12 density-correlated r_d")
    val = sign * c_r * nu * (1.0 + delta_8)
    return derived(
        value=val,
        uncertainty=abs(val) * 0.3,
        fn_id=fn_id,
        provenance="CCDR §13 cascade-history density-stratified r_d (OP12 sign)",
        parameters_used={"C_R": c_r, "SIGN_DELTA_R_D": sign,
                         "NU": nu, "delta_8": delta_8},
    )


def tgft_rg_nu(nu: Optional[float] = None) -> DerivationResult:
    """Identity check: extracted ν equals committed ν (P-B11).

    The 'derivation' here is the trivial assertion that the RVM running
    coefficient ν is the one committed to in core/parameters.py. The
    measurement extracts ν from data; agreement at ≤1σ confirms.
    """
    fn_id = "rvm_cosmology.tgft_rg_nu@v1"
    if nu is None:
        return pending(["NU"], fn_id, "P-B11 TGFT-RG condensate ν (OP11)")
    return derived(
        value=nu,
        uncertainty=abs(nu) * 0.10,
        fn_id=fn_id,
        provenance="P-B11 TGFT-RG condensate identification",
        parameters_used={"NU": nu},
    )
