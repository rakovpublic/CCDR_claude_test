"""Serialise the audit to op11_report.json and a human-readable summary.

Also owns the RATIONALE.md gate (CLAUDE_op11_nu.md §6): DATASET_DEPENDENT_DOCUMENTED
is reachable only when RATIONALE.md exists with valid frontmatter, and the
file's sha256 is embedded in the report so any later edit invalidates the
cached classification.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from .candidates import NU_JOINT, NU_STANDALONE
from .classification import OP11Classification, is_committable
from .results import (
    HierarchicalResult,
    OP11Report,
    PerDatasetChi2Result,
    ProfileLikelihoodResult,
    TensionMetricsResult,
)
from .synthesis import _find_consensus_third_value

_HERE = pathlib.Path(__file__).resolve().parent
REPORT_PATH = _HERE / "op11_report.json"
RATIONALE_PATH = _HERE / "RATIONALE.md"

_REQUIRED_FRONTMATTER = (
    "op11_classification",
    "committed_nu",
    "committed_nu_uncertainty",
    "operational_definition",
    "framework_section_reference",
    "author",
    "date",
)


# ---------------------------------------------------------------------------
# RATIONALE.md gate
# ---------------------------------------------------------------------------
def _normalise(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(_normalise(path.read_bytes())).hexdigest()


def _parse_frontmatter(text: str) -> Optional[dict]:
    """Parse a leading `---`-delimited block of `key: value` lines. Returns the
    mapping, or None if no well-formed frontmatter block is present. Minimal by
    design — no YAML dependency (the parent project declares none)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"').strip("'")
        fm[key.strip()] = value
    return None  # no closing delimiter


def rationale_status() -> Tuple[bool, bool, Optional[str], Optional[dict]]:
    """Return (present, valid, sha256, frontmatter).

    `valid` requires the closing-delimited frontmatter to carry every required
    key and to self-declare op11_classification == DATASET_DEPENDENT_DOCUMENTED
    with numeric committed_nu / committed_nu_uncertainty."""
    if not RATIONALE_PATH.exists():
        return False, False, None, None
    sha = _sha256_file(RATIONALE_PATH)
    fm = _parse_frontmatter(RATIONALE_PATH.read_text(encoding="utf-8"))
    if fm is None:
        return True, False, sha, None
    if any(k not in fm for k in _REQUIRED_FRONTMATTER):
        return True, False, sha, fm
    if fm["op11_classification"] != OP11Classification.DATASET_DEPENDENT_DOCUMENTED.value:
        return True, False, sha, fm
    try:
        float(fm["committed_nu"])
        float(fm["committed_nu_uncertainty"])
    except (TypeError, ValueError):
        return True, False, sha, fm
    return True, True, sha, fm


# ---------------------------------------------------------------------------
# Committed-value resolution
# ---------------------------------------------------------------------------
def _audit_revision() -> str:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_HERE), stderr=subprocess.DEVNULL,
        ).decode().strip()
        return f"git:{sha}"
    except Exception:
        return "git:unknown"


def _joint_uncertainty() -> float:
    """Joint extractor posterior width, sourced from the cached nu extraction."""
    try:
        from ccdr.data.loaders._common import read_cached_json
        data, _ = read_cached_json("nu_extraction")
        for row in data["rows"]:
            if str(row[0]).startswith("joint"):
                return float(row[2])
    except Exception:
        pass
    return abs(NU_JOINT) * 0.25


def _resolve_committed(
    classification: OP11Classification,
    path1: List[PerDatasetChi2Result],
    path2: List[ProfileLikelihoodResult],
    frontmatter: Optional[dict],
) -> Tuple[Optional[float], Optional[float], str]:
    if classification == OP11Classification.RESOLVED_JOINT:
        rejecters = sorted({r.dataset_name for r in path1
                            if r.nu_label == "standalone" and not r.accepts_at_95})
        prov = ("OP11 Path 1: joint extractor accepted by all datasets at 95%; "
                f"standalone rejected by {rejecters or 'none individually'}")
        return NU_JOINT, _joint_uncertainty(), prov
    if classification == OP11Classification.RESOLVED_STANDALONE:
        rejecters = sorted({r.dataset_name for r in path1
                            if r.nu_label == "joint" and not r.accepts_at_95})
        prov = ("OP11 Path 1: standalone extractor accepted by all datasets at 95%; "
                f"joint rejected by {rejecters or 'none individually'}")
        return NU_STANDALONE, abs(NU_STANDALONE) * 0.25, prov
    if classification == OP11Classification.RESOLVED_THIRD_VALUE:
        third = _find_consensus_third_value(path2)
        lo = max(p.nu_mle - p.nu_mle_uncertainty for p in path2)
        hi = min(p.nu_mle + p.nu_mle_uncertainty for p in path2)
        unc = 0.5 * (hi - lo)
        prov = "OP11 Path 2: consensus value in the 1-sigma overlap of all per-dataset profiles"
        return third, unc, prov
    if classification == OP11Classification.DATASET_DEPENDENT_DOCUMENTED:
        if frontmatter is None:
            return None, None, ""
        prov = (f"{frontmatter.get('operational_definition', '')} "
                f"({frontmatter.get('framework_section_reference', '')})").strip()
        return (float(frontmatter["committed_nu"]),
                float(frontmatter["committed_nu_uncertainty"]),
                prov)
    return None, None, f"BLOCKED on OP11: {classification.value}"


# ---------------------------------------------------------------------------
# Report assembly + serialisation
# ---------------------------------------------------------------------------
def build_report(
    classification: OP11Classification,
    path1: List[PerDatasetChi2Result],
    path2: List[ProfileLikelihoodResult],
    path3: List[TensionMetricsResult],
    path4: Optional[HierarchicalResult],
    datasets,
    rationale_sha256: Optional[str],
    frontmatter: Optional[dict],
    notes: str = "",
) -> OP11Report:
    committed_nu, committed_unc, provenance = _resolve_committed(
        classification, path1, path2, frontmatter)
    data_revision = {ds.name: f"sha256:{ds.data_sha256}" for ds in datasets}
    return OP11Report(
        classification=classification,
        committed_nu=committed_nu,
        committed_nu_uncertainty=committed_unc,
        provenance=provenance,
        audit_revision=_audit_revision(),
        data_revision=data_revision,
        diagnostics={
            "path1": [asdict(r) for r in path1],
            "path2": [asdict(r) for r in path2],
            "path3": [asdict(r) for r in path3],
            "path4": asdict(path4) if path4 is not None else None,
        },
        rationale_sha256=(f"sha256:{rationale_sha256}" if rationale_sha256 else None),
        timestamp=datetime.now(timezone.utc),
        framework_revision_flag=(classification == OP11Classification.MODEL_MISSPECIFIED),
        notes=notes,
    )


def report_to_dict(report: OP11Report) -> dict:
    return {
        "classification": report.classification.value,
        "committed_nu": report.committed_nu,
        "committed_nu_uncertainty": report.committed_nu_uncertainty,
        "provenance": report.provenance,
        "audit_revision": report.audit_revision,
        "data_revision": report.data_revision,
        "diagnostics": report.diagnostics,
        "rationale_sha256": report.rationale_sha256,
        "timestamp": report.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "framework_revision_flag": report.framework_revision_flag,
        "notes": report.notes,
    }


def write_report(report: OP11Report, path: pathlib.Path = REPORT_PATH) -> None:
    path.write_text(json.dumps(report_to_dict(report), indent=2) + "\n",
                    encoding="utf-8")


def human_summary(report: OP11Report) -> str:
    lines = [
        "OP11 nu-resolution audit",
        "=" * 40,
        f"classification : {report.classification.value}",
        f"committed NU   : {report.committed_nu}"
        + (f" +/- {report.committed_nu_uncertainty}" if report.committed_nu is not None else ""),
        f"provenance     : {report.provenance}",
        f"audit revision : {report.audit_revision}",
        f"framework flag : {report.framework_revision_flag}",
        "",
        "Path 1 (per-dataset chi2 at competing nu):",
    ]
    for r in report.diagnostics["path1"]:
        verdict = "accept" if r["accepts_at_95"] else "REJECT"
        lines.append(
            f"  {r['dataset_name']:<18} {r['nu_label']:<11} "
            f"chi2={r['chi2']:.3g} dof={r['dof']} p={r['p_value']:.3g} -> {verdict}"
        )
    p4 = report.diagnostics["path4"]
    if p4 is not None:
        lines += [
            "",
            f"Path 4 (hierarchical): nu_global={p4['nu_global_mean']:.3g} "
            f"+/- {p4['nu_global_std']:.2g}, tau_mean={p4['tau_mean']:.2g}, "
            f"universality={p4['universality_assessment']}",
        ]
    return "\n".join(lines)


__all__ = [
    "REPORT_PATH", "RATIONALE_PATH", "rationale_status", "build_report",
    "report_to_dict", "write_report", "human_summary",
]
