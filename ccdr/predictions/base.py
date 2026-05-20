"""Prediction protocol and shared glue.

Every prediction module exposes module-level constants:
  ID, NAME, PASS_THRESHOLD_SIGMA (or PASS_THRESHOLD_FRACTIONAL)
and three functions:
  derive() -> DerivationResult
  measure() -> MeasurementResult
  test() -> TestResult

The `compare` helper provides the standard σ-comparison used by most
predictions. Predictions with non-σ comparisons (e.g. exclusion checks)
implement their own logic inside test().
"""
from typing import Optional

from ccdr.core.parameters import PARAMETERS_REVISION
from ccdr.core.status import (
    DerivationResult, DerivationStatus,
    MeasurementResult, MeasurementStatus,
    TestResult, TestStatus,
)


def parameter_pending_result(prediction_id: str, d: DerivationResult) -> TestResult:
    return TestResult(
        prediction_id=prediction_id,
        status=TestStatus.PARAMETER_PENDING,
        derivation=d,
        measurement=MeasurementResult(status=MeasurementStatus.MEASURED),
        parameters_revision=PARAMETERS_REVISION,
        notes=f"Blocked on: {d.missing_parameters or 'derivation incomplete'}",
    )


def derivation_incomplete_result(prediction_id: str, d: DerivationResult) -> TestResult:
    return TestResult(
        prediction_id=prediction_id,
        status=TestStatus.NOT_RUN,
        derivation=d,
        measurement=MeasurementResult(status=MeasurementStatus.MEASURED),
        parameters_revision=PARAMETERS_REVISION,
        notes="Derivation incomplete",
    )


def measurement_failed_result(prediction_id: str, d: DerivationResult,
                              m: MeasurementResult) -> TestResult:
    return TestResult(
        prediction_id=prediction_id,
        status=TestStatus.INCONCLUSIVE,
        derivation=d,
        measurement=m,
        parameters_revision=PARAMETERS_REVISION,
        notes=f"Measurement status: {m.status.value}",
    )


def sigma_verdict(d: DerivationResult, m: MeasurementResult, pass_sigma: float,
                  fail_sigma: float = 3.0) -> tuple:
    """Standard σ-based comparison. Returns (TestStatus, sigma)."""
    denom = (d.uncertainty ** 2 + m.uncertainty ** 2) ** 0.5
    if denom == 0:
        return (TestStatus.INCONCLUSIVE, None)
    sigma = (m.value - d.value) / denom
    if abs(sigma) <= pass_sigma:
        return (TestStatus.CONFIRM, sigma)
    if abs(sigma) > fail_sigma:
        return (TestStatus.REJECT, sigma)
    return (TestStatus.INCONCLUSIVE, sigma)


def run_sigma_test(prediction_id: str, d: DerivationResult, m: MeasurementResult,
                   pass_sigma: float) -> TestResult:
    verdict, sigma = sigma_verdict(d, m, pass_sigma)
    return TestResult(
        prediction_id=prediction_id,
        status=verdict,
        derivation=d,
        measurement=m,
        test_statistic=sigma,
        pass_threshold=pass_sigma,
        parameters_revision=PARAMETERS_REVISION,
    )


def handle_derivation(prediction_id: str, d: DerivationResult) -> Optional[TestResult]:
    """Return a non-None TestResult iff the derivation blocks the pipeline."""
    if d.status == DerivationStatus.PARAMETER_PENDING:
        return parameter_pending_result(prediction_id, d)
    if d.status == DerivationStatus.DERIVATION_INCOMPLETE:
        return derivation_incomplete_result(prediction_id, d)
    if d.status == DerivationStatus.DERIVATION_FAILED:
        return TestResult(
            prediction_id=prediction_id,
            status=TestStatus.INCONCLUSIVE,
            derivation=d,
            measurement=MeasurementResult(status=MeasurementStatus.MEASURED),
            parameters_revision=PARAMETERS_REVISION,
            notes="Derivation failed",
        )
    return None
