"""CDT chirality count (P-A15) — direct counter."""
from typing import Iterable, Tuple


def chirality_count(ensemble) -> Tuple[float, float, int]:
    """Count chirality eigenvalue +1 vs -1 in CDT ensemble.

    Payload contract: iterable of +1/-1 signs.
    Returns (signed count, Poisson uncertainty, n_samples).
    """
    samples = [int(s) for s in ensemble]
    n = len(samples)
    if n == 0:
        return (0.0, 0.0, 0)
    count = sum(1 for s in samples if s > 0)
    return (float(count), count ** 0.5, n)
