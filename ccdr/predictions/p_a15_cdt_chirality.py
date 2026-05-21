"""P-A15 — CDT chirality count (CDT-plusplus ensemble bundled in cache)."""
from ccdr.core.parameters import N_CDT_LATTICE
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.lattice_count import cdt_chirality
from ccdr.data.loaders.tier_b import load_cdt_chirality_ensemble
from ccdr.data.loaders._common import DataUnavailable
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A15"
NAME = "CDT chirality count"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "CDT-plusplus ensemble"
_ESTIMATOR_ID = "chirality.chirality_count"


def derive():
    return cdt_chirality(N_4=N_CDT_LATTICE)


def measure():
    try:
        payload, sha = load_cdt_chirality_ensemble()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    plus = payload["plus"]
    total = payload["total"]
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=float(plus),
        uncertainty=plus ** 0.5,
        data_source=_DATA_SOURCE, data_sha256=sha,
        estimator_id=_ESTIMATOR_ID, n_samples=total,
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
