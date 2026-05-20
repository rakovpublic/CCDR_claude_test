"""Symbolic modified action (placeholder).

Provides a single sympy expression for the cascade-modified Einstein-Hilbert
action. Used by `derivations/theory_consistency.py` only for symbolic
comparison; not consumed by data measurements.

If sympy is unavailable in the runtime, the expression is a string sentinel.
"""
try:
    import sympy as _sp

    g, R, Lambda, nu, phi = _sp.symbols("g R Lambda nu phi", real=True, positive=True)
    MODIFIED_ACTION = _sp.sqrt(-g) * (R - 2 * Lambda + nu * phi)
except Exception:  # pragma: no cover — sympy is optional at scaffold time
    MODIFIED_ACTION = "sqrt(-g) * (R - 2*Lambda + nu*phi)"


__all__ = ["MODIFIED_ACTION"]
