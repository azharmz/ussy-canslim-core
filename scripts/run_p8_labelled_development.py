#!/usr/bin/env python3
"""Evaluate authoritative P8 DEVELOPMENT morphology labels without outcome data."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date, timedelta
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from canslim_research.labelled_morphology import LABELLED_EVAL_VERSION, MorphologyLabel, evaluate_positive_label
from canslim_research.ohlcv_providers import r2_ticker_provider, tiingo_provider, yahoo_provider
from canslim_research.ohlcv_router import route_ohlcv
from canslim_research.pattern_engine_v02 import PATTERN_ENGINE_VERSION, detect_patterns_v02
from canslim_research.pattern_identity import BASE_IDENTITY_VERSION, cluster_base_identities
from canslim_research.pattern_lineage import BASE_LINEAGE_VERSION, cluster_base_lineages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate P8 authoritative DEVELOPMENT labels")
    parser.add_argument("--labels", default="data/p8/labels_v0.csv")
    parser.add_argument("--example-id")
    parser.add_argument("--context-calendar-days", type=int, default=240)
    parser.add_argument("--boundary-tolerance-days", type=int, default=10)
    parser.add_argument("--pivot-date-tolerance-days", type=int, default=3)
    parser.add_argument("--pivot-price-tolerance-pct", type=float, default=0.01)
    parser.add_argument("--output", default="results/p8-labelled-development.json")
    return parser.parse_args()


def _optional_float(value):
    return None if value is None or not value.strip() else float(value)


def _optional_text(value):
    return None if value is None or not value.strip() else value.strip()


def _load_labels(path: Path) -> list[MorphologyLabel]:
    labels = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["split"] != "DEVELOPMENT":
                continue
            labels.append(MorphologyLabel(
                example_id=row["example_id"], symbol=row["symbol"], pattern=row["pattern"], label=row["label"],
                window_start=row["window_start"], window_end=_optional_text(row.get("window_end")), asof_date=row["asof_date"],
                expected_pivot_source_date=_optional_text(row.get("expected_pivot_source_date")),
                expected_pivot_level=_optional_float(row.get("expected_pivot_level")), provenance=row["provenance"],
                source_name=row["source_name"], source_reference=row["source_reference"], rationale=row["rationale"], split=row["split"],
                window_start_precision=(row.get("window_start_precision") or "DAY").strip().upper(),
                pivot_price_adjustment_factor=float(row.get("pivot_price_adjustment_factor") or 1.0),
            ))
    return labels


def _evaluation_security_id(label: MorphologyLabel, routed) -> tuple[str, str]:
    security_id = routed.metadata.get("security_id")
    if security_id:
        return str(security_id), "R2_SECURITY_ID"
    return f"P8-TICKER:{label.symbol.upper()}", "P8_EXTERNAL_TICKER"


def _run_label(label, *, context_days, boundary_tolerance, pivot_date_tolerance, pivot_price_tolerance):
    context_start = (date.fromisoformat(label.window_start) - timedelta(days=context_days)).isoformat()
    routed = route_ohlcv({
        "r2": lambda: r2_ticker_provider(ticker=label.symbol, start=context_start, end=label.asof_date),
        "yahoo": lambda: yahoo_provider(ticker=label.symbol, start=context_start, end=label.asof_date),
        "tiingo": lambda: tiingo_provider(ticker=label.symbol, start=context_start, end=label.asof_date),
    })
    security_id, security_identity_kind = _evaluation_security_id(label, routed)
    candidates = detect_patterns_v02(routed.rows)
    identities = cluster_base_identities(candidates, security_id=security_id)
    lineages = cluster_base_lineages(identities)
    agreement = evaluate_positive_label(label, lineages, identities, candidates, boundary_tolerance_days=boundary_tolerance, pivot_date_tolerance_days=pivot_date_tolerance, pivot_price_tolerance_pct=pivot_price_tolerance)
    return {"label": label.__dict__, "security_id": security_id, "security_identity_kind": security_identity_kind, "context_start": context_start, "selected_source": routed.source, "source_metadata": dict(routed.metadata), "input_row_count": len(routed.rows), "candidate_count": len(candidates), "base_identity_count": len(identities), "base_lineage_count": len(lineages), "agreement": agreement.to_dict(), "same_pattern_lineages": [item.to_dict() for item in lineages if item.pattern_type == label.pattern]}


def _detector_resolution_state(result: dict) -> str:
    candidate = result["agreement"].get("matched_raw_candidate")
    if candidate is None:
        return "NO_MATCHED_CANDIDATE"
    return str(candidate.get("pattern_evidence_state") or "UNKNOWN")


def _summary_counts(results: list[dict]) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    agreement = Counter(item["agreement"]["agreement_state"] for item in results)
    detector_resolution = Counter(_detector_resolution_state(item) for item in results)
    joint = Counter(
        f'{item["agreement"]["agreement_state"]}:{_detector_resolution_state(item)}'
        for item in results
    )
    return dict(sorted(agreement.items())), dict(sorted(detector_resolution.items())), dict(sorted(joint.items()))


def main() -> int:
    args = parse_args()
    if args.context_calendar_days < 180:
        raise ValueError("context-calendar-days must be >=180 for the active 120-session prior-uptrend window")
    if args.pivot_price_tolerance_pct < 0:
        raise ValueError("pivot-price-tolerance-pct must be nonnegative")
    labels = _load_labels(ROOT / args.labels)
    if args.example_id:
        labels = [label for label in labels if label.example_id == args.example_id]
    if not labels:
        raise ValueError("no DEVELOPMENT labels selected")
    results = [_run_label(label, context_days=args.context_calendar_days, boundary_tolerance=args.boundary_tolerance_days, pivot_date_tolerance=args.pivot_date_tolerance_days, pivot_price_tolerance=args.pivot_price_tolerance_pct) for label in labels]
    agreement_counts, detector_resolution_counts, joint_counts = _summary_counts(results)
    report = {
        "stage":"P8",
        "scope":"AUTHORITATIVE_LABELLED_DEVELOPMENT",
        "pattern_engine_version":PATTERN_ENGINE_VERSION,
        "base_identity_version":BASE_IDENTITY_VERSION,
        "base_lineage_version":BASE_LINEAGE_VERSION,
        "labelled_eval_version":LABELLED_EVAL_VERSION,
        "context_calendar_days":args.context_calendar_days,
        "boundary_tolerance_days":args.boundary_tolerance_days,
        "pivot_date_tolerance_days":args.pivot_date_tolerance_days,
        "pivot_price_tolerance_pct":args.pivot_price_tolerance_pct,
        "result_count":len(results),
        "agreement_counts":agreement_counts,
        "matched_detector_evidence_state_counts":detector_resolution_counts,
        "agreement_by_detector_evidence_state":joint_counts,
        "results":results,
        "guardrails":[
            "DEVELOPMENT split only; VALIDATION labels are not read into detector comparison",
            "reference-first authoritative labels and anchors are frozen before detector comparison",
            "OHLCV is truncated at each label asof_date; no future bars are supplied",
            "source dimensions are scored only at their published precision; absent dimensions remain unscored",
            "source pivot prices remain immutable; documented split-adjustment factors normalize only the comparison basis",
            "R2 membership absence is explicit UNAVAILABLE and may fall through to Yahoo/Tiingo; ambiguous or broken R2 resolution remains terminal",
            "external-source evaluation identities are P8-local ticker keys and do not alter the frozen Musaffa universe",
            "authoritative scoring uses only raw windows actually emitted by the frozen detector; selected windows are mapped back to stable base_id/lineage",
            "agreement requires fidelity on every source-provided pattern/boundary/pivot dimension",
            "MATCH describes source-dimension agreement only; matched detector PASS/AMBIGUOUS state is reported separately and ambiguity is never promoted to clean confirmation",
            "no return/CAGR/PF outcome is inspected"
        ]
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
