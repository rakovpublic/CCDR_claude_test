"""P-A06 — Sub-BAO harmonic peak in BOSS Lyα flux power spectrum."""
from ccdr.core.parameters import RHO_CASCADE, K_STAR
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.cascade_residue import subbao_harmonics
from ccdr.data.loaders.boss_lyalpha import load_pf_k
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.harmonic import harmonic_peak_detector
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A06"
NAME = "Sub-BAO harmonic"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "BOSS Lyα P_F(k)"
_ESTIMATOR_ID = "harmonic.harmonic_peak_detector"


def derive():
    return subbao_harmonics(rho=RHO_CASCADE, k_star=K_STAR)


def measure():
    try:
        payload, sha = load_pf_k()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = harmonic_peak_detector(payload)
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
