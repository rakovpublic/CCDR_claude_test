"""P-A18 — Right-handed neutrino mass M_R from crystal boundary."""
from ccdr.core.parameters import CRYSTAL_BOUNDARY_ENERGY
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.particle_inventory import right_handed_nu_mass
from ccdr.data.loaders.neutrino import load_kamland_zen, load_katrin
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.see_saw import see_saw_consistency
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A18"
NAME = "Right-handed neutrino mass M_R"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "KamLAND-Zen + KATRIN"
_ESTIMATOR_ID = "see_saw.see_saw_consistency"


def derive():
    return right_handed_nu_mass(crystal_boundary_energy=CRYSTAL_BOUNDARY_ENERGY)


def measure():
    obs = []
    shas = []
    for fn in (load_kamland_zen, load_katrin):
        try:
            payload, sha = fn()
            obs.extend(payload)
            shas.append(sha)
        except DataUnavailable:
            continue
    if not obs:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = see_saw_consistency(obs)
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
