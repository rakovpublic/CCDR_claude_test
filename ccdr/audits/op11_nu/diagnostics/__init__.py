"""OP11 diagnostic paths.

Path 1 (per-dataset chi2), Path 2 (profile likelihood), Path 3 (tension
metrics), Path 4 (hierarchical Bayesian). Each is deterministic given fixed
data; classification logic lives in synthesis.py, not here.
"""
from .path1_per_dataset_chi2 import run_path1
from .path2_profile_likelihood import run_path2
from .path3_tension_metrics import run_path3
from .path4_hierarchical import run_path4

__all__ = ["run_path1", "run_path2", "run_path3", "run_path4"]
