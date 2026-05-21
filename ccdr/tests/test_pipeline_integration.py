"""End-to-end smoke test: every prediction produces one TestResult."""
from ccdr.core.status import TestResult, TestStatus, MeasurementStatus
from ccdr.core.parameters import pending_parameters
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


def test_theory_only_predictions_always_confirm():
    """P-A04 (AS-EPRL γ) and P-A16 (DA/O bound) consume no framework
    parameters and no data; they must always return CONFIRM."""
    theory_only = {"P-A04", "P-A16"}
    for mod in all_prediction_modules():
        if mod.ID not in theory_only:
            continue
        r = mod.test()
        assert r.status == TestStatus.CONFIRM, (
            f"{mod.ID} expected CONFIRM, got {r.status}"
        )


def test_status_distribution_matches_parameter_state():
    """If every parameter is None (empty scaffold), only the theory-only
    predictions can confirm. If parameters are committed, Tier A
    predictions with bundled data should produce CONFIRM or INCONCLUSIVE
    verdicts (REJECT is allowed but signals a real conflict)."""
    pending = set(pending_parameters())
    for mod in all_prediction_modules():
        r = mod.test()
        if pending and mod.ID not in {"P-A04", "P-A16"}:
            # Empty-scaffold path: parameter-bearing predictions cannot
            # legitimately CONFIRM.
            assert r.status != TestStatus.CONFIRM
