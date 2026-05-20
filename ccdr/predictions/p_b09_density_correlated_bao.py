"""P-B09 — Density-correlated BAO sound horizon (Tier B stub: OP12 sign inversion)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B09"
NAME = "Density-correlated δr_d"
MISSING = ("C_R", "SIGN_DELTA_R_D")
REPAIR = "Resolve OP12 (sign inversion)"

derive = make_pending_derive(
    "rvm_cosmology.delta_rd@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("DESI DR2/DR3 (Tier B stub)")
test = make_pending_test(ID, derive)
