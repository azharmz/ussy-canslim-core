from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "portfolio-construction-v1"
EXIT_COST_RATE = 0.001


def cagr_from_initial(final_equity: float, initial_equity: float, first_date: pd.Timestamp, last_date: pd.Timestamp):
    days = (last_date - first_date).days
    if days <= 0 or final_equity <= 0 or initial_equity <= 0:
        return None
    return float((final_equity / initial_equity) ** (365.25 / days) - 1.0)


def max_drawdown(series: pd.Series) -> float:
    x = pd.to_numeric(series, errors="coerce").dropna()
    return float((x / x.cummax() - 1.0).min())


def rebuild_annual_returns(curves: pd.DataFrame, initial_equity: float) -> pd.DataFrame:
    rows = []
    for variant, vg in curves.groupby("variant", sort=False):
        vg = vg.sort_values("date")
        for col in ("gross_equity", "cost20bp_rt_equity"):
            prev = initial_equity
            for year, g in vg.groupby(vg["date"].dt.year, sort=True):
                end = float(g.iloc[-1][col])
                rows.append({"year": int(year), "curve": col, "return": end / prev - 1.0, "variant": variant})
                prev = end
    return pd.DataFrame(rows)


def main() -> None:
    trades = pd.read_csv(OUT / "portfolio_trades.csv")
    curves = pd.read_csv(OUT / "equity_curves.csv")
    summary_path = OUT / "summary.json"
    summary = json.loads(summary_path.read_text())

    trades["exit_date"] = pd.to_datetime(trades["exit_date"], errors="coerce").dt.normalize()
    curves["date"] = pd.to_datetime(curves["date"], errors="coerce").dt.normalize()
    initial_equity = float(summary["initial_equity"])

    audit = {}
    for variant in ("X1", "X3"):
        mask_v = curves["variant"].eq(variant)
        last_date = curves.loc[mask_v, "date"].max()
        censored = trades[(trades["variant"] == variant) & (trades["exit_reason"] == "CENSORED_OPEN")].copy()

        # PORT1 methodology says censored positions are marked at the sample boundary,
        # not liquidated. A mid-sample censor would affect later capacity/cash allocation
        # and cannot be repaired safely after the fact, so fail hard instead.
        bad = censored[censored["exit_date"] != last_date]
        if len(bad):
            raise RuntimeError(
                f"{variant}: {len(bad)} censored positions end before portfolio sample boundary; "
                "allocation must be re-simulated rather than post-processed"
            )

        final_mask = mask_v & curves["date"].eq(last_date)
        if final_mask.sum() != 1:
            raise RuntimeError(f"{variant}: expected exactly one final curve row")

        marked_value = float(censored["exit_notional"].sum()) if len(censored) else 0.0
        phantom_exit_cost = marked_value * EXIT_COST_RATE
        if len(censored):
            curves.loc[final_mask, "cash"] -= marked_value
            curves.loc[final_mask, "market_value"] += marked_value
            curves.loc[final_mask, "cumulative_cost"] -= phantom_exit_cost
            curves.loc[final_mask, "cost20bp_rt_equity"] += phantom_exit_cost
            curves.loc[final_mask, "position_count"] += len(censored)
            gross_equity = float(curves.loc[final_mask, "gross_equity"].iloc[0])
            curves.loc[final_mask, "gross_exposure"] = (
                float(curves.loc[final_mask, "market_value"].iloc[0]) / gross_equity
                if gross_equity > 0 else float("nan")
            )

        row = next(v for v in summary["variants"] if v["variant"] == variant)
        final = curves.loc[final_mask].iloc[0]
        first_date = pd.Timestamp(row["first_date"])

        gross_final = float(final["gross_equity"])
        cost_final = float(final["cost20bp_rt_equity"])
        gross_curve = curves.loc[mask_v, "gross_equity"]
        cost_curve = curves.loc[mask_v, "cost20bp_rt_equity"]

        # Total return and CAGR use the declared 100,000 initial capital consistently.
        row["gross_total_return"] = gross_final / initial_equity - 1.0
        row["gross_cagr"] = cagr_from_initial(gross_final, initial_equity, first_date, last_date)
        row["gross_max_drawdown"] = max_drawdown(gross_curve)
        row["cost20bp_rt_total_return"] = cost_final / initial_equity - 1.0
        row["cost20bp_rt_cagr"] = cagr_from_initial(cost_final, initial_equity, first_date, last_date)
        row["cost20bp_rt_max_drawdown"] = max_drawdown(cost_curve)
        row["final_censored_position_count"] = int(len(censored))
        row["final_censored_mark_value"] = marked_value
        row["phantom_exit_cost_removed"] = phantom_exit_cost

        audit[variant] = {
            "portfolio_first_date": str(first_date.date()),
            "portfolio_last_date": str(last_date.date()),
            "censored_positions": int(len(censored)),
            "mid_sample_censored_positions": int(len(bad)),
            "censored_treated_as_mark_to_market_not_exit": True,
            "phantom_exit_cost_removed": phantom_exit_cost,
            "cagr_denominator": "declared_initial_equity",
        }

    curves.to_csv(OUT / "equity_curves.csv", index=False)
    pd.DataFrame(summary["variants"]).to_csv(OUT / "portfolio_summary.csv", index=False)
    rebuild_annual_returns(curves, initial_equity).to_csv(OUT / "annual_returns.csv", index=False)
    summary["censored_position_accounting"] = audit
    summary["censored_positions_are_forced_exits"] = False
    summary["cagr_denominator"] = "declared_initial_equity"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (OUT / "censored_accounting_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True))
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
