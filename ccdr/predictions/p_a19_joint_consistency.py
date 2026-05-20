"""P-A19 — Joint multi-channel consistency (CL5+CL6+CL7)."""
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.joint_inference import posterior
from ccdr.data.estimators.joint import joint_posterior
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)
from ccdr.predictions import (
    p_a08_secular_w_drift as P08,
    p_a09_bulk_weyl_bmode as P09,
    p_a10_b_to_smumu_pattern as P10,
    p_a11_boundary_deformation as P11,
)

ID = "P-A19"
NAME = "Joint multi-channel consistency CL5+CL6+CL7"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "Composition of P-A08, P-A09, P-A10, P-A11"
_ESTIMATOR_ID = "joint.joint_posterior"


def derive():
    components = [P08.derive(), P09.derive(), P10.derive(), P11.derive()]
    return posterior(component_results=components)


def measure():
    component_measurements = []
    for mod in (P08, P09, P10, P11):
        m = mod.measure()
        if m.status == MeasurementStatus.MEASURED and m.value is not None:
            component_measurements.append((m.value, m.uncertainty or 0.0))
    if not component_measurements:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = joint_posterior(component_measurements)
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=val, uncertainty=unc,
        data_source=_DATA_SOURCE, data_sha256="",
        estimator_id=_ESTIMATOR_ID, n_samples=n,
    )


def test():
    d = derive()
    blocker = handle_derivation(ID, d)
    if blocker:
        return blocker
    m = measure()
    if m.status != MeasurementStatus.MEASURED:
        return measurement_failed_result(ID, d, m)
    return run_sigma_test(ID, d, m, PASS_THRESHOLD_SIGMA)
