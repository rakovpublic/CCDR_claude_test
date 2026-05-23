"""Competing nu candidates and the third-value scan grid (CLAUDE_op11_nu.md §12).

NU_CANDIDATES holds the two extractor values whose 500x disagreement OP11 is
about: the joint extractor (~5e-3) and the standalone extractor (~1e-5). These
are the only two labelled candidates evaluated by Path 1.

THIRD_VALUE_GRID is a log-spaced scan bracketing both candidates. Path 2
profiles each dataset's likelihood over this grid; Path 3/4 reuse it as the
parameter range. The grid is fixed (no re-tuning — that is the protective-belt
failure mode warned against in §15).
"""
import math

# The two competing extractor values (CLAUDE_op11_nu.md §1, §12).
NU_JOINT = 5.08e-3
NU_STANDALONE = 1.0e-5

NU_CANDIDATES = {
    "joint": NU_JOINT,
    "standalone": NU_STANDALONE,
}


def _log_grid(lo: float, hi: float, n: int) -> tuple:
    step = (math.log10(hi) - math.log10(lo)) / (n - 1)
    return tuple(10.0 ** (math.log10(lo) + i * step) for i in range(n))


# Log-spaced grid from well below standalone to well above joint. Fixed at 121
# points so the grid spacing is reproducible and dense enough to localise a
# third-value peak to a few percent in log-nu.
NU_GRID_LO = 1.0e-6
NU_GRID_HI = 5.0e-2
NU_GRID_N = 121
THIRD_VALUE_GRID = _log_grid(NU_GRID_LO, NU_GRID_HI, NU_GRID_N)


def third_value_labels() -> tuple:
    return tuple(f"third_value_grid_{i}" for i in range(len(THIRD_VALUE_GRID)))


__all__ = [
    "NU_JOINT",
    "NU_STANDALONE",
    "NU_CANDIDATES",
    "THIRD_VALUE_GRID",
    "NU_GRID_LO",
    "NU_GRID_HI",
    "NU_GRID_N",
    "third_value_labels",
]
