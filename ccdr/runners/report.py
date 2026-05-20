"""One-page human-readable report from a run_all.py JSON dump."""
import json
import sys
from collections import Counter


def render(report_json: dict) -> str:
    lines = []
    counts = report_json.get("status_counts", {})
    lines.append("CCDR PIPELINE REPORT")
    lines.append("=" * 60)
    lines.append(f"Total predictions: {report_json.get('n_predictions', 0)}")
    lines.append("Status counts:")
    for status in ("CONFIRM", "REJECT", "INCONCLUSIVE",
                   "PARAMETER_PENDING", "NOT_RUN"):
        lines.append(f"  {status:18s} {counts.get(status, 0)}")
    lines.append("")
    lines.append("Per-prediction:")
    for row in report_json.get("results", []):
        lines.append(f"  {row['id']:8s} {row['status']:18s}  "
                     f"stat={row.get('test_statistic')}  "
                     f"rev={row['parameters_revision']}")
        if row.get("notes"):
            lines.append(f"     · {row['notes']}")
    return "\n".join(lines)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv:
        with open(argv[0]) as f:
            data = json.load(f)
    else:
        data = json.loads(sys.stdin.read())
    print(render(data))


if __name__ == "__main__":
    main()
