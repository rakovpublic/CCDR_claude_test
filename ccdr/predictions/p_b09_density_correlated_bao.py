"""P-B09 — Density-correlated BAO sound horizon δr_d/r_d."""
from ccdr.core.parameters import C_R, SIGN_DELTA_R_D, NU
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.rvm_cosmology import delta_rd
from ccdr.data.loaders.tier_b import load_desi_density_rd
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B09"
NAME = "Density-correlated δr_d"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "DESI DR2 density-binned r_d"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    return delta_rd(c_r=C_R, sign=SIGN_DELTA_R_D, nu=NU)


def measure():
    try:
        rows, sha = load_desi_density_rd()
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
