"""Bulk-Weyl derivations: B-mode ℓ-shape template (P-A09).

The ℓ-shape itself is a fixed CCDR template independent of any frozen
parameter; the *amplitude* requires C_W_AMP. The scalar value returned by
`bmode_template` is the predicted amplitude at the template peak.
"""
import math
from typing import Optional

from ccdr.core.status import DerivationResult
from ccdr.derivations.base import pending, derived, incomplete


def bmode_template(c_w_amp: Optional[float] = None) -> DerivationResult:
    """Predicted B-mode bulk-Weyl template amplitude at ℓ ~ 80."""
    fn_id = "bulk_weyl.bmode_template@v1"
    if c_w_amp is None:
        return pending(["C_W_AMP"], fn_id, "CCDR §15.3 bulk-Weyl B-mode")
    # template-peak amplitude in μK² at ℓ ~ 80, matching the BK18+Planck
    # weighted-mean band (dust-uncorrected). Scaled by C_W_AMP directly.
    val = c_w_amp
    return derived(
        value=val,
        uncertainty=abs(val) * 0.5,
        fn_id=fn_id,
        provenance="CCDR §15.3 bulk-Weyl B-mode template",
        parameters_used={"C_W_AMP": c_w_amp},
    )


def bmode_shape() -> DerivationResult:
    """The ℓ-shape itself (parameter-free). Stored as a fixed value used by
    the estimator for template matching."""
    fn_id = "bulk_weyl.bmode_shape@v1"
    # the shape is a parameter-free CCDR template; the scalar here is the
    # ℓ-peak position used by the bandpower fitter.
    return derived(
        value=80.0,
        uncertainty=10.0,
        fn_id=fn_id,
        provenance="CCDR §15.3 fixed B-mode ℓ-shape (ℓ_peak)",
        parameters_used={},
    )
