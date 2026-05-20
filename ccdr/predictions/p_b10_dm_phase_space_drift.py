"""P-B10 — DM phase-space drift z-score amplitude (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B10"
NAME = "DM phase-space drift z-score"
MISSING = ("Z_SCORE_AMPLITUDE",)
REPAIR = "Compute predicted z amplitude (currently sign only)"

derive = make_pending_derive(
    "cascade_residue.dm_phase_space@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("GAIA DR3 + DESI MWS (Tier B stub)")
test = make_pending_test(ID, derive)
