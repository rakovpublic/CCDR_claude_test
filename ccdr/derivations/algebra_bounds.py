"""Algebraic bounds: division-algebra / octonion N ≤ 11 (P-A16).

Parameter-free.
"""
from ccdr.core.status import DerivationResult
from ccdr.derivations.base import derived


def dao_max_N() -> DerivationResult:
    """Maximum allowed lattice dimension from division-algebra / octonion bound."""
    fn_id = "algebra_bounds.dao_max_N@v1"
    return derived(
        value=11.0,
        uncertainty=0.0,
        fn_id=fn_id,
        provenance="Synthesis §21.3 P24 DA/O bound",
        parameters_used={},
    )
