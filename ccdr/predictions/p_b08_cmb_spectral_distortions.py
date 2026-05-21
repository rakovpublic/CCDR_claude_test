"""P-B08 — Staged CMB spectral distortions μ (FIRAS upper limit check)."""
from ccdr.core.parameters import PER_STAGE_ENERGY_INJECTION, N_CASCADE, PARAMETERS_REVISION
from ccdr.core.status import (
    MeasurementResult, MeasurementStatus, TestResult, TestStatus,
)
from ccdr.derivations.cascade_residue import mu_y_per_stage
from ccdr.data.loaders.tier_b import load_firas
from ccdr.data.loaders._common import DataUnavailable
from ccdr.predictions.base import handle_derivation, measurement_failed_result

ID = "P-B08"
NAME = "Staged μ from cascade stages (FIRAS upper limit)"
_DATA_SOURCE = "FIRAS COBE"
_ESTIMATOR_ID = "scalar_weighted.select"


def derive():
    return mu_y_per_stage(
        per_stage_energy_injection=PER_STAGE_ENERGY_INJECTION,
        n_total=N_CASCADE,
    )


def measure():
    try:
        payload, sha = load_firas()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    mu_ul, mu_sigma = payload["mu_upper_limit"]
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=mu_ul, uncertainty=mu_sigma,
        data_source=_DATA_SOURCE, data_sha256=sha,
        estimator_id=_ESTIMATOR_ID, n_samples=1,
    )


def test():
    d = derive()
    blocker = handle_derivation(ID, d)
    if blocker:
        return blocker
    m = measure()
    if m.status != MeasurementStatus.MEASURED:
        return measurement_failed_result(ID, d, m)
    # Upper-limit consistency check: PASS iff predicted μ ≤ FIRAS μ UL.
    ratio = d.value / m.value if m.value else float("inf")
    if ratio <= 1.0:
        status = TestStatus.CONFIRM
    elif ratio <= 3.0:
        status = TestStatus.INCONCLUSIVE
    else:
        status = TestStatus.REJECT
    return TestResult(
        prediction_id=ID, status=status,
        derivation=d, measurement=m,
        test_statistic=ratio, pass_threshold=1.0,
        parameters_revision=PARAMETERS_REVISION,
        notes=f"predicted_mu={d.value:.2e}, firas_ul={m.value:.2e}",
    )
