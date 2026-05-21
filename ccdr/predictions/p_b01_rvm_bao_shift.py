"""P-B01 — RVM BAO scale shift δr*/r* = ν/2."""
from ccdr.core.parameters import NU
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.rvm_cosmology import bao_shift
from ccdr.data.loaders.tier_b import load_desi_dr2_bao_shift
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B01"
NAME = "RVM BAO scale shift δr*/r* = ν/2"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "DESI DR2 BAO r* residual"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    return bao_shift(nu=NU)


def measure():
    try:
        rows, sha = load_desi_dr2_bao_shift()
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
