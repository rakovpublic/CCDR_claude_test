"""P-B05 — PTA × cosmic-web κ correlation amplitude."""
from ccdr.core.parameters import R_PREDICTED
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.rvm_cosmology import pta_kappa_correlation
from ccdr.data.loaders.tier_b import load_nanograv_kappa_correlation
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B05"
NAME = "PTA × κ correlation amplitude"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "NANOGrav 15-yr × Planck PR4 / ACT DR6 lensing"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    return pta_kappa_correlation(r_predicted=R_PREDICTED)


def measure():
    try:
        rows, sha = load_nanograv_kappa_correlation()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = weighted_mean(rows)
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
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
