"""Boundary-deformation derivations: ringdown QNM deviation, ε_ℓm spectrum.

P-A05 (ringdown QNM), P-A11 (boundary deformation spectrum).
"""
from typing import Optional

from ccdr.core.status import DerivationResult
from ccdr.derivations.base import pending, derived


def qnm_deviation(
    epsilon_bd: Optional[float] = None,
    alpha_j: Optional[float] = None,
    spin: float = 0.7,
    mass_solar: float = 50.0,
) -> DerivationResult:
    """Fractional deviation of dominant 2,2,0 QNM from Kerr.

    δω/ω_Kerr = ε_bd · spin^α_j   (CCDR §15.5 / Synthesis §22).
    """
    fn_id = "boundary_deformation.qnm_deviation@v1"
    missing = []
    if epsilon_bd is None:
        missing.append("EPSILON_BD")
    if alpha_j is None:
        missing.append("ALPHA_J")
    if missing:
        return pending(missing, fn_id, "CCDR §15.5 boundary deformation QNM")
    dom = epsilon_bd * (spin ** alpha_j)
    return derived(
        value=dom,
        uncertainty=abs(dom) * 0.4,
        fn_id=fn_id,
        provenance="CCDR §15.5 / Synthesis §22 QNM deviation",
        parameters_used={"EPSILON_BD": epsilon_bd, "ALPHA_J": alpha_j,
                         "spin": spin, "mass_solar": mass_solar},
    )


def epsilon_spectrum(
    alpha_j: Optional[float] = None,
    alpha_t: Optional[float] = None,
    alpha_w: Optional[float] = None,
    epsilon_bd: Optional[float] = None,
) -> DerivationResult:
    """Predicted fractional residual of boundary-deformation ε_ℓm spectrum.

    The full spectrum is a function (ℓ,m) → ε_ℓm; the scalar value returned
    here is the typical fractional residual:
        residual = epsilon_bd · ⟨α⟩  (mean exponent)
    """
    fn_id = "boundary_deformation.epsilon_spectrum@v1"
    missing = []
    if alpha_j is None:
        missing.append("ALPHA_J")
    if alpha_t is None:
        missing.append("ALPHA_T")
    if alpha_w is None:
        missing.append("ALPHA_W")
    if epsilon_bd is None:
        missing.append("EPSILON_BD")
    if missing:
        return pending(missing, fn_id, "CCDR §15.5 ε_ℓm spectrum")
    mean_alpha = (alpha_j + alpha_t + alpha_w) / 3.0
    residual = epsilon_bd * mean_alpha
    return derived(
        value=residual,
        uncertainty=abs(residual) * 0.4,
        fn_id=fn_id,
        provenance="CCDR §15.5 boundary-deformation ε_ℓm spectrum",
        parameters_used={"ALPHA_J": alpha_j, "ALPHA_T": alpha_t,
                         "ALPHA_W": alpha_w, "EPSILON_BD": epsilon_bd},
    )
