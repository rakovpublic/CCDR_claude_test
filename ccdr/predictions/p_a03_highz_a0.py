"""P-A03 — High-z Milgrom a₀ → cH₀ transition."""
from ccdr.core.parameters import NU, Z_TRANSITION
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.grain_boundary import a0_z_evolution
from ccdr.data.loaders.rotation_curves import load_kmos3d, load_sparc, load_manga
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.rotation_curve import rotation_curve_a0_extractor
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A03"
NAME = "High-z Milgrom acceleration transition"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "KMOS3D + SPARC + MaNGA"
_ESTIMATOR_ID = "rotation_curve.rotation_curve_a0_extractor"


def derive():
    return a0_z_evolution(nu=NU, z_star=Z_TRANSITION, z=1.0)


def measure():
    curves = []
    shas = []
    for fn in (load_kmos3d, load_sparc, load_manga):
        try:
            payload, sha = fn()
            curves.extend(payload)
            shas.append(sha)
        except DataUnavailable:
            continue
    if not curves:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = rotation_curve_a0_extractor(curves)
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
