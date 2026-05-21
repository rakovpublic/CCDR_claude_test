"""P-A11 — Boundary-deformation ε_ℓm spectrum (EHT + GWTC-3 composite)."""
from ccdr.core.parameters import ALPHA_J, ALPHA_T, ALPHA_W, EPSILON_BD
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.boundary_deformation import epsilon_spectrum
from ccdr.data.loaders.eht import load_m87_sgrA
from ccdr.data.loaders.gwtc3 import load_ringdowns
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.boundary_residual import boundary_deformation_residual
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A11"
NAME = "Boundary-deformation ε_ℓm spectrum"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "EHT M87*/SgrA* + GWTC-3 ringdowns"
_ESTIMATOR_ID = "boundary_residual.boundary_deformation_residual"


def derive():
    return epsilon_spectrum(
        alpha_j=ALPHA_J, alpha_t=ALPHA_T, alpha_w=ALPHA_W,
        epsilon_bd=EPSILON_BD,
    )


def measure():
    joint = []
    shas = []
    for fn in (load_m87_sgrA, load_ringdowns):
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
    val, unc, n = boundary_deformation_residual(joint)
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
