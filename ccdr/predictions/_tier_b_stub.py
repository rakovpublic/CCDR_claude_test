"""Shared Tier B stub: returns PARAMETER_PENDING with the OP / repair note.

Each tier-B prediction module sets module-level ID, NAME, MISSING, REPAIR
and aliases ``derive``, ``measure``, ``test`` to ``_derive``, ``_measure``,
``_test`` below.
"""
from ccdr.core.parameters import PARAMETERS_REVISION
from ccdr.core.status import (
    DerivationResult, DerivationStatus,
    MeasurementResult, MeasurementStatus,
    TestResult, TestStatus,
)


def make_pending_derive(fn_id: str, missing: tuple, repair: str):
    def _derive() -> DerivationResult:
        return DerivationResult(
            status=DerivationStatus.PARAMETER_PENDING,
            missing_parameters=missing,
            derivation_function_id=fn_id,
            provenance=repair,
        )
    return _derive


def make_pending_measure(source: str):
    def _measure() -> MeasurementResult:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=source, estimator_id="tier-b-stub", n_samples=0,
        )
    return _measure


def make_pending_test(prediction_id: str, derive_fn):
    def _test() -> TestResult:
        d = derive_fn()
        return TestResult(
            prediction_id=prediction_id,
            status=TestStatus.PARAMETER_PENDING,
            derivation=d,
            measurement=MeasurementResult(status=MeasurementStatus.MEASURED),
            parameters_revision=PARAMETERS_REVISION,
            notes=f"Tier-B stub blocked on: {d.missing_parameters}",
        )
    return _test
