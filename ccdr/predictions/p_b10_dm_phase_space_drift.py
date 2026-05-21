"""P-B10 — DM phase-space drift z-score amplitude."""
from ccdr.core.parameters import Z_SCORE_AMPLITUDE
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.cascade_residue import dm_phase_space_zscore
from ccdr.data.loaders.tier_b import load_gaia_phase_space
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.scalar_weighted import weighted_mean
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-B10"
NAME = "DM phase-space drift z-score"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "GAIA DR3 + DESI MWS"
_ESTIMATOR_ID = "scalar_weighted.weighted_mean"


def derive():
    return dm_phase_space_zscore(z_score_amplitude=Z_SCORE_AMPLITUDE)


def measure():
    try:
        rows, sha = load_gaia_phase_space()
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
