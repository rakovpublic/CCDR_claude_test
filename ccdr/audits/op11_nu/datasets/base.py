"""NuDataset protocol (CLAUDE_op11_nu.md §7).

A dataset loader exposes a name, its degrees of freedom, the sha256 of the
cached data it reads, and a pure `evaluate_chi2(nu)` that returns the chi-square
of the framework prediction at a *passed-in* nu.

Hard constraint (§11 #3): loaders are framework-blind. They must not import
ccdr.derivations or ccdr.core.parameters, and `evaluate_chi2` must never read
the committed nu — it only ever uses the nu handed to it. The closed-form
framework prediction for each observable is inlined here with a CCDR citation
rather than imported, precisely so the likelihood cannot depend on the value
the audit is trying to decide.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class NuDataset(Protocol):
    name: str
    degrees_of_freedom: int
    data_sha256: str

    def evaluate_chi2(self, nu: float) -> float:
        """Return chi-square of this dataset against the framework prediction
        at nu. Pure: no fitting of nu, no nuisance optimisation here. Any
        nuisance marginalisation is done at construction time against a fixed
        reference; see each loader's docstring."""
        ...


__all__ = ["NuDataset"]
