# CLAUDE.md — OP11 Resolution Audit

This directory is the OP11 audit. It runs *before* any prediction depending on ν, and its output gates `core/parameters.py` from committing a ν value. Until this audit produces a classification in the allowed set, every ν-dependent prediction returns `PARAMETER_PENDING`.

OP11 is the documented 500× disagreement between the joint and standalone ν extractors (joint ≈ 5×10⁻³, standalone ≈ 10⁻⁵). The current parent project committed ν = 5.08×10⁻³ without diagnosing the disagreement. This module diagnoses it, then either resolves it or documents a defensible dataset-dependent choice.

## 1. Diagnostic-first principle

The 500× discrepancy is not a measurement-precision problem; it's a model-misspecification signal. If the framework's ν is a single physical constant, then per-dataset fits must agree within their uncertainties. The fact that they don't has exactly three possible explanations, and the audit's job is to distinguish them:

(a) **One extractor has a methodological bug** → the other extractor's value is correct; fix the bug and commit.
(b) **The datasets genuinely prefer different ν values** → ν is not a universal constant in the framework as written. The framework must either choose one operational definition with documented theoretical rationale, or accept that the prediction list inherits a ν-dependency-on-observable.
(c) **A dataset has an unmodelled systematic** → identify which, and either correct for it or exclude.

The audit must not collapse the disagreement by picking one extractor without first determining which of (a)/(b)/(c) is true.

## 2. The audit pipeline

```
                  [public data + framework predictions]
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
       PATH 1            PATH 2            PATH 3
   per-dataset      profile-likelihood   tension metrics
       χ²            overlap analysis    (anesthetic)
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                          PATH 4 (only if 1-3 ambiguous)
                          hierarchical Bayesian
                          per-dataset νᵢ with global hyperprior
                              │
                              ▼
                       SYNTHESIS
                  combine diagnostic outputs
                              │
                              ▼
                      CLASSIFICATION
              one of nine OP11Classification values
                              │
                              ▼
                  op11_report.json  (committed)
                              │
                              ▼
              core/parameters.py reads → commits or blocks NU
```

Every stage is deterministic given fixed data and a fixed random seed. The audit produces the same classification on the same inputs every time. This is enforced.

## 3. Frozen taxonomy

In `audits/op11_nu/classification.py`:

```python
from enum import Enum

class OP11Classification(Enum):
    AUDIT_NOT_RUN              = "AUDIT_NOT_RUN"
    AUDIT_INCOMPLETE           = "AUDIT_INCOMPLETE"     # diagnostic crashed or chain failed
    INSUFFICIENT_DATA          = "INSUFFICIENT_DATA"    # dataset(s) too sparse
    RESOLVED_JOINT             = "RESOLVED_JOINT"       # all datasets prefer joint
    RESOLVED_STANDALONE        = "RESOLVED_STANDALONE"  # all datasets prefer standalone
    RESOLVED_THIRD_VALUE       = "RESOLVED_THIRD_VALUE" # both rejected; profile peaks elsewhere
    DATASET_DEPENDENT_DOCUMENTED = "DATASET_DEPENDENT_DOCUMENTED"  # genuine disagreement + chosen extractor
    DATASET_DEPENDENT_UNRESOLVED = "DATASET_DEPENDENT_UNRESOLVED"  # disagreement, no commit
    MODEL_MISSPECIFIED         = "MODEL_MISSPECIFIED"   # no value of ν fits all data
```

These nine are exhaustive. Adding a tenth value is a CI failure. Each value has a corresponding action:

| Classification | NU committed? | Predictions depending on ν return |
|---|---|---|
| `AUDIT_NOT_RUN` | No | `PARAMETER_PENDING` |
| `AUDIT_INCOMPLETE` | No | `PARAMETER_PENDING` |
| `INSUFFICIENT_DATA` | No | `PARAMETER_PENDING` |
| `RESOLVED_JOINT` | Yes (joint) | `CONFIRM` / `REJECT` per data |
| `RESOLVED_STANDALONE` | Yes (standalone) | `CONFIRM` / `REJECT` per data |
| `RESOLVED_THIRD_VALUE` | Yes (third value) | `CONFIRM` / `REJECT` per data |
| `DATASET_DEPENDENT_DOCUMENTED` | Yes (documented operational ν) | `CONFIRM` / `REJECT` per data |
| `DATASET_DEPENDENT_UNRESOLVED` | No | `PARAMETER_PENDING` |
| `MODEL_MISSPECIFIED` | No | `PARAMETER_PENDING`, **plus** framework-revision flag raised |

`DATASET_DEPENDENT_DOCUMENTED` is *only* reachable through `RATIONALE.md` (see §6). Without an explicit human-authored rationale file, the classification stops at `DATASET_DEPENDENT_UNRESOLVED`.

## 4. Repository layout

```
audits/op11_nu/
├── CLAUDE.md                   # this file
├── __init__.py
├── classification.py           # OP11Classification enum + helpers
├── results.py                  # DiagnosticResult, OP11Report dataclasses
├── candidates.py               # NU_CANDIDATES dict (joint, standalone, + scan grid)
├── datasets/                   # per-dataset likelihood loaders
│   ├── __init__.py
│   ├── pantheon_plus_sn.py
│   ├── desi_dr2_bao.py
│   ├── planck_growth.py
│   ├── nanograv_15yr.py
│   └── base.py                 # NuDataset protocol
├── diagnostics/
│   ├── __init__.py
│   ├── path1_per_dataset_chi2.py
│   ├── path2_profile_likelihood.py
│   ├── path3_tension_metrics.py
│   └── path4_hierarchical.py
├── synthesis.py                # combines diagnostic outputs → classification
├── run_audit.py                # entry point: runs all diagnostics, writes report
├── report.py                   # generates op11_report.json + human-readable summary
├── RATIONALE.md                # human-authored; only present if DOCUMENTED chosen
├── tests/
│   ├── test_classification_frozen.py
│   ├── test_diagnostics_deterministic.py
│   ├── test_synthesis_exhaustive.py
│   ├── test_no_version_tags.py
│   └── test_dataset_loaders_no_framework_imports.py
└── op11_report.json            # written by run_audit.py; consumed by parameters.py
```

## 5. Core data structures

In `results.py`:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict
from .classification import OP11Classification

@dataclass(frozen=True)
class PerDatasetChi2Result:
    dataset_name: str
    nu_value: float
    nu_label: str               # "joint" | "standalone" | "third_value_grid_<i>"
    chi2: float
    dof: int
    p_value: float
    accepts_at_95: bool         # p_value > 0.05

@dataclass(frozen=True)
class ProfileLikelihoodResult:
    dataset_name: str
    nu_grid: tuple              # immutable; sorted
    log_likelihood: tuple
    nu_mle: float
    nu_mle_uncertainty: float

@dataclass(frozen=True)
class TensionMetricsResult:
    dataset_pair: tuple         # ("pantheon_plus_sn", "desi_dr2_bao")
    log_R: float
    log_I: float
    log_suspiciousness: float
    tension_sigma: float

@dataclass(frozen=True)
class HierarchicalResult:
    nu_global_mean: float
    nu_global_std: float
    tau_mean: float             # between-dataset spread
    tau_95_upper: float
    universality_assessment: str   # "UNIVERSAL" | "DATASET_DEPENDENT" | "MARGINAL"
    per_dataset_nu: Dict[str, tuple]  # name → (mean, std)

@dataclass(frozen=True)
class OP11Report:
    classification: OP11Classification
    committed_nu: Optional[float]
    committed_nu_uncertainty: Optional[float]
    provenance: str
    audit_revision: str         # git SHA at audit time
    data_revision: Dict[str, str]  # per-dataset sha256
    diagnostics: dict           # path1, path2, path3, path4 results
    rationale_sha256: Optional[str]  # only if DOCUMENTED
    timestamp: datetime
    framework_revision_flag: bool   # True only if MODEL_MISSPECIFIED
    notes: str = ""
```

## 6. The `RATIONALE.md` gate

The `DATASET_DEPENDENT_DOCUMENTED` classification is the most consequential — it says "yes, the datasets disagree, and we are committing to one operational definition anyway." This requires explicit human authorship; it cannot be reached by automation.

The gate works as follows. `audits/op11_nu/RATIONALE.md` must exist with this exact frontmatter:

```yaml
---
op11_classification: DATASET_DEPENDENT_DOCUMENTED
committed_nu: 5.08e-3
committed_nu_uncertainty: 0.4e-3
operational_definition: "ν at present epoch from late-time SN expansion history"
framework_section_reference: "CCDR §3.4 eq 3.21"
author: "<name>"
date: "YYYY-MM-DD"
---
```

…followed by a written justification of *why* this is the canonical operational definition, and what theoretical implications follow from accepting that other datasets prefer different values.

The audit code computes `sha256(RATIONALE.md)` and embeds it in `op11_report.json`. Any change to the rationale invalidates the previous classification and forces a re-run. The classification is `DATASET_DEPENDENT_DOCUMENTED` *only if* the file exists with valid frontmatter; otherwise it remains `DATASET_DEPENDENT_UNRESOLVED`.

This prevents the silent-commit pattern that produced the current R11 state (where ν was committed at 5.08×10⁻³ without any documented rationale).

## 7. Canonical diagnostic: Path 1 (per-dataset χ²)

This is the highest-leverage first step. It's pure evaluation — no fitting — and can resolve OP11 outright if one extractor has a methodological bug.

```python
# diagnostics/path1_per_dataset_chi2.py
"""
Path 1: per-dataset goodness-of-fit at competing ν values.

For each (dataset, ν_candidate), compute χ² and p-value.
Output is structured PerDatasetChi2Result list; classification logic
lives in synthesis.py, not here.
"""
from scipy.stats import chi2 as chi2_dist
from typing import List
from ..datasets import iter_datasets
from ..candidates import NU_CANDIDATES
from ..results import PerDatasetChi2Result

DIAGNOSTIC_FN_ID = "path1_per_dataset_chi2@v1"

def run_path1() -> List[PerDatasetChi2Result]:
    results = []
    for ds in iter_datasets():
        for label, nu_value in NU_CANDIDATES.items():
            chi2_val = ds.evaluate_chi2(nu_value)
            dof = ds.degrees_of_freedom
            p = float(chi2_dist.sf(chi2_val, dof))
            results.append(PerDatasetChi2Result(
                dataset_name=ds.name,
                nu_value=nu_value,
                nu_label=label,
                chi2=float(chi2_val),
                dof=int(dof),
                p_value=p,
                accepts_at_95=(p > 0.05),
            ))
    return results
```

The dataset interface (in `datasets/base.py`):

```python
from typing import Protocol

class NuDataset(Protocol):
    name: str
    degrees_of_freedom: int
    data_sha256: str

    def evaluate_chi2(self, nu: float) -> float:
        """Return χ² of this dataset against framework prediction at ν.
        Pure: no fitting of ν, no nuisance optimisation here.
        Nuisances are profiled inside the dataset loader at construction time
        if needed, against a fixed ν_reference; see datasets/<source>.py docstrings.
        """
        ...
```

Path 1 unit tests (in `tests/test_diagnostics_deterministic.py`) verify:
- Same inputs → same outputs across runs (determinism)
- `evaluate_chi2(nu)` is monotone-or-bowl-shaped in ν per dataset (sanity)
- χ² is finite and non-negative
- p-values are in [0, 1]

## 8. Synthesis logic

In `synthesis.py`, the classification function takes the four diagnostic outputs and returns exactly one `OP11Classification`. The logic is explicit, ordered, and falls through to the most-blocking classification first.

```python
# synthesis.py
from typing import List
from .results import (PerDatasetChi2Result, ProfileLikelihoodResult,
                      TensionMetricsResult, HierarchicalResult)
from .classification import OP11Classification

def classify(
    path1: List[PerDatasetChi2Result],
    path2: List[ProfileLikelihoodResult],
    path3: List[TensionMetricsResult],
    path4: HierarchicalResult | None,
    rationale_present: bool,
    rationale_valid: bool,
) -> OP11Classification:
    """Decision tree for OP11 classification. Order matters — earlier
    branches dominate.

    See docstring of each helper for the precise threshold."""

    if not path1 or any(r.dof < 1 for r in path1):
        return OP11Classification.INSUFFICIENT_DATA

    joint_accepted_by   = {r.dataset_name for r in path1 if r.nu_label == "joint" and r.accepts_at_95}
    sa_accepted_by      = {r.dataset_name for r in path1 if r.nu_label == "standalone" and r.accepts_at_95}
    all_datasets        = {r.dataset_name for r in path1}

    # Case 1: joint resolves cleanly
    if joint_accepted_by == all_datasets and sa_accepted_by != all_datasets:
        return OP11Classification.RESOLVED_JOINT

    # Case 2: standalone resolves cleanly
    if sa_accepted_by == all_datasets and joint_accepted_by != all_datasets:
        return OP11Classification.RESOLVED_STANDALONE

    # Case 3: both rejected by all datasets; check Path 2 for a third value
    if not joint_accepted_by and not sa_accepted_by:
        third = _find_consensus_third_value(path2)
        if third is not None:
            return OP11Classification.RESOLVED_THIRD_VALUE
        return OP11Classification.MODEL_MISSPECIFIED

    # Case 4: partial agreement — datasets disagree
    # Promote to DOCUMENTED only with valid rationale
    if path4 is not None and path4.universality_assessment == "UNIVERSAL":
        # Hierarchical model says ν is universal despite Path 1 noise
        return OP11Classification.RESOLVED_JOINT  # joint already overlaps universal posterior

    if rationale_present and rationale_valid:
        return OP11Classification.DATASET_DEPENDENT_DOCUMENTED
    return OP11Classification.DATASET_DEPENDENT_UNRESOLVED

def _find_consensus_third_value(profiles: List[ProfileLikelihoodResult]) -> float | None:
    """Look for a ν value in the overlap region of all per-dataset profiles
    at the 1σ level. Returns the value if found, else None."""
    ...
```

The synthesis is exhaustive: every combination of diagnostic outputs maps to exactly one classification. `tests/test_synthesis_exhaustive.py` enumerates fixture cases covering each branch.

## 9. The report

`run_audit.py` produces `op11_report.json` with the schema below. This is the only file `core/parameters.py` reads.

```json
{
  "classification": "DATASET_DEPENDENT_DOCUMENTED",
  "committed_nu": 5.08e-3,
  "committed_nu_uncertainty": 0.4e-3,
  "provenance": "Pantheon+ late-time fit; CCDR §3.4 eq 3.21",
  "audit_revision": "git:f3a1b2c",
  "data_revision": {
    "pantheon_plus_sn": "sha256:...",
    "desi_dr2_bao":     "sha256:...",
    "planck_growth":    "sha256:...",
    "nanograv_15yr":    "sha256:..."
  },
  "diagnostics": {
    "path1": [ /* PerDatasetChi2Result list */ ],
    "path2": [ /* ProfileLikelihoodResult list */ ],
    "path3": [ /* TensionMetricsResult list */ ],
    "path4": { /* HierarchicalResult or null */ }
  },
  "rationale_sha256": "sha256:...",
  "timestamp": "2026-05-20T12:34:56Z",
  "framework_revision_flag": false,
  "notes": ""
}
```

The report is committed to git. The audit is reproducible: re-running `python -m ccdr.audits.op11_nu.run_audit` on the same data must produce a bit-identical report (modulo timestamp).

## 10. Integration with `core/parameters.py`

The parent project's `core/parameters.py` reads the report and gates NU:

```python
# core/parameters.py (the relevant section)
import json, pathlib
from typing import Optional

_OP11_REPORT_PATH = pathlib.Path(__file__).parent.parent / "audits" / "op11_nu" / "op11_report.json"

_COMMITTABLE = {
    "RESOLVED_JOINT", "RESOLVED_STANDALONE", "RESOLVED_THIRD_VALUE",
    "DATASET_DEPENDENT_DOCUMENTED",
}

def _load_nu() -> tuple[Optional[float], Optional[float], str]:
    if not _OP11_REPORT_PATH.exists():
        return None, None, "BLOCKED: OP11 audit has not been run"
    report = json.loads(_OP11_REPORT_PATH.read_text())
    if report["classification"] not in _COMMITTABLE:
        return None, None, f"BLOCKED on OP11: {report['classification']}"
    return (
        report["committed_nu"],
        report["committed_nu_uncertainty"],
        report["provenance"],
    )

NU, NU_UNCERTAINTY, NU_PROVENANCE = _load_nu()
```

When `NU is None`, every prediction module that depends on ν (and reads `is_parameter_pending("NU")`) returns `TestStatus.PARAMETER_PENDING`. This is automatic — the audit gating uses the parent project's existing pending mechanism.

## 11. Hard constraints

These are non-negotiable. CI enforces each.

1. **Frozen classification taxonomy.** The nine `OP11Classification` values are closed. No `_v76`-style variants. No "borderline_with_caveat" variants. Enforced by `tests/test_classification_frozen.py` which hashes the enum members.

2. **Deterministic diagnostics.** Each diagnostic returns the same output on the same inputs with the same random seed. `tests/test_diagnostics_deterministic.py` runs each diagnostic twice on cached inputs and asserts identical output.

3. **Dataset loaders are framework-blind.** `datasets/*.py` modules must not import from `ccdr.derivations` or `ccdr.core.parameters` (apart from importing `is_parameter_pending` itself, which is allowed). Enforced by `tests/test_dataset_loaders_no_framework_imports.py` AST-walking each loader. The likelihoods compute `χ²(nu)` given a *passed-in* ν — they do not read the committed value.

4. **No silent ν commitment.** The only path to a non-None `NU` in `core/parameters.py` is through `op11_report.json` with classification in `_COMMITTABLE`. There is no manual override. If a developer wants a different ν for a one-off run, they must change the report (which is git-tracked and shows up in code review) or change the audit's data/methodology.

5. **Exhaustive synthesis.** `synthesis.classify(...)` must return some `OP11Classification` value for every combination of inputs. No `None` return. No exception falling through. Enforced by `tests/test_synthesis_exhaustive.py` with fixture coverage.

6. **Rationale gate is sha256-tied.** `DATASET_DEPENDENT_DOCUMENTED` is only valid while the `RATIONALE.md` sha256 in `op11_report.json` matches the file on disk. If `RATIONALE.md` is edited without re-running the audit, the next audit run will produce a different report (and the parent project should not trust the cached one). `tests/test_rationale_sha_check.py` validates this.

7. **No version tags in any field.** Standard lint as in the main project: scan for `_v\d+`, `_resolved_like`, `_committed_v\d+`, etc. Fail CI if found.

## 12. Implementation order

**Phase 0 — Infrastructure**

1. `classification.py` — the nine-value enum
2. `results.py` — the five dataclasses
3. `candidates.py` — `NU_CANDIDATES = {"joint": 5.08e-3, "standalone": 1.0e-5}` with a third-value scan grid
4. `tests/test_classification_frozen.py` and `tests/test_no_version_tags.py` — must pass on empty scaffold

**Phase 1 — Datasets**

5. `datasets/base.py` — `NuDataset` protocol
6. `datasets/pantheon_plus_sn.py` — SN late-time likelihood; ν enters through ρ_vac(H) modifying μ(z)
7. `datasets/desi_dr2_bao.py` — BAO likelihood
8. `datasets/planck_growth.py` — growth fσ₈ likelihood
9. `datasets/nanograv_15yr.py` — PTA spectral-index likelihood
10. `tests/test_dataset_loaders_no_framework_imports.py` — passes after each loader added

**Phase 2 — Diagnostics**

11. `diagnostics/path1_per_dataset_chi2.py` + tests — fast; can run today
12. `diagnostics/path2_profile_likelihood.py` + tests — slower; needs profile machinery
13. `diagnostics/path3_tension_metrics.py` + tests — depends on path 2 chains or paired likelihoods; uses anesthetic
14. `diagnostics/path4_hierarchical.py` + tests — only if 1-3 are ambiguous; uses numpyro or emcee

**Phase 3 — Synthesis and reporting**

15. `synthesis.py` — the classification decision tree
16. `report.py` — serialise to JSON; produce human-readable summary
17. `run_audit.py` — entry point
18. `tests/test_synthesis_exhaustive.py` — covers every branch
19. `tests/test_diagnostics_deterministic.py` — re-run identity check

**Phase 4 — Integration**

20. Modify `core/parameters.py` to gate NU on `op11_report.json`
21. Run the audit. Inspect classification.
22. If `DATASET_DEPENDENT_UNRESOLVED`: either write `RATIONALE.md` (consciously committing to an operational definition) or accept that ν-dependent predictions stay `PARAMETER_PENDING`.
23. If `MODEL_MISSPECIFIED`: framework-revision flag is raised. This is the Lakatos-retraction trigger for the cascade mechanism's ν section. Do not paper over.

## 13. What success looks like

After this audit is built and run:

- `python -m ccdr.audits.op11_nu.run_audit` produces `op11_report.json` deterministically from cached data
- The report's classification is one of nine values; CI checks that
- The report's provenance is reproducible (audit revision, data sha256s)
- `core/parameters.py` either commits NU with provenance, or sets NU = None with a clear blocking reason
- Every prediction depending on ν that was `CONFIRM` in R11 either: stays `CONFIRM` (with a now-documented ν), or reverts to `PARAMETER_PENDING` (which is the honest state if the audit didn't resolve)
- The next time someone runs `python -m ccdr.runners.run_all`, the result count for ν-dependent predictions reflects the audit's true outcome, not a silent commit

## 14. What success does not include

- An auto-generated `RATIONALE.md`. The whole point is that this file is human-authored.
- A classification like `RESOLVED_PARTIAL` or `RESOLVED_WEIGHTED_AVERAGE`. The nine values are closed. If the diagnostics disagree, the answer is `DATASET_DEPENDENT_UNRESOLVED` until a human takes a position.
- A way for `core/parameters.py` to read NU from anywhere except `op11_report.json`.
- A "manual override" flag that lets `NU = 5.08e-3` be set without the report. The R11 result we're cleaning up came from exactly that pattern.
- An audit that flips classification because the dataset chains were re-sampled with different seeds. Determinism is mandatory.

## 15. The `MODEL_MISSPECIFIED` case

If the audit returns `MODEL_MISSPECIFIED`, this is not a bug. It's a finding. The framework's ν mechanism cannot fit the joint observational constraints with any single value.

In this case:
- `framework_revision_flag = true` is set in `op11_report.json`
- The parent project's CI should surface this prominently (e.g. fail a check named `framework_consistency`)
- Acceptable responses: revisit §3.4 of CCDR to derive a more flexible ν(observable) dependence; accept that one dataset has a systematic the framework can't model; retract the prediction set that depends on uniform ν
- Unacceptable response: re-tune candidates, broaden tolerances, or add a free parameter that absorbs the disagreement. That's the protective-belt failure mode.

## 16. For Claude Code

Read this file completely. The OP11 audit is its own self-contained sub-project. Implement Phase 0 first and let the four lint tests pass on the empty scaffold. Then implement datasets and diagnostics in order. Make one commit per dataset, one per diagnostic.

When you reach Phase 4 (integration), do not write `RATIONALE.md` yourself. The file is the human authoring step. If the audit returns `DATASET_DEPENDENT_UNRESOLVED`, leave it. The parent project's predictions will correctly report `PARAMETER_PENDING` and the next human action is for someone to either (a) write the rationale and re-run, or (b) accept that ν is not committable and revise the framework.

If at any point you find yourself wanting to:

- Add a tenth classification value
- Have the audit auto-generate `RATIONALE.md` from the diagnostic outputs
- Add a `manual_override` parameter to `core/parameters.py`
- Introduce a `BORDERLINE_WITH_CAVEAT` or similar transitional classification
- Skip Path 1 because "we know joint is right" — that's exactly the assumption the audit is meant to test
- Loosen the p-value threshold from 0.05 because it's "too strict"
- Make `evaluate_chi2(nu)` call `_load_nu()` internally (creating a circular dependency)

— stop. Re-read §11. These constraints exist because OP11 is the canonical case where the previous testing infrastructure silently smoothed over disagreement. The audit's value comes precisely from refusing to do that, even at the cost of leaving predictions in `PARAMETER_PENDING` longer than feels comfortable.

OP11 is a fact about the current state of the framework + data. The audit reports that fact. It does not make it go away.
