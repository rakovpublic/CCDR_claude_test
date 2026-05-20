"""P-A13 — Dark-photon kinetic mixing ε."""
from ccdr.core.parameters import NU
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.photon_dispersion import dark_photon_epsilon
from ccdr.data.loaders.dark_photon import load_babar_limits, load_lhcb_dp
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.exclusion import exclusion_consistency_check
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A13"
NAME = "Dark-photon kinetic mixing ε"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "BaBar + LHCb dark-photon"
_ESTIMATOR_ID = "exclusion.exclusion_consistency_check"


def derive():
    return dark_photon_epsilon(nu=NU)


def measure():
    curves = []
    shas = []
    for fn in (load_babar_limits, load_lhcb_dp):
        try:
            payload, sha = fn()
            curves.append(payload)
            shas.append(sha)
        except DataUnavailable:
            continue
    if not curves:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = exclusion_consistency_check(curves)
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
