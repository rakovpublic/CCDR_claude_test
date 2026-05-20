"""P-A12 — CL4 joint density-stratified excess (composition of P-A01 + P-A07)."""
from ccdr.core.parameters import NU
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.grain_boundary import joint_density_sign
from ccdr.data.loaders.filament_catalogues import load_disperse_or_bisous
from ccdr.data.loaders.vast_voids import load_vast_catalogue
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.correlation import exponential_correlation_fit
from ccdr.data.estimators.kurtosis import transverse_kurtosis
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A12"
NAME = "CL4 joint density-stratified excess"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "Filament catalogues + VAST voids"
_ESTIMATOR_ID = "composite.A01+A07"


def derive():
    return joint_density_sign(nu=NU)


def measure():
    try:
        fil_payload, fil_sha = load_disperse_or_bisous()
        void_payload, void_sha = load_vast_catalogue()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    r_tex, _, _ = exponential_correlation_fit(fil_payload)
    k4, _, _ = transverse_kurtosis(void_payload)
    # Joint observable: sign of combined excess; convert to scalar = +1 / -1
    excess_fil = 1.0 if r_tex > 0 else -1.0
    excess_void = 1.0 if k4 > 3.0 else -1.0
    same_sign = 1.0 if excess_fil == excess_void else -1.0
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=same_sign, uncertainty=0.5,
        data_source=_DATA_SOURCE,
        data_sha256=fil_sha + "|" + void_sha,
        estimator_id=_ESTIMATOR_ID, n_samples=2,
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
