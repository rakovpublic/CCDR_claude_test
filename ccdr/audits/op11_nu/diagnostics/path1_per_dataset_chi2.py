"""Path 1: per-dataset goodness-of-fit at competing nu values.

For each (dataset, nu_candidate), compute chi-square and p-value. This is pure
evaluation — no fitting — and is the highest-leverage first step: it resolves
OP11 outright if one extractor is excluded by every dataset's goodness-of-fit.

Classification logic lives in synthesis.py, not here. This module only produces
structured PerDatasetChi2Result records.
"""
from typing import List

from .._stats import chi2_sf
from ..candidates import NU_CANDIDATES
from ..datasets import iter_datasets
from ..results import PerDatasetChi2Result

DIAGNOSTIC_FN_ID = "path1_per_dataset_chi2@v1"


def run_path1(datasets=None) -> List[PerDatasetChi2Result]:
    if datasets is None:
        datasets = iter_datasets()
    results: List[PerDatasetChi2Result] = []
    for ds in datasets:
        for label, nu_value in NU_CANDIDATES.items():
            chi2_val = float(ds.evaluate_chi2(nu_value))
            dof = int(ds.degrees_of_freedom)
            p = chi2_sf(chi2_val, dof) if dof >= 1 else float("nan")
            results.append(PerDatasetChi2Result(
                dataset_name=ds.name,
                nu_value=nu_value,
                nu_label=label,
                chi2=chi2_val,
                dof=dof,
                p_value=p,
                accepts_at_95=(p > 0.05),
            ))
    return results


__all__ = ["run_path1", "DIAGNOSTIC_FN_ID"]
