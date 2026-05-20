"""P-A09 — Bulk-Weyl B-mode template."""
from ccdr.core.parameters import C_W_AMP
from ccdr.core.status import MeasurementResult, MeasurementStatus
from ccdr.derivations.bulk_weyl import bmode_template
from ccdr.data.loaders.cmb_bmode import load_bk18_bandpowers, load_planck_pr4_bmode
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.data.estimators.bmode import bmode_template_fit
from ccdr.predictions.base import (
    handle_derivation, measurement_failed_result, run_sigma_test,
)

ID = "P-A09"
NAME = "Bulk-Weyl B-mode template"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "BICEP/Keck 18 + Planck PR4"
_ESTIMATOR_ID = "bmode.bmode_template_fit"


def derive():
    return bmode_template(c_w_amp=C_W_AMP)


def measure():
    bp = []
    shas = []
    for fn in (load_bk18_bandpowers, load_planck_pr4_bmode):
        try:
            payload, sha = fn()
            bp.extend(payload)
            shas.append(sha)
        except DataUnavailable:
            continue
    if not bp:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    val, unc, n = bmode_template_fit(bp)
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
