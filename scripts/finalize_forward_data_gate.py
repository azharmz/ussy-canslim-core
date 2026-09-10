from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "forward-validation-v1"
FORWARD_START = pd.Timestamp("2026-09-10")


def main() -> None:
    summary_path = OUT / "summary.json"
    gate_path = OUT / "gate_status.json"
    summary = json.loads(summary_path.read_text())
    gate = json.loads(gate_path.read_text())

    market_asof = pd.Timestamp(gate["market_data_asof"]).normalize()
    data_gate_pass = bool(market_asof >= FORWARD_START)
    calendar_gate = bool(gate.get("calendar_gate_pass"))
    trade_gate = bool(gate.get("trade_gate_pass"))
    review_eligible = bool(data_gate_pass and calendar_gate and trade_gate)

    if not data_gate_pass:
        status = "WAITING_FOR_POST_BOUNDARY_DATA"
        interpretation = (
            "Market-regime source does not yet reach the FWD1 forward boundary. "
            "Candidate/trade counts are operationally recorded but must not be interpreted as evidence of no signals."
        )
    elif review_eligible:
        status = "REVIEW_ELIGIBLE"
        interpretation = "Source freshness and both frozen evidence gates pass; formal review is allowed, not automatic production promotion."
    else:
        status = "ACCUMULATING"
        interpretation = "Post-boundary market data are available; FWD1 is accumulating evidence under frozen rules."

    gate["data_gate_pass"] = data_gate_pass
    gate["minimum_market_data_asof"] = str(FORWARD_START.date())
    gate["status"] = status
    gate["review_eligible"] = review_eligible
    gate["candidate_zero_interpretable"] = bool(data_gate_pass)
    gate["source_freshness_interpretation"] = interpretation
    gate["production_ready"] = False

    summary["gate"] = gate
    summary["source_data_ready_for_forward_inference"] = data_gate_pass
    summary["forward_candidate_count_interpretable"] = bool(data_gate_pass)

    gate_path.write_text(json.dumps(gate, indent=2, sort_keys=True, default=str))
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    print(json.dumps(gate, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
