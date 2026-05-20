"""P-B12 — Optical-phonon DM mass + cross-section (Tier B stub: BSM1)."""
from ccdr.predictions._tier_b_stub import (
    make_pending_derive, make_pending_measure, make_pending_test,
)

ID = "P-B12"
NAME = "Optical-phonon DM (m_DM, σ_DM)"
MISSING = ("M_DM_GEV", "SIGMA_DM_CM2")
REPAIR = "Sharpen mass and cross-section predictions from EW crystallisation"

derive = make_pending_derive(
    "particle_inventory.optical_phonon_dm@v1-pending", MISSING, REPAIR,
)
measure = make_pending_measure("XENONnT / LZ / PandaX (Tier B stub)")
test = make_pending_test(ID, derive)
