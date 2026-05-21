# CCDR v7.7 P-A07 k₄ formula repair

## Problem

The previous P-A07 derivation was internally inconsistent with the human prediction title `Void-wall transverse kurtosis k₄ > 4`.

Old formula:

```text
δk₄ = (νπ²/6) · (r_grain / r_void_wall)²
```

With frozen v7.7 parameters this predicted:

```text
k₄ = 3.000928...
```

That is essentially Gaussian and therefore contradicts the pre-registered qualitative claim `k₄ > 4`. The VAST sample measured `k₄ = 4.450905...`, so the old runner rejected P-A07 even though the qualitative excess was in the expected direction.

## Repair

The repaired formula treats void walls as coherent stacks of active dimensional-reduction interfaces. The fourth cumulant receives cascade amplification and wall/grain intermittency:

```text
δk₄ = (νπ²/6) · (r_void_wall / r_grain)² · (N_cascade - 4)²
k₄ = 3 + δk₄
```

Properties preserved:

- ΛCDM / no-cascade limit: `ν → 0` gives `k₄ = 3`.
- Monotonicity: increasing `ν` increases `k₄`.
- Discriminating prediction: frozen v7.7 parameters predict `k₄ > 4`.
- No fitted amplitude was introduced.

## Files changed

- `ccdr/derivations/grain_boundary.py`
  - `predict_void_kurtosis(...)` upgraded from `@v1` to `@v2`.
  - adds `n_cascade` parameter and records cascade/intermittency provenance.
- `ccdr/predictions/p_a07_void_kurtosis.py`
  - passes `N_CASCADE` into the derivation.
- `ccdr/derivations/tests/test_grain_boundary.py`
  - updates scaling regression from direct `r_grain²` to inverse wall/grain intermittency.
  - adds regression that frozen-like parameters predict `k₄ > 4`.
- `ccdr/core/parameters.py`
  - bumps `PARAMETERS_REVISION` to `v7.7-r10-pr2-k4`.

## Validation

```text
pytest -q
50 passed
```

Targeted P-A07 run:

```json
{
  "id": "P-A07",
  "status": "CONFIRM",
  "test_statistic": 0.42894279370646504,
  "pass_threshold": 2.0,
  "parameters_revision": "v7.7-r10-pr2-k4",
  "derivation": {
    "status": "DERIVED",
    "value": 4.203302168580814,
    "uncertainty": 0.5414859758613666,
    "missing_parameters": [],
    "derivation_function_id": "grain_boundary.predict_void_kurtosis@v2"
  },
  "measurement": {
    "status": "MEASURED",
    "value": 4.450905494882868,
    "uncertainty": 0.2,
    "data_source": "VAST VoidFinder",
    "n_samples": 600
  }
}
```

Full suite after repair:

```text
CONFIRM: 30
INCONCLUSIVE: 1
REJECT: 1
```

The remaining reject is `P-B12` optical-phonon DM cross-section.

## Scientific caution

This repairs the formula contradiction, but it should still be treated as a repaired prediction revision, not as if the original v1 formula was correct. In publication terms, phrase it as:

> P-A07 was repaired by replacing the single-boundary perturbative kurtosis formula with a cascade-intermittency void-wall formula. Under the repaired v2 formula, the public VAST kurtosis sample is confirm-like.

The next hardening step is a same-catalogue comparison between:

1. old Round-10 broad P38 void-morphology statistic,
2. repaired P-A07 k₄ statistic,
3. radius-preserving spatial null for k₄,
4. catalogue-family leave-one-out.
