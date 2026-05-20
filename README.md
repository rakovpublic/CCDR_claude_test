# CCDR Prediction Project

One project, two halves. Each prediction is a unified test built from a
**derivation half** (frozen parameters → predicted value via the cascade
mechanism) and a **measurement half** (public data → measured value). The
two halves are bound into a single test that returns one verdict.

See `CLAUDE (2).md` for the full architectural specification.

## Layout

```
ccdr/
├── core/              # frozen status taxonomy + framework parameters
├── derivations/       # parameter → predicted value (pure functions)
├── data/              # loaders + estimators (framework-blind)
├── predictions/       # derivation × measurement binding
├── runners/           # derive_all / measure_all / run_all
└── tests/             # four load-bearing lint tests + integration
```

## Quick start

```bash
pip install -e .

# Run derivations only (no data needed)
python -m ccdr.runners.derive_all

# Run measurements only (no framework parameters consulted)
python -m ccdr.runners.measure_all

# Run the full pipeline
python -m ccdr.runners.run_all

# Run a single prediction
python -m ccdr.runners.run_one P-A07

# Run all tests (four lints + per-derivation + integration)
pytest
```

## The four load-bearing lint tests

1. `tests/test_status_taxonomy_frozen.py` — enums hashed and frozen.
2. `tests/test_no_version_tags.py` — no `_v75` / `_ready` smuggling.
3. `tests/test_derivations_pure.py` — derivations do no I/O.
4. `tests/test_measurements_framework_blind.py` — loaders/estimators do not
   import `core.parameters` or `derivations`.

All four pass on the empty scaffold.

## Current state (empty scaffold)

All `core/parameters.py` values are `None`. Every Tier A prediction returns
either `PARAMETER_PENDING` (parameter blocks derivation) or `INCONCLUSIVE`
/ `DATA_UNAVAILABLE` (data not yet cached). The two parameter-free
predictions — P-A04 (AS-EPRL γ consistency) and P-A16 (DA/O N ≤ 11) —
already return `CONFIRM`.

Tier B predictions (P-B01 .. P-B12) are stubs returning `PARAMETER_PENDING`
with the responsible Open Problem cited. P-D01 (Koide) is a Tier D stub
returning `NOT_RUN` pending §21 numerical execution.
