"""P-A01 — Filament orientational correlation length."""
from ccdr.core.parameters import NU, R_GRAIN_MPC_H, R_STAR_BAO
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.grain_boundary import predict_filament_texture
from ccdr.data.loaders.filament_catalogues import load_disperse_or_bisous
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.correlation import exponential_correlation_fit
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A01"
NAME = "Filament orientational correlation length"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "DisPerSE/Bisous filament catalogue"
_ESTIMATOR_ID = "correlation.exponential_correlation_fit"


def derive():
    return predict_filament_texture(
        nu=NU, r_grain_mpc_h=R_GRAIN_MPC_H, r_star_bao=R_STAR_BAO,
    )


def measure():
    try:
        catalogue = load_disperse_or_bisous()
    except DataUnavailable as e:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE,
            estimator_id=_ESTIMATOR_ID,
        )
    payload, sha = catalogue
    r_tex, unc, n = exponential_correlation_fit(payload)
    if n < 10:
        status = MeasurementStatus.INSUFFICIENT_STATISTICS
    else:
        status = MeasurementStatus.MEASURED
    return MeasurementResult(
        status=status,
        value=r_tex, uncertainty=unc,
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
