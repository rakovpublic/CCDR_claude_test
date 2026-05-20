"""Frozen framework parameters.

Every parameter listed here is either committed (non-None) with a provenance
comment, or pending (None) with a comment naming the Open Problem (OP) or
derivation gap that blocks it. Derivations that consume a None-valued
parameter must return `DerivationStatus.PARAMETER_PENDING`.

Revision tag is incremented whenever a parameter value is committed or
changed. The tag is recorded in every TestResult.

See CLAUDE.md §7 constraint 8 — PARAMETER_PENDING is sticky.
"""

# ---------------------------------------------------------------------------
# Revision tag: bump whenever any value below changes from None or vice versa.
# ---------------------------------------------------------------------------
PARAMETERS_REVISION = "v7.7-r10-pr1-empty"

# ---------------------------------------------------------------------------
# Cascade / TGFT-RG core
# ---------------------------------------------------------------------------
NU = None                    # OP11: 500x ν spread between joint and standalone extractors
NU_BULK = None               # cascade bulk running coefficient (P-A08)
RHO_CASCADE = None           # cascade-stage suppression ratio (P-A02, P-A06)
N_CASCADE = None             # total cascade stages (P-A02; candidates 6, 8, 11)
ALPHA_CASCADE = None         # cosmic-string scaling parameter (P-A14)
BETA_COOLING = None          # cascade-cooling exponent (P-A08)
K_STAR = None                # sub-BAO harmonic anchor (P-A06)
M_0_DM_GEV = None            # cascade base mass at EW crystallisation (P-A02)

# ---------------------------------------------------------------------------
# Grain-boundary / filament / void scales
# ---------------------------------------------------------------------------
R_GRAIN_MPC_H = None         # grain size scale in Mpc/h (P-A01, P-A03, P-A07, P-B02)
R_STAR_BAO = None            # BAO scale at filament-formation epoch (P-A01)
Z_TRANSITION = None          # Milgrom a₀ transition redshift (P-A03)

# ---------------------------------------------------------------------------
# Boundary deformation / spectral
# ---------------------------------------------------------------------------
EPSILON_BD = None            # boundary-deformation amplitude (P-A05)
ALPHA_J = None               # spin-related deformation exponent (P-A05, P-A11)
ALPHA_T = None               # time-mode deformation exponent (P-A11)
ALPHA_W = None               # weight/azimuthal deformation exponent (P-A11)

# ---------------------------------------------------------------------------
# Flavour / particle inventory
# ---------------------------------------------------------------------------
LATTICE_SCALE_TEV = None     # flavour Wilson lattice scale (P-A10)
F_PQ = None                  # Peccei-Quinn scale (P-A17, BSM2)
CRYSTAL_BOUNDARY_ENERGY = None  # right-handed neutrino mass anchor (P-A18, BSM4)

# ---------------------------------------------------------------------------
# Bulk Weyl
# ---------------------------------------------------------------------------
C_W_AMP = None               # B-mode bulk-Weyl amplitude (P-A09; template-only without)

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
