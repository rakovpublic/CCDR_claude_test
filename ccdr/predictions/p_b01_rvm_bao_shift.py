"""P-B01 — RVM BAO scale shift δr*/r* = ν/2 (Tier B stub: blocked on OP11)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B01"
NAME = "RVM BAO scale shift"
MISSING = ("NU",)
REPAIR = "OP11: ν 500× discrepancy between joint and standalone extractors"

derive = make_pending_derive(
    "rvm_cosmology.bao_shift@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("DESI DR2 (Tier B stub)")
test = make_pending_test(ID, derive)
