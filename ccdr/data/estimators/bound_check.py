"""Pure bound checks (P-A16 DA/O N ≤ 11)."""
from typing import Tuple


def consistency_check_N_le_11(N: int = 11) -> Tuple[float, float, int]:
    """Return (1.0, 0.0, 1) if N ≤ 11, (0.0, 0.0, 1) otherwise.

    This 'estimator' takes the candidate N from the call site (e.g. a
    surveyed value); it does not import anything from the framework.
    """
    return (1.0 if N <= 11 else 0.0, 0.0, 1)
