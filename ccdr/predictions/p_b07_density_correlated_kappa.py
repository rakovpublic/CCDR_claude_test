"""P-B07 — Density-correlated Ω_DM/Ω_B in lensing convergence (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B07"
NAME = "Density-correlated Δκ"
MISSING = ("NU", "C_KAPPA")
REPAIR = "Commit Δκ amplitude prediction"

derive = make_pending_derive(
    "cascade_residue.delta_kappa@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("ACT DR6 + DES Y3 + KiDS-1000 (Tier B stub)")
test = make_pending_test(ID, derive)
