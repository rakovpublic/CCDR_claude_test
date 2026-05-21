"""P-B04 — PTA GW spectral index shift δn_GW = -ν/3."""
from ccdr.core.parameters import NU
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.rvm_cosmology import pta_spectral_shift
from ccdr.data.loaders.tier_b import load_nanograv_spectral_index
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B04"
NAME = "PTA GW spectral index shift"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "NANOGrav 15-yr spectral index posterior"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    return pta_spectral_shift(nu=NU)


def measure():
    try:
        rows, sha = load_nanograv_spectral_index()
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
