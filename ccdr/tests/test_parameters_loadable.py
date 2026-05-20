"""Lint: parameters module loads cleanly and PARAMETERS_REVISION is a string."""
from ccdr.core import parameters as P


def test_revision_is_string():
    assert isinstance(P.PARAMETERS_REVISION, str)
    assert P.PARAMETERS_REVISION


def test_all_parameters_callable():
    snapshot = P.all_parameters()
    assert isinstance(snapshot, dict)
    # PARAMETERS_REVISION must NOT appear in the snapshot
    assert "PARAMETERS_REVISION" not in snapshot


def test_pending_parameters_returns_list():
    pending = P.pending_parameters()
    assert isinstance(pending, list)
    # In the empty scaffold every parameter is pending.
    assert pending  # non-empty
