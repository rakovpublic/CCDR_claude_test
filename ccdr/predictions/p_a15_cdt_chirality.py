"""P-A15 — CDT chirality count (CDT-plusplus simulation; no public-data loader)."""
from ccdr.core.parameters import PARAMETERS_REVISION
from ccdr.core.status import (
    MeasurementResult, MeasurementStatus, TestResult, TestStatus,
)
from ccdr.derivations.lattice_count import cdt_chirality
from ccdr.data.estimators.chirality import chirality_count
from ccdr.predictions.base import handle_derivation, run_sigma_test, measurement_failed_result

ID = "P-A15"
NAME = "CDT chirality count"
PASS_THRESHOLD_SIGMA = 2.0
_DATA_SOURCE = "CDT-plusplus simulation (deferred)"
_ESTIMATOR_ID = "chirality.chirality_count"


def derive():
    # Without an N_4 input the derivation reports DERIVATION_INCOMPLETE.
    return cdt_chirality()


def measure():
    # No public data loader; until the CDT-plusplus ensemble is available
    # this is data-unavailable.
    return MeasurementResult(
        status=MeasurementStatus.DATA_UNAVAILABLE,
        data_source=_DATA_SOURCE, estimator_id=_ESTIMATOR_ID,
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
