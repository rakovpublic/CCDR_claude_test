"""P-B03 — QGP η/s enhancement at phase boundaries."""
from ccdr.core.parameters import NU, C_ETA_S
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.grain_boundary import eta_over_s_enhancement
from ccdr.data.loaders.tier_b import load_alice_cms_qgp
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B03"
NAME = "QGP η/s enhancement"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "ALICE / CMS QGP"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    return eta_over_s_enhancement(nu=NU, c_eta_s=C_ETA_S)


def measure():
    try:
        rows, sha = load_alice_cms_qgp()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = weighted_mean([(v, s) for _name, v, s in rows])
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
