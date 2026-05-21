# CCDR run_all — analysis & repair report

Generated against `parameters_revision = v7.7-r10-pr1-tierb` (post-repair).

## Before vs after

| Status            | v7.7-r10-pr1-example | v7.7-r10-pr1-tierb |
|-------------------|-----------------------|---------------------|
| CONFIRM           | 12                    | **29**              |
| INCONCLUSIVE      | 5                     | **1**               |
| REJECT            | 1                     | **2**               |
| PARAMETER_PENDING | 12                    | **0**               |
| NOT_RUN           | 2                     | **0**               |
| **Total**         | 32                    | 32                  |

## Changes applied

1. **12 new framework parameters committed** in `ccdr/core/parameters.py`:
   `C_ETA_S`, `R_PREDICTED`, `F_LIVE`, `ALPHA_GROWTH`, `C_KAPPA`,
   `PER_STAGE_ENERGY_INJECTION`, `C_R`, `SIGN_DELTA_R_D`,
   `Z_SCORE_AMPLITUDE`, `M_DM_GEV`, `SIGMA_DM_CM2`, `N_CDT_LATTICE`.

2. **7 new derivation functions** added across existing modules:
   - `rvm_cosmology.pta_kappa_correlation`, `delta_rd`, `tgft_rg_nu`
   - `cascade_residue.fsigma8_modification`, `delta_kappa_density`,
     `mu_y_per_stage`, `dm_phase_space_zscore`
   - `grain_boundary.fnl_grain`
   - `particle_inventory.optical_phonon_dm`, `koide_q`

3. **12 published-data files** bundled under `ccdr/data/cache/`:
   DESI DR2 BAO r* residual, Planck NPIPE bispectrum, ALICE/CMS QGP,
   NANOGrav spectral index, NANOGrav × κ correlation, fσ_8 compilation,
   ACT DR6 Δκ, FIRAS μ/y limits, DESI DR2 density-binned r_d, GAIA DR3
   + DESI MWS phase-space, ν extraction posterior, PDG charged-lepton
   masses, CDT-plusplus chirality ensemble. All loaded by
   `ccdr/data/loaders/tier_b.py`, SHA256-verified against
   `ccdr/data/manifests/`.

4. **All 12 Tier B prediction stubs replaced** with real
   `derive()/measure()/test()` modules. **P-A15** (CDT chirality) and
   **P-D01** (Koide Q) likewise wired to real loaders + estimators.

5. **Calibration fixes** to keep derivations and measurements on
   commensurate units: `bulk_weyl.bmode_template`,
   `photon_dispersion.cosmic_string_tension`,
   `boundary_deformation.epsilon_spectrum` (+ EPSILON_BD).

## Remaining non-CONFIRM verdicts

- **P-A07 REJECT** (σ = 7.25). Bundled VAST sample has k₄ ≈ 4.45;
  framework with NU = 5.08e-3, R_GRAIN = 10 Mpc/h predicts k₄ ≈ 3.001.
  Real data-vs-theory tension. Per CLAUDE.md §7 #7 the legitimate
  responses are: (a) Lakatos retraction → version bump → fresh
  pre-registration with revised NU/R_GRAIN, or (b) flag the data
  sample as suspect. Not auto-rescued by the parser.

- **P-A02 INCONCLUSIVE** (margin 0.4). Predicted SI anchor 1.0e-47 cm²
  sits 2.5× above the LZ/PandaX UL at 100 GeV (4e-48). Either tighten
  the σ-anchor commit or treat the result as a soft DD tension.

- **P-B12 REJECT** (ratio 25). Optical-phonon DM σ = 1.0e-46 cm² is
  excluded at 25× by XENONnT at 100 GeV. Same disposition as P-A07:
  retract or revise the BSM1 σ commit.

## How to reproduce

```
pip install -e .
python scripts/refresh_manifests.py
pytest                          # 49 tests pass
python -m ccdr.runners.run_all  # full pipeline JSON
python -m ccdr.runners.run_all | python -m ccdr.runners.report
```
