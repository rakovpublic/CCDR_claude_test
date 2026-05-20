# CLAUDE.md — CCDR Prediction Project

This is one project, not two. Each prediction has a **derivation half** (frozen parameters → predicted value via the cascade mechanism) and a **measurement half** (public data → measured value). The two halves are bound into a single test that returns one verdict. The project's purpose is to build, maintain, and run that bound pipeline for the Tier A and Tier B predictions specified in `predictions_data.py`.

## 1. The unified pipeline

Every prediction goes through five stages, in this order, with no shortcuts:

```
                    [core/parameters.py]
                            │
                            ▼
   1.  DERIVE         (pure math, no data)
       derivations/<topic>.py
       returns DerivationResult{ value, uncertainty, status, provenance }
                            │
                            ▼
   2.  PREDICT        (binding derived value to a measurement plan)
       predictions/<id>.py :: predicted_value()
                            │
                            ▼
   3.  MEASURE        (data loader + estimator, no framework parameters)
       data/loaders/<source>.py + predictions/<id>.py :: measured_value()
       returns MeasurementResult{ value, uncertainty, data_sha256 }
                            │
                            ▼
   4.  COMPARE        (compute test statistic)
       predictions/<id>.py :: test_statistic()
                            │
                            ▼
   5.  VERDICT        (CONFIRM | REJECT | INCONCLUSIVE | NOT_RUN | PARAMETER_PENDING)
       returns TestResult
```

The architectural commitment: every stage is independently testable. Stage 1 has unit tests with no data. Stages 3–5 have unit tests with synthetic data. Stage 2 just hands off — it should have no logic of its own beyond calling stages 1 and 3.

A prediction with a brilliant test against amazing data but a hand-waved derivation is not testable. A prediction with an immaculate derivation but a sloppy estimator is not testable either. Both halves get the same engineering rigour.

## 2. Core data structures

All in `core/status.py`. Frozen — do not extend.

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

class DerivationStatus(Enum):
    DERIVED = "DERIVED"                       # value computed from frozen params
    PARAMETER_PENDING = "PARAMETER_PENDING"   # one or more frozen params missing
    DERIVATION_INCOMPLETE = "DERIVATION_INCOMPLETE"  # math not fully worked out
    DERIVATION_FAILED = "DERIVATION_FAILED"   # runtime error in derivation

class MeasurementStatus(Enum):
    MEASURED = "MEASURED"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    DATA_QUALITY_FAILED = "DATA_QUALITY_FAILED"   # SHA256 mismatch, format error
    INSUFFICIENT_STATISTICS = "INSUFFICIENT_STATISTICS"

class TestStatus(Enum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOT_RUN = "NOT_RUN"
    PARAMETER_PENDING = "PARAMETER_PENDING"

@dataclass(frozen=True)
class DerivationResult:
    status: DerivationStatus
    value: Optional[float] = None
    uncertainty: Optional[float] = None
    provenance: str = ""              # e.g. "CCDR §8.3, grain-boundary kernel"
    missing_parameters: tuple = ()
    parameters_used: dict = field(default_factory=dict)   # name → value at time of derivation
    derivation_function_id: str = ""  # which fn produced this

@dataclass(frozen=True)
class MeasurementResult:
    status: MeasurementStatus
    value: Optional[float] = None
    uncertainty: Optional[float] = None
    data_source: str = ""
    data_sha256: str = ""
    estimator_id: str = ""           # which estimator produced this
    n_samples: int = 0

@dataclass(frozen=True)
class TestResult:
    prediction_id: str
    status: TestStatus
    derivation: DerivationResult
    measurement: MeasurementResult
    test_statistic: Optional[float] = None
    pass_threshold: Optional[float] = None
    parameters_revision: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""
```

A `TestResult` *contains* the `DerivationResult` and `MeasurementResult` it was built from. The full provenance chain is in every result — no separate logs to consult.

## 3. Repository layout

```
ccdr/
├── pyproject.toml
├── README.md
├── core/
│   ├── parameters.py           # Frozen framework parameters with provenance
│   ├── status.py               # Frozen taxonomies (above)
│   ├── cascade.py              # χ_k function, ν algebra, mass-tower helper
│   ├── rvm.py                  # ρ_vac(H), C₀(t), Λ(t)
│   ├── action.py               # Symbolic modified action (sympy)
│   └── perturbations.py        # Cascade-modified linear theory
│
├── derivations/                # ── HALF 1: parameter → predicted value ──
│   ├── __init__.py
│   ├── base.py                 # @derivation decorator + helpers
│   ├── grain_boundary.py       # δk₄, r_texture, a₀, η/s — shared mechanism
│   ├── cascade_residue.py      # mass-tower, ν-dependent amplitudes
│   ├── rvm_cosmology.py        # w(z) drift, BAO shift, growth deficit
│   ├── photon_dispersion.py    # cosmic-string h_c, dark-photon ε
│   ├── boundary_deformation.py # ε_ℓm spectrum (P-A11, P-A05)
│   ├── bulk_weyl.py            # B-mode ℓ-shape template (P-A09)
│   ├── flavour_wilson.py       # b→sμμ pattern (P-A10)
│   ├── lattice_count.py        # CDT chirality count (P-A15)
│   ├── algebra_bounds.py       # DA/O N≤11 (P-A16)
│   ├── particle_inventory.py   # axion m_a, νR M_R (P-A17, P-A18)
│   ├── joint_inference.py      # CL5+CL6+CL7 posterior (P-A19)
│   ├── theory_consistency.py   # AS-EPRL γ comparison (P-A04)
│   └── tests/                  # Unit tests for derivations (no data)
│       └── test_*.py
│
├── predictions/                # ── BINDING: derivation × measurement ──
│   ├── __init__.py
│   ├── base.py                 # Prediction protocol with derive()/measure()/test()
│   ├── p_a01_filament_correlation.py
│   ├── p_a02_mass_tower.py
│   ├── p_a03_highz_a0.py
│   ├── p_a04_as_eprl_consistency.py
│   ├── p_a05_ringdown_qnm.py
│   ├── p_a06_subbao_harmonics.py
│   ├── p_a07_void_kurtosis.py
│   ├── p_a08_secular_w_drift.py
│   ├── p_a09_bulk_weyl_bmode.py
│   ├── p_a10_b_to_smumu_pattern.py
│   ├── p_a11_boundary_deformation.py
│   ├── p_a12_cl4_joint_p3_p38.py
│   ├── p_a13_dark_photon_mixing.py
│   ├── p_a14_cosmic_string_tension.py
│   ├── p_a15_cdt_chirality.py
│   ├── p_a16_dao_bound.py
│   ├── p_a17_axion_mass.py
│   ├── p_a18_right_handed_nu.py
│   ├── p_a19_joint_consistency.py
│   ├── p_b01_rvm_bao_shift.py        # Tier B stubs return PARAMETER_PENDING
│   └── ...                            # one stub per Tier B prediction
│
├── data/                       # ── HALF 2: data loading and estimators ──
│   ├── __init__.py
│   ├── manifests/              # SHA256 manifests for every data source
│   ├── loaders/                # one module per public source
│   ├── estimators/             # reusable estimators called by predictions
│   ├── cache/                  # local cached copies (gitignored)
│   └── tests/                  # Unit tests for loaders + estimators
│
├── runners/
│   ├── derive_all.py           # Run derivations only, no data
│   ├── measure_all.py          # Run measurements only, no derivations
│   ├── run_all.py              # Full pipeline
│   ├── run_one.py
│   └── report.py
│
└── tests/
    ├── test_status_taxonomy_frozen.py     # Lint: enums unchanged
    ├── test_no_version_tags.py            # Lint: no _v\d+ in status strings
    ├── test_derivations_pure.py           # Lint: derivations do no I/O
    ├── test_measurements_framework_blind.py  # Lint: measurements don't import params
    ├── test_parameters_loadable.py
    └── test_pipeline_integration.py       # End-to-end on synthetic data
```

## 4. Canonical per-prediction module

This is the template. Every prediction module follows it. The example here is P-A07 (void kurtosis) because it has the cleanest derivation. Other predictions vary only in which derivation function and which loader they import.

```python
# predictions/p_a07_void_kurtosis.py
"""
P-A07 — Void-wall transverse kurtosis k₄ > 4
Source: CCDR §8.3 (grain-boundary scattering at void walls)
"""
from ccdr.core.parameters import NU, R_GRAIN_MPC_H, PARAMETERS_REVISION
from ccdr.core.status import (
    DerivationResult, DerivationStatus,
    MeasurementResult, MeasurementStatus,
    TestResult, TestStatus,
)
from ccdr.derivations.grain_boundary import predict_void_kurtosis
from ccdr.data.loaders.vast_voids import load_vast_catalogue
from ccdr.data.estimators.kurtosis import transverse_kurtosis

ID = "P-A07"
NAME = "Void-wall transverse kurtosis k₄ > 4"
PASS_THRESHOLD_SIGMA = 2.0

def derive() -> DerivationResult:
    """Compute predicted k₄ from frozen framework parameters.
    Pure function: no data, no I/O, no globals beyond core/parameters."""
    return predict_void_kurtosis(nu=NU, r_grain_mpc_h=R_GRAIN_MPC_H)

def measure() -> MeasurementResult:
    """Compute measured k₄ from VAST VoidFinder catalogue.
    No reference to framework parameters; pure data + estimator."""
    catalogue, sha256 = load_vast_catalogue()
    k4_meas, k4_unc, n_voids = transverse_kurtosis(catalogue)
    if n_voids < 100:
        return MeasurementResult(
            status=MeasurementStatus.INSUFFICIENT_STATISTICS,
            data_source="VAST VoidFinder",
            data_sha256=sha256,
            estimator_id="kurtosis.transverse_kurtosis",
            n_samples=n_voids,
        )
    return MeasurementResult(
        status=MeasurementStatus.MEASURED,
        value=k4_meas,
        uncertainty=k4_unc,
        data_source="VAST VoidFinder",
        data_sha256=sha256,
        estimator_id="kurtosis.transverse_kurtosis",
        n_samples=n_voids,
    )

def test() -> TestResult:
    """Full pipeline. Calls derive(), then measure(), then compares."""
    d = derive()
    if d.status == DerivationStatus.PARAMETER_PENDING:
        return TestResult(
            prediction_id=ID,
            status=TestStatus.PARAMETER_PENDING,
            derivation=d,
            measurement=MeasurementResult(status=MeasurementStatus.MEASURED),
            parameters_revision=PARAMETERS_REVISION,
            notes=f"Blocked on: {d.missing_parameters}",
        )
    m = measure()
    if m.status != MeasurementStatus.MEASURED:
        return TestResult(
            prediction_id=ID,
            status=TestStatus.INCONCLUSIVE,
            derivation=d,
            measurement=m,
            parameters_revision=PARAMETERS_REVISION,
            notes=f"Measurement status: {m.status.value}",
        )
    # Both halves succeeded. Compare.
    sigma = (m.value - d.value) / (d.uncertainty**2 + m.uncertainty**2)**0.5
    if abs(sigma) <= PASS_THRESHOLD_SIGMA:
        verdict = TestStatus.CONFIRM
    elif abs(sigma) > 3.0:
        verdict = TestStatus.REJECT
    else:
        verdict = TestStatus.INCONCLUSIVE
    return TestResult(
        prediction_id=ID,
        status=verdict,
        derivation=d,
        measurement=m,
        test_statistic=sigma,
        pass_threshold=PASS_THRESHOLD_SIGMA,
        parameters_revision=PARAMETERS_REVISION,
    )
```

And the corresponding derivation function it imports:

```python
# derivations/grain_boundary.py
"""
Grain-boundary phonon-scattering derivations.
Shared across P-A01 (filament texture), P-A03 (a₀), P-A07 (void k₄), P-B03 (η/s).

Provenance: CCDR §8.2 (filaments), §8.3 (voids), §6.1 (Milgrom).
"""
import math
from typing import Optional
from ccdr.core.status import DerivationResult, DerivationStatus

DERIVATION_FN_ID = "grain_boundary.predict_void_kurtosis@v1"

def predict_void_kurtosis(
    nu: Optional[float],
    r_grain_mpc_h: Optional[float],
) -> DerivationResult:
    """
    Predict transverse kurtosis k₄ of void-wall radial-drift distribution
    from grain-boundary phonon-scattering kernel convolution.

    Derivation pathway (CCDR §8.3 eq 8.17):
      Lorentzian grain-density profile f(r) = (r_g/π) / (r² + r_g²)
      convolved with Gaussian transverse-momentum kernel.
      4th cumulant of result: κ₄ / σ⁴ = 3 + δk₄
      where δk₄ = c_4(ν) × (r_grain / r_void_wall)²
      and c_4(ν) ≈ ν × π² / 6
    """
    missing = []
    if nu is None: missing.append("NU")
    if r_grain_mpc_h is None: missing.append("R_GRAIN_MPC_H")
    if missing:
        return DerivationResult(
            status=DerivationStatus.PARAMETER_PENDING,
            missing_parameters=tuple(missing),
            derivation_function_id=DERIVATION_FN_ID,
            provenance="CCDR §8.3 eq 8.17",
        )

    r_void_wall_mpc_h = 30.0  # typical void-wall scale; could be itself a parameter
    c4 = nu * math.pi**2 / 6.0
    delta_k4 = c4 * (r_grain_mpc_h / r_void_wall_mpc_h)**2
    k4 = 3.0 + delta_k4
    # Uncertainty: propagate fractional uncertainty on ν (~10%) and r_grain (~30%)
    rel_unc_sq = (0.10)**2 + (2 * 0.30)**2  # quadratic in r_grain
    uncertainty = delta_k4 * rel_unc_sq**0.5

    return DerivationResult(
        status=DerivationStatus.DERIVED,
        value=k4,
        uncertainty=uncertainty,
        provenance="CCDR §8.3 eq 8.17 (grain-boundary scattering kernel)",
        parameters_used={"NU": nu, "R_GRAIN_MPC_H": r_grain_mpc_h},
        derivation_function_id=DERIVATION_FN_ID,
    )
```

And the derivation has its own unit test, independent of data:

```python
# derivations/tests/test_grain_boundary.py
from ccdr.derivations.grain_boundary import predict_void_kurtosis
from ccdr.core.status import DerivationStatus

def test_returns_pending_when_nu_missing():
    r = predict_void_kurtosis(nu=None, r_grain_mpc_h=10.0)
    assert r.status == DerivationStatus.PARAMETER_PENDING
    assert "NU" in r.missing_parameters

def test_lambda_cdm_limit():
    """ν → 0 should give Gaussian k₄ = 3."""
    r = predict_void_kurtosis(nu=0.0, r_grain_mpc_h=10.0)
    assert r.status == DerivationStatus.DERIVED
    assert abs(r.value - 3.0) < 1e-10

def test_excess_kurtosis_monotonic_in_nu():
    """Larger ν → larger δk₄."""
    r1 = predict_void_kurtosis(nu=1e-3, r_grain_mpc_h=10.0)
    r2 = predict_void_kurtosis(nu=5e-3, r_grain_mpc_h=10.0)
    assert r2.value > r1.value

def test_excess_kurtosis_scales_as_r_grain_squared():
    """δk₄ should scale as r_grain² (CCDR §8.3 eq 8.17)."""
    r1 = predict_void_kurtosis(nu=5e-3, r_grain_mpc_h=10.0)
    r2 = predict_void_kurtosis(nu=5e-3, r_grain_mpc_h=20.0)
    ratio = (r2.value - 3.0) / (r1.value - 3.0)
    assert abs(ratio - 4.0) < 0.01
```

This is the pattern. Every Tier A prediction has: a derivation function with its own unit tests, a measurement function, and a glue layer that produces a `TestResult`. The derivation is testable today even before any data is loaded.

## 5. Per-prediction derivation pathways

The mapping from prediction → derivation module → required parameters. This is the build manifest for the derivation library.

| ID | Derivation function | Inputs (frozen params) | Math source |
|---|---|---|---|
| P-A01 | `grain_boundary.predict_filament_texture(nu, r_grain, r_star)` | NU, R_GRAIN, R_STAR_BAO | CCDR §8.2 |
| P-A02 | `cascade_residue.mass_tower(m_0, rho, N)` | M_0_DM_GEV, RHO_CASCADE, N_CASCADE | CCDR §4.5, §7 |
| P-A03 | `grain_boundary.a0_z_evolution(nu, z_star)` | NU, Z_TRANSITION | CCDR §6.1 |
| P-A04 | `theory_consistency.as_eprl_gamma(cascade_stage_k)` | none (theory only) | TGFT-RG + Bahr-Steinhaus |
| P-A05 | `boundary_deformation.qnm_deviation(spin, mass)` | EPSILON_BD, ALPHA_J | CCDR §15.5 / Synthesis §22 |
| P-A06 | `cascade_residue.subbao_harmonics(rho, k_star)` | RHO_CASCADE, K_STAR | CCDR §13 |
| P-A07 | `grain_boundary.predict_void_kurtosis(nu, r_grain)` | NU, R_GRAIN | CCDR §8.3 |
| P-A08 | `rvm_cosmology.w_z_drift(nu_bulk, beta)` | NU_BULK, BETA_COOLING | CCDR §15.2 |
| P-A09 | `bulk_weyl.bmode_template(c_w_amp)` (template only) | none for shape; C_W for amplitude | CCDR §15.3 |
| P-A10 | `flavour_wilson.b_to_smumu_pattern(lattice_scale)` | LATTICE_SCALE_TEV | CCDR §15.4 |
| P-A11 | `boundary_deformation.epsilon_spectrum(alpha_J, alpha_T, alpha_W)` | scaling exponents | CCDR §15.5 |
| P-A12 | `grain_boundary.joint_density_sign(P-A01, P-A07)` | none (composition) | CL4 |
| P-A13 | `photon_dispersion.dark_photon_epsilon(nu)` | NU | Synthesis §21.4 BSM3 |
| P-A14 | `photon_dispersion.cosmic_string_tension(alpha)` | ALPHA_CASCADE | Synthesis §21.4 BSM5 |
| P-A15 | `lattice_count.cdt_chirality(N_4)` | CDT ensemble parameters | Synthesis §21.4 BSM6 |
| P-A16 | `algebra_bounds.dao_max_N()` | none | Synthesis §21.3 P24 |
| P-A17 | `particle_inventory.axion_mass(f_PQ)` | F_PQ | Synthesis §21.4 BSM2 |
| P-A18 | `particle_inventory.right_handed_nu_mass()` | crystal boundary energy | Synthesis §21.4 BSM4 |
| P-A19 | `joint_inference.posterior(P-A08, P-A09, P-A10, P-A11)` | composition | CL5+CL6+CL7 |

Tier B predictions get derivation function stubs that return `DERIVATION_INCOMPLETE` with the specific math gap documented. They are not implementable until either (a) the framework freezes the missing parameter, or (b) the missing math is worked out in the derivation library.

## 6. Per-prediction measurement pathways

The mapping from prediction → loader → estimator.

| ID | Loader | Estimator |
|---|---|---|
| P-A01 | `filament_catalogues.load_disperse_or_bisous()` | `correlation.exponential_correlation_fit()` |
| P-A02 | `xenonnt.load_2025() + lz.load_2024() + pandax.load_2024()` | `mass_tower_consistency_check()` |
| P-A03 | `kmos3d.load() + sparc.load() + manga.load()` | `rotation_curve_a0_extractor()` |
| P-A04 | (none — theory only) | (sympy comparison) |
| P-A05 | `gwtc3.load_high_snr_ringdowns()` | `ringdown_qnm.population_deviation()` |
| P-A06 | `boss_lyalpha.load_pf_k()` | `harmonic_peak_detector()` |
| P-A07 | `vast_voids.load_catalogue()` | `kurtosis.transverse_kurtosis()` |
| P-A08 | `pantheon_plus.load() + desi_dr2.load()` | `w_z_reconstruction()` |
| P-A09 | `bk18.load_bandpowers() + planck_pr4.load_bmode()` | `bmode_template_fit()` |
| P-A10 | `lhcb_b2smumu.load_run3()` | `wilson_coefficient_fitter()` |
| P-A11 | `eht.load_m87_sgrA() + gwtc3.load_ringdowns()` | `boundary_deformation_residual()` |
| P-A12 | `filament_catalogues + vast_voids` | (composition of A01 + A07 estimators) |
| P-A13 | `babar_dark_photon.load_limits() + lhcb_dp.load()` | `exclusion_consistency_check()` |
| P-A14 | `nanograv_15yr.load()` | `cosmic_string_template_fit()` |
| P-A15 | CDT-plusplus simulation (no public-data loader) | `chirality_count()` |
| P-A16 | (none — bound check) | `consistency_check_N_le_11()` |
| P-A17 | `admx.load() + haystac.load()` | `exclusion_consistency_check()` |
| P-A18 | `nubb_decay.load_kamland_zen() + katrin.load()` | `see_saw_consistency()` |
| P-A19 | composition of A08, A09, A10, A11 loaders | `joint_posterior()` |

## 7. Hard constraints

These are non-negotiable. Violations are CI failures.

1. **Frozen status taxonomies.** `DerivationStatus`, `MeasurementStatus`, `TestStatus` are each closed enums. No `..._like`, no `_v75`, no per-release variants. Enforced by `tests/test_status_taxonomy_frozen.py` which hashes the enum members.

2. **Pre-registration enforced by git.** Each derivation function has `DERIVATION_FN_ID = "<name>@v1"`. Changes to the function bump the version (`@v2`), recorded in the result's `derivation_function_id`. Pre-registration means: the derivation function (with its version) must be committed *before* the data loader for its measurement counterpart. CI enforces this via commit-order linting.

3. **Derivations are pure functions.** No I/O, no globals beyond `core/parameters`, no random state without explicit seed. Enforced by `tests/test_derivations_pure.py` which monkey-patches `open`, `requests`, etc., and runs every derivation function — any I/O attempt fails the test.

4. **Measurements are framework-blind.** A measurement function takes data and an estimator; it does *not* know what the framework predicts. Enforced by `tests/test_measurements_framework_blind.py` which greps every loader/estimator module for imports from `core.parameters` or `derivations` and fails if any are found.

5. **One prediction = one verdict.** Each `predictions/p_xxx.py` exposes one `test()` returning one `TestResult`. If a prediction has multiple data sources, they are combined inside the measurement function — not exposed as separate verdicts.

6. **Data SHA256 in every result.** Every `MeasurementResult` carries `data_sha256`. Mismatch with the manifest → `MeasurementStatus.DATA_QUALITY_FAILED`. No silent data updates.

7. **No recovery cascades.** A `REJECT` result does not get "improved" to `CONFIRM` by a parser change. The legitimate responses to `REJECT` are: (a) update the framework (Lakatos retraction, version bump, fresh pre-registration), or (b) flag a data-quality problem (move to `INCONCLUSIVE`, document, block promotion until resolved).

8. **`PARAMETER_PENDING` is sticky.** A prediction returning `PARAMETER_PENDING` does not become `CONFIRM` because the parser got cleverer. It becomes `CONFIRM` only when the missing parameter is committed in `core/parameters.py` and the derivation actually runs.

## 8. The four load-bearing lint tests

These tests are the project's spine. Place them in `tests/`:

### tests/test_status_taxonomy_frozen.py
```python
import hashlib
from ccdr.core.status import DerivationStatus, MeasurementStatus, TestStatus

EXPECTED_HASHES = {
    "DerivationStatus": "<hash of frozen members>",
    "MeasurementStatus": "<hash of frozen members>",
    "TestStatus": "<hash of frozen members>",
}

def _enum_hash(enum_cls):
    members = sorted(m.name + "=" + m.value for m in enum_cls)
    return hashlib.sha256(("|".join(members)).encode()).hexdigest()

def test_taxonomies_frozen():
    for cls in (DerivationStatus, MeasurementStatus, TestStatus):
        h = _enum_hash(cls)
        assert h == EXPECTED_HASHES[cls.__name__], (
            f"{cls.__name__} was modified. The taxonomy is frozen. "
            f"See CLAUDE.md §7 constraint 1."
        )
```

### tests/test_no_version_tags.py
```python
import re, pkgutil, importlib
import ccdr.predictions, ccdr.derivations

FORBIDDEN = re.compile(r"_v\d+|_confirm_like|_ready|_compatible|_schema_backed")

def test_no_version_tagged_status_strings():
    for pkg in (ccdr.predictions, ccdr.derivations):
        for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
            mod = importlib.import_module(name)
            for attr in dir(mod):
                val = getattr(mod, attr, None)
                if isinstance(val, str) and FORBIDDEN.search(val):
                    raise AssertionError(
                        f"Forbidden version-tagged string in {name}.{attr}: {val!r}\n"
                        f"The status taxonomy is closed. See CLAUDE.md §7."
                    )
```

### tests/test_derivations_pure.py
```python
import pkgutil, importlib, builtins
from unittest.mock import patch
import ccdr.derivations
from ccdr.core.status import DerivationResult, DerivationStatus

def _all_derivation_fns():
    fns = []
    for finder, name, ispkg in pkgutil.walk_packages(ccdr.derivations.__path__, "ccdr.derivations."):
        if ".tests" in name or name.endswith(".base"):
            continue
        mod = importlib.import_module(name)
        for attr in dir(mod):
            val = getattr(mod, attr)
            if callable(val) and getattr(val, "__module__", None) == name:
                if not attr.startswith("_"):
                    fns.append((name, attr, val))
    return fns

def test_derivations_do_no_io():
    """Every derivation function must succeed (or fail cleanly with PARAMETER_PENDING)
    even when filesystem and network are unavailable."""
    def _refuse_open(*args, **kwargs):
        raise OSError("derivations may not perform I/O (see CLAUDE.md §7 #3)")
    with patch("builtins.open", _refuse_open):
        for mod_name, attr, fn in _all_derivation_fns():
            try:
                # Call with all-None arguments; should return PARAMETER_PENDING, not crash
                import inspect
                sig = inspect.signature(fn)
                nones = {p: None for p in sig.parameters}
                result = fn(**nones)
                assert isinstance(result, DerivationResult), (
                    f"{mod_name}.{attr} did not return DerivationResult"
                )
            except OSError as e:
                raise AssertionError(
                    f"{mod_name}.{attr} attempted I/O. Derivations must be pure. "
                    f"See CLAUDE.md §7 constraint 3."
                ) from e
```

### tests/test_measurements_framework_blind.py
```python
import pkgutil, importlib, ast, pathlib
import ccdr.data

FORBIDDEN_IMPORTS = ("ccdr.core.parameters", "ccdr.derivations")

def test_no_framework_imports_in_measurements():
    """Loaders and estimators must not import framework parameters or
    derivation modules. The measurement half is framework-blind."""
    data_root = pathlib.Path(ccdr.data.__file__).parent
    for py_file in data_root.rglob("*.py"):
        if "tests" in py_file.parts:
            continue
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = node.module if hasattr(node, "module") else None
                names = ([module] if module else []) + [a.name for a in node.names]
                for n in names:
                    if n and any(n.startswith(f) for f in FORBIDDEN_IMPORTS):
                        raise AssertionError(
                            f"{py_file}: forbidden import of {n}. "
                            f"Measurements are framework-blind. "
                            f"See CLAUDE.md §7 constraint 4."
                        )
```

The four lints together enforce the architectural commitments. If they pass on an empty repo, they will catch every drift the project tries to introduce later. If they don't pass on empty, they're broken and need fixing before any code is written.

## 9. Implementation order

The order is chosen so that each step produces something runnable, and so that the test infrastructure proves itself before any predictions ride on it.

**Phase 0 — Core infrastructure (mandatory; nothing else builds without this)**

1. `core/status.py` — the three enums and three dataclasses
2. `core/parameters.py` — populated with the parameter names from §6 of the docx, all values set to `None` and a comment naming the OP that blocks each
3. The four lint tests in `tests/` — they must pass on the empty scaffold

**Phase 1 — Derivation library on synthetic / theory-only predictions**

4. `derivations/algebra_bounds.py` + tests → enables P-A16
5. `derivations/theory_consistency.py` + tests → enables P-A04
6. `derivations/lattice_count.py` + tests → enables P-A15 (requires CDT-plusplus build; defer if build fails in the sandbox)
7. `derivations/grain_boundary.py` + tests → enables P-A01, P-A03, P-A07, P-B03
8. `derivations/cascade_residue.py` + tests → enables P-A02, P-A06, P-B06
9. `derivations/rvm_cosmology.py` + tests → enables P-A08, P-B01
10. `derivations/photon_dispersion.py` + tests → enables P-A13, P-A14
11. `derivations/boundary_deformation.py` + tests → enables P-A05, P-A11
12. `derivations/bulk_weyl.py` + tests → enables P-A09 (template, not amplitude)
13. `derivations/flavour_wilson.py` + tests → enables P-A10
14. `derivations/particle_inventory.py` + tests → enables P-A17, P-A18

At this point: derivations are testable in isolation. Every Tier A prediction has a derivation function that either produces a value or returns `PARAMETER_PENDING`. No data has been touched yet. `python -m ccdr.runners.derive_all` should work.

**Phase 2 — Data layer**

15. `data/manifests/*.json` — SHA256 manifests for every source (start with placeholders; populate as loaders are built)
16. `data/loaders/*.py` + tests — one loader per source, in the order matching prediction implementation order in Phase 3
17. `data/estimators/*.py` + tests — estimators with synthetic-data unit tests

`python -m ccdr.runners.measure_all` should now work — runs every loader and estimator on real data without referring to the framework.

**Phase 3 — Bind derivation × measurement into predictions**

Implement in this order (lowest external-blocker risk first):

18. P-A16 (DA/O bound) — no data, no estimator
19. P-A04 (AS-EPRL) — no data, no estimator
20. P-A14 (cosmic strings, NANOGrav) — template fit
21. P-A07 (void kurtosis, VAST) — clean estimator
22. P-A10 (b→sμμ, LHCb) — Wilson-coefficient fit
23. P-A13 (dark photon, BaBar/LHCb) — exclusion check
24. P-A17 (axion, ADMX) — exclusion check
25. P-A11 (boundary deformation, EHT + GWTC-3) — composite
26. P-A05 (ringdown QNM, GWTC-3) — population fit
27. P-A01 (filament correlation) — catalogue dependent
28. P-A06 (sub-BAO, BOSS Lyα)
29. P-A03 (high-z a₀, KMOS3D + SPARC)
30. P-A18 (νR, 0νββ data)
31. P-A02 (mass tower consistency check vs current DD)
32. P-A08 (w drift, DR2-capable form)
33. P-A09 (B-mode template, BK18 upper limit)
34. P-A15 (CDT chirality — if Phase-1 CDT-plusplus succeeded)
35. P-A12 (CL4 joint) — depends on A01 + A07
36. P-A19 (joint A08+A09+A10+A11) — depends on all four

**Phase 4 — Tier B stubs**

37. One file per Tier B prediction, returning `PARAMETER_PENDING` with the specific OP cited. Do not implement test logic — that comes after parameter commitment.

**Phase 5 — Tier D stubs**

38. One file for each SM-D entry pending §21 execution. Same pattern as Tier B but with `DERIVATION_INCOMPLETE` status and `§21` note.

**Phase 6 — Runners and report**

39. `runners/derive_all.py` — run all derivations, no data needed
40. `runners/measure_all.py` — run all measurements, no derivations needed (useful for data-quality monitoring independent of framework)
41. `runners/run_all.py` — full pipeline
42. `runners/report.py` — JSON in, one-page summary out, broken down by status

## 10. What success looks like

When this is built:

- `python -m ccdr.runners.derive_all` runs the entire derivation library without touching any data. Every Tier A derivation produces a `DerivationResult` of `DERIVED` or `PARAMETER_PENDING`. The output tells you exactly which framework parameters need committing to unlock how many predictions.

- `python -m ccdr.runners.measure_all` runs every loader and estimator without referring to the framework. Every Tier A measurement produces a `MeasurementResult` of `MEASURED` or one of the data-failure statuses. The output tells you the state of public data independent of any theoretical position.

- `python -m ccdr.runners.run_all` runs the full pipeline. Each Tier A prediction returns one `TestResult` with both halves attached. The report counts CONFIRM, REJECT, INCONCLUSIVE, PARAMETER_PENDING.

- The pre-registration lint catches commits that change a derivation function alongside its corresponding measurement.

- The no-version-tags lint catches any attempt to introduce a `_v75`-style status name.

- The pure-derivation lint catches any attempt to load data inside a derivation.

- The framework-blind-measurement lint catches any attempt to use framework parameters inside a measurement.

- Adding a new prediction is: one derivation function (with unit tests), one prediction module, one loader if needed. No changes to existing predictions, no changes to the taxonomy.

## 11. What success does not include

- Running a prediction whose derivation returned `PARAMETER_PENDING`. It stays pending until the parameter is committed.
- A derivation that imports data. If it needs data, it's not a derivation; it's a measurement or a fit.
- A measurement that imports framework parameters. If it needs them, it's not a measurement; it's a fit.
- Multiple "routes" through a prediction. One prediction, one derivation, one measurement, one verdict.
- A version-tagged status. The taxonomy is closed.
- A "_ready" or "_compatible" or "_schema_backed" intermediate state. The five `TestStatus` values are exhaustive.

---

## 12. For Claude Code

Read this file completely. Read `predictions_data.py` for the structured prediction list. Then implement Phase 0 in full and let the four lint tests pass on the empty scaffold before writing any derivation code. The infrastructure is load-bearing — if the lints don't pass on an empty repo, they will not catch violations in a full one.

Implement derivations and predictions in the order in §9. Make one commit per derivation function and one commit per prediction module. The commit message format: `derive(P-A07): grain-boundary void kurtosis from §8.3 eq 8.17`. For predictions: `predict(P-A07): bind void-kurtosis derivation to VAST loader`.

If at any point during implementation you find yourself wanting to:

- Add a 6th `TestStatus` value
- Add a version suffix to a status string
- Import data inside a derivation
- Import framework parameters inside a measurement
- Return multiple `TestResult`s from one prediction
- Add a "recovery" code path that flips an earlier `REJECT` to `CONFIRM`

— stop. Re-read §7. The constraints are there because each one corresponds to a specific failure mode that the previous testing infrastructure ran into.

The derivation library and the test harness are halves of the same project. Build them together.
