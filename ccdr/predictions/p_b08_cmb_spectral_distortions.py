"""P-B08 — Staged CMB spectral distortions μ, y (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B08"
NAME = "Staged μ, y from cascade stages"
MISSING = ("PER_STAGE_ENERGY_INJECTION",)
REPAIR = "Compute per-stage energy injection from cascade rate"

derive = make_pending_derive(
    "cascade_residue.mu_y_stages@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("FIRAS / PIXIE (Tier B stub)")
test = make_pending_test(ID, derive)
