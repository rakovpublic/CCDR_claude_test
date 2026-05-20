"""P-A08 — Secular w(z) drift in dark-energy equation of state."""
from ccdr.core.parameters import NU_BULK, BETA_COOLING
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.rvm_cosmology import w_z_drift
from ccdr.data.loaders.sn_bao import load_pantheon_plus, load_desi_dr2
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.w_reconstruction import w_z_reconstruction
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A08"
NAME = "Secular w(z) drift"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "Pantheon+ + DESI DR2"
_ESTIMATOR_ID = "w_reconstruction.w_z_reconstruction"


def derive():
    return w_z_drift(nu_bulk=NU_BULK, beta=BETA_COOLING, z=0.5)


def measure():
    joint = []
    shas = []
    for fn in (load_pantheon_plus, load_desi_dr2):
        try:
            payload, sha = fn()
            joint.extend(payload)
            shas.append(sha)
        except DataUnavailable:
            continue
    if not joint:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = w_z_reconstruction(joint)
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=val, uncertainty=unc,
        data_source=_DATA_SOURCE, data_sha256="|".join(shas),
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
