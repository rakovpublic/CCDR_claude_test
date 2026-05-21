"""P-B06 — Frozen-vs-live DM fraction in fσ_8(z)."""
from ccdr.core.parameters import F_LIVE, ALPHA_GROWTH
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.cascade_residue import fsigma8_modification
from ccdr.data.loaders.tier_b import load_fsigma8
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B06"
NAME = "Frozen-vs-live DM in fσ_8"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "Planck + DESI fσ_8 compilation"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    # evaluate the multiplicative modification at z=0.5 (centre of the compilation)
    return fsigma8_modification(f_live=F_LIVE, alpha_growth=ALPHA_GROWTH, z=0.5)


def measure():
    try:
        rows, sha = load_fsigma8()
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
