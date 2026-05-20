"""Run every prediction's measure() and print a summary. No derivation called."""
import json
from collections import Counter

from ccdr.runners._collect import all_prediction_modules


def main():
    mods = all_prediction_modules()
    by_status = Counter()
    rows = []
    for mod in mods:
        m = mod.measure()
        by_status[m.status.value] += 1
        rows.append({
            "id": mod.ID,
            "name": getattr(mod, "NAME", ""),
            "status": m.status.value,
            "value": m.value,
            "uncertainty": m.uncertainty,
            "data_source": m.data_source,
            "data_sha256": m.data_sha256,
            "estimator_id": m.estimator_id,
            "n_samples": m.n_samples,
        })
    summary = {
        "n_predictions": len(rows),
        "status_counts": dict(by_status),
        "measurements": rows,
    }
    print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    main()
