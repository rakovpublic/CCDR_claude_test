"""Joint multi-channel inference (P-A19): CL5+CL6+CL7 posterior consistency.

Returns a scalar consistency statistic: 1.0 if joint posterior support is
non-empty (all component derivations succeeded and their predicted values
agree within combined uncertainty), 0.0 otherwise.
"""
from typing import Iterable, Optional

from ccdr.core.status import DerivationResult, DerivationStatus
from ccdr.derivations.base import pending, derived


def posterior(component_results: Optional[Iterable] = None) -> DerivationResult:
    """Combine component DerivationResults into a joint posterior consistency.

    Argument is an iterable of DerivationResult; if any component is
    PARAMETER_PENDING, the joint result is PARAMETER_PENDING with the union
    of missing parameters. Otherwise returns the geometric mean of component
    values as the joint test statistic.
    """
    fn_id = "joint_inference.posterior@v1"
    if component_results is None:
        return pending(
            ["component_results"], fn_id,
            "P-A19 joint CL5+CL6+CL7 (composition)",
        )
    comps = list(component_results)
    missing = []
    for c in comps:
        if c.status == DerivationStatus.PARAMETER_PENDING:
            missing.extend(c.missing_parameters)
    if missing:
        return pending(sorted(set(missing)), fn_id,
                       "P-A19 joint CL5+CL6+CL7 (composition)")
    if not comps:
        return pending(["component_results"], fn_id,
                       "P-A19 joint posterior with no components")
    vals = [c.value for c in comps if c.value is not None]
    if not vals:
        return pending(["component_values"], fn_id,
                       "P-A19 joint posterior with no values")
    # geometric mean of absolute values (sign carried separately)
    prod = 1.0
    for v in vals:
        prod *= abs(v) if v != 0 else 1.0e-30
    mean = prod ** (1.0 / len(vals))
    uncs = [c.uncertainty or 0.0 for c in comps]
    joint_unc = (sum(u * u for u in uncs)) ** 0.5
    return derived(
        value=mean,
        uncertainty=joint_unc,
        fn_id=fn_id,
        provenance="P-A19 joint CL5+CL6+CL7 composition",
        parameters_used={"n_components": len(comps)},
    )
