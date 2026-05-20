"""Run one prediction by ID and print the TestResult."""
import argparse
import json
import sys

from ccdr.runners._collect import all_prediction_modules
from ccdr.runners.run_all import _result_to_row


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run one CCDR prediction.")
    parser.add_argument("prediction_id", help="e.g. P-A07")
    args = parser.parse_args(argv)
    for mod in all_prediction_modules():
        if mod.ID == args.prediction_id:
            r = mod.test()
            print(json.dumps(_result_to_row(r), indent=2, default=str))
            return 0
    print(f"Unknown prediction id: {args.prediction_id}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
