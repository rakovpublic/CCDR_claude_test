"""P-A04 — AS-EPRL γ consistency (theory only, no data)."""
from datetime import datetime

from ccdr.core.parameters import PARAMETERS_REVISION
from ccdr.core.status import (
    MeasurementResult, MeasurementStatus, TestResult, TestStatus,
)
from ccdr.derivations.theory_consistency import as_eprl_gamma
from ccdr.predictions.base import handle_derivation

ID = "P-A04"
NAME = "AS-EPRL γ consistency"
PASS_THRESHOLD = 0.05  # fractional


def derive():
    return as_eprl_gamma()


def measure():
    # No data — the 'measurement' is the symbolic comparison itself,
    # already done inside the derivation. Synthesise a trivially-MEASURED
    # result of 0 with no uncertainty.
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=0.0, uncertainty=0.0,
        data_source="theory-only (sympy)",
        data_sha256="",
        estimator_id="sympy-symbolic",
        n_samples=1,
    )


def test():
    d = derive()
    blocker = handle_derivation(ID, d)
    if blocker:
        return blocker
    m = measure()
    diff = abs(d.value - m.value)
    if diff <= PASS_THRESHOLD:
        status = TestStatus.CONFIRM
    elif diff > 3 * PASS_THRESHOLD:
        status = TestStatus.REJECT
    else:
        status = TestStatus.INCONCLUSIVE
    return TestResult(
        prediction_id=ID, status=status,
        derivation=d, measurement=m,
        test_statistic=diff, pass_threshold=PASS_THRESHOLD,
        parameters_revision=PARAMETERS_REVISION,
    )
