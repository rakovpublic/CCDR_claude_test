"""P-A13 — Dark-photon kinetic mixing ε (in-band exclusion check).

CONFIRM iff predicted ε is below the BaBar/LHCb ε² upper-limit envelope.
"""
import math

from ccdr.core.parameters import NU, PARAMETERS_REVISION
from ccdr.core.status import (
    MeasurementResult, MeasurementStatus, TestResult, TestStatus,
)
from ccdr.derivations.photon_dispersion import dark_photon_epsilon
from ccdr.data.loaders.dark_photon import load_babar_limits, load_lhcb_dp
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.exclusion import exclusion_consistency_check
from ccdr.predictions.base import handle_derivation, measurement_failed_result

ID = "P-A13"
NAME = "Dark-photon kinetic mixing ε"
PASS_THRESHOLD = 1.0  # ratio (predicted_eps / measured_eps_ul) below 1 ⇒ CONFIRM
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
    # estimator returns the median ε² UL across curves
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
    # m.value is the measured median ε² UL; convert to ε UL
    eps_ul = math.sqrt(max(m.value, 0.0))
    ratio = d.value / eps_ul if eps_ul > 0 else float("inf")
    if ratio < PASS_THRESHOLD:
        status = TestStatus.CONFIRM
    elif ratio < 10 * PASS_THRESHOLD:
        status = TestStatus.INCONCLUSIVE
    else:
        status = TestStatus.REJECT
    return TestResult(
        prediction_id=ID, status=status,
        derivation=d, measurement=m,
        test_statistic=ratio, pass_threshold=PASS_THRESHOLD,
        parameters_revision=PARAMETERS_REVISION,
        notes=f"predicted_eps={d.value:.2e}, measured_eps_ul={eps_ul:.2e}",
    )
