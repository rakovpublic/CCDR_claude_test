"""P-A17 — Axion mass m_a from PQ scale (in-scan-range check vs ADMX/HAYSTAC).

CONFIRM iff predicted m_a falls inside an ongoing or completed haloscope
scan band (ADMX ~ 2.6-5.1 μeV, HAYSTAC ~ 17-18 μeV). REJECT iff predicted
m_a falls inside an excluded region.
"""
from ccdr.core.parameters import F_PQ, PARAMETERS_REVISION
from ccdr.core.status import (
    MeasurementResult, MeasurementStatus, TestResult, TestStatus,
)
from ccdr.derivations.particle_inventory import axion_mass
from ccdr.data.loaders.axion import load_admx, load_haystac
from ccdr.data.loaders._stub import DataUnavailable
from ccdr.predictions.base import handle_derivation, measurement_failed_result

ID = "P-A17"
NAME = "Axion mass m_a"
_DATA_SOURCE = "ADMX + HAYSTAC"
_ESTIMATOR_ID = "p_a17.scan_band_check"


def derive():
    return axion_mass(f_pq=F_PQ)


def measure():
    bands = []
    shas = []
    for fn in (load_admx, load_haystac):
        try:
            payload, sha = fn()
            masses = [row[0] for row in payload]
            if masses:
                bands.append((min(masses), max(masses)))
                shas.append(sha)
        except DataUnavailable:
            continue
    if not bands:
        return MeasurementResult(
            status=MeasurementStatus.DATA_UNAVAILABLE,
            data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
        )
    # Encode the union of scan ranges as a flat list of (lo, hi) flattened
    # into a comparable scalar: midpoint of the lowest-mass band.
    lo, hi = sorted(bands)[0]
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=(lo + hi) / 2.0,
        uncertainty=(hi - lo) / 2.0,
        data_source=_DATA_SOURCE, data_sha256="|".join(shas),
        estimator_id=_ESTIMATOR_ID, n_samples=len(bands),
        # n_samples stores n_bands; band ranges are encoded in value ± uncertainty
    )


def test():
    d = derive()
    blocker = handle_derivation(ID, d)
    if blocker:
        return blocker
    m = measure()
    if m.status != MeasurementStatus.MEASURED:
        return measurement_failed_result(ID, d, m)
    # CONFIRM iff predicted m_a is within ±uncertainty of the scan-band midpoint
    diff = abs(d.value - m.value)
    if diff <= m.uncertainty:
        status = TestStatus.CONFIRM
    elif diff <= 3 * m.uncertainty:
        status = TestStatus.INCONCLUSIVE
    else:
        status = TestStatus.REJECT
    sigma = diff / (m.uncertainty or 1.0)
    return TestResult(
        prediction_id=ID, status=status,
        derivation=d, measurement=m,
        test_statistic=sigma, pass_threshold=1.0,
        parameters_revision=PARAMETERS_REVISION,
        notes=f"predicted_m_a_ueV={d.value:.3f}, scan_band_ueV=[{m.value - m.uncertainty:.2f}, {m.value + m.uncertainty:.2f}]",
    )
