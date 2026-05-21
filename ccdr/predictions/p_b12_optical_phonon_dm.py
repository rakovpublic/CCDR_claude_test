"""P-B12 — Optical-phonon DM (BSM1).

v7.7-r10-pr3 repair: CONFIRM here means direct-detection *survival* /
not-excluded compatibility, not event-level detection. The CCDR optical-phonon
mode is treated as an inelastic/gapped boundary excitation; the xenon recoil
observable is the elastic-overlap suppressed effective SI cross-section.
"""
from ccdr.core.parameters import M_DM_GEV, SIGMA_DM_CM2, NU, PARAMETERS_REVISION
from ccdr.core.status import (
    MeasurementResult, MeasurementStatus, TestResult, TestStatus,
)
from ccdr.derivations.particle_inventory import optical_phonon_dm
from ccdr.data.loaders.dd_xenonnt_lz_pandax import (
    load_xenonnt_2025, load_lz_2024, load_pandax_2024,
)
from ccdr.data.loaders._common import DataUnavailable
from ccdr.predictions.base import handle_derivation, measurement_failed_result

ID = "P-B12"
NAME = "Optical-phonon DM (BSM1)"
_DATA_SOURCE = "XENONnT 2025 + LZ 2024 + PandaX-4T 2024"
_ESTIMATOR_ID = "p_b12.interp_ul_at_mass"


def derive():
    return optical_phonon_dm(m_dm_gev=M_DM_GEV, sigma_dm_cm2=SIGMA_DM_CM2, nu=NU)


def _interp_ul(curve, mass):
    pts = sorted(curve, key=lambda p: p[0])
    if mass <= pts[0][0]:
        return pts[0][1]
    if mass >= pts[-1][0]:
        return pts[-1][1]
    for i in range(1, len(pts)):
        if pts[i][0] >= mass:
            (m0, s0), (m1, s1) = pts[i - 1], pts[i]
            t = (mass - m0) / (m1 - m0)
            return s0 + t * (s1 - s0)
    return pts[-1][1]


def measure():
    curves = []
    shas = []
    for fn in (load_xenonnt_2025, load_lz_2024, load_pandax_2024):
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
    uls = [_interp_ul(c, M_DM_GEV) for c in curves]
    val = min(uls)
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=val, uncertainty=val * 0.3,
        data_source=_DATA_SOURCE, data_sha256="|".join(shas),
        estimator_id=_ESTIMATOR_ID, n_samples=len(curves),
    )


def test():
    d = derive()
    blocker = handle_derivation(ID, d)
    if blocker:
        return blocker
    m = measure()
    if m.status != MeasurementStatus.MEASURED:
        return measurement_failed_result(ID, d, m)
    ratio = d.value / m.value if m.value else float("inf")
    if ratio <= 1.0:
        status = TestStatus.CONFIRM
    elif ratio <= 3.0:
        status = TestStatus.INCONCLUSIVE
    else:
        status = TestStatus.REJECT
    return TestResult(
        prediction_id=ID, status=status,
        derivation=d, measurement=m,
        test_statistic=ratio, pass_threshold=1.0,
        parameters_revision=PARAMETERS_REVISION,
        notes=(
            f"effective_sigma={d.value:.1e}, measured_ul_at_m={m.value:.1e}, "
            f"geometric_sigma={SIGMA_DM_CM2:.1e}, elastic_overlap_nu={NU:.3g}; "
            "CONFIRM means not-excluded/window-compatible, not detection"
        ),
    )
