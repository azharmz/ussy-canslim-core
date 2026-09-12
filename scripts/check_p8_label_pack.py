#!/usr/bin/env python3
"""Check whether a P8 morphology label pack satisfies preregistered coverage readiness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from canslim_research.morphology_label_pack import parse_label_pack  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check P8 morphology label-pack coverage")
    parser.add_argument("--labels", required=True, help="Morphology label-pack JSON")
    parser.add_argument("--output", help="Optional JSON summary output")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Exit nonzero when the pack is not ready for broader DEVELOPMENT validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads((ROOT / args.labels).read_text(encoding="utf-8"))
    _, summary = parse_label_pack(payload)
    result = summary.to_dict()
    result["label_file"] = args.labels
    print(json.dumps(result, indent=2))

    if args.output:
        output = ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.require_ready and not summary.ready_for_broader_development_validation:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
