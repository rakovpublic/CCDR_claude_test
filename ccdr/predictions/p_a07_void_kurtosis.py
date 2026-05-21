"""P-A07 — Void-wall transverse kurtosis k₄ > 4."""
from ccdr.core.parameters import NU, R_GRAIN_MPC_H, N_CASCADE
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.grain_boundary import predict_void_kurtosis
from ccdr.data.loaders.vast_voids import load_vast_catalogue
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.kurtosis import transverse_kurtosis
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A07"
NAME = "Void-wall transverse kurtosis k₄ > 4"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "VAST VoidFinder"
_ESTIMATOR_ID = "kurtosis.transverse_kurtosis"


def derive():
    return predict_void_kurtosis(nu=NU, r_grain_mpc_h=R_GRAIN_MPC_H, n_cascade=N_CASCADE)


def measure():
    try:
        payload, sha = load_vast_catalogue()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    k4, unc, n = transverse_kurtosis(payload)
    if n < 100:
        return MeasurementResult(
            status=MeasurementStatus.INSUFFICIENT_STATISTICS,
            data_source=_DATA_SOURCE, data_sha256=sha,
            estimator_id=_ESTIMATOR_ID, n_samples=n,
        )
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=k4, uncertainty=unc,
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
