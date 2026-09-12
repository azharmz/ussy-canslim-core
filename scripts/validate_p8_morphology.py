#!/usr/bin/env python3
"""Validate P8 lineage output against independently adjudicated morphology labels."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from canslim_research.pattern_validation import (  # noqa: E402
    MorphologyLabel,
    evaluate_morphology_labels,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate P8 morphology labels")
    parser.add_argument("--report", required=True, help="P8 pattern-engine JSON report")
    parser.add_argument("--labels", required=True, help="Independent morphology-label JSON")
    parser.add_argument("--output", default="results/p8-morphology-validation.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = json.loads((ROOT / args.report).read_text(encoding="utf-8"))
    payload = json.loads((ROOT / args.labels).read_text(encoding="utf-8"))
    raw_labels = payload["labels"] if isinstance(payload, dict) else payload
    labels = [MorphologyLabel.from_dict(row) for row in raw_labels]
    lineages = report.get("all_base_lineages")
    if not isinstance(lineages, list):
        raise ValueError("P8 report must contain all_base_lineages")

    result = evaluate_morphology_labels(labels, lineages)
    result.update(
        {
            "pattern_report": args.report,
            "label_file": args.labels,
            "ticker": report.get("ticker"),
            "security_id": report.get("security_id"),
            "pattern_engine_version": report.get("pattern_engine_version"),
            "base_identity_version": report.get("base_identity_version"),
            "base_lineage_version": report.get("base_lineage_version"),
            "conflict_layer_version": report.get("conflict_layer_version"),
        }
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
