# Theory-Faithful CAN SLIM Candidate Specification v1

Date: 2026-09-12
Status: FROZEN FOR IMPLEMENTATION DESIGN
Upstream authority: `docs/methodology/oneil-theory-fidelity-audit-v1.md` (#26-#31)

## 1. Purpose

Translate the completed O'Neil/IBD Theory Fidelity Audit into an explicit, versioned candidate contract before implementation.

Required order remains:

```text
Theory -> specification -> implementation -> validation -> performance
```

This specification does **not** modify frozen CAN SLIM quantitative v1, FWD1, EXH2, X3, or PORT1. It defines the separate post-v1 theory-faithful path.

## 2. Architectural separation

The theory-faithful path is split into three contracts:

```text
#33 Pattern Recognition Engine
    -> recognizes proper base morphology + landmarks + pivot

#34 Candidate Generator
    -> attaches breakout, volume, C/A, leadership, sponsorship, market states

#35 Candidate Validation
    -> validates morphology/landmarks/candidate semantics before performance research
```

Execution/fill/entry optimization and the detailed sell engine remain outside candidate generation and belong downstream (#36 or a later dedicated risk/sell implementation track).

## 3. No single universal candidate Boolean

The engine must preserve distinct stages rather than collapsing everything into one `PASS/FAIL` field.

Canonical candidate-stage vocabulary:

```text
BASE_RECOGNIZED
PIVOT_DEFINED
PIVOT_CROSSED
BREAKOUT_CONFIRMED
CANSLIM_ELIGIBLE
NOT_ELIGIBLE
NOT_EVALUABLE
```

A record may legitimately reach `PIVOT_CROSSED` while volume confirmation is pending, or have a valid confirmed breakout while institutional/industry evidence remains `NOT_EVALUABLE`.

Simple factual fields may be Boolean. Methodological concepts use explicit state/evidence enums.

## 4. Required data basis

### 4.1 Daily market data

Primary technical source: existing PIT daily OHLCV in R2.

Required at minimum:

```text
security_id
session_date
open
high
low
close
volume
```

The implementation must use only information available through the as-of date being evaluated.

### 4.2 Benchmark data

Required for RS-line and market context:

```text
S&P 500-compatible benchmark daily price series
market-state inputs used by the versioned M implementation
```

SPY may be used as a transparent benchmark proxy when explicitly versioned. Proprietary IBD market-state data must not be fabricated.

### 4.3 Fundamental / institutional data

Use PIT-safe upstream data contracts only:

- quarterly EPS and revenue facts for C evidence;
- annual EPS/earnings history for A evidence;
- historical 13F/institutional state for I evidence where evaluable;
- any future industry classification/ranking only if PIT-compatible and explicitly versioned.

Missing or stale evidence must remain `NOT_EVALUABLE/NOT_IMPLEMENTED`, never coerced to PASS or FAIL.

## 5. Base / morphology contract (#33 input-output boundary)

### 5.1 Recognized pattern types

Core:

```text
CUP_WITH_HANDLE
CUP_WITHOUT_HANDLE
DOUBLE_BOTTOM
FLAT_BASE
```

Additional legitimate structures:

```text
ASCENDING_BASE
BASE_ON_BASE
IPO_BASE   # special-case, only where eligibility/context is known
```

Fallback:

```text
UNCLASSIFIED_BASE
AMBIGUOUS_BASE
```

The detector must not force every consolidation into a named pattern.

### 5.2 Required base fields

```text
base_id
security_id
pattern_type
pattern_confidence_or_evidence_state
base_start_date
base_end_or_breakout_ready_date
base_duration_sessions
base_depth_pct
prior_uptrend_state
fault_flags
```

Pattern-specific landmarks must be persisted, not inferred again downstream.

Examples:

```text
left_peak
cup_low
right_side_high
handle_start
handle_high
handle_low
first_bottom
middle_peak
second_bottom
flat_left_high
ascending_pullback_1..3
parent_base_id        # for base-on-base
```

Exact geometric detector thresholds belong to #33 implementation design and must be derived from this theory contract, not optimized against returns.

## 6. Pivot contract

Canonical rule:

```text
pivot_level = pattern-specific structural resistance
```

Mapping:

| Pattern | Structural pivot |
|---|---|
| CUP_WITH_HANDLE | highest price in valid handle |
| CUP_WITHOUT_HANDLE | prior / left-side high |
| DOUBLE_BOTTOM | middle peak of W |
| FLAT_BASE | base / left-side high |
| ASCENDING_BASE | final / pattern structural resistance |
| BASE_ON_BASE | pivot from second-base morphology |

Required fields:

```text
pivot_level
pivot_landmark_type
pivot_source_date
pivot_definition_version
```

Do not use an arbitrary rolling N-session high as the canonical pivot.

Legacy fixed-dollar buffers above resistance are not part of the current canonical pivot definition.

## 7. Breakout-event contract

A breakout event begins when price passes/clears the proper pattern-specific pivot.

Preserve distinct facts:

```text
breakout_date
pivot_crossed_intraday
first_tradeable_daily_bar_crossed_pivot
open_above_pivot
gap_through_pivot
close_above_pivot
close_position_quality
extension_from_pivot_pct
```

`close_above_pivot` is breakout-quality/hold evidence, not the universal identity of whether the pivot was crossed.

The traditional 5% buy zone is stored as execution/extension state:

```text
within_traditional_buy_zone = 0 <= extension_from_pivot_pct <= 5
extended_above_traditional_buy_zone = extension_from_pivot_pct > 5
```

Being >5% extended does not erase a valid breakout event.

## 8. Breakout-volume contract

Canonical strong-volume confirmation for daily-EOD implementation:

```text
volume_avg_50_prior = mean(volume of prior 50 completed sessions)
volume_ratio = breakout_day_volume / volume_avg_50_prior
strong_volume_confirmed_on_breakout = volume_ratio >= 1.40
```

The breakout session must be excluded from its own 50-session baseline.

Required confirmation states:

```text
CONFIRMED_ON_BREAKOUT
PENDING_CONFIRMATION
CONFIRMED_LATER
UNCONFIRMED
NOT_EVALUABLE
```

Required fields:

```text
volume_ratio
volume_confirmation_state
volume_confirmation_date
```

Initial-day confirmation is preferred. If later confirmation is implemented, chronology must be preserved and the later date must never be backdated to T0.

A low-volume pivot cross may remain a recorded breakout event but is not a textbook fully confirmed breakout.

## 9. Candidate-stage definitions

### 9.1 BASE_RECOGNIZED

Requirements:

```text
recognized valid/eligible O'Neil base morphology
AND required pattern landmarks available
```

`UNCLASSIFIED_BASE` may be retained for research evidence but does not qualify as a named theory-faithful setup.

### 9.2 PIVOT_DEFINED

Requirements:

```text
BASE_RECOGNIZED
AND valid pattern-specific pivot_level derived from stored landmark(s)
```

### 9.3 PIVOT_CROSSED

Requirements:

```text
PIVOT_DEFINED
AND price crosses pivot on the evaluated session
```

No close-above-pivot requirement is imposed merely to acknowledge the crossing event.

### 9.4 BREAKOUT_CONFIRMED

Canonical textbook daily implementation:

```text
PIVOT_CROSSED
AND volume_confirmation_state == CONFIRMED_ON_BREAKOUT
```

If a future version admits `CONFIRMED_LATER` as a full candidate state, that rule and the permitted window must be preregistered before validation and performance testing.

### 9.5 CANSLIM_ELIGIBLE

This is a **composite eligibility state**, not a claim that every CAN SLIM letter has the same Boolean role.

Minimum candidate contract:

```text
BREAKOUT_CONFIRMED
AND C_screen_state == PASS
AND A_screen_state == PASS
AND L_individual_leadership_state in {PASS, STRONG}
AND M_entry_state == ALLOW_NEW_BUYS
```

S and I are preserved as evidence layers rather than forced into an additional universal Boolean gate:

- S breakout-demand confirmation is already represented by breakout volume; broader supply evidence is attached separately.
- I sponsorship evidence is attached separately and may be `POSITIVE/NEUTRAL/NEGATIVE/NOT_EVALUABLE`; lack of a proprietary/full I score must not be silently converted to FAIL.

Industry-group leadership is also separate evidence until a defensible PIT group/ranking contract exists.

## 10. C — Current earnings contract

Role: **primary fundamental screening criterion plus quality/context evidence**.

Required state:

```text
C_screen_state = PASS / FAIL / NOT_EVALUABLE
```

Required evidence fields where available:

```text
quarterly_eps_yoy
quarterly_revenue_yoy
quarterly_eps_acceleration
quarterly_revenue_acceleration
margin_or_quality_evidence
fundamental_available_on
```

### 10.1 Core screening semantics

The theory audit supports approximately 25%+ recent quarterly EPS growth as the normal O'Neil/IBD growth screen. Therefore the candidate spec freezes:

```text
C_core_eps_pass = quarterly_eps_yoy >= 25%
```

Revenue growth is required evidence and strongly preferred confirmation, but **this specification does not require `revenue_yoy >=25%` as a universal hard identity rule** because the theory audit did not establish that exact conjunction as the sole canonical definition of C.

A future stricter variant may require a sales threshold only as a separately versioned hypothesis; it must not be selected from historical return optimization.

If EPS comparison is structurally undefined or data availability is not PIT-safe, use `NOT_EVALUABLE` rather than fabricating a growth rate.

## 11. A — Annual earnings contract

Role: **primary fundamental screening criterion plus consistency/quality evidence**.

Required state:

```text
A_screen_state = PASS / FAIL / NOT_EVALUABLE
```

Required evidence fields:

```text
annual_eps_history
annual_eps_growth_measure
annual_growth_consistency
roe_or_quality_evidence_if_available
annual_fundamental_available_on
```

### 11.1 Core screening semantics

The theory audit supports sustained multi-year annual earnings growth around 25%+ as the normal growth standard. #32 freezes the **conceptual minimum**:

```text
A_core_growth_pass = sustained multi-year annual EPS growth >= approximately 25%
```

However, #32 does **not** freeze the old v1 rule "each of the latest three annual YoY observations must individually be >=25%" as canonical O'Neil identity. That implementation was intentionally stricter than the theory.

The exact reproducible aggregation (e.g. multi-year growth rate plus consistency constraints) must be specified in the #34 fundamental adapter using only theory-supported semantics, before candidate validation and before any performance review. It may not be chosen by maximizing CAGR/PF.

Until that adapter is frozen and evaluable, A must remain explicit `NOT_EVALUABLE` rather than treated as automatic PASS.

## 12. L — Individual leadership contract

Role: **leader screen plus confirmation/divergence evidence**.

Required states/fields:

```text
rs_rating_proxy_percentile
L_individual_leadership_state = PASS / FAIL / NOT_EVALUABLE
rs_line_value
rs_line_slope
rs_line_base_period_high
rs_line_at_base_period_high
rs_line_new_high_before_price
rs_line_bearish_divergence
```

General leader screen:

```text
rs_rating_proxy_percentile >= 80
```

This is a transparent RS proxy screen, not a claim to replicate IBD's proprietary/current 2026 RS formula exactly.

RS line is a separate object, conventionally versus the S&P 500. Prefer a line at/near its base-period high; preserve a new RS-line high before price breakout as especially strong evidence and a falling line near price highs as bearish-divergence evidence.

The first theory-faithful candidate version may use `RS >=80` as the minimum individual-L eligibility screen while attaching RS-line evidence separately. Any rule that turns RS-line evidence into an additional hard gate must be explicitly versioned before #35 and must not be selected from performance.

## 13. Industry leadership contract

Role: **context/evidence**, separate from individual-stock RS.

Fields:

```text
industry_classification_state
industry_group_id
industry_group_strength
stock_rank_within_group
industry_evidence_state = POSITIVE / NEUTRAL / NEGATIVE / NOT_EVALUABLE / NOT_IMPLEMENTED
```

Do not fabricate IBD's proprietary industry-group ranking from incompatible taxonomies. Until a PIT-compatible group/ranking history is available, industry evidence may remain `NOT_IMPLEMENTED` without invalidating otherwise evaluable core candidates.

## 14. S — Supply / demand contract

Role: **demand confirmation/evidence plus supply descriptors**.

The canonical candidate-level demand confirmation is the breakout-volume contract in section 8.

Additional evidence fields where defensibly available:

```text
shares_outstanding
float
buyback_state
accumulation_distribution_evidence
supply_evidence_state
```

Do not invent a hard shares/float cutoff without a theory-supported, versioned rule and PIT-safe data.

## 15. I — Institutional sponsorship contract

Role: **confirmation/quality evidence and trend descriptor**, not an automatic universal hard gate.

Required state:

```text
I_evidence_state = POSITIVE / NEUTRAL / NEGATIVE / NOT_EVALUABLE / NOT_IMPLEMENTED
```

Evidence may include:

```text
fund_count_latest
fund_count_prior
fund_count_trend
quality_of_sponsors_if_defensible
ownership_concentration_if_defensible
institutional_available_on
```

The existing manager-count delta is a transparent narrow proxy for sponsorship trend; it must not be mislabeled as the whole meaning of I.

A negative or unavailable I state must be preserved for analysis. #32 does not promote a hard `I must PASS` gate.

## 16. M — Market direction contract

Role: **market context + entry timing gate + risk throttle**.

Required state:

```text
M_market_state = CONFIRMED_UPTREND / UPTREND_UNDER_PRESSURE / CORRECTION / UNKNOWN
M_entry_state = ALLOW_NEW_BUYS / CAUTION / BLOCK_NEW_BUYS / NOT_EVALUABLE
```

Canonical semantics:

```text
CONFIRMED_UPTREND -> ALLOW_NEW_BUYS
CORRECTION        -> BLOCK_NEW_BUYS
```

`UPTREND_UNDER_PRESSURE` must remain distinguishable from both states and may imply reduced exposure/caution rather than a fabricated universal binary equivalent. The exact market-state algorithm is a versioned transparent proxy unless proprietary IBD states are actually available.

Candidate eligibility requires `M_entry_state == ALLOW_NEW_BUYS` for the initial theory-faithful implementation.

## 17. N contract

`N` contains more than chart breakout: new products/services, management, conditions and/or new price highs. The current project has a defensible technical `N_price` path but no PIT catalyst dataset that can fully represent non-price `N`.

Preserve:

```text
N_price_state
N_catalyst_state = POSITIVE / NEGATIVE / NOT_EVALUABLE / NOT_IMPLEMENTED
```

A theory-faithful **price-pattern candidate** may proceed with `N_catalyst_state = NOT_IMPLEMENTED`, but must not be described as having fully implemented every semantic of N.

## 18. Evidence-state vocabulary

Use explicit states rather than null-driven inference:

```text
PASS
FAIL
STRONG
POSITIVE
NEUTRAL
NEGATIVE
PENDING_CONFIRMATION
CONFIRMED_ON_BREAKOUT
CONFIRMED_LATER
UNCONFIRMED
ALLOW_NEW_BUYS
CAUTION
BLOCK_NEW_BUYS
NOT_EVALUABLE
NOT_IMPLEMENTED
AMBIGUOUS
```

Every non-evaluable state should carry a reason code where practical.

## 19. Candidate record minimum schema

Identity / chronology:

```text
security_id
symbol_asof
asof_date
base_id
pattern_type
base_start_date
breakout_date
```

Pattern/pivot:

```text
pattern_evidence_state
fault_flags
pivot_level
pivot_landmark_type
pivot_source_date
```

Breakout:

```text
pivot_crossed_intraday
open_above_pivot
gap_through_pivot
close_above_pivot
close_position_quality
extension_from_pivot_pct
within_traditional_buy_zone
```

Volume:

```text
volume_avg_50_prior
volume_ratio
volume_confirmation_state
volume_confirmation_date
```

CAN SLIM evidence:

```text
C_screen_state
A_screen_state
N_price_state
N_catalyst_state
S_evidence_state
L_individual_leadership_state
rs_rating_proxy_percentile
rs_line_* fields
industry_evidence_state
I_evidence_state
M_market_state
M_entry_state
```

Composite stage:

```text
candidate_stage
eligibility_reason_codes
spec_version
pattern_engine_version
candidate_generator_version
```

## 20. Fault / disqualification handling

Do not erase evidence. A detected structure may be retained with fault flags even if it is not eligible as a proper base.

Examples:

```text
V_SHAPED_CUP
WIDE_AND_LOOSE
HANDLE_TOO_LOW
HANDLE_TOO_DEEP
INSUFFICIENT_PRIOR_UPTREND
DOUBLE_BOTTOM_STRUCTURE_INVALID
FLAT_BASE_TOO_DEEP
PATTERN_AMBIGUOUS
PIVOT_UNDEFINED
MARKET_CORRECTION
C_SCREEN_FAIL
A_SCREEN_FAIL
L_SCREEN_FAIL
VOLUME_UNCONFIRMED
```

Fault categories must distinguish:

```text
STRUCTURAL_INVALIDITY
QUALITY_WARNING
MISSING_EVIDENCE
TIMING_DISQUALIFIER
```

Do not collapse a quality warning into structural invalidity unless theory explicitly supports that treatment.

## 21. Candidate eligibility decision graph

Canonical first implementation:

```text
valid named proper base
        |
pattern-specific pivot defined
        |
pivot crossed
        |
strong breakout volume confirmed on breakout day
        |
C core screen PASS
        |
A core screen PASS
        |
individual L screen PASS (RS proxy >=80)
        |
M permits new buys
        |
CANSLIM_ELIGIBLE
```

Attach but do not universally hard-gate in v1 of the theory-faithful path:

```text
RS-line confirmation/divergence
industry-group leadership
broader S supply descriptors
I sponsorship state
N non-price catalyst state
close-above-pivot quality
5% execution-zone state
```

This separation follows the completed #30 role audit. It is not permission to ignore these evidence layers; they must be persisted for #35 validation and later research.

## 22. What #32 explicitly forbids

- No arbitrary rolling-high pivot in place of a pattern-specific landmark.
- No claim that every 35-session consolidation is an O'Neil base.
- No forcing every consolidation into CWH/DB/Flat/etc.
- No requirement that close > pivot merely to acknowledge that the pivot was crossed.
- No use of the 5% buy zone to define whether a breakout exists.
- No backdating of later volume confirmation.
- No claim that `RS>=80` alone completely implements L.
- No fabricated proprietary industry, Sponsorship, Accumulation/Distribution or Market ratings.
- No coercing `NOT_EVALUABLE` into PASS or FAIL.
- No optimization of morphology/fundamental/leadership/market thresholds against historical CAGR/PF before #35 semantic validation.
- No retrofit into frozen v1/FWD1/EXH2.

## 23. Validation order for #35

Before performance testing, validate in this order:

1. morphology label agreement against human-labelled fixtures;
2. landmark accuracy;
3. pivot accuracy by pattern type;
4. breakout-date accuracy;
5. volume-confirmation chronology;
6. PIT correctness of C/A/I/M/RS inputs;
7. state-machine consistency and reason codes;
8. candidate reproducibility across repeated runs;
9. only after these pass: candidate distribution and later performance research.

Primary metrics for pattern/candidate validity should include precision/recall or confusion matrices, landmark/pivot error, chronology errors and PIT violations—not CAGR as the first acceptance criterion.

## 24. Sell/risk contract boundary

#31 is preserved as downstream theory authority, but detailed sell rules do not determine whether a pre-entry candidate exists.

Candidate records should retain enough identity to link to later execution/risk records. Downstream implementation may use:

- maximum-loss discipline referenced to actual fill;
- failed-breakout/technical-deterioration states;
- 20%-25% normal profit zone;
- eight-week exceptional-winner hold rule;
- round-trip state;
- climax/exhaustion evidence;
- market-level exposure reduction.

These are not to be silently embedded in #33 pattern detection or #34 pre-entry candidate generation.

## 25. Freeze decision

This document freezes **Theory-Faithful Candidate Specification v1** for implementation design.

Any material change to:

- stage semantics;
- hard eligibility contract;
- pattern/pivot meaning;
- breakout-volume confirmation;
- C/A/L/M eligibility roles;
- evidence-vs-gate classification;

requires a new version and decision record before performance testing.

## 26. Next action

Proceed to **#33 — O'Neil Pattern Recognition Engine**. Build the morphology/landmark/pivot subsystem from daily R2 OHLCV against this specification. Do not yet build the final #34 candidate generator and do not use trading returns to tune detector definitions.
