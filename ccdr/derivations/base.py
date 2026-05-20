"""Helpers shared by derivation modules.

Provides the `@derivation` decorator that tags a function with its
DERIVATION_FN_ID, plus convenience builders for the common
PARAMETER_PENDING / DERIVATION_INCOMPLETE shapes.

All derivation functions must:
  - Be pure (no I/O, no globals beyond `core/parameters`).
  - Return a `DerivationResult`.
  - Accept all required parameters as keyword arguments so the
    pure-derivation lint test can call them with `None` defaults.
"""
from functools import wraps
from typing import Iterable, Optional

from ccdr.core.status import DerivationResult, DerivationStatus


def derivation(fn_id: str):
    """Tag a derivation function with a stable version id."""
    def _decorator(fn):
        fn.derivation_function_id = fn_id

        @wraps(fn)
        def _wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        _wrapper.derivation_function_id = fn_id
        return _wrapper
    return _decorator


def pending(missing: Iterable[str], fn_id: str, provenance: str = "") -> DerivationResult:
    return DerivationResult(
        status=DerivationStatus.PARAMETER_PENDING,
        missing_parameters=tuple(missing),
        derivation_function_id=fn_id,
        provenance=provenance,
    )


def incomplete(fn_id: str, provenance: str = "", note: str = "") -> DerivationResult:
    return DerivationResult(
        status=DerivationStatus.DERIVATION_INCOMPLETE,
        derivation_function_id=fn_id,
        provenance=(provenance + (" | " + note if note else "")).strip(),
    )


def derived(value: float, uncertainty: float, fn_id: str,
            provenance: str, parameters_used: Optional[dict] = None) -> DerivationResult:
    return DerivationResult(
        status=DerivationStatus.DERIVED,
        value=value,
        uncertainty=uncertainty,
        provenance=provenance,
        parameters_used=parameters_used or {},
        derivation_function_id=fn_id,
    )


__all__ = ["derivation", "pending", "incomplete", "derived"]
