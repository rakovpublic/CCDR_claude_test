"""The RATIONALE.md gate is sha256-tied (CLAUDE_op11_nu.md §6, §11 #6).

DATASET_DEPENDENT_DOCUMENTED is reachable only with a valid, human-authored
RATIONALE.md, and the file's sha256 is embedded in the report so any later edit
invalidates the cached classification.
"""
import hashlib

import pytest

from ccdr.audits.op11_nu import report as R
from ccdr.audits.op11_nu.classification import OP11Classification as C
from ccdr.audits.op11_nu.results import PerDatasetChi2Result
from ccdr.audits.op11_nu.synthesis import classify

VALID = """---
op11_classification: DATASET_DEPENDENT_DOCUMENTED
committed_nu: 5.08e-3
committed_nu_uncertainty: 0.4e-3
operational_definition: "nu at present epoch from late-time SN expansion history"
framework_section_reference: "CCDR §3.4 eq 3.21"
author: "A. Researcher"
date: "2026-05-23"
---

Justification body goes here.
"""

MISSING_KEY = """---
op11_classification: DATASET_DEPENDENT_DOCUMENTED
committed_nu: 5.08e-3
---
body
"""

WRONG_CLASS = VALID.replace("DATASET_DEPENDENT_DOCUMENTED", "RESOLVED_JOINT")


def _sha(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode()).hexdigest()


def test_absent_rationale(monkeypatch, tmp_path):
    monkeypatch.setattr(R, "RATIONALE_PATH", tmp_path / "nope.md")
    present, valid, sha, fm = R.rationale_status()
    assert (present, valid, sha, fm) == (False, False, None, None)


def test_valid_rationale_sha_matches(monkeypatch, tmp_path):
    path = tmp_path / "RATIONALE.md"
    path.write_text(VALID, encoding="utf-8")
    monkeypatch.setattr(R, "RATIONALE_PATH", path)
    present, valid, sha, fm = R.rationale_status()
    assert present and valid
    assert sha == _sha(VALID)
    assert fm["committed_nu"] == "5.08e-3"


def test_edit_changes_sha(monkeypatch, tmp_path):
    path = tmp_path / "RATIONALE.md"
    path.write_text(VALID, encoding="utf-8")
    monkeypatch.setattr(R, "RATIONALE_PATH", path)
    _, _, sha1, _ = R.rationale_status()
    path.write_text(VALID + "\nextra line\n", encoding="utf-8")
    _, _, sha2, _ = R.rationale_status()
    assert sha1 != sha2, "editing RATIONALE.md must change the embedded sha256"


def test_missing_key_is_invalid(monkeypatch, tmp_path):
    path = tmp_path / "RATIONALE.md"
    path.write_text(MISSING_KEY, encoding="utf-8")
    monkeypatch.setattr(R, "RATIONALE_PATH", path)
    present, valid, sha, fm = R.rationale_status()
    assert present and not valid


def test_wrong_self_declared_class_is_invalid(monkeypatch, tmp_path):
    path = tmp_path / "RATIONALE.md"
    path.write_text(WRONG_CLASS, encoding="utf-8")
    monkeypatch.setattr(R, "RATIONALE_PATH", path)
    present, valid, sha, fm = R.rationale_status()
    assert present and not valid


def _partial_path1():
    return [
        PerDatasetChi2Result("A", 1.0, "joint", 1.0, 1, 0.5, True),
        PerDatasetChi2Result("A", 1.0, "standalone", 1.0, 1, 0.001, False),
        PerDatasetChi2Result("B", 1.0, "joint", 1.0, 1, 0.001, False),
        PerDatasetChi2Result("B", 1.0, "standalone", 1.0, 1, 0.5, True),
    ]


def test_documented_report_embeds_sha(monkeypatch, tmp_path):
    path = tmp_path / "RATIONALE.md"
    path.write_text(VALID, encoding="utf-8")
    monkeypatch.setattr(R, "RATIONALE_PATH", path)
    present, valid, sha, fm = R.rationale_status()
    cls = classify(_partial_path1(), [], [], None, present, valid)
    assert cls == C.DATASET_DEPENDENT_DOCUMENTED
    report = R.build_report(cls, _partial_path1(), [], [], None, (), sha, fm)
    assert report.committed_nu == pytest.approx(5.08e-3)
    assert report.committed_nu_uncertainty == pytest.approx(0.4e-3)
    assert report.rationale_sha256 == f"sha256:{_sha(VALID)}"
