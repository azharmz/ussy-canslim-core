from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "forward-validation-v1"
DST = ROOT / "evidence" / "fwd1" / "latest"
LEDGER = ROOT / "evidence" / "fwd1" / "observations.csv"

KEEP = [
    "summary.json",
    "gate_status.json",
    "forward_candidates.csv",
    "forward_trade_candidates.csv",
    "portfolio_trades.csv",
    "portfolio_skips.csv",
    "equity_curves.csv",
    "censored_accounting_audit.csv",
    "spy_pointer.json",
    "r2_publication.json",
]


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)

    summary = json.loads((SRC / "summary.json").read_text())
    gate = json.loads((SRC / "gate_status.json").read_text())
    variants = {v["variant"]: v for v in summary["variants"]}
    x1, x3 = variants["X1"], variants["X3"]

    for name in KEEP:
        source = SRC / name
        if not source.exists():
            raise RuntimeError(f"Missing FWD1 evidence file: {name}")
        shutil.copy2(source, DST / name)

    fields = [
        "run_id", "code_sha", "collected_at_utc", "market_data_asof",
        "data_gate_pass", "forward_candidate_count_interpretable",
        "forward_candidate_count", "forward_candidate_symbols",
        "x1_candidate_trades", "x1_portfolio_entries", "x1_closed_trades",
        "x3_candidate_trades", "x3_portfolio_entries", "x3_closed_trades",
        "completed_calendar_months", "calendar_gate_pass", "trade_gate_pass",
        "gate_status",
    ]
    row = {
        "run_id": summary["run_id"],
        "code_sha": summary["code_sha"],
        "collected_at_utc": summary["collected_at_utc"],
        "market_data_asof": summary["market_data_asof"],
        "data_gate_pass": gate.get("data_gate_pass", False),
        "forward_candidate_count_interpretable": summary.get("forward_candidate_count_interpretable", False),
        "forward_candidate_count": summary["forward_candidate_count"],
        "forward_candidate_symbols": summary["forward_candidate_symbols"],
        "x1_candidate_trades": x1.get("candidate_trade_count", 0),
        "x1_portfolio_entries": x1.get("portfolio_entry_count", 0),
        "x1_closed_trades": x1.get("closed_portfolio_trade_count", 0),
        "x3_candidate_trades": x3.get("candidate_trade_count", 0),
        "x3_portfolio_entries": x3.get("portfolio_entry_count", 0),
        "x3_closed_trades": x3.get("closed_portfolio_trade_count", 0),
        "completed_calendar_months": gate["completed_calendar_months"],
        "calendar_gate_pass": gate["calendar_gate_pass"],
        "trade_gate_pass": gate["trade_gate_pass"],
        "gate_status": gate["status"],
    }

    existing = []
    if LEDGER.exists() and LEDGER.stat().st_size:
        with LEDGER.open(newline="") as f:
            for old in csv.DictReader(f):
                existing.append({k: old.get(k, "") for k in fields})
    if not any(str(r.get("run_id")) == str(row["run_id"]) for r in existing):
        existing.append({k: str(row[k]) for k in fields})

    with LEDGER.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(existing)

    print(json.dumps({"persisted_run_id": row["run_id"], "ledger_rows": len(existing), "latest_dir": str(DST)}, indent=2))


if __name__ == "__main__":
    main()
