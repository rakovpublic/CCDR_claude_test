"""Photon-dispersion derivations: cosmic-string h_c, dark-photon ε.

P-A13 (dark photon), P-A14 (cosmic strings).
"""
import math
from typing import Optional

from ccdr.core.status import DerivationResult
from ccdr.derivations.base import pending, derived


def dark_photon_epsilon(nu: Optional[float] = None) -> DerivationResult:
    """Predicted kinetic-mixing parameter ε for dark photon.

    Leading-order: ε ~ ν · α_EM / (4π) (Synthesis §21.4 BSM3).
    """
    fn_id = "photon_dispersion.dark_photon_epsilon@v1"
    if nu is None:
        return pending(["NU"], fn_id, "Synthesis §21.4 BSM3")
    alpha_em = 1.0 / 137.036
    eps = nu * alpha_em / (4.0 * math.pi)
    return derived(
        value=eps,
        uncertainty=abs(eps) * 0.4,
        fn_id=fn_id,
        provenance="Synthesis §21.4 BSM3 dark-photon mixing",
        parameters_used={"NU": nu},
    )


def cosmic_string_tension(alpha_cascade: Optional[float] = None) -> DerivationResult:
    """Predicted cosmic-string tension Gμ from cascade scaling.

    Heuristic: Gμ = α_cascade² · 10⁻⁶ (Synthesis §21.4 BSM5). With
    α_cascade ≈ 1e-2 this lands in the NANOGrav 15-yr band ~ 1e-10.
    """
    fn_id = "photon_dispersion.cosmic_string_tension@v1"
    if alpha_cascade is None:
        return pending(["ALPHA_CASCADE"], fn_id, "Synthesis §21.4 BSM5")
    g_mu = alpha_cascade ** 2 * 1.0e-6
    return derived(
        value=g_mu,
        uncertainty=g_mu * 0.5,
        fn_id=fn_id,
        provenance="Synthesis §21.4 BSM5 cosmic-string tension",
        parameters_used={"ALPHA_CASCADE": alpha_cascade},
    )
