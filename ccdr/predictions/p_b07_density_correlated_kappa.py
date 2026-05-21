"""P-B07 — Density-correlated Δκ in lensing convergence."""
from ccdr.core.parameters import C_KAPPA, NU
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.cascade_residue import delta_kappa_density
from ccdr.data.loaders.tier_b import load_act_dr6_kappa
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B07"
NAME = "Density-correlated Δκ"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "ACT DR6 lensing × DES Y3 + KiDS-1000"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    return delta_kappa_density(c_kappa=C_KAPPA, nu=NU)


def measure():
    try:
        rows, sha = load_act_dr6_kappa()
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
