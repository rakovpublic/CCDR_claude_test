"""P-B02 — Filament non-Gaussian bispectrum f_NL^grain (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B02"
NAME = "Filament f_NL^grain"
MISSING = ("R_GRAIN_MPC_H",)
REPAIR = "Commit r_grain (grain size scale) as frozen parameter"

derive = make_pending_derive(
    "grain_boundary.fnl_grain@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("Planck NPIPE bispectrum / Euclid (Tier B stub)")
test = make_pending_test(ID, derive)
