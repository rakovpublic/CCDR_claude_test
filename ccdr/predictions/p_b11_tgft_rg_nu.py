"""P-B11 — TGFT-RG condensate ν (joint-extractor consistency)."""
from ccdr.core.parameters import NU
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.rvm_cosmology import tgft_rg_nu
from ccdr.data.loaders.tier_b import load_nu_extraction
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import select_observable
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B11"
NAME = "TGFT-RG condensate ν"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "Joint DESI DR2 + Pantheon+ ν extraction"
_ESTIMATOR_ID = "scalar_weighted.select_observable"


def derive():
    return tgft_rg_nu(nu=NU)


def measure():
    try:
        rows, sha = load_nu_extraction()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = select_observable(rows, "joint_DESI_Pantheon")
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
