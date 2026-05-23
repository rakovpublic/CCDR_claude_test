"""Entry point: run all diagnostics, classify, write op11_report.json.

    python -m ccdr.audits.op11_nu.run_audit

Re-running on the same cached data produces a bit-identical report modulo the
timestamp. If any diagnostic raises, the classification is AUDIT_INCOMPLETE and
a report is still written (no NU is committed).
"""
from __future__ import annotations

from .classification import OP11Classification
from .datasets import iter_datasets
from .diagnostics import run_path1, run_path2, run_path3, run_path4
from .report import build_report, human_summary, rationale_status, write_report
from .results import OP11Report
from .synthesis import classify


def run_audit(write: bool = True) -> OP11Report:
    present, valid, rationale_sha, frontmatter = rationale_status()
    notes = ""
    try:
        datasets = iter_datasets()
        path1 = run_path1(datasets)
        path2 = run_path2(datasets)
        path3 = run_path3(path2)
        path4 = run_path4(path2)
        classification = classify(path1, path2, path3, path4, present, valid)
    except Exception as exc:  # diagnostic crashed -> AUDIT_INCOMPLETE
        datasets = ()
        path1 = path2 = path3 = []
        path4 = None
        classification = OP11Classification.AUDIT_INCOMPLETE
        notes = f"diagnostic failure: {type(exc).__name__}: {exc}"

    report = build_report(
        classification, path1, path2, path3, path4, datasets,
        rationale_sha, frontmatter, notes=notes,
    )
    if write:
        write_report(report)
    return report


def main() -> OP11Report:
    report = run_audit(write=True)
    print(human_summary(report))
    return report


if __name__ == "__main__":
    main()
