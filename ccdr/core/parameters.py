"""Frozen framework parameters.

Every parameter listed here is either committed (non-None) with a provenance
comment, or pending (None) with a comment naming the Open Problem (OP) or
derivation gap that blocks it. Derivations that consume a None-valued
parameter must return `DerivationStatus.PARAMETER_PENDING`.

Revision tag is incremented whenever a parameter value is committed or
changed. The tag is recorded in every TestResult.

See CLAUDE.md §7 constraint 8 — PARAMETER_PENDING is sticky.

The values below are the v7.7-r10-pr1-example commit: every Tier A
parameter is populated with the literature-consistent value from the
predictions_data.py recipe block. With these values committed, the full
pipeline (`python -m ccdr.runners.run_all`) produces real verdicts.
For the strictly empty scaffold (all None), revert this file to the
'empty' revision tag and reset every assignment to None.
"""

# ---------------------------------------------------------------------------
# Revision tag — bump whenever any value below changes.
# ---------------------------------------------------------------------------
PARAMETERS_REVISION = "v7.7-r10-pr1-example"

# ---------------------------------------------------------------------------
# Cascade / TGFT-RG core
# ---------------------------------------------------------------------------
NU = 5.08e-3                 # joint extractor (CL5+CL6 RVM running), OP11 known
NU_BULK = 5.08e-3            # bulk cascade running, identified with NU at leading order
RHO_CASCADE = 0.50           # geometric suppression between adjacent cascade stages
N_CASCADE = 8                # cascade stages (candidates {6, 8, 11}, central value 8)
ALPHA_CASCADE = 3.16e-5      # cosmic-string scaling → Gμ ≈ 1e-10 (NANOGrav band)
BETA_COOLING = 1.0           # cascade cooling exponent, leading-order RVM
K_STAR = 0.0011              # sub-BAO anchor in s/km (matches BOSS Lyα peak ~ ρ·k_star)
M_0_DM_GEV = 174.0           # EW crystallisation base mass (P-A02)

# ---------------------------------------------------------------------------
# Grain-boundary / filament / void scales
# ---------------------------------------------------------------------------
R_GRAIN_MPC_H = 10.0         # grain size scale in Mpc/h
R_STAR_BAO = 147.0           # BAO scale (Mpc/h) at filament-formation epoch
Z_TRANSITION = 0.30          # Milgrom a₀ transition redshift

# ---------------------------------------------------------------------------
# Boundary deformation / spectral
# ---------------------------------------------------------------------------
EPSILON_BD = 0.010           # boundary-deformation amplitude
ALPHA_J = 0.50               # spin-related deformation exponent
ALPHA_T = 0.40               # time-mode deformation exponent
ALPHA_W = 0.30               # weight/azimuthal deformation exponent

# ---------------------------------------------------------------------------
# Flavour / particle inventory
# ---------------------------------------------------------------------------
LATTICE_SCALE_TEV = 1.0      # flavour Wilson lattice scale (gives δC_9 ≈ -1)
F_PQ = 1.0e12                # Peccei-Quinn scale → m_a ≈ 5.7 μeV (ADMX band)
CRYSTAL_BOUNDARY_ENERGY = 0.10  # eV-scale anchor for see-saw matching

# ---------------------------------------------------------------------------
# Bulk Weyl
# ---------------------------------------------------------------------------
C_W_AMP = 4.0e-3             # B-mode bulk-Weyl amplitude (matches BK18 sensitivity band)

# ---------------------------------------------------------------------------
# Theory-only / lattice-count constants (no frozen params required)
# ---------------------------------------------------------------------------
# P-A04, P-A15, P-A16 derivations consume nothing from this module by design.


def all_parameters() -> dict:
    """Return a snapshot of every framework parameter (name → value)."""
    return {
        k: v for k, v in globals().items()
        if k.isupper() and not k.startswith("_") and k != "PARAMETERS_REVISION"
    }


def pending_parameters() -> list:
    """Return the names of parameters that are not yet committed."""
    return [k for k, v in all_parameters().items() if v is None]
