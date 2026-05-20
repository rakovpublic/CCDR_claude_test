"""P-B03 — QGP η/s enhancement (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B03"
NAME = "QGP η/s enhancement"
MISSING = ("NU", "C_ETA_S")
REPAIR = "Compute c_η/s from cascade phase-boundary mechanism"

derive = make_pending_derive(
    "grain_boundary.eta_over_s_enhancement@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("ALICE / CMS QGP (Tier B stub)")
test = make_pending_test(ID, derive)
