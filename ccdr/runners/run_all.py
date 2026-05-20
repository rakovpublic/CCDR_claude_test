"""Run the full pipeline (derive × measure → verdict) for every prediction."""
import json
from collections import Counter

from ccdr.runners._collect import all_prediction_modules


def _result_to_row(r):
    return {
        "id": r.prediction_id,
        "status": r.status.value,
        "test_statistic": r.test_statistic,
        "pass_threshold": r.pass_threshold,
        "parameters_revision": r.parameters_revision,
        "derivation": {
            "status": r.derivation.status.value,
            "value": r.derivation.value,
            "uncertainty": r.derivation.uncertainty,
            "missing_parameters": list(r.derivation.missing_parameters),
            "derivation_function_id": r.derivation.derivation_function_id,
        },
        "measurement": {
            "status": r.measurement.status.value,
            "value": r.measurement.value,
            "uncertainty": r.measurement.uncertainty,
            "data_source": r.measurement.data_source,
            "data_sha256": r.measurement.data_sha256,
            "n_samples": r.measurement.n_samples,
        },
        "notes": r.notes,
    }


def main():
    mods = all_prediction_modules()
    by_status = Counter()
    rows = []
    for mod in mods:
        r = mod.test()
        by_status[r.status.value] += 1
        rows.append(_result_to_row(r))
    summary = {
        "n_predictions": len(rows),
        "status_counts": dict(by_status),
        "results": rows,
    }
    print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    main()
