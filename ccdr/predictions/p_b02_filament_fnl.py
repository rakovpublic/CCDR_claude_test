"""P-B02 — Filament non-Gaussian bispectrum f_NL^grain."""
from ccdr.core.parameters import R_GRAIN_MPC_H, R_STAR_BAO
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.grain_boundary import fnl_grain
from ccdr.data.loaders.tier_b import load_planck_bispectrum
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import select_observable
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B02"
NAME = "Filament f_NL^grain"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "Planck NPIPE bispectrum"
_ESTIMATOR_ID = "scalar_weighted.select_observable"


def derive():
    return fnl_grain(r_grain_mpc_h=R_GRAIN_MPC_H, r_star_bao=R_STAR_BAO)


def measure():
    try:
        rows, sha = load_planck_bispectrum()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = select_observable(rows, "grain_proxy")
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
