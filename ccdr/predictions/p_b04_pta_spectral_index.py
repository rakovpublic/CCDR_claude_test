"""P-B04 — PTA GW spectral-index shift δn_GW = -ν/3 (Tier B stub)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B04"
NAME = "PTA GW spectral index shift"
MISSING = ("NU",)
REPAIR = "Commit ν (OP11)"

derive = make_pending_derive(
    "rvm_cosmology.pta_spectral_shift@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("NANOGrav 15-yr (Tier B stub)")
test = make_pending_test(ID, derive)
