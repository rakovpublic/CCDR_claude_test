"""P-A17 — Axion mass m_a from PQ scale, consistency with ADMX / HAYSTAC."""
from ccdr.core.parameters import F_PQ
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.particle_inventory import axion_mass
from ccdr.data.loaders.axion import load_admx, load_haystac
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.exclusion import exclusion_consistency_check
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A17"
NAME = "Axion mass m_a"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "ADMX + HAYSTAC"
_ESTIMATOR_ID = "exclusion.exclusion_consistency_check"


def derive():
    return axion_mass(f_pq=F_PQ)


def measure():
    curves = []
    shas = []
    for fn in (load_admx, load_haystac):
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
