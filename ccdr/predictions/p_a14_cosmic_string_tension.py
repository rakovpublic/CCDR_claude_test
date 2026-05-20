"""P-A14 — Cosmic-string tension Gμ from NANOGrav 15-yr."""
from ccdr.core.parameters import ALPHA_CASCADE
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.photon_dispersion import cosmic_string_tension
from ccdr.data.loaders.nanograv import load_15yr
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.cosmic_string import cosmic_string_template_fit
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A14"
NAME = "Cosmic-string tension Gμ"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "NANOGrav 15-yr"
_ESTIMATOR_ID = "cosmic_string.cosmic_string_template_fit"


def derive():
    return cosmic_string_tension(alpha_cascade=ALPHA_CASCADE)


def measure():
    try:
        payload, sha = load_15yr()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = cosmic_string_template_fit(payload)
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
