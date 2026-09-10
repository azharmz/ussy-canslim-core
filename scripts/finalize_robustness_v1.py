from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "robustness-v1"


def cagr_from_total_return(total_return: float, first_date: str, last_date: str):
    first = pd.Timestamp(first_date)
    last = pd.Timestamp(last_date)
    days = (last - first).days
    growth = 1.0 + float(total_return)
    if days <= 0 or growth <= 0:
        return None
    return float(growth ** (365.25 / days) - 1.0)


def main() -> None:
    path = OUT / "summary.json"
    summary = json.loads(path.read_text())
    for row in summary["variants"]:
        row["gross_cagr"] = cagr_from_total_return(
            row["gross_total_return"], row["first_date"], row["last_date"]
        )
        row["cost20bp_rt_cagr"] = cagr_from_total_return(
            row["cost20bp_rt_total_return"], row["first_date"], row["last_date"]
        )
        spy_cagr = row["spy_price_only"]["cagr"]
        row["gross_cagr_minus_spy_price_cagr"] = (
            float(row["gross_cagr"] - spy_cagr) if row["gross_cagr"] is not None and spy_cagr is not None else None
        )
    summary["portfolio_cagr_denominator"] = "declared_initial_equity"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    print(json.dumps({
        row["variant"]: {
            "gross_cagr": row["gross_cagr"],
            "cost20bp_rt_cagr": row["cost20bp_rt_cagr"],
        }
        for row in summary["variants"]
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
