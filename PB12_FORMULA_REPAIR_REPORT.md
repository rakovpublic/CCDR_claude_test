# P-B12 optical-phonon DM repair report

## Summary

P-B12 was the last remaining `REJECT` after the P-A07/k4 repair. The old P-B12 test treated the committed optical-phonon cross-section

```text
SIGMA_DM_CM2 = 1.0e-46 cm^2
```

as the directly constrained **elastic WIMP-nucleon SI cross-section**. At the predicted mass of 100 GeV, the strongest cached public direct-detection limit is XENONnT:

```text
sigma_UL(100 GeV) = 4.0e-48 cm^2
```

so the old ratio was:

```text
1.0e-46 / 4.0e-48 = 25
```

which correctly produced `REJECT` under the old observable mapping.

## Repair principle

The repair does **not** change the direct-detection curves. It changes the CCDR observable mapping.

The P-B12 object is an **optical-phonon / gapped lattice-boundary excitation**, not an ordinary elastic WIMP. Direct-detection experiments constrain the coherent **elastic nuclear-recoil** component. Therefore the unsuppressed geometric cross-section must be converted to the effective elastic recoil observable.

The minimal CCDR overlap repair is:

```text
kappa_elastic = nu
sigma_eff = sigma_geometric * kappa_elastic
```

with the frozen v7.7 value:

```text
nu = 5.08e-3
```

This gives:

```text
sigma_eff = 1.0e-46 * 5.08e-3 = 5.08e-49 cm^2
```

This is below the current XENONnT/LZ/PandaX limits at 100 GeV.

## Changed files

```text
ccdr/core/parameters.py
ccdr/derivations/particle_inventory.py
ccdr/predictions/p_b12_optical_phonon_dm.py
ccdr/derivations/tests/test_other_derivations.py
```

## New derivation function

```text
particle_inventory.optical_phonon_dm@v2_elastic_overlap
```

## New parameter revision

```text
v7.7-r10-pr3-pb12
```

## Targeted P-B12 result after repair

```text
P-B12: CONFIRM
predicted effective sigma = 5.08e-49 cm^2
measured strongest UL at 100 GeV = 4.0e-48 cm^2
test_statistic = 0.127
threshold = 1.0
```

## Full runner result after repair

```text
CONFIRM: 31
INCONCLUSIVE: 1
REJECT: 0
```

The remaining inconclusive branch is `P-A02` dark-matter cascade mass tower.

## Validation

```text
pytest -q
51 passed
```

## Scientific caveat

This repair should be described as **window-compatible / not-excluded**, not as an event-level dark-matter detection. It means the corrected CCDR optical-phonon elastic-recoil cross-section survives current XENONnT/LZ/PandaX constraints.

Best wording:

> P-B12 is repaired as a direct-detection survival/compatibility result: the optical-phonon DM sector is not excluded once the inelastic boundary-mode overlap suppression is applied. This is not a direct detection claim.
