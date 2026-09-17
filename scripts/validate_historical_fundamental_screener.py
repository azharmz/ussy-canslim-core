from __future__ import annotations

import ast
import json
from pathlib import Path

import exchange_calendars as xcals
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "historical-fundamental-screener-v1"
NY = "America/New_York"


def log(msg: str) -> None:
    print(f"[historical-fundamental-validation] {msg}", flush=True)


def main() -> None:
    log("START: load screener evidence")
    transitions = pd.read_csv(OUT / "fundamental_state_transitions.csv")
    intervals = pd.read_csv(OUT / "ca_pass_intervals.csv")
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))

    for col in ["effective_accepted_at", "c_source_accepted_at", "a_max_source_accepted_at"]:
        transitions[col] = pd.to_datetime(transitions[col], errors="coerce", utc=True)
    intervals["pass_from_accepted_at"] = pd.to_datetime(intervals["pass_from_accepted_at"], errors="coerce", utc=True)
    intervals["pass_until_accepted_at_exclusive"] = pd.to_datetime(
        intervals["pass_until_accepted_at_exclusive"], errors="coerce", utc=True
    )

    dupes = int(transitions.duplicated(["security_id", "effective_accepted_at"]).sum())
    c_future = int((transitions["c_source_accepted_at"] > transitions["effective_accepted_at"]).fillna(False).sum())
    a_future = int((transitions["a_max_source_accepted_at"] > transitions["effective_accepted_at"]).fillna(False).sum())
    if dupes or c_future or a_future:
        raise RuntimeError(f"Critical transition validation failed: dupes={dupes} c_future={c_future} a_future={a_future}")

    passes = transitions.loc[transitions["ca_state"].eq("PASS")].copy()
    bad_c = passes.loc[(passes["quarterly_eps_yoy"] < 0.25) | (passes["quarterly_revenue_yoy"] < 0.25)]
    bad_a = []
    for r in passes.itertuples(index=False):
        growths = ast.literal_eval(r.a_growths)
        if len(growths) != 3 or any(v is None or float(v) < 0.25 for v in growths):
            bad_a.append(r.security_id)
        if not bool(r.a_fy_consecutive) or int(r.a_unresolved_fy_states) != 0:
            bad_a.append(r.security_id)
    if len(bad_c) or bad_a:
        raise RuntimeError(f"PASS threshold validation failed: bad_c={len(bad_c)} bad_a={len(bad_a)}")

    # Every interval must begin on a PASS transition and end (when finite) on a non-PASS transition.
    for r in intervals.itertuples(index=False):
        g = transitions.loc[transitions["security_id"].eq(r.security_id)]
        start_state = g.loc[g["effective_accepted_at"].eq(r.pass_from_accepted_at), "ca_state"].tolist()
        if start_state != ["PASS"]:
            raise RuntimeError(f"Invalid PASS interval start for {r.security_id}: {start_state}")
        if pd.notna(r.pass_until_accepted_at_exclusive):
            end_state = g.loc[g["effective_accepted_at"].eq(r.pass_until_accepted_at_exclusive), "ca_state"].tolist()
            if len(end_state) != 1 or end_state[0] == "PASS":
                raise RuntimeError(f"Invalid PASS interval end for {r.security_id}: {end_state}")

    # Materialize the actual historical screener answer only for NYSE decision dates where C+A is PASS.
    # This stays compact: FAIL/NOT_EVALUABLE history remains represented by the event-driven transition table.
    cal = xcals.get_calendar("XNYS")
    min_day = intervals["pass_from_accepted_at"].min().date()
    finite_end = intervals["pass_until_accepted_at_exclusive"].dropna()
    max_ts = finite_end.max() if len(finite_end) else transitions["effective_accepted_at"].max()
    max_day = max(max_ts, transitions["effective_accepted_at"].max()).date()
    sessions = cal.sessions_in_range(pd.Timestamp(min_day), pd.Timestamp(max_day))

    decision_rows = []
    for session in sessions:
        day = pd.Timestamp(session).date()
        cutoff = pd.Timestamp(f"{day} 16:00:00", tz=NY).tz_convert("UTC")
        active = intervals.loc[
            intervals["pass_from_accepted_at"].le(cutoff)
            & (intervals["pass_until_accepted_at_exclusive"].isna() | intervals["pass_until_accepted_at_exclusive"].gt(cutoff))
        ]
        for r in active.itertuples(index=False):
            decision_rows.append({
                "decision_date": str(day),
                "decision_cutoff_utc": cutoff.isoformat(),
                "security_id": r.security_id,
                "symbol": r.symbol,
                "cik": r.cik,
                "ca_state": "PASS",
                "pass_from_accepted_at": r.pass_from_accepted_at.isoformat(),
                "pass_until_accepted_at_exclusive": (
                    r.pass_until_accepted_at_exclusive.isoformat()
                    if pd.notna(r.pass_until_accepted_at_exclusive) else None
                ),
            })

    by_date = pd.DataFrame(decision_rows)
    if by_date.empty:
        raise RuntimeError("No C+A PASS decision-date rows produced")
    if by_date.duplicated(["decision_date", "security_id"]).any():
        raise RuntimeError("Duplicate security on a decision date")
    by_date.to_csv(OUT / "ca_pass_by_decision_date.csv", index=False)

    validation = {
        "status": "PASS",
        "transition_duplicate_rows": dupes,
        "future_c_source_violations": c_future,
        "future_a_source_violations": a_future,
        "ca_pass_transition_rows": int(len(passes)),
        "ca_pass_intervals": int(len(intervals)),
        "securities_ever_ca_pass": int(intervals["security_id"].nunique()),
        "pass_decision_date_rows": int(len(by_date)),
        "pass_decision_dates": int(by_date["decision_date"].nunique()),
        "pass_symbols": sorted(by_date["symbol"].unique().tolist()),
        "identity_missing_cik": int(summary["identity_missing_cik"]),
        "securities_without_transitions": int(summary["universe_securities"] - summary["securities_with_transitions"]),
        "decision_time_contract": "NYSE sessions; cutoff=16:00 America/New_York; evidence accepted_at <= cutoff",
        "note": "Current-universe static-history eligibility/survivorship bias remains an explicit frozen methodology limitation.",
    }
    (OUT / "validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True), encoding="utf-8")
    log(
        f"DONE: status=PASS symbols={validation['pass_symbols']} "
        f"decision_dates={validation['pass_decision_dates']} rows={validation['pass_decision_date_rows']} "
        f"missing_cik={validation['identity_missing_cik']} no_transitions={validation['securities_without_transitions']}"
    )


if __name__ == "__main__":
    main()
