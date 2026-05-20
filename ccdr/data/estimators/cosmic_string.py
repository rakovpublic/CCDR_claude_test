"""Cosmic-string template fit (P-A14)."""
from typing import Iterable, Tuple


def cosmic_string_template_fit(posterior) -> Tuple[float, float, int]:
    """Extract Gμ amplitude from NANOGrav 15-yr posterior samples.

    Payload contract: iterable of float Gμ samples.
    """
    samples = [float(x) for x in posterior]
    n = len(samples)
    if n == 0:
        return (0.0, 0.0, 0)
    mean = sum(samples) / n
    if n > 1:
        var = sum((s - mean) ** 2 for s in samples) / (n - 1)
        unc = (var ** 0.5)
    else:
        unc = mean * 0.5
    return (mean, unc, n)
