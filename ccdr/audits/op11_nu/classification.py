"""OP11 classification taxonomy.

The nine values below are closed and exhaustive (CLAUDE_op11_nu.md §3, §11
constraint 1). Adding a tenth value is a CI failure — see
tests/test_classification_frozen.py, which hashes the enum members.

Do NOT add transitional values such as RESOLVED_PARTIAL,
RESOLVED_WEIGHTED_AVERAGE, or BORDERLINE_WITH_CAVEAT. If the diagnostics
disagree, the answer is DATASET_DEPENDENT_UNRESOLVED until a human takes a
position via RATIONALE.md.
"""
from enum import Enum


class OP11Classification(Enum):
    AUDIT_NOT_RUN                = "AUDIT_NOT_RUN"
    AUDIT_INCOMPLETE             = "AUDIT_INCOMPLETE"      # diagnostic crashed or chain failed
    INSUFFICIENT_DATA            = "INSUFFICIENT_DATA"     # dataset(s) too sparse
    RESOLVED_JOINT               = "RESOLVED_JOINT"        # all datasets prefer joint
    RESOLVED_STANDALONE          = "RESOLVED_STANDALONE"   # all datasets prefer standalone
    RESOLVED_THIRD_VALUE         = "RESOLVED_THIRD_VALUE"  # both rejected; profile peaks elsewhere
    DATASET_DEPENDENT_DOCUMENTED = "DATASET_DEPENDENT_DOCUMENTED"  # genuine disagreement + chosen extractor
    DATASET_DEPENDENT_UNRESOLVED = "DATASET_DEPENDENT_UNRESOLVED"  # disagreement, no commit
    MODEL_MISSPECIFIED           = "MODEL_MISSPECIFIED"    # no value of nu fits all data


# Classifications for which core/parameters.py is allowed to commit a NU value.
# Every other classification leaves NU = None and predictions PARAMETER_PENDING.
COMMITTABLE = frozenset({
    OP11Classification.RESOLVED_JOINT,
    OP11Classification.RESOLVED_STANDALONE,
    OP11Classification.RESOLVED_THIRD_VALUE,
    OP11Classification.DATASET_DEPENDENT_DOCUMENTED,
})


def is_committable(c: "OP11Classification") -> bool:
    return c in COMMITTABLE


__all__ = ["OP11Classification", "COMMITTABLE", "is_committable"]
