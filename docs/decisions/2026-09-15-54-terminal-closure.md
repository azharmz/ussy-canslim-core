# #54 Terminal Closure — PIT Leader-Cohort / Institutional-Demand Evidence Study

Date: 2026-09-15

Status: **COMPLETE / FROZEN WITH EXPLICIT PRODUCTION DEBT**

## Purpose

This decision closes #54. The project will not extend #54 merely to reproduce proprietary IBD infrastructure or to force a deterministic market-leadership boolean where authoritative evidence does not supply a reproducible aggregation rule.

## Authoritative theory boundary

William J. O'Neil's market-direction framework distinguishes index price/volume evidence from market-leading-stock evidence. For an up-trending market, the leader evidence includes new market-leading stocks being among the first stocks to move to new price highs while the market rises on strong volume, together with institutional money moving into those new leaders. For a down-trending market, the framework includes a majority of new leaders ceasing to make new highs and institutional selling of new leaders.

This supports observing leading-stock price/new-high/volume behavior as market evidence. It does **not** provide a universal reproducible numeric rule such as a required count, percentage, percentile, or fixed aggregation threshold for converting an arbitrary project cohort into `leadership_confirming=True` or `weakening_confirmed=True`.

Modern IBD educational practice likewise treats a follow-through day as a beginning rather than sufficient proof of a durable uptrend and continues to watch leading stocks, breakouts, relative strength and exposure progression.

## Evidence completed inside #54

### 1. Frozen semantic evidence-study boundary

`54-pit-leader-cohort-institutional-demand-study-v1` established admissible PIT evidence families and a fail-closed research boundary. It does not authorize future-return selection or performance-driven threshold tuning.

### 2. Historical Cycle 1 retained as research history

`54-cycle1-candidate-leader-selector-v1` and its provider/data-readiness audits remain frozen research evidence. The attempted broad-market percentile architecture is **DEFERRED / NON-BLOCKING** for CAN SLIM v1.

The project will not build a ~7,500-security OHLCV panel merely to approximate the proprietary IBD RS Rating. The Tiingo/Yahoo audit inconsistency is preserved as historical source-audit debt and is not a #54 closure blocker because that architecture is no longer a production prerequisite.

### 3. Minimum reproducible RS-line evidence completed

Contract `54-rs-line-evidence-v1` provides PIT stock-versus-canonical-`SP500` evidence:

- RS-line value = stock price / canonical S&P 500 price;
- prior-session direction: `RISING`, `FALLING`, or `FLAT`;
- at-input-window-high evidence;
- new-input-window-high evidence;
- explicit source provenance and as-of checks;
- fail-closed `NOT_EVALUABLE` states.

It explicitly does not claim equivalence to the proprietary IBD RS Rating and does not emit #51 production booleans.

### 4. Stock-level institutional sponsorship source is already available

The canonical SEC 13F production path in `azharmz/ussy-fundamentals` already provides PIT-audited stock-level institutional sponsorship evidence for deterministic U.S.-ISIN identities and publishes canonical R2 sponsorship snapshots.

This closes the stock-level CAN SLIM `I` data-source question. SEC 13F is quarterly/delayed ownership evidence; it is **not** treated as real-time institutional buying/selling, an IBD Accumulation/Distribution Rating, or a market-state leadership boolean.

## Market-level institutional-demand conclusion

The authoritative framework supports interpreting price/volume behavior of leading stocks as observable evidence associated with institutional demand/selling. Existing project evidence can therefore preserve and expose relevant observations such as:

- leading/candidate stocks moving toward or into new highs;
- breakouts from proper bases;
- strong volume accompanying upward price moves;
- RS-line strengthening/new-high evidence;
- leader deterioration/breakdown evidence where already frozen elsewhere.

However, the project has not found an authoritative, reproducible aggregation rule that says how many such observations, or what percentage of a project-defined cohort, is sufficient to assert the market-level booleans required by frozen #51.

Creating a rule such as `N leaders`, `X% of candidates`, or a new volume/RS threshold solely to make the boolean evaluable would violate the project's theory-fidelity governance.

## Frozen #51/#46 consequence

Therefore #54 closes without manufacturing a production boolean:

- `leadership_confirming`: remains `None` / `NOT_EVALUABLE` when no separately authorized evidence source supplies the frozen #51 requirement;
- `weakening_confirmed`: remains `None` / `NOT_EVALUABLE` under the same condition;
- #50 must continue to preserve those missing values rather than promote `FOLLOW_THROUGH_CONFIRMED` to `UPTREND_HEALTHY` or `UPTREND_WEAKENING` by assumption;
- frozen #46 and #45 semantics are unchanged.

This is an explicit **production evidence debt**, not a failed study.

## Closure decisions

1. **#54 research objective: COMPLETE.** The evidence boundary, reproducible RS-line sidecar, stock-level institutional sponsorship source boundary, and unresolved market-level aggregation boundary are now known.
2. **Full-market OHLCV reconstruction: DEFERRED / NON-BLOCKING.** Do not resume without explicit governance reopening and a concrete production need.
3. **Project approximation of IBD RS Rating: NOT REQUIRED.** Do not represent project relative-strength calculations as IBD RS Rating.
4. **Sector ETF substitution: NOT REQUIRED / NOT AUTHORIZED as CAN SLIM leadership proxy.**
5. **SEC 13F: APPROVED for stock-level sponsorship `I`; NOT APPROVED as daily market-level institutional-flow confirmation.**
6. **Market-level leader confirmation: EVIDENCE OBSERVABLE, DETERMINISTIC AGGREGATION NOT AUTHORIZED.** Preserve as `NOT_EVALUABLE` rather than inventing thresholds.
7. **No further #54 research is required for CAN SLIM v1 closure.** Reopen only if genuinely new authoritative evidence provides a reproducible aggregation rule or an approved production source directly satisfies #51.
8. **No automatic #55.** The next project phase is end-to-end CAN SLIM v1 integration/closure, not another theory-expansion workstream.

## Terminal verdict

**#54 — COMPLETE / FROZEN WITH EXPLICIT PRODUCTION DEBT**

**MINIMUM THEORY-FAITHFUL LEADERSHIP EVIDENCE PATH: COMPLETE**

**MARKET-LEVEL `leadership_confirming` / `weakening_confirmed`: NOT_EVALUABLE WITHOUT NEW AUTHORIZED EVIDENCE**

**FULL-MARKET OHLCV / PROPRIETARY-RS REPLICATION: DEFERRED / NON-BLOCKING**

**NEXT PHASE: END-TO-END CAN SLIM v1 INTEGRATION AUDIT → PRODUCTION BASELINE FREEZE**
