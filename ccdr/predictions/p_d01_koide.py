"""P-D01 — Koide Q = 2/3 (PDG charged-lepton masses)."""
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.particle_inventory import koide_q
from ccdr.data.loaders.tier_b import load_pdg_lepton_masses
from ccdr.data.loaders._common import DataUnavailable
from ccdr.data.estimators.koide import koide_q as koide_estimator
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-D01"
NAME = "Koide Q = 2/3"
PASS_THRESHOLD_SIGMA = 3.0
_DATA_SOURCE = "PDG charged-lepton masses"
_ESTIMATOR_ID = "koide.koide_q"


def derive():
    return koide_q()


def measure():
    try:
        masses, sha = load_pdg_lepton_masses()
    except DataUnavailable:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    q, sigma, n = koide_estimator(masses)
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=q, uncertainty=sigma,
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
