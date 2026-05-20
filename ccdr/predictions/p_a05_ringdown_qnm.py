"""P-A05 — Ringdown QNM population deviation."""
from ccdr.core.parameters import EPSILON_BD, ALPHA_J
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.boundary_deformation import qnm_deviation
from ccdr.data.loaders.gwtc3 import load_high_snr_ringdowns
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.ringdown_qnm import population_deviation
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A05"
NAME = "Ringdown QNM population deviation"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "GWTC-3 high-SNR ringdowns"
_ESTIMATOR_ID = "ringdown_qnm.population_deviation"


def derive():
    return qnm_deviation(epsilon_bd=EPSILON_BD, alpha_j=ALPHA_J)


def measure():
    try:
        payload, sha = load_high_snr_ringdowns()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = population_deviation(payload)
    return MeasurementResult(
        status=MeasurementStatus.MEASURED if n > 0 else MeasurementStatus.INSUFFICIENT_STATISTICS,
        value=val, uncertainty=unc,
        data_source=_DATA_SOURCE, data_sha256=sha,
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
