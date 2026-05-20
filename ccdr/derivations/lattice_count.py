"""Lattice-count derivations: CDT chirality count (P-A15).

The CDT-plusplus numerical execution is deferred; this module provides the
analytic stand-in. When CDT-plusplus is wired in, this becomes a wrapper.
"""
from typing import Optional

from ccdr.core.status import DerivationResult
from ccdr.derivations.base import pending, derived, incomplete


def cdt_chirality(N_4: Optional[int] = None) -> DerivationResult:
    """Predicted chirality count C in CDT ensemble of size N_4.

    Analytic limit: C ≈ N_4 / 2 (parameter-free CDT prediction).
    If N_4 is not supplied, returns DERIVATION_INCOMPLETE — the count must
    come from a CDT-plusplus run, not a closed-form expression.
    """
    fn_id = "lattice_count.cdt_chirality@v1"
    if N_4 is None:
        return incomplete(
            fn_id,
            "Synthesis §21.4 BSM6 (CDT chirality)",
            "requires CDT-plusplus numerical ensemble; supply N_4 to use the analytic limit",
        )
    val = N_4 / 2.0
    return derived(
        value=val,
        uncertainty=val ** 0.5,  # Poisson
        fn_id=fn_id,
        provenance="Synthesis §21.4 BSM6 CDT chirality (analytic limit)",
        parameters_used={"N_4": N_4},
    )
