"""P-B05 — PTA × cosmic-web κ correlation amplitude (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B05"
NAME = "PTA × κ correlation amplitude"
MISSING = ("R_PREDICTED",)
REPAIR = "Compute predicted r amplitude from reducing-volume mechanism"

derive = make_pending_derive(
    "rvm_cosmology.pta_kappa_corr@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("NANOGrav 15-yr × Planck PR4 lensing (Tier B stub)")
test = make_pending_test(ID, derive)
