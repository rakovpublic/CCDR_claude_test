"""Lint: status taxonomies are closed enums; hashes are fixed.

If this test fails, the taxonomy has been modified. The taxonomy is frozen.
See CLAUDE.md §7 constraint 1.
"""
import hashlib

from ccdr.core.status import DerivationStatus, MeasurementStatus, TestStatus

EXPECTED_HASHES = {
    "DerivationStatus": "e4c18a7fa03d1496041a2369c882c89faf2ca6198637548dbb0830c112db6312",
    "MeasurementStatus": "5da30248a32661abe98819e58c2cc0aecfd82b4d21a2e9db86a1977ced5d25ec",
    "TestStatus": "949c5537b069fa066d6fde670c57a8b5a4ec300b9bd21db4fb8f0ad6e83dbd75",
}


def _enum_hash(enum_cls):
    members = sorted(m.name + "=" + m.value for m in enum_cls)
    return hashlib.sha256(("|".join(members)).encode()).hexdigest()


def test_taxonomies_frozen():
    for cls in (DerivationStatus, MeasurementStatus, TestStatus):
        h = _enum_hash(cls)
        assert h == EXPECTED_HASHES[cls.__name__], (
            f"{cls.__name__} was modified. The taxonomy is frozen. "
            f"See CLAUDE.md §7 constraint 1."
        )
