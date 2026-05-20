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
