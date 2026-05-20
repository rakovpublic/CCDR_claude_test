"""P-B06 — Frozen-vs-live DM fraction in fσ_8 growth (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B06"
NAME = "Frozen-vs-live DM fraction in fσ_8"
MISSING = ("F_LIVE", "ALPHA_GROWTH")
REPAIR = "Derive f_live and α from first principles rather than fitting"

derive = make_pending_derive(
    "cascade_residue.frozen_live_fraction@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("Planck + DESI fσ_8 (Tier B stub)")
test = make_pending_test(ID, derive)
