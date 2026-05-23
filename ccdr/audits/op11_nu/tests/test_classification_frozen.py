"""Lint: the OP11 classification taxonomy is closed (CLAUDE_op11_nu.md §11 #1).

The nine values are exhaustive. Adding a tenth (or renaming one) changes the
hash and fails this test. No _v76-style variants, no BORDERLINE_WITH_CAVEAT.
"""
import hashlib

from ccdr.audits.op11_nu.classification import OP11Classification, COMMITTABLE

EXPECTED_HASH = "dcd8aa8bfe250ceb60b2dd8635eed0f73b26a1fecdfe5b8c6222c2443713a900"

EXPECTED_MEMBERS = {
    "AUDIT_NOT_RUN", "AUDIT_INCOMPLETE", "INSUFFICIENT_DATA",
    "RESOLVED_JOINT", "RESOLVED_STANDALONE", "RESOLVED_THIRD_VALUE",
    "DATASET_DEPENDENT_DOCUMENTED", "DATASET_DEPENDENT_UNRESOLVED",
    "MODEL_MISSPECIFIED",
}


def _enum_hash(enum_cls):
    members = sorted(m.name + "=" + m.value for m in enum_cls)
    return hashlib.sha256(("|".join(members)).encode()).hexdigest()


def test_exactly_nine_values():
    assert len(list(OP11Classification)) == 9
    assert {m.name for m in OP11Classification} == EXPECTED_MEMBERS


def test_taxonomy_frozen():
    assert _enum_hash(OP11Classification) == EXPECTED_HASH, (
        "OP11Classification was modified. The taxonomy is frozen. "
        "See CLAUDE_op11_nu.md §11 constraint 1."
    )


def test_committable_subset():
    assert COMMITTABLE == {
        OP11Classification.RESOLVED_JOINT,
        OP11Classification.RESOLVED_STANDALONE,
        OP11Classification.RESOLVED_THIRD_VALUE,
        OP11Classification.DATASET_DEPENDENT_DOCUMENTED,
    }
    # The blocking classifications must never be committable.
    for blocked in (
        OP11Classification.AUDIT_NOT_RUN, OP11Classification.AUDIT_INCOMPLETE,
        OP11Classification.INSUFFICIENT_DATA,
        OP11Classification.DATASET_DEPENDENT_UNRESOLVED,
        OP11Classification.MODEL_MISSPECIFIED,
    ):
        assert blocked not in COMMITTABLE
