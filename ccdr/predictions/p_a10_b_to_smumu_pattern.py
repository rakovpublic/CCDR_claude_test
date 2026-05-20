"""P-A10 — b→sμμ Wilson-coefficient pattern (δC_9)."""
from ccdr.core.parameters import LATTICE_SCALE_TEV
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.flavour_wilson import b_to_smumu_pattern
from ccdr.data.loaders.lhcb_b2smumu import load_run3
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.wilson import wilson_coefficient_fitter
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A10"
NAME = "b→sμμ Wilson-coefficient pattern"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "LHCb b→sμμ Run-3"
_ESTIMATOR_ID = "wilson.wilson_coefficient_fitter"


def derive():
    return b_to_smumu_pattern(lattice_scale_tev=LATTICE_SCALE_TEV)


def measure():
    try:
        payload, sha = load_run3()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = wilson_coefficient_fitter(payload)
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
