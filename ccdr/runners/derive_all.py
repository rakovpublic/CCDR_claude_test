"""Run every prediction's derive() and print a summary. No data touched."""
import json
from collections import Counter

from ccdr.core.status import DerivationStatus
from ccdr.runners._collect import all_prediction_modules


def main():
    mods = all_prediction_modules()
    by_status = Counter()
    rows = []
    for mod in mods:
        d = mod.derive()
        by_status[d.status.value] += 1
        rows.append({
            "id": mod.ID,
            "name": getattr(mod, "NAME", ""),
            "status": d.status.value,
            "value": d.value,
            "uncertainty": d.uncertainty,
            "missing_parameters": list(d.missing_parameters),
            "derivation_function_id": d.derivation_function_id,
            "provenance": d.provenance,
        })
    summary = {
        "n_predictions": len(rows),
        "status_counts": dict(by_status),
        "predictions": rows,
    }
    print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    main()
