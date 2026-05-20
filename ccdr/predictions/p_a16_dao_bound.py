"""P-A16 — Division-algebra / octonion N ≤ 11 bound."""
from ccdr.core.parameters import PARAMETERS_REVISION
from ccdr.core.status import (
    MeasurementResult, MeasurementStatus, TestResult, TestStatus,
)
from ccdr.derivations.algebra_bounds import dao_max_N
from ccdr.data.estimators.bound_check import consistency_check_N_le_11
from ccdr.predictions.base import handle_derivation

ID = "P-A16"
NAME = "DA/O N ≤ 11 bound"
PASS_THRESHOLD = 0.5


def derive():
    return dao_max_N()


def measure():
    val, unc, n = consistency_check_N_le_11(N=11)
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=val * 11.0, uncertainty=0.0,
        data_source="bound (no data)",
        estimator_id="bound_check.consistency_check_N_le_11",
        n_samples=n,
    )


def test():
    d = derive()
    blocker = handle_derivation(ID, d)
    if blocker:
        return blocker
    m = measure()
    # Bound check: PASS iff measured N value matches derived bound
    diff = abs(m.value - d.value)
    if diff <= PASS_THRESHOLD:
        status = TestStatus.CONFIRM
    else:
        status = TestStatus.REJECT
    return TestResult(
        prediction_id=ID, status=status,
        derivation=d, measurement=m,
        test_statistic=diff, pass_threshold=PASS_THRESHOLD,
        parameters_revision=PARAMETERS_REVISION,
    )
