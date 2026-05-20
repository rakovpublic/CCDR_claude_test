"""P-A02 — Dark-matter cascade mass tower (consistency vs direct-detection exclusions)."""
from ccdr.core.parameters import M_0_DM_GEV, RHO_CASCADE, N_CASCADE
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.cascade_residue import mass_tower
from ccdr.data.loaders.dd_xenonnt_lz_pandax import (
    load_xenonnt_2025, load_lz_2024, load_pandax_2024,
)
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.mass_tower import mass_tower_consistency_check
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A02"
NAME = "Dark-matter cascade mass tower"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "XENONnT 2025 + LZ 2024 + PandaX-4T 2024"
_ESTIMATOR_ID = "mass_tower.mass_tower_consistency_check"


def derive():
    return mass_tower(m_0=M_0_DM_GEV, rho=RHO_CASCADE, n_total=N_CASCADE)


def _try_load(fn):
    try:
        return fn()
    except DataUnavailable:
        return None


def measure():
    payloads = []
    shas = []
    for fn in (load_xenonnt_2025, load_lz_2024, load_pandax_2024):
        loaded = _try_load(fn)
        if loaded is None:
            continue
        payload, sha = loaded
        payloads.append(payload)
        shas.append(sha)
    if not payloads:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = mass_tower_consistency_check(payloads)
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
