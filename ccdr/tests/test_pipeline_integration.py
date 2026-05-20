"""End-to-end smoke test: every prediction produces one TestResult."""
from ccdr.core.status import TestResult, TestStatus, MeasurementStatus
from ccdr.runners._collect import all_prediction_modules


def test_every_prediction_has_required_attributes():
    mods = all_prediction_modules()
    assert mods, "no prediction modules collected"
    for mod in mods:
        assert isinstance(mod.ID, str) and mod.ID.startswith("P-")
        assert callable(mod.derive)
        assert callable(mod.measure)
        assert callable(mod.test)


def test_every_prediction_returns_test_result():
    for mod in all_prediction_modules():
        r = mod.test()
        assert isinstance(r, TestResult), f"{mod.ID} returned {type(r)}"
        assert r.prediction_id == mod.ID


def test_empty_scaffold_no_confirms_or_rejects():
    """In the empty scaffold every parameter is None; no Tier A prediction
    can produce CONFIRM or REJECT without committed parameters.
    P-A04 (theory-only) and P-A16 (bound check) are the two exceptions
    that legitimately return CONFIRM with no frozen parameters."""
    theory_only = {"P-A04", "P-A16"}
    for mod in all_prediction_modules():
        r = mod.test()
        if mod.ID in theory_only:
            assert r.status in (TestStatus.CONFIRM, TestStatus.INCONCLUSIVE), (
                f"{mod.ID} expected CONFIRM, got {r.status}"
            )
        else:
            assert r.status != TestStatus.CONFIRM, (
                f"{mod.ID} unexpectedly produced CONFIRM with no committed params"
            )
            assert r.status != TestStatus.REJECT, (
                f"{mod.ID} unexpectedly produced REJECT with no committed params"
            )
