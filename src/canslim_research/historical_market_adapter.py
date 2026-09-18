from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from canslim_research.market_state_consumer import entry_permission_for_state
from canslim_research.market_state_v1 import IndexBar, MarketState, classify_market

VERSION = "fa-first-historical-m-adapter-v0.1"


@dataclass(frozen=True, slots=True)
class HistoricalMarketDecision:
    asof_date: str
    market_state: str
    M_entry_state: str
    classifier_reason: str
    entry_reason: str
    provenance: str = "HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY"
    version: str = VERSION


def replay_historical_market(
    *,
    index_series: dict[str, Sequence[IndexBar]],
) -> tuple[HistoricalMarketDecision, ...]:
    """Replay the reproducible index-only subset of frozen #46/#50 causally.

    No #51 leadership/weakening booleans or correction-reset evidence are
    fabricated. Each date is classified only from bars available through that
    date, starting from NOT_EVALUABLE.
    """
    if not index_series:
        return ()

    dates_by_index = {
        index_id: [bar.date for bar in bars]
        for index_id, bars in index_series.items()
    }
    common_dates = sorted(set.intersection(*(set(v) for v in dates_by_index.values())))
    prior_state = MarketState.NOT_EVALUABLE.value
    out: list[HistoricalMarketDecision] = []

    for asof_date in common_dates:
        causal = {
            index_id: tuple(bar for bar in bars if bar.date <= asof_date)
            for index_id, bars in index_series.items()
        }
        result = classify_market(
            index_series=causal,
            prior_state=prior_state,
            leadership_confirming=None,
            weakening_confirmed=None,
            correction_reset=False,
        )
        if result.asof_date != asof_date:
            raise ValueError("historical M replay produced non-exact asof date")
        entry_state, entry_reason = entry_permission_for_state(result.state)
        out.append(HistoricalMarketDecision(
            asof_date=asof_date,
            market_state=result.state,
            M_entry_state=entry_state,
            classifier_reason=result.reason,
            entry_reason=entry_reason,
        ))
        prior_state = result.state

    return tuple(out)


def decision_on(
    decisions: Sequence[HistoricalMarketDecision],
    asof_date: str,
) -> HistoricalMarketDecision:
    matches = [row for row in decisions if row.asof_date == asof_date]
    if len(matches) != 1:
        raise ValueError(f"historical M requires exactly one decision for {asof_date}")
    return matches[0]
