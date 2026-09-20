# Historical Golden-Case Reconstruction v1

Status: ACTIVE / VALIDATION ONLY / NEVER PRODUCTION

This workstream is isolated from CAN SLIM v2 production. It must not modify production READY pointers, candidate publication, frozen O'Neil Pattern Engine semantics, or live execution/lifecycle state.

## Purpose

Replay documented historical O'Neil/CAN SLIM examples using historical data available at the relevant date, then compare the frozen engine's observed result with a source-backed reference oracle. This is not a backtest.

## Non-negotiable boundaries

- Reconstruction means historical/as-of data, not current 2026 READY data.
- C/A may be accepted as REFERENCE_PASS when an authoritative example explicitly documents the relevant fundamental evidence.
- Expected pattern/pivot/breakout facts are oracle fields only; never detector inputs.
- Canonical frozen O'Neil Pattern Engine: azharmz/ussy-oneil-patterns at c433cc1e35a5aa32a46f732cd8c5545935e36e40; schema oneil-pattern-output-v2; engine 33-core-p8-frozen-v1.
- Mismatch is validation evidence, not permission to tune morphology.
- Artifacts: HISTORICAL_RECONSTRUCTION_FIXTURE / NEVER_PRODUCTION.

## Two entry layers

Original O'Neil/source-faithful: assess the breakout-day T buy opportunity from proper base, pivot/buy point, price-volume action and buy zone. Do not impose USSY T+1 Open.

USSY adaptation: after completed T daily data is known, evaluate the frozen causal T+1 Open contract. A valid original breakout may coexist with USSY MISSED_EXTENDED; classify that as an execution-adaptation gap.

Daily OHLCV cannot reconstruct exact intraday ordering/cumulative volume at crossing; label this limitation explicitly.

## Methodology classification

Tag every reconstructed field/rule: ORIGINAL, OPERATIONALIZATION, DATA_ADAPTATION, PROXY, ENGINEERING, or UNAVAILABLE. USSY cross-sectional RS is a proxy/data adaptation, not the proprietary IBD RS Rating.

## Golden Case 001 — LRCX 2020 — ORACLE VERIFIED

Authoritative source:
- Investor's Business Daily, "How To Buy Stocks: Lam Research's Cup With Handle Launched A 75% Advance"
- https://www.investors.com/how-to-invest/investors-corner/how-to-buy-stocks-lam-research-cup-with-handle-launched-75-percent-advance/

Source facts verified directly for the reconstruction oracle:
- expected family: CUP_WITH_HANDLE
- reported pivot/buy point: 381.96
- reported breakout date: 2020-11-04
- base duration: 13 weeks
- base depth: 24%
- handle duration: two weeks
- prior advance: more than 113%
- quarterly earnings growth: 78%
- sales/revenue growth: 47%
- the later ~75% advance is context only and MUST NOT be supplied to signal-time reconstruction

Oracle state: FROZEN_SOURCE_ORACLE_V1.
Do not silently add facts not explicitly supported by the source. Subsequent return is not a validation target.


## LRCX replay finding — frozen evidence

Replay lineage:
- reconstruction branch: validation/historical-golden-reconstruction-v1
- frozen pattern engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40
- price basis: DATA_ADAPTATION restoring the contemporaneous pre-2024 10-for-1 split basis
- detector cutoff: 2020-11-04; T+1 bar is excluded from detector input

Expected vs observed morphology:
- Oracle CUP_WITH_HANDLE structure is present in the frozen landmark vocabulary: 2020-08-03 high 387.70 -> 2020-09-11 low 292.28 -> 2020-10-14 right rim 381.96 -> 2020-10-28 handle low 333.31.
- Exact cup body is CUP_RECOGNIZED with no cup faults; depth 24.6118%, 52 sessions, right-rim/left-rim ratio 98.52%.
- Open-right-edge handle is causally observable by 2020-11-04, but frozen handle semantics return HANDLE_REJECTED solely for BELOW_CUP_MIDPOINT. Its depth is 12.737%.
- The implied open-right-edge pivot is 381.95999, an exact practical match to the 381.96 source oracle.
- Therefore the final CWH mismatch is localized to handle morphology semantics, not candidate OHLCV, cup landmarks, cup segmentation, cup-body recognition, or pivot reconstruction.
- Classification: MORPHOLOGY_FIDELITY_GAP / HANDLE_GATE_BELOW_CUP_MIDPOINT. No frozen-engine tuning is authorized by this finding.

Breakout-day observation (ORIGINAL layer):
- 2020-11-04 OHLC on contemporaneous basis: O 373.89 / H 383.20 / L 367.28 / C 380.34.
- The daily high crossed the 381.96 pivot, while the close finished 0.424% below pivot.
- Daily-bar evidence therefore supports BREAKOUT_DAY_CONFIRMED_FROM_DAILY_BAR for a price crossing, with INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.
- Observed volume was 1,528,000 versus prior-50-session mean about 1,760,441 (-13.20%). This raw daily comparison does not independently reproduce a strong +40% volume-confirmation condition. Preserve the distinction between the official source oracle and this reconstructed provider/bar calculation.

USSY T+1 observation (OPERATIONALIZATION layer):
- 2020-11-05 open: 390.00.
- T+1 open was +2.105% versus the 381.96 pivot and +2.540% versus the breakout-day close.
- 390.00 remained inside the original 5% buy zone upper bound of 401.058.
- This is an execution observation only. It does not override the frozen CAN SLIM candidate eligibility result or retroactively convert the rejected frozen handle into a production candidate.

Three-layer disposition:
| Layer | Reference / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | CWH, 24% depth, pivot 381.96 | cup/pivot reconstructed; handle rejected BELOW_CUP_MIDPOINT | FIDELITY GAP |
| Original breakout day | breakout 2020-11-04 | high crossed pivot; close below; reconstructed volume not elevated vs prior-50 mean | DAILY-BAR PARTIAL / SOURCE ORACLE PRESERVED |
| USSY execution adaptation | evaluate only after finalized T | T+1 open 390.00, within 5% buy zone | EXECUTION OBSERVATION; NO RETROACTIVE FILL |



## CWH numeric audit 001 — LRCX 2020

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

This audit separates numeric agreement from the final categorical detector state.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITH_HANDLE | cup recognized; final handle rejected | categorical mismatch localized to handle |
| Pivot | 381.96 | 381.95999 | -0.00001 (~0.000003%); practical exact match |
| Base depth | 24.0% | 24.6118% | +0.6118 percentage point |
| Base duration | 13 weeks | 52 trading sessions | approximately 10.4 trading weeks; calendar/source counting convention not directly identical |
| Handle duration | 2 weeks | open-right handle observable through breakout | source duration supported; engine rejection is not a missing-handle-data problem |
| Cup left rim | source summary does not publish exact date/price | 2020-08-03 / 387.70 | engine-only reconstruction; not scored against absent oracle |
| Cup low | source summary does not publish exact price | 2020-09-11 / 292.28 | engine-only reconstruction; not scored |
| Right rim / pivot area | pivot 381.96 | 2020-10-14 / 381.96 | exact practical price agreement |
| Handle low | source summary does not publish exact price | 2020-10-28 / 333.31 | engine-only reconstruction; not scored |
| Handle depth | source summary does not publish exact percentage | 12.737% | engine-only reconstruction; not scored |
| Final handle gate | source calls structure valid CWH | HANDLE_REJECTED: BELOW_CUP_MIDPOINT | **true source-fidelity gap** |

Numeric adjudication: **LRCX is not a broad morphology failure.** Pivot reconstruction is effectively exact and base depth is within 0.612 percentage point of the source's rounded 24%. The cup body is recognized with no cup faults. The meaningful disagreement is the frozen handle semantic gate BELOW_CUP_MIDPOINT. Base-duration figures are retained but not treated as a clean numeric mismatch because the source reports weeks while the engine reports trading sessions and their boundary/counting conventions are not guaranteed identical.

Audit conclusion: **CUP_GEOMETRY_MATCH / PIVOT_MATCH / HANDLE_SEMANTICS_GAP**. This supersedes any shorthand interpretation that LRCX was an across-the-board CWH miss.

## Historical L comparison-universe decision v1

Status: FROZEN FOR GOLDEN RECONSTRUCTION / NOT PRODUCTION.

The production L gate is a cross-sectional RS proxy percentile and therefore cannot be reconstructed from LRCX alone. A 2026 READY/Musaffa membership must not be projected backward to 2020.

Source audit found no existing PIT historical US-wide membership asset in ussy-data or this repository. The research-quality reference is a survivorship-aware security master such as CRSP, but no licensed CRSP dataset is available in this workstream. Free/current exchange lists are not acceptable substitutes for an exact 2020-11-04 broad-universe membership.

For Golden Case 001, freeze:
- L_individual_state: NOT_EVALUABLE
- reason: HISTORICAL_COMPARISON_UNIVERSE_NOT_AVAILABLE
- rs_proxy_percentile: null
- proprietary historical IBD RS Rating, if later sourced, is REFERENCE ORACLE only and must not be substituted for the USSY cross-sectional proxy.
- current/future survivor membership must not be back-projected.

This is a data-availability limitation, not an L FAIL and not permission to invent a smaller comparison set. The case remains useful because frozen morphology and breakout-volume gates already determine v2 ineligibility independently of L.

A future reusable historical-L fixture may replace NOT_EVALUABLE only when it pins a defensible PIT membership source, identity rules, decision date, constituent manifest checksum, OHLCV lineage, RS formula/version and producer identity. Such a fixture is isolated historical reconstruction data and must never advance production READY pointers.


## Golden Case 001 — consolidated CAN SLIM v2 eligibility

Decision date: 2020-11-04. This section evaluates the frozen production-v2 contract without changing any upstream evidence.

| Frozen v2 gate | Reconstructed state | Eligibility effect |
|---|---|---|
| Watchlist C/A | NOT EVALUABLE AS QUALIFIED: C quarterly reference is documented, but required A annual evidence is not documented | WATCHLIST_NOT_QUALIFIED |
| Pattern | expected source CWH; frozen engine does not recognize the source-faithful handle (BELOW_CUP_MIDPOINT) | PATTERN_NOT_RECOGNIZED |
| Pivot | defined at 381.95999 and daily high crossed it | passes pivot-defined / pivot-crossed gates |
| Breakout volume | reconstructed daily volume does not meet the frozen >=1.40 prior-50-volume confirmation rule | BREAKOUT_VOLUME_UNCONFIRMED |
| L | NOT_EVALUABLE because no defensible PIT historical comparison universe is available | L_NOT_EVALUABLE |
| M | FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS from the frozen historical index-only replay | passes M gate |

Frozen v2 disposition: **NOT_ELIGIBLE**.

Reason set: WATCHLIST_NOT_QUALIFIED; PATTERN_NOT_RECOGNIZED; BREAKOUT_VOLUME_UNCONFIRMED; L_NOT_EVALUABLE.

M is not a blocker. Pivot definition/crossing are not blockers.

This disposition must not be read as a claim that the documented O'Neil trade was invalid. It answers the separate production-adaptation question: the frozen USSY CAN SLIM v2 contract would not have produced an eligible candidate from the reconstructed evidence available here. The principal source-fidelity discrepancy remains the handle morphology gate; the reconstructed breakout-volume rule is an additional production-contract mismatch. Missing A/L evidence remains NOT_EVALUABLE rather than FAIL.

The T+1 open of 390.00 therefore remains an execution observation only: no production fill is authorized because eligibility was false before the execution layer.


## Golden Case 002 — AMD 2019 — MORPHOLOGY/BREAKOUT REPLAY VERIFIED

Decision/breakout date: 2019-11-04.

Frozen source oracle for the replay:
- expected family: CUP_WITHOUT_HANDLE
- reported pivot/buy point: 35.55
- reported breakout date: 2019-11-04
- source-reported cup low: 27.43
- source context reports breakout volume about 67% above average
- quarterly reference evidence is C-layer evidence only; do not infer A annual evidence from it

Replay identity:
- branch: validation/historical-golden-reconstruction-v1
- successful run: 35411908528
- producer commit: 09aeb26b0a49ddb72efe179072ff2cca5d0ae87c
- frozen Pattern Engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- candidate detector cutoff: 2019-11-04; T+1 2019-11-05 is excluded from detector input
- candidate price basis: provider historical basis unchanged; no reconstruction split transform applied

Source-fidelity morphology finding:
- Frozen engine emits a source-faithful OPEN_RIGHT_EDGE_CNH candidate with LEFT_RIM 2019-08-09, CUP_LOW 2019-10-03, pivot_source_date 2019-08-09 and pivot 35.54999924.
- Candidate state: CUP_WITHOUT_HANDLE_RECOGNIZED / RECOGNIZED.
- Candidate depth: 22.841066%; detector_faults: [].
- Observed trough price is 27.43 and pivot is an exact practical match to the 35.55 oracle.
- Therefore AMD provides a positive source-fidelity case for frozen CUP_WITHOUT_HANDLE morphology and pivot reconstruction. Other emitted historical candidates are not substituted for the source-faithful candidate.

Breakout-day observation (ORIGINAL layer):
- 2019-11-04 OHLC: O 35.189999 / H 36.450001 / L 34.759998 / C 36.290001.
- Both daily high and close are above the 35.55 pivot; close is +2.0816% versus pivot and remains inside the original 5% buy zone upper bound 37.3275.
- Volume: 83,343,800 versus frozen prior-50 completed-session mean 49,447,172, or +68.5512% / ratio 1.6855.
- This exceeds the frozen USSY >=1.40 breakout-volume confirmation threshold and closely corroborates the source-reported approximately +67% volume expansion.
- Daily bars support BREAKOUT_DAY_CONFIRMED_FROM_DAILY_BAR. Exact intraday crossing/cumulative-volume sequence remains INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

Historical M (DATA_ADAPTATION layer):
- market_state: FOLLOW_THROUGH_CONFIRMED.
- M_entry_state: ALLOW_NEW_BUYS.
- reason: NO_NEW_STATE_CHANGING_EVIDENCE / M45_NEW_ENTRIES_ALLOWED.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY, adapter fa-first-historical-m-adapter-v0.1.
- The index-only limitation remains explicit; leadership/weakening/correction-reset facts are not fabricated.

USSY T+1 observation (OPERATIONALIZATION layer):
- 2019-11-05 open: 36.560001.
- T+1 open is +2.8411% versus pivot and +0.7440% versus breakout-day close.
- T+1 open remains inside the original 5% buy zone.
- Therefore this case does not exhibit a T+1 extended-price adaptation gap. This is still an execution observation, not an automatic production fill.

Three-layer disposition:
| Layer | Reference / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | CUP_WITHOUT_HANDLE, pivot 35.55 | source-faithful candidate RECOGNIZED; pivot 35.549999; trough 27.43; no faults | SOURCE-FIDELITY MATCH |
| Original breakout day | breakout 2019-11-04 with strong volume | high/close above pivot; volume ratio 1.6855; close inside 5% zone | DAILY-BAR MATCH; INTRADAY TIMING UNAVAILABLE |
| USSY execution adaptation | evaluate after finalized T | T+1 open 36.56, +2.84% vs pivot, inside 5% zone | NO EXTENDED-PRICE ADAPTATION GAP |

Historical L follows the frozen Golden Case 001 governance: no defensible PIT broad comparison-universe asset is available in this workstream. Freeze L_individual_state=NOT_EVALUABLE / HISTORICAL_COMPARISON_UNIVERSE_NOT_AVAILABLE rather than back-projecting a current universe.

### Golden Case 002 — current CAN SLIM v2 reconstruction boundary

The morphology, pivot, breakout-volume and M hard gates are positively reconstructed for AMD. Historical L remains NOT_EVALUABLE. C quarterly reference evidence may be recorded as reference evidence, but A annual evidence must remain NOT_DOCUMENTED unless an authoritative source is frozen. Therefore do not label the complete frozen-v2 candidate ELIGIBLE yet; missing watchlist C/A qualification and L remain evidence-availability blockers, not negative morphology/breakout findings.

The important validation result is narrower and stronger: unlike LRCX, AMD reproduces the documented O'Neil pattern family, pivot and breakout-volume behavior under the frozen engine without tuning.


## Golden Case 003 — IPHI 2019 — DOUBLE-BOTTOM FIDELITY/LIFECYCLE REPLAY VERIFIED

Decision/breakout date: 2019-10-15.

Frozen source oracle:
- expected family: DOUBLE_BOTTOM
- reported pivot/buy point: 64.85
- reported breakout date: 2019-10-15
- source context: third-stage double-bottom; breakout subsequently failed and the historical example invokes the O'Neil loss-cut discipline

Replay identity:
- successful lifecycle run: 35413742554
- producer commit: 8b88fe1f0da94c1b9a434da62b19a92f2700f7ff
- frozen Pattern Engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- candidate provider: Tiingo fallback because Yahoo/yfinance no longer returned the delisted symbol
- detector cutoff: 2019-10-15; post-T bars are excluded from morphology and revealed only for lifecycle
- provider historical basis unchanged; no corporate-action transform applied

Source-fidelity morphology finding:
- The closest frozen-engine DOUBLE_BOTTOM uses LEFT_HIGH 2019-08-08, TROUGH_1 2019-08-28, MIDDLE_PEAK 2019-09-20 and TROUGH_2 2019-10-02.
- Engine pivot is 64.75 versus source oracle 64.85, a 0.10 absolute difference.
- Candidate state is DOUBLE_BOTTOM_AMBIGUOUS / AMBIGUOUS with fault NO_SECOND_TROUGH_UNDERCUT.
- Therefore the engine reconstructs the intended structural neighborhood and near-matching pivot but does not recognize the documented double bottom under its frozen second-trough-undercut gate.
- Classification: MORPHOLOGY_FIDELITY_GAP / NO_SECOND_TROUGH_UNDERCUT. No detector threshold is changed.

Breakout-day observation (ORIGINAL layer):
- 2019-10-15 OHLC: O 63.41 / H 66.20 / L 63.41 / C 64.99.
- Daily high and close are above oracle pivot 64.85; close is +0.2159% versus pivot and inside the 5% buy zone.
- Volume 983,203 versus prior-50 completed-session mean 857,768.86, or +14.6233% / ratio 1.1462.
- This does not meet the frozen USSY >=1.40 breakout-volume confirmation threshold.
- Daily bars establish price crossing but not exact intraday crossing/cumulative-volume timing.

Historical M:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS on 2019-10-15.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY.
- M is not a blocker in this reconstruction.

USSY T+1 observation:
- 2019-10-16 open: 65.06.
- +0.3238% versus oracle pivot and +0.1077% versus breakout close.
- Open remains inside the original 5% buy zone.
- Therefore there is no T+1 extended-price adaptation gap. This remains an execution observation, not a production fill.

Original O'Neil loss-cut lifecycle observation:
- Reference basis is the oracle pivot 64.85; 7% level = 60.3105 and 8% level = 59.662.
- On 2019-10-22 the daily low reached 59.50, breaching both the -7% and -8% reference levels; close 59.81 was below -7% but still above the -8% close threshold.
- On 2019-10-23 close reached 59.09, the first reconstructed close below the -8% reference level.
- Exact intraday stop timing is not reconstructed from daily bars.
- This causally corroborates the documented failed-breakout/loss-cut character of the golden case without inventing an intraday fill.

Three-layer disposition:

| Layer | Reference / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | DOUBLE_BOTTOM, pivot 64.85 | structural neighborhood reproduced; pivot 64.75; AMBIGUOUS because NO_SECOND_TROUGH_UNDERCUT | MORPHOLOGY_FIDELITY_GAP |
| Original breakout/lifecycle | breakout 2019-10-15 followed by failed trade/loss cut | price crossed pivot; later low breaches 8% on Oct 22 and close breaches 8% on Oct 23 | DAILY-BAR LIFECYCLE CORROBORATION |
| USSY adaptation | evaluate at finalized T then T+1 Open | T+1 65.06, inside 5% zone; morphology and volume hard gates remain unsatisfied | NO EXTENDED-PRICE GAP; NO PRODUCTION FILL |

Historical L remains NOT_EVALUABLE under the same frozen governance as Cases 001-002. The frozen v2 contract also lacks pattern recognition and >=1.40 breakout-volume confirmation here, so this case must not be converted into an eligible production trade merely because the historical source labels it a valid O'Neil setup.


## Golden Case 004 — AAPL 2019 — FLAT-BASE FIDELITY REPLAY VERIFIED

Decision/breakout date: 2019-09-11 (source breakout week ending 2019-09-13).

Frozen source oracle:
- expected family: FLAT_BASE
- pivot/buy point: 221.37
- breakout observation date used for daily replay: 2019-09-11

Replay identity:
- successful run: 35417737472
- producer commit: 0e5b80786fcee7d50138647ab65e8b2576023ee8
- frozen Pattern Engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- Yahoo pre-2020 AAPL bars were restored to contemporaneous 2019 basis for the later 4-for-1 split: OHLC/adj_close x4, volume /4
- detector cutoff remains 2019-09-11

Source-fidelity morphology finding:
- Frozen landmarks independently recover the exact oracle left high: 2019-07-31 at 221.369995.
- Base low is 2019-08-05 at 192.580002, giving depth 13.0054%.
- Frozen FLAT_BASE candidate therefore carries pivot 221.369995, effectively exact to oracle 221.37.
- Confirmed-structure candidate is REJECTED with TOO_SHORT and WIDE_LOOSE; open-right-edge candidate through 2019-09-11 is AMBIGUOUS with WIDE_LOOSE.
- Classification: MORPHOLOGY_FIDELITY_GAP / FLAT_BASE_GEOMETRY_GATE. No detector threshold is changed.

Breakout-day observation:
- 2019-09-11 OHLC: O 218.07 / H 223.71 / L 217.73 / C 223.59.
- High and close exceed 221.37; close is +1.0028% versus pivot and remains in the 5% buy zone.
- Volume 44,289,600 versus prior-50 completed-session mean 25,930,154: +70.8035%, ratio 1.7080.
- The frozen USSY >=1.40 breakout-volume threshold therefore passes.

Historical M:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS on 2019-09-11.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY.
- M is not a blocker.

USSY T+1 observation:
- 2019-09-12 open: 224.80.
- +1.5494% versus pivot and +0.5412% versus breakout close.
- T+1 open remains inside the original 5% buy zone.
- Therefore there is no extended-price execution-adaptation gap.

Three-layer disposition:

| Layer | Expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | FLAT_BASE, pivot 221.37 | exact left-high/pivot recovered; candidate not RECOGNIZED because TOO_SHORT/WIDE_LOOSE or WIDE_LOOSE | MORPHOLOGY_FIDELITY_GAP |
| Original breakout | price-volume breakout through 221.37 | high/close above pivot; prior-50 volume ratio 1.7080 | DAILY-BAR BREAKOUT CORROBORATION |
| USSY adaptation | finalized T then T+1 Open | 224.80, +1.55% vs pivot, inside 5% zone | NO EXTENDED-PRICE GAP; pattern gate prevents production eligibility |

Historical L remains NOT_EVALUABLE under frozen governance. This case completes first-pass coverage of all four frozen core morphology families without tuning the detector.


## Cross-case fidelity matrix v1 — first-pass adjudication

Status: FIRST-PASS COMPLETE / VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED.

| Case | Frozen core family | Oracle pivot | Engine pivot | Morphology result | Breakout-volume reconstruction | Historical M | T+1 vs 5% zone | Primary finding |
|---|---|---:|---:|---|---|---|---|---|
| LRCX 2020 | CUP_WITH_HANDLE | 381.96 | 381.95999 | cup/pivot match; final handle rejected | below frozen 1.40 threshold | ALLOW_NEW_BUYS | inside | HANDLE_GATE_BELOW_CUP_MIDPOINT fidelity gap |
| AMD 2019 | CUP_WITHOUT_HANDLE | 35.55 | 35.549999 | RECOGNIZED, no faults | 1.6855, passes | ALLOW_NEW_BUYS | inside | positive morphology/pivot fidelity control |
| IPHI 2019 | DOUBLE_BOTTOM | 64.85 | 64.75 | AMBIGUOUS | 1.1462, fails | ALLOW_NEW_BUYS | inside | NO_SECOND_TROUGH_UNDERCUT fidelity gap |
| AAPL 2019 | FLAT_BASE | 221.37 | 221.369995 | REJECTED/AMBIGUOUS | 1.7080, passes | ALLOW_NEW_BUYS | inside | FLAT_BASE geometry-gate fidelity gap |

### What the four cases establish

1. Pivot reconstruction is not the dominant problem in this first-pass suite. LRCX, AMD and AAPL reproduce the source pivot to practical equality; IPHI differs by only 0.10.
2. The principal source-fidelity discrepancies are localized morphology semantics, not an inability to locate the relevant price structures:
   - CWH: handle upper-half gate (`BELOW_CUP_MIDPOINT`).
   - DOUBLE_BOTTOM: strict second-trough-undercut gate (`NO_SECOND_TROUGH_UNDERCUT`).
   - FLAT_BASE: duration/tightness geometry (`TOO_SHORT` / `WIDE_LOOSE`).
3. CUP_WITHOUT_HANDLE has a positive historical control: AMD is recognized with source-faithful pivot/trough and no detector faults. Therefore the suite is not merely a collection of detector failures.
4. Breakout-volume adaptation is independently material. AMD and AAPL pass the frozen >=1.40 prior-50 threshold; LRCX and IPHI do not. This is separate from morphology fidelity.
5. Historical M is not responsible for any of the four discrepancies: every replay returns `ALLOW_NEW_BUYS` under the frozen historical index-only adapter.
6. T+1 Open is not the source of rejection in these four examples. Every reconstructed T+1 open remains inside the original 5% buy zone. This does not prove T+1 is generally harmless; it only bounds these four cases.
7. Historical L remains intentionally NOT_EVALUABLE because no defensible PIT broad comparison universe is frozen. This must not be converted to either PASS or FAIL.

### Action classification

| Finding | Action now | Production implication |
|---|---|---|
| AMD CWOH positive match | PRESERVE as regression control | none; confirms one frozen family can reproduce a documented example |
| LRCX handle gate | OPEN VALIDATION QUESTION | no production change; research whether the frozen upper-half requirement is source-faithful across multiple authoritative CWH examples |
| IPHI second-trough undercut gate | OPEN VALIDATION QUESTION | no production change; research whether strict undercut is universal, optional, or provider-sensitive |
| AAPL flat-base geometry gates | OPEN VALIDATION QUESTION | no production change; determine whether daily detector duration/tightness semantics align with documented weekly flat-base examples |
| Breakout-volume mismatches | KEEP SEPARATE FROM MORPHOLOGY | do not alter morphology to compensate for volume behavior |
| Historical L unavailable | DATA GAP / HOLD | acquire defensible PIT universe only if justified; never back-project current membership |
| T+1 observations | PRESERVE AS ADAPTATION EVIDENCE | no rule change from four cases |

### Decision gate before any engine revision

No frozen-engine modification is justified by one golden case. A morphology rule may move from validation question to change proposal only after:
- multiple independent authoritative examples for the same family are reconstructed;
- the discrepancy repeats under defensible historical price bases/providers;
- the source methodology supports the proposed semantic interpretation;
- positive controls and counterexamples are included so relaxing a gate is not evaluated only on cases it would rescue;
- the proposal is reviewed separately from this historical-reconstruction branch.

Until that evidence exists, `c433cc1e35a5aa32a46f732cd8c5545935e36e40` remains the authoritative frozen Pattern Engine for this workstream.

### Next validation tranche

The next work is **targeted replication**, not broad backtesting and not detector tuning. Priorities:
1. Add at least two independent authoritative examples for each discrepant family: CWH, DOUBLE_BOTTOM and FLAT_BASE.
2. Include at least one source-backed negative/counterexample per family where possible.
3. Replay with the same frozen engine and classify whether each gate discrepancy repeats.
4. Only then issue a morphology-fidelity adjudication for that family: source-faithful, over-restrictive, under-restrictive, or unresolved.

CUP_WITHOUT_HANDLE does not need immediate gate investigation; AMD remains the positive-control case while resources focus on the three observed discrepancy families.


## Targeted replication candidate registry v1

Status: SOURCE DISCOVERY STARTED / ORACLE NOT YET FROZEN.

Purpose: expand only the three morphology families with first-pass fidelity gaps. Candidate inclusion here is not evidence that a setup will rescue or contradict the frozen detector.

### Source-methodology anchors

Authoritative IBD educational material defines the common pattern boundaries used to frame source review:
- CUP_WITH_HANDLE: minimum base length seven weeks; the handle requires at least five trading sessions. The LRCX educational example explicitly notes its handle was two weeks and 13% deep.
- DOUBLE_BOTTOM: IBD's buying checklist describes a seven-week minimum and a buy point above the middle peak of the W.
- FLAT_BASE: minimum five weeks, generally no more than 15% deep; buy point above the highest point in the base.

These are source-methodology anchors only. They do not overwrite the frozen detector semantics.

### Candidate queue

| Priority | Family | Candidate/source | Why useful | Oracle status |
|---|---|---|---|---|
| 1 | FLAT_BASE | Synopsys (SNPS), IBD educational flat-base case | Source describes a six-week flat base and breakout on May 18 with volume 163% above average; directly useful against AAPL TOO_SHORT/WIDE_LOOSE | SOURCE LOCATED; exact year/pivot/date facts must be frozen from article before replay |
| 2 | DOUBLE_BOTTOM | Mobileye (MBLY), IBD Stock Guide Spring 2017 | Source explicitly labels a first-stage eight-week double-bottom base and describes a June 17 move with volume 52% above average | SOURCE LOCATED; determine exact base landmarks/buy point before replay |
| 3 | CUP_WITH_HANDLE | Edwards Lifesciences (EW), IBD Top Stocks 2019 | Source explicitly describes a later solid cup with handle, 16.3% correction and proper buy point 195.10 around July 22-24 | SOURCE LOCATED; freeze exact source chronology before replay |
| 4 | CUP_WITH_HANDLE | BRP Group (BRP), IBD Top Stocks 2020 | Source explicitly identifies a cup-with-handle and new buy point 18.88 | SOURCE LOCATED; may be setup/pre-breakout rather than completed historical breakout, so suitability requires source adjudication |

### Selection rules

A candidate becomes a frozen reconstruction case only when the authoritative source supplies enough information to establish, without chart-fitting:
- symbol and historical period;
- source-labelled pattern family;
- source buy point/pivot or sufficient explicit source structure to identify it;
- breakout/decision date when the validation question requires breakout behavior;
- no use of the expected landmarks as detector inputs.

For each discrepant family, the target remains at least two additional independent authoritative examples plus a negative/counterexample when a defensible source exists.

### Immediate execution order

1. SNPS flat-base source-oracle extraction, because its source-described six-week duration directly tests whether the AAPL geometry discrepancy repeats on an unambiguously >=5-week educational example.
2. MBLY double-bottom source-oracle extraction, because the source explicitly calls the base eight weeks and therefore supplies an independent structural example.
3. EW cup-with-handle source-oracle extraction, with special attention to handle geometry and whether the frozen upper-half gate agrees.
4. BRP is reserve CWH evidence until a completed breakout can be source-frozen.

No detector code or production rule is changed by this registry.


## Golden Case 005 — SNPS flat-base source oracle v1

Status: FROZEN_SOURCE_ORACLE_V1 / REPLAY NOT YET ADJUDICATED.

Authoritative source:
- Investor's Business Daily, "Synopsys Blasted From This Bullish Pattern Found In Many Market Winners."
- The article identifies Synopsys (SNPS) as the educational example.

Source facts frozen as oracle fields:
- expected family: FLAT_BASE
- prior peak / base high: 392.79 on 2023-04-04
- source buy point: 392.79
- base duration: six weeks
- base trading range/depth characterization: tight 8% range
- breakout date: 2023-05-18
- breakout move: gap up 8.7%
- breakout volume: 163% above its 50-day average
- source buy-zone upper bound: 412.43
- prior context: an earlier cup-with-handle breakout occurred Feb. 1; this fact is context only and must not be used to force the flat-base detector

Year resolution:
- RESOLVED: 2023. Independent contemporaneous company evidence places the earnings release on 2023-05-17, immediately before the source-described May 18 breakout; the source chronology also references the May 25 buyback catalyst.
- Replay decision date T is therefore frozen at 2023-05-18; T+1 is 2023-05-19.
- Provider OHLCV must still fail closed if the 2023 fixture does not corroborate the source chronology/price neighborhood.

Validation question:
Does the frozen FLAT_BASE detector independently recover the source-labelled six-week structure and 392.79 pivot when supplied only historical bars through the resolved May-18 decision date?

Special reason for selection:
This is an independent test of the AAPL finding. Unlike AAPL's frozen candidate, the source explicitly characterizes SNPS as a six-week flat base, which is above IBD's five-week educational minimum. If the frozen engine still fails TOO_SHORT, that would materially strengthen the duration-semantics fidelity concern. WIDE_LOOSE must be evaluated separately.

Oracle-input prohibition:
392.79, six weeks, 8%, and May 18 are comparison/oracle fields. They may be used to select and validate the historical fixture, but never injected as detector landmarks or pattern boundaries.

Next checkpoint:
1. resolve/freeze the unique historical year and candidate OHLCV basis;
2. truncate detector input at breakout date T;
3. run frozen engine unchanged;
4. compare emitted FLAT_BASE family, pivot, duration/depth and faults;
5. only afterward reconstruct breakout volume, M and T+1.


## Golden Case 005 — SNPS 2023 — FLAT-BASE REPLICATION VERIFIED

Replay identity:
- successful corrected run: 35418641005
- producer commit: 1d718ae31336491b9929a9c65df3efda99e79c4f
- the earlier run 35418204224 is INVALID AS EVIDENCE because inherited AAPL dates remained in the first SNPS script revision
- frozen Pattern Engine unchanged: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- decision date: 2023-05-18; T+1: 2023-05-19
- provider historical basis unchanged

Source-fidelity morphology finding:
- The frozen engine independently recovers the exact source high/pivot: LEFT_HIGH 2023-04-04, pivot 392.79000854 versus oracle 392.79.
- It independently locates BASE_LOW 2023-04-25 and measures depth 8.2538%, closely consistent with the source's approximately 8% characterization.
- The confirmed-structure FLAT_BASE candidate is REJECTED with TOO_SHORT and WIDE_LOOSE.
- The open-right-edge FLAT_BASE through breakout day preserves the same 2023-04-04 / 2023-04-25 structure and exact pivot, but is AMBIGUOUS with WIDE_LOOSE.
- Therefore the AAPL FLAT_BASE discrepancy repeats on a second independent source-labelled flat base. In SNPS, however, the source explicitly calls the base six weeks, so the frozen TOO_SHORT result is now a stronger duration-semantics fidelity concern rather than merely an uncertain AAPL boundary.
- Classification: REPEATED_MORPHOLOGY_FIDELITY_GAP / FLAT_BASE_DURATION_AND_TIGHTNESS_SEMANTICS.
- No detector rule is changed.

Important cross-pattern observation:
- The same 2023-04-04 pivot / 2023-04-25 low is also emitted as a RECOGNIZED open-right-edge CUP_WITHOUT_HANDLE with no faults.
- A separate longer cup-with-handle candidate using 2023-04-04 as right rim is also recognized.
- These alternate-family outputs do not replace the source oracle. They are evidence that the frozen engine sees the price structure but classifies the source-labelled six-week flat base differently.

Breakout-day observation:
- 2023-05-18 OHLC: O 387.50 / H 410.91 / L 386.50 / C 409.71.
- High and close exceed 392.79; close is +4.3076% versus pivot and remains barely inside the original 5% buy zone upper bound 412.4295.
- Volume 2,005,700 versus prior-50 completed-session mean 738,404: +171.6264%, ratio 2.7163.
- This exceeds the frozen USSY >=1.40 breakout-volume threshold and is directionally consistent with the source's very large breakout-volume expansion.
- Daily bars support BREAKOUT_DAY_CONFIRMED_FROM_DAILY_BAR; exact intraday crossing/cumulative-volume timing is unavailable.

Historical M:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS on 2023-05-18.
- classifier reason: VALID_DAY4_PLUS_FOLLOW_THROUGH.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY.
- M is not a blocker.

USSY T+1 execution adaptation:
- 2023-05-19 open: 413.03.
- +5.1529% versus pivot and +0.8103% versus breakout close.
- This is just outside the original 5% buy-zone upper bound 412.4295.
- Classification: MISSED_EXTENDED / T1_OPEN_ABOVE_5PCT_BUY_ZONE.
- This is the first golden reconstruction in the suite where an original breakout-day opportunity and the USSY T+1 Open adaptation materially diverge on the 5% buy-zone rule.

Three-layer disposition:

| Layer | Source / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | six-week FLAT_BASE, pivot 392.79, ~8% range | exact pivot/high and ~8.25% depth recovered; FLAT_BASE rejected/ambiguous on TOO_SHORT/WIDE_LOOSE | REPEATED MORPHOLOGY FIDELITY GAP |
| Original breakout | 2023-05-18 with exceptional volume | high/close above pivot; close +4.31%; volume ratio 2.7163 | DAILY-BAR BREAKOUT CORROBORATION |
| USSY adaptation | finalized T then T+1 Open | 413.03 = +5.153% vs pivot, outside 5% zone | MISSED_EXTENDED / EXECUTION ADAPTATION GAP |

### Flat-base validation state after AAPL + SNPS

The flat-base question is no longer supported by only one golden example:
- AAPL: source pivot exactly recovered; FLAT_BASE fails/ambiguous on TOO_SHORT/WIDE_LOOSE.
- SNPS: source explicitly says six weeks and ~8%; exact pivot and ~8.25% provider depth recovered, yet FLAT_BASE again fails/ambiguous on TOO_SHORT/WIDE_LOOSE.

This is **repeat evidence**, not authorization to relax the detector. At least one further independent authoritative flat-base example and a defensible counterexample/negative control should be reconstructed before a family-level semantic change proposal is considered.


## Golden Case 006 — TSM 2024 — DOUBLE-BOTTOM REPLICATION VERIFIED

Replay identity:
- successful run: 35420754613
- producer commit: 0d28126a589367e2b05b24b6c80161abdbafcd0c
- frozen Pattern Engine unchanged: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- decision date: 2024-05-10; T+1: 2024-05-13
- source oracle: DOUBLE_BOTTOM, buy point 148.43

Source-fidelity morphology finding:
- The frozen engine independently emits a RECOGNIZED DOUBLE_BOTTOM whose pivot is 148.42999268, effectively exact versus the source oracle 148.43.
- Structural signature: LEFT_HIGH 2024-02-09; TROUGH_1 2024-03-19; MIDDLE_PEAK 2024-04-10; TROUGH_2 2024-04-22.
- normalized_status: RECOGNIZED.
- native_state: DOUBLE_BOTTOM_RECOGNIZED.
- detector_faults: [].
- measured depth: 6.9468%.
- Therefore TSM is a positive-control double-bottom case. The IPHI NO_SECOND_TROUGH_UNDERCUT discrepancy does **not** automatically repeat on another authoritative double-bottom.
- Classification: SOURCE_FIDELITY_MATCH / DOUBLE_BOTTOM_POSITIVE_CONTROL.

The detector also emits other alternative DOUBLE_BOTTOM candidates, several with NO_SECOND_TROUGH_UNDERCUT or other faults. Those are not substituted for the source-faithful candidate: the decisive fact is that the frozen engine independently recovers the source pivot 148.43 with a fault-free RECOGNIZED double-bottom.

Breakout-day observation:
- 2024-05-10 OHLC: O 147.22 / H 150.50 / L 146.93 / C 149.26.
- high and close exceed pivot 148.43; close is +0.5592% versus pivot and remains inside the 5% buy zone.
- volume: 23,671,400 versus prior-50 completed-session mean 16,163,340.
- volume expansion: +46.4512%, ratio 1.4645.
- therefore the frozen USSY >=1.40 breakout-volume requirement passes.
- This daily reconstruction corroborates IBD's contemporaneous report that TSM broke out of a double-bottom at 148.43. Exact intraday crossing/cumulative-volume timing is not reconstructed.

USSY T+1 execution adaptation:
- 2024-05-13 open: 148.0200.
- open is -0.2762% below pivot and -0.8308% below breakout close.
- The script's strict original-buy-zone boolean is false because the open is below the pivot, not because price is extended above the 5% upper bound.
- Classification: T1_OPEN_BELOW_PIVOT / NOT_EXTENDED.
- This must not be mislabeled MISSED_EXTENDED. Whether a production order would fill depends on the production entry/order semantics, which is a separate operationalization question.

Double-bottom adjudication after IPHI + TSM:
- IPHI remains a real source-fidelity discrepancy: official source calls the setup DOUBLE_BOTTOM, while the source-near frozen candidate is AMBIGUOUS on NO_SECOND_TROUGH_UNDERCUT.
- TSM is a clean positive control: exact source pivot recovered as DOUBLE_BOTTOM_RECOGNIZED with no faults.
- Consequently the current evidence does **not** justify saying the frozen undercut gate is generally incompatible with O'Neil double bottoms.
- The correct next question is narrower: why does IPHI's documented double bottom fail that gate while TSM passes? Possible explanations to test separately are source morphology nuance, provider/price-basis differences, landmark selection, or an over-restrictive gate for a subset of documented examples.
- No detector change is authorized.

Three-layer disposition:

| Layer | Source / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | DOUBLE_BOTTOM, pivot 148.43 | exact pivot 148.42999268; RECOGNIZED; no faults | SOURCE-FIDELITY MATCH |
| Original breakout | breakout through 148.43 | high/close above pivot; volume ratio 1.4645 | DAILY-BAR BREAKOUT CORROBORATION |
| USSY adaptation | finalized T then T+1 Open | open 148.02, slightly below pivot | T1_OPEN_BELOW_PIVOT / NOT_EXTENDED |

### Double-bottom validation state

TSM changes the interpretation of the IPHI result. The family now has both:
- IPHI: documented DOUBLE_BOTTOM with a localized NO_SECOND_TROUGH_UNDERCUT fidelity gap.
- TSM: documented DOUBLE_BOTTOM with exact pivot and fault-free recognition.

The next double-bottom replication should therefore be selected to discriminate the undercut semantics directly, ideally an authoritative example whose two trough relationship can be reconstructed unambiguously. It should not be chosen merely to accumulate another passing case.


## Golden Case 007 — WMT 2024 — DOUBLE-BOTTOM LANDMARK/SEGMENTATION FIDELITY GAP

Replay identity:
- valid diagnostic run: 35428260263
- producer commit: 6aedc85b7b09c63591d95b112217532366857e37
- frozen Pattern Engine unchanged: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- source oracle: DOUBLE_BOTTOM; pivot 60.89; first low 58.88; second low 58.55; breakout date 2024-05-16
- diagnostic oracle landmarks are comparison-only and are never injected into detector generation.

Detector result:
- no emitted DOUBLE_BOTTOM candidate matched any of the source-target 2024 oracle landmarks used by the diagnostic.
- `oracle_candidate_matches=[]`.
- diagnostic landmark/segment arrays for the source-target path are empty.
- the engine does emit an older, unrelated fault-free DOUBLE_BOTTOM (2023-09-13 / 2023-10-06 / 2023-11-15 / 2023-12-11; pivot 56.64666748). That older candidate must not be substituted for the source-labelled 2024 structure.
- therefore WMT does not test the `NO_SECOND_TROUGH_UNDERCUT` morphology gate at all: the source-target structure fails upstream of morphology assessment.
- boundary diagnostic run `35428665101` localizes the failure further: primary, auxiliary, and fused landmark vocabularies contain no April-May 2024 landmarks; consequently atomic and multiturn segment sets also contain no April-May 2024 structure.
- classification refined to: `MORPHOLOGY_FIDELITY_GAP / LANDMARK_GENERATION_MISS`.
- segmentation is downstream-empty, not independently implicated by this replay.
- no detector change is authorized.

Breakout / execution observations, retained separately from morphology:
- 2024-05-16: O 64.22 / H 64.42 / L 62.94 / C 64.01 versus oracle pivot 60.89.
- close is +5.1240% above pivot, just above the conventional 5% buy-zone ceiling 63.9345.
- volume 60,545,600 versus prior-50 completed-session mean 15,207,442: total ratio 3.9813x, or +298.13% above average.
- T+1 2024-05-17 open 64.24: +5.5017% versus pivot and therefore above the 5% buy zone.
- historical M on 2024-05-16: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS.
- these observations do not repair the morphology miss and must not be used as detector inputs.

Double-bottom adjudication after IPHI + TSM + WMT:
- IPHI: source-near candidate reaches morphology but is AMBIGUOUS due `NO_SECOND_TROUGH_UNDERCUT`.
- TSM: source structure is independently recovered with exact pivot and fault-free `DOUBLE_BOTTOM_RECOGNIZED`.
- WMT: source-labelled 2024 structure is not emitted because landmark generation itself produces no April-May 2024 landmarks; segmentation is downstream-empty.
- Consequently there is still no evidence that one universal double-bottom gate is the dominant family-level problem. The discrepancies occupy different layers.
- WMT boundary diagnosis is now localized to landmark generation. Any future engineering investigation belongs in the landmark extractor workstream and must be tested against independent positive/negative controls before proposing a frozen-engine change; do not relax `NO_SECOND_TROUGH_UNDERCUT` or tune morphology from this case.


## Required data by component

| Component | Reconstruction input |
|---|---|
| C | authoritative reference fact where documented |
| A | authoritative reference fact where documented; if annual evidence is not explicit, do not infer it |
| N | reference fact if documented; otherwise NOT_DOCUMENTED |
| S | historical OHLCV/volume; broader supply evidence only if available |
| L | historical comparison universe on same date; official historical RS separately if available |
| I | reference fact if documented; otherwise NOT_DOCUMENTED |
| M | historical market context through T only |
| Pattern/base | candidate historical OHLCV only |
| Pivot | engine-derived; 381.96 is oracle only |
| Breakout | historical price/volume |
| Original entry | breakout-day/source-faithful assessment |
| USSY execution | historical T+1 Open |
| Lifecycle | future historical bars revealed causally |

NOT_DOCUMENTED and NOT_EVALUABLE are not FAIL.

## Replay stages

1. Freeze authoritative source oracle. COMPLETE for LRCX v1.
2. Acquire/freeze candidate historical OHLCV with sufficient pre-base warm-up.
3. Run frozen O'Neil Pattern Engine on candidate data truncated as-of T.
4. Compare observed family, landmarks, pivot and ambiguity state against oracle.
5. Reconstruct breakout-day price/volume and original O'Neil entry opportunity.
6. Only after morphology/pivot replay, freeze comparison-universe identity/OHLCV for L and reconstruct M.
7. Assemble CAN SLIM v2 reconstruction evidence preserving NOT_DOCUMENTED.
8. Cross explicit boundary into USSY adaptation and reveal T+1 Open.
9. Evaluate USSY execution without retroactive fills.
10. Reveal later bars causally and replay lifecycle.
11. Publish expected-vs-observed discrepancies with lineage.

## Output contract

Preserve: case_id; symbol; decision/breakout date; authoritative source; source retrieval date; oracle facts/version; OHLCV provider/price basis/corporate-action policy/range/checksum; comparison-universe identity/checksum; M input identity; frozen Pattern Engine SHA/version; expected/observed pattern and pivot; breakout price/volume; original_oneil_entry; USSY T+1 execution; adaptation gap; lifecycle result; discrepancy classification; producer commit/run identity.

## Coverage matrix

| Area | LRCX 2020 | Next |
|---|---|---|
| Source oracle | VERIFIED/FROZEN v1 | preserve provenance |
| C quarterly reference | VERIFIED | reference only |
| A annual reference | NOT YET DOCUMENTED | do not infer |
| Cup with handle | VERIFIED oracle; cup/pivot reconstructed; final handle gate mismatch | frozen finding documented |
| Pivot | VERIFIED 381.96; observed 381.95999 on oracle structure | MATCH |
| Breakout | VERIFIED 2020-11-04; daily high crossed pivot | reconstruction complete |
| S / breakout volume | reconstructed; frozen v2 volume confirmation not met | BREAKOUT_VOLUME_UNCONFIRMED |
| L | NOT_EVALUABLE — PIT historical comparison universe unavailable | do not fabricate/back-project 2026 membership |
| I | not frozen | source fact or NOT_DOCUMENTED |
| N | not frozen | source fact or NOT_DOCUMENTED |
| M | FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS | reconstruction complete |
| Original entry | daily crossing reconstructed; intraday timing unavailable; volume discrepancy preserved | source-fidelity adjudication needed |
| T+1 adaptation | 2020-11-05 open 390.00; inside 5% buy zone | observation complete; eligibility boundary preserved |
| Lifecycle | not reconstructed | causal future-bar replay |
| DOUBLE_BOTTOM | IPHI 2019 structural neighborhood/pivot reproduced; frozen engine AMBIGUOUS on NO_SECOND_TROUGH_UNDERCUT; failed-trade lifecycle causally corroborated | COVERED / FIDELITY GAP CASE |
| FLAT_BASE | AAPL 2019 exact oracle pivot recovered; frozen engine fails geometry gates (TOO_SHORT/WIDE_LOOSE) while breakout volume and T+1 are corroborated | COVERED / FIDELITY GAP CASE |
| CUP_WITHOUT_HANDLE | AMD 2019 source-faithful candidate RECOGNIZED; pivot 35.549999 vs oracle 35.55; breakout volume ratio 1.6855 | COVERED / POSITIVE FIDELITY CASE |

## Recovery boundary

Freeze reusable stages with lineage:
source oracle -> candidate OHLCV -> morphology raw result -> comparison-universe manifest -> L/M raw reconstruction -> execution/lifecycle -> report.

Semantic changes to source, price basis, universe, decision date, methodology contract or frozen engine identity invalidate affected downstream checkpoints.

## Progress accounting

CAN SLIM v2 engineering implementation remains 100% complete.

Historical reconstruction first-pass core-pattern coverage is complete: all four frozen families now have a source-backed replay, with AMD as the positive morphology control and LRCX/IPHI/AAPL carrying localized fidelity questions. No frozen-engine change is authorized. Targeted multi-example replication is the next validation tranche. IPHI Golden Case 003 morphology/pivot, breakout, M, T+1 and original O'Neil loss-cut lifecycle are complete; the frozen engine preserves a DOUBLE_BOTTOM fidelity gap at NO_SECOND_TROUGH_UNDERCUT. AMD Golden Case 002 morphology/pivot, breakout-volume, historical M and T+1 reconstruction are now complete as a positive CUP_WITHOUT_HANDLE fidelity case; C/A and L evidence boundaries remain explicit. LRCX source oracle, candidate OHLCV replay, price-basis audit, morphology/pivot diagnosis, breakout-day daily-bar observation, T+1 observation and historical M replay are complete. Historical L is explicitly NOT_EVALUABLE because a defensible PIT comparison universe is unavailable. Consolidated CAN SLIM v2 eligibility reconstruction is complete for LRCX: NOT_ELIGIBLE under the frozen v2 contract. Lifecycle reconstruction remains separate.


## Golden Case 008 — EW 2019 — CUP_WITH_HANDLE

Status: **COMPLETE / FROZEN — VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**

Source oracle: IBD Top Stocks 2019 describes Edwards Lifesciences (EW) as a solid cup with handle, 16.3% deep, with proper buy point 195.10. Source chronology distinguishes thin-volume pivot crossing around July 22–23 from the July 24 breakaway gap / strong-volume confirmation.

Price-basis adaptation: Yahoo historical 2019 bars reflect the later 3-for-1 split basis. For source-faithful reconstruction, OHLC/adj_close are restored x3 and volume /3 before detector replay. Oracle facts remain reference-only and are not detector inputs.

Frozen engine replay (run 35433862533, engine c433cc1e35a5aa32a46f732cd8c5545935e36e40):
- source-target diagnostic: null; no CUP_WITH_HANDLE candidate matching the 195.10 source structure was emitted.
- primary/fused landmarks do contain the source-near cup body: SWING_HIGH 2019-03-18 at 197.85999 and SWING_LOW 2019-05-29 at 165.689999.
- atomic segment: start 2019-03-18, trough 2019-05-29, recovery null, depth 16.25897%, closely matching the source 16.3% depth.
- therefore the evidence localizes the discrepancy downstream of cup-body landmark/depth discovery: the frozen engine does not assemble/recognize the documented CWH structure by the July 24 as-of date.

Classification: **MORPHOLOGY_FIDELITY_GAP / CWH_ASSEMBLY_OR_HANDLE_RECOGNITION_MISS**. This is distinct from LRCX's explicit BELOW_CUP_MIDPOINT rejection: EW reaches a source-faithful cup-body geometry but produces no source-target CWH diagnostic. No detector tuning is authorized from this case alone.

Breakaway confirmation observation on 2019-07-24 (daily-bar reconstruction): O 218.16, H 219.71, L 210.73, C 214.88, volume 3,633,500 on contemporaneous basis. Prior-50-session average volume 1,307,968; ratio 2.77797x (+177.80%), comfortably above the frozen >=1.40 confirmation threshold. Close was +10.14% above the 195.10 pivot and already outside the original 5% buy zone. Daily OHLCV cannot reconstruct exact intraday entry timing.

USSY T+1 observation: 2019-07-25 open 212.55, +8.94% vs pivot and -1.08% vs July 24 close; outside the original 5% buy zone => **MISSED_EXTENDED / T1_OPEN_ABOVE_5PCT_BUY_ZONE** if July 24 strong-volume confirmation is used as finalized T.

Historical M: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS. Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe limitation.

CWH adjudication after LRCX + EW: two authoritative CWH examples now show source-fidelity discrepancies, but not the same terminal gate. LRCX is an explicit handle midpoint-gate rejection; EW preserves the source-like cup body yet fails to assemble/recognize the source-target CWH. This supports continued targeted CWH replication and component-level diagnostics, not a family-wide rule change.



## CWH numeric audit 002 — EW 2019

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITH_HANDLE | source-near cup body found; source-target CWH not assembled | categorical mismatch downstream of cup body |
| Pivot | 195.10 | no source-target CWH pivot emitted | **not reconstructed as final CWH pivot** |
| Base depth | 16.3% | 16.25897% | -0.04103 percentage point; practical exact match |
| Cup left/high area | source summary does not publish exact landmark | 2019-03-18 / 197.85999 | engine-only landmark; not scored against absent oracle |
| Cup low | source summary does not publish exact landmark | 2019-05-29 / 165.689999 | engine-only landmark; not scored against absent oracle |
| Atomic cup segment | valid CWH implied by source | source-near cup body discovered | **geometry evidence present** |
| Handle geometry | valid handle implied by source label | no source-target handle/CWH diagnostic emitted | **true assembly/handle gap** |
| Breakaway confirmation | strong-volume gap 2019-07-24 | volume 2.77797x prior-50; close +10.14% vs pivot | strong daily confirmation corroborated |

Numeric adjudication: **EW's cup depth is essentially exact**: 16.25897% versus the source's rounded 16.3%, a difference of only 0.041 percentage point. The engine also independently finds the high/low landmarks that generate this source-like cup body. The failure occurs after cup-body discovery: it does not assemble/recognize the source-target handle and therefore emits no final CWH pivot matching 195.10.

Audit conclusion: **CUP_DEPTH_MATCH / CUP_BODY_GEOMETRY_PRESENT / CWH_ASSEMBLY_OR_HANDLE_GAP**. The 195.10 pivot cannot be scored as an engine numeric miss because the source-target final CWH candidate itself is absent; it is better classified as a downstream assembly/recognition absence rather than a wrong emitted pivot.

## Targeted replication checkpoint — BRP 2020 CWH suitability

Status: **SOURCE-ORACLE SUITABILITY REVIEWED / NOT PROMOTED TO COMPLETED-BREAKOUT GOLDEN CASE**.

Authoritative IBD Top Stocks 2020 material explicitly identifies BRP Group (BRP) as forming a cup-with-handle and gives a new buy point of 18.88. The source language is prospective: the stock "is forming a handle" / "is forming a cup-with-handle base". It does not, in the located passage, freeze a completed breakout date through 18.88 with breakout-day price/volume evidence.

Decision: retain BRP as **PRE-BREAKOUT / SETUP-STATE CWH EVIDENCE**, not as a completed-breakout replication equivalent to LRCX or EW. Do not infer a breakout date from later bars merely to make the case fit the validation template. This preserves source fidelity and the oracle-input prohibition.

Usefulness: BRP can later test whether the frozen engine recognizes a source-labelled in-progress CWH as-of the publication/setup state, but it cannot by itself answer the current completed-breakout CWH discrepancy question. The next CWH replication candidate should therefore be another authoritative example with an explicit completed breakout chronology, pivot, and sufficient historical date resolution.


## Golden Case 009 — NVO 2024 — CWH REPLICATION VERIFIED

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Replay identity:
- successful run: 35438338999
- producer commit: 0481bcb8754571918e299d01296ca2344380dc8b
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- source oracle: CUP_WITH_HANDLE, pivot 137.22, breakout 2024-06-04
- provider price basis retained unchanged; breakout bar price neighborhood corroborates the 137.22 oracle scale.

Source-fidelity morphology finding:
- The frozen engine does emit an open-right-edge CUP_WITH_HANDLE candidate relevant to the source period, but it is **AMBIGUOUS**, not RECOGNIZED.
- Engine structure: LEFT_RIM 2023-11-24; CUP_LOW 2023-12-11; RIGHT_RIM 2024-03-07; HANDLE_LOW 2024-05-03.
- Engine pivot: 138.27999878 versus source oracle 137.22 (~0.77% higher).
- Cup depth: 10.369949%.
- Terminal detector fault: **DEEP_HANDLE_EXCEPTIONAL**.
- Classification: **MORPHOLOGY_FIDELITY_GAP / DEEP_HANDLE_EXCEPTIONAL**.

Breakout-day reconstruction (2024-06-04):
- O 136.44 / H 140.00 / L 135.78 / C 139.92; volume 5,071,200.
- Source pivot 137.22 was crossed and the close finished +1.9676% above pivot, inside the original 5% buy zone.
- Prior-50-session average volume: 3,712,446; breakout volume +36.60% (1.366x), below the USSY >=1.40 confirmation threshold.
- Daily-bar limitation remains INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

USSY T+1 observation (2024-06-05):
- open 141.36; +3.0171% versus source pivot and +1.0292% versus breakout close.
- T+1 open remained inside the original 5% buy zone: **T1_OPEN_IN_BUY_ZONE / NOT_EXTENDED**.

Historical M reconstruction:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS.
- Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe boundary.

CWH adjudication after LRCX + EW + NVO:
- Three independent authoritative CWH examples now produce three distinct terminal fidelity mechanisms under the frozen engine: LRCX -> BELOW_CUP_MIDPOINT; EW -> CWH assembly/handle-recognition miss after source-like cup body; NVO -> DEEP_HANDLE_EXCEPTIONAL with a near-source pivot.
- This strengthens evidence that CWH source-fidelity is not yet robust, but does **not** identify one universal gate whose removal is justified.
- No detector tuning or production-rule change is authorized from these cases alone. Any engine revision requires a separate component-level study with authoritative positive and negative controls.



## CWH numeric audit 003 — NVO 2024

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITH_HANDLE | CUP_WITH_HANDLE_AMBIGUOUS | same family found; final-state mismatch |
| Pivot | 137.22 | 138.27999878 | +1.059999 / **+0.7725%** |
| Cup depth | source oracle does not publish a numeric depth in the frozen record | 10.369949% | engine-only value; not scored |
| Left rim | not numerically frozen from source | 2023-11-24 | not scored |
| Cup low | not numerically frozen from source | 2023-12-11 | not scored |
| Right rim | not numerically frozen from source | 2024-03-07 | not scored |
| Handle low | not numerically frozen from source | 2024-05-03 | not scored |
| Handle/final gate | source labels valid CWH | DEEP_HANDLE_EXCEPTIONAL | **true source-fidelity gap** |
| Breakout close vs oracle pivot | breakout 2024-06-04 | close 139.92 = +1.9676% | pivot crossed; inside 5% zone |
| Breakout volume | source numeric oracle not frozen | 1.366x prior-50 | below USSY 1.40 threshold; not scored as source morphology mismatch |

Numeric adjudication: NVO differs materially from EW because the frozen engine **does find the same pattern family and a near-source pivot**. The pivot difference is only 1.06 price units, or about **0.77% above the IBD 137.22 oracle**. There is no frozen source depth/landmark number with which to score the engine's 10.369949% cup depth or individual landmark dates, so those fields must remain unscored rather than labelled mismatches.

The actual documented disagreement is categorical at the handle gate: IBD treats the setup as a valid CWH while the frozen engine retains it as AMBIGUOUS due to DEEP_HANDLE_EXCEPTIONAL.

Audit conclusion: **CWH_FAMILY_MATCH / PIVOT_NEAR_MATCH_0.77PCT / HANDLE_DEPTH_SEMANTICS_GAP**. This supersedes shorthand that could imply the entire NVO morphology failed.

## Golden Case 010 — AVTR 2021 — CWOH REPLICATION

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Replay identity:
- successful first run: 35439158198
- producer commit: 72dcf424c366a08c3b4c91995aaecfca6bcc7515
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- source oracle: CUP_WITHOUT_HANDLE, pivot 33.99, breakout 2021-06-16
- provider historical basis retained unchanged; breakout bar neighborhood independently corroborates the oracle price scale.

Source-fidelity morphology finding:
- The frozen engine emits multiple CUP_WITHOUT_HANDLE_RECOGNIZED structures, but none of the emitted source pivots is near the source oracle 33.99 at the 2021-06-16 as-of date.
- Representative latest recognized structure uses LEFT_RIM 2020-10-21 / CUP_LOW 2020-10-30 with pivot 25.70000076 and no detector faults; other recognized CWOH pivots include 28.97999954, 19.50, and 18.09000015.
- Therefore generic pattern-family recognition is present, but the source-labelled AVTR base is not reconstructed.
- Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_BASE_NOT_RECONSTRUCTED**.

Breakout-day reconstruction (2021-06-16):
- O 33.36 / H 34.50 / L 33.25 / C 34.05; volume 5,454,200.
- Oracle pivot 33.99 was crossed; close finished +0.1765% above pivot and inside the 5% buy zone.
- Prior-50-session average volume 3,960,106; breakout volume +37.73% (1.3773x), narrowly below the USSY >=1.40 confirmation threshold.
- Daily-bar limitation remains INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

USSY T+1 observation (2021-06-17):
- open 34.05; +0.1765% versus pivot and unchanged versus breakout close.
- T+1 open remained inside the original 5% buy zone: **T1_OPEN_IN_BUY_ZONE / NOT_EXTENDED**.

Historical M reconstruction:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS.
- Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe boundary.

CWOH adjudication checkpoint:
- AMD remains the clean source-fidelity positive control.
- AVTR shows that recognizing some CWOH structures on the same security is not sufficient: source-target base selection/assembly can still miss the authoritative base.
- No detector tuning is authorized from this single discrepancy; continue the planned 10-case CWOH tranche.


## Golden Case 011 — SE 2019 — CWOH REPLICATION

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Source oracle: IBD Top Stocks 2019 identifies Sea Limited (SE) as a cup-without-handle base with 38.10 buy point and states the stock moved into the buy range on 2019-11-20. This is treated as an intraday pivot-cross event; the daily replay must not silently reinterpret it as a close-confirmed breakout.

Replay identity:
- successful run: 35439712313
- producer commit: 957ea5bc19dd231dd473a9c824d7df98a4349bea
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- provider historical basis retained unchanged.

Source-fidelity morphology finding:
- The frozen engine recognizes an open-right-edge CUP_WITHOUT_HANDLE through the oracle date with LEFT_RIM 2019-08-19, CUP_LOW 2019-10-21, pivot 36.90000153, depth 28.428188%, and no detector faults.
- IBD oracle pivot is 38.10, so the family is recognized but pivot/base geometry does not exactly reproduce the source-labelled structure.
- Classification: **MORPHOLOGY_FIDELITY_GAP / CWOH_PIVOT_GEOMETRY_MISMATCH**.

Breakout-day reconstruction (2019-11-20):
- O 37.02 / H 38.98 / L 36.69 / C 37.27; volume 4,860,100.
- High crossed the 38.10 oracle pivot, but close finished 2.1785% below pivot; therefore this is consistent with an intraday pivot cross that faded by the close, not a close-confirmed breakout.
- Prior-50-session average volume 4,004,580; volume +21.36% (1.2136x), below the USSY >=1.40 confirmation threshold.
- Daily-bar limitation: INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

USSY T+1 observation (2019-11-21):
- open 37.28; 2.1522% below oracle pivot and therefore not in the original buy zone at the open.
- State: **T1_OPEN_BELOW_PIVOT / NOT_EXTENDED**.

Historical M reconstruction: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS. Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe boundary.

CWOH checkpoint after AMD + AVTR + SE:
- AMD: clean source-fidelity positive control.
- AVTR: source-target base not reconstructed despite generic CWOH recognition.
- SE: source family recognized, but engine pivot geometry differs from the authoritative 38.10 source pivot.
- Continue the planned 10-case CWOH tranche; no detector tuning is authorized from these cases alone.


## Golden Case 012 — AMZN 2023 — CWOH REPLICATION

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Authoritative IBD oracle: Amazon formed a cup-without-handle after a September 2023 pullback, with buy point 145.86. IBD describes the breakout in the week of Nov. 17; daily OHLCV establishes the first actual 145.86 pivot cross on 2023-11-20 (Nov. 17 high was 145.23). Daily replay therefore uses 2023-11-20 as the causal breakout session and 2023-11-21 as T+1.

Replay identity:
- valid successful run: 35439948453
- producer commit: 8d26eb6ab928e32924badcab50420e0c9e5a9ffd
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- provider basis unchanged.

Morphology finding:
- frozen engine emits CUP_WITHOUT_HANDLE_RECOGNIZED candidates, but the source-labelled September-November base/pivot 145.86 is not reconstructed.
- Representative recognized structure at the oracle as-of uses LEFT_RIM 2023-04-27 / CUP_LOW 2023-05-02 / pivot 110.86000061 / depth 8.758794%, no faults.
- Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_BASE_NOT_RECONSTRUCTED**.

Breakout day 2023-11-20:
- O 145.13 / H 146.63 / L 144.73 / C 146.13; volume 41,951,200.
- high and close above 145.86; close +0.1851% versus pivot and inside 5% buy zone.
- prior-50 average volume 55,536,578; breakout volume -24.46% versus average, below USSY >=1.40 confirmation threshold.

T+1 2023-11-21:
- open 143.91; -1.3369% versus pivot and -1.5192% versus breakout close.
- **T1_OPEN_BELOW_PIVOT / NOT_EXTENDED**.

Historical M: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS. Historical L remains NOT_EVALUABLE.

CWOH progress: AMD, AVTR, SE, AMZN = **4 / 10 valid cases**.


## CWH completion tranche — Golden Cases 013–019

Status: **CWH 10/10 COMPLETE / FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Batch replay: run 35441720017 (OLED, TOL, URBN, SHOP, RBLX, DUOL; all jobs SUCCESS). TSLA required a corporate-action basis correction for Yahoo's later 2022 3-for-1 split; authoritative corrected replay is run 35441985710. Earlier TSLA batch evidence is superseded and must not be used.

### 013 OLED 2019
IBD oracle: second-stage CUP_WITH_HANDLE, pivot 177.05, breakout 2019-06-18. Daily replay: O 176.08 / H 186.31 / L 175.94 / C 184.70; volume 1,028,500 vs prior50 743,744 (~1.383x). T+1 2019-06-19 open 185.80, +4.9421% vs pivot, still inside 5% zone. Frozen engine does not reproduce the source-target 177.05 CWH; emitted CWH candidates are faulted (including DEEP_HANDLE_EXCEPTIONAL / BELOW_CUP_MIDPOINT). Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.


## CWH numeric audit 004 — OLED 2019

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | second-stage CUP_WITH_HANDLE | CWH candidates emitted, but no source-target 177.05 structure | family vocabulary present; target assembly mismatch |
| Pivot | 177.05 | no source-target CWH pivot emitted | **not numerically scoreable as a final target pivot** |
| Base depth | no numeric depth frozen in oracle | no source-target geometry emitted | not scored |
| Base/handle landmarks | no numeric landmarks frozen in oracle | emitted candidates carry DEEP_HANDLE_EXCEPTIONAL / BELOW_CUP_MIDPOINT | not scored against absent oracle |
| Breakout date | 2019-06-18 | daily high 186.31 and close 184.70 crossed 177.05 | **breakout chronology corroborated** |
| Breakout close vs pivot | breakout | +4.3208% | inside 5% buy zone |
| Breakout volume | no numeric source ratio frozen | ~1.383x prior-50 | below USSY 1.40 by ~0.017x; not a morphology-oracle mismatch |
| T+1 open vs pivot | n/a to source morphology | +4.9421% | inside 5% zone |

Numeric adjudication: the frozen OLED oracle currently supplies a precise pivot and breakout date, but **does not contain source-published numeric depth, duration, or handle landmarks**. Therefore it would be incorrect to call those dimensions numeric mismatches. The daily market data strongly corroborates the oracle's 177.05 breakout level/date: the 2019-06-18 bar trades through the pivot and closes 4.3208% above it.

Unlike LRCX, EW, and NVO, the frozen engine does not emit a source-target CWH whose pivot/geometry can be compared directly to 177.05. It emits other CWH candidates with handle-related faults. The defensible discrepancy is therefore target structure selection/assembly, not a demonstrated error in a particular oracle depth or landmark.

Audit conclusion: **ORACLE_PIVOT_AND_BREAKOUT_CORROBORATED / SOURCE_TARGET_CWH_NOT_ASSEMBLED / NUMERIC_GEOMETRY_NOT_SCOREABLE_FROM_CURRENT_ORACLE**.

### 014 TSLA 2020
IBD oracle: off-kilter CUP_WITH_HANDLE, pivot 466.00, breakout 2020-11-18. Yahoo current history is adjusted for the later 2022 3-for-1 split; replay restores contemporaneous Nov-2020 basis by multiplying OHLC by 3 and dividing volume by 3. Corrected breakout: O 448.35 / H 496.00 / L 443.50 / C 486.64; volume 78,044,000 vs prior50 48,526,294 (~1.608x); close +4.4292% vs pivot and inside 5% zone. T+1 open 492.00, +5.5794%, above the 5% zone: **MISSED_EXTENDED / T1_OPEN_ABOVE_5PCT_BUY_ZONE**. Engine's representative CWH is AMBIGUOUS with pivot 358.998 and DEEP_HANDLE_EXCEPTIONAL, not the source-target structure. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.


## CWH numeric audit 005 — TSLA 2020

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

Authoritative replay for this audit is corrected run 35441985710 on the restored contemporaneous pre-2022-split price basis. Earlier uncorrected TSLA evidence remains superseded.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | off-kilter CUP_WITH_HANDLE | source-near open-right-edge CUP_WITH_HANDLE_AMBIGUOUS | **same family and source-near structure found** |
| Pivot | 466.00 | 465.90000916 | -0.099991 / **-0.02146%**; practical exact match |
| Source-near right rim | pivot implies source area | 2020-10-14 / 465.90000916 | practical pivot match |
| Source-near handle low | not numerically frozen from source | 2020-11-13 | not scored |
| Engine depth field | no numeric source depth frozen | 11.579787% | not scored against absent oracle |
| Final state | valid off-kilter CWH per source | AMBIGUOUS | categorical mismatch |
| Faults on source-near candidate | source accepts structure | SHARP_V; FRAGMENTED_BOTTOM; DEEP_HANDLE_EXCEPTIONAL | **true morphology-semantics gap** |
| Breakout date | 2020-11-18 | high 496.00 / close 486.64 crossed pivot | **chronology corroborated** |
| Breakout volume | no source ratio frozen in current oracle | 1.6083x prior-50 | passes USSY 1.40 confirmation |
| Breakout close vs pivot | breakout | +4.4292% | inside 5% zone |
| T+1 open vs pivot | n/a to source morphology | +5.5794% | outside 5% zone |

Numeric adjudication: the earlier tranche summary understated how close the frozen engine gets to the authoritative TSLA setup. The replay contains an **open-right-edge CWH candidate with pivot 465.90000916**, only about **0.0215% below the 466.00 oracle**. This is the appropriate source-near candidate for numeric comparison; the unrelated 358.998 CWH candidate must not be used as if it were the source-target pivot.

The remaining discrepancy is therefore not source-target pivot reconstruction. It is the engine's morphology semantics: the source-near candidate is retained as AMBIGUOUS because of SHARP_V, FRAGMENTED_BOTTOM, and DEEP_HANDLE_EXCEPTIONAL. Since the frozen oracle does not contain numeric source depth/handle measurements, those individual dimensions remain unscored.

Audit conclusion: **CWH_FAMILY_MATCH / PIVOT_PRACTICAL_EXACT_MATCH_0.0215PCT / SOURCE_NEAR_STRUCTURE_FOUND / MORPHOLOGY_SEMANTICS_GAP**. This supersedes the earlier shorthand SOURCE_TARGET_CWH_NOT_RECONSTRUCTED for TSLA.

### 015 TOL 2024
IBD retrospective oracle: CUP_WITH_HANDLE pivot 128.75; breakout occurred one week before the 2024-05-22 selloff, reconstructed as 2024-05-15. Daily replay: O 131.56 / H 135.37 / L 131.05 / C 134.92; volume 2,067,000 vs prior50 1,213,256 (~1.704x); close +4.7922% and inside 5% zone. T+1 open 133.91, +4.0078%, inside zone. Frozen engine does not reconstruct the 128.75 source-target CWH; representative candidates are faulted BELOW_CUP_MIDPOINT. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.


## CWH numeric audit 006 — TOL 2024

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITH_HANDLE | source-near open-right-edge CUP_WITH_HANDLE_AMBIGUOUS | same family / nearby structure found |
| Pivot | 128.75 | 130.63000488 | +1.880005 / **+1.4602%** |
| Source-near right rim | source pivot area 128.75 | 2024-04-01 / 130.63000488 | near, not exact |
| Source-near handle low | not numerically frozen from source | 2024-04-19 | not scored |
| Engine depth field | no numeric source depth frozen | 9.866872% on the narrower source-near candidate | not scored |
| Final state | valid CWH per source | AMBIGUOUS | categorical mismatch |
| Fault on narrower source-near candidate | source accepts structure | DEEP_HANDLE_EXCEPTIONAL | **true morphology-semantics gap** |
| Breakout date | reconstructed 2024-05-15 from retrospective source timing | high 135.37 / close 134.92 crossed 128.75 | chronology/price corroborated, date remains reconstructed rather than explicit source date |
| Breakout volume | no source numeric ratio frozen | 1.70368x prior-50 | passes USSY 1.40 confirmation |
| Breakout close vs oracle pivot | breakout | +4.7922% | inside 5% zone |
| T+1 open vs oracle pivot | n/a to source morphology | +4.0078% | inside 5% zone |

Numeric adjudication: the full frozen output contains a much more relevant TOL CWH than the earlier shorthand implied. An open-right-edge candidate has right-rim/pivot 130.63000488 and handle low 2024-04-19. Its pivot is about **1.46% above** the 128.75 IBD oracle: a near match, but not practical-exact in the same sense as LRCX or TSLA. A narrower source-near candidate carries an engine depth of 9.866872%, but the frozen oracle has no source-published numeric depth with which to score it.

The defensible gap is therefore two-part: a modest pivot/structure-boundary difference plus the DEEP_HANDLE_EXCEPTIONAL semantic gate. The prior blanket SOURCE_TARGET_CWH_NOT_RECONSTRUCTED wording is too coarse because a nearby source-relevant CWH structure is in fact emitted.

Audit conclusion: **CWH_FAMILY_MATCH / PIVOT_NEAR_MATCH_1.46PCT / SOURCE_NEAR_STRUCTURE_FOUND / HANDLE_DEPTH_SEMANTICS_GAP**.

### 016 URBN 2025
IBD oracle: CUP_WITH_HANDLE pivot 74.45, breakout 2025-07-21. Daily replay: O 72.81 / H 75.98 / L 72.69 / C 74.62; volume 2,126,000 vs prior50 2,205,444 (~0.964x); close +0.2283%. T+1 open 75.79, +1.7999%, inside 5% zone. Frozen engine does not reproduce source-target 74.45 CWH; representative candidates carry DEEP_HANDLE_EXCEPTIONAL. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.


## CWH numeric audit 007 — URBN 2025

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITH_HANDLE | source-near open-right-edge CUP_WITH_HANDLE_AMBIGUOUS | same family / nearby structure found |
| Pivot | 74.45 | 75.80000305 | +1.350003 / **+1.8133%** |
| Source-near right rim | source pivot area 74.45 | 2025-05-28 / 75.80000305 | near, not exact |
| Source-near handle low | not numerically frozen from source | 2025-06-23 | not scored |
| Engine depth field | no numeric source depth frozen | 24.193839% | not scored |
| Final state | valid CWH per source | AMBIGUOUS | categorical mismatch |
| Faults on source-near candidate | source accepts structure | SHARP_V; DEEP_HANDLE_EXCEPTIONAL | **true morphology-semantics gap** |
| Breakout date | 2025-07-21 | high 75.98 / close 74.62 crossed 74.45 | **chronology corroborated** |
| Breakout volume | no source numeric ratio frozen | 0.96398x prior-50 | below USSY 1.40 confirmation; separate from morphology fidelity |
| Breakout close vs oracle pivot | breakout | +0.2283% | inside 5% zone |
| T+1 open vs oracle pivot | n/a to source morphology | +1.7999% | inside 5% zone |

Numeric adjudication: the full output contains a source-near open-right-edge CWH with pivot 75.80000305, about **1.81% above** the 74.45 oracle. This is materially closer to the source setup than the older 58–61 pivots visible among other emitted historical structures, so the earlier blanket SOURCE_TARGET_CWH_NOT_RECONSTRUCTED description is too coarse.

The engine nevertheless does not reproduce the oracle pivot as closely as LRCX or TSLA, and the source-near candidate remains AMBIGUOUS due to SHARP_V and DEEP_HANDLE_EXCEPTIONAL. Since no source numeric depth or handle landmarks are frozen, the engine's 24.193839% depth and handle date are retained as observations, not scored mismatches.

Audit conclusion: **CWH_FAMILY_MATCH / PIVOT_NEAR_MATCH_1.81PCT / SOURCE_NEAR_STRUCTURE_FOUND / SHARP_V_AND_HANDLE_DEPTH_SEMANTICS_GAP**.

### 017 SHOP 2025
IBD oracle: early-stage deep CUP_WITH_HANDLE pivot 112.38, breakout 2025-06-11. Daily replay: O 111.625 / H 117.36 / L 111.29 / C 114.13; volume 14,078,100 vs prior50 14,202,128 (~0.991x); close +1.5572%. T+1 open 113.25, +0.7742%, inside 5% zone. Frozen engine does not reproduce the source-target CWH; representative candidate pivot 111.00 is faulted BELOW_CUP_MIDPOINT. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.


## CWH numeric audit 008 — SHOP 2025

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | early-stage deep CUP_WITH_HANDLE | multiple CUP_WITH_HANDLE_AMBIGUOUS candidates | family vocabulary present |
| Pivot | 112.38 | 111.00 on closest pivot candidate | -1.38 / **-1.2280%** |
| Closest candidate right rim | source pivot area 112.38 | 2025-03-25 / 111.00 | near, not exact |
| Closest candidate handle low | not numerically frozen from source | 2025-04-04 | not scored |
| Closest candidate depth | no numeric source depth frozen | 22.937211% | not scored |
| Final state | valid CWH per source | AMBIGUOUS | categorical mismatch |
| Fault on closest-pivot candidate | source accepts structure | BELOW_CUP_MIDPOINT | **true morphology-semantics gap** |
| Breakout date | 2025-06-11 | high 117.36 / close 114.13 crossed 112.38 | **chronology corroborated** |
| Breakout volume | no source numeric ratio frozen | 0.99127x prior-50 | below USSY 1.40 confirmation; separate from morphology fidelity |
| Breakout close vs oracle pivot | breakout | +1.5572% | inside 5% zone |
| T+1 open vs oracle pivot | n/a to source morphology | +0.7742% | inside 5% zone |

Numeric adjudication: the earlier tranche summary already mentioned the 111.00 candidate but treated SHOP broadly as SOURCE_TARGET_CWH_NOT_RECONSTRUCTED. Full-output review shows that 111.00 is the **closest emitted CWH pivot to the 112.38 oracle**, only about **1.23% lower**. Its structural signature is LEFT_RIM 2024-11-13, CUP_LOW 2025-03-13, RIGHT_RIM 2025-03-25, HANDLE_LOW 2025-04-04, with engine depth 22.937211%.

Other emitted CWH candidates use materially higher pivots (115.37, 115.62, 120.72, 129.38), so the 111.00 structure is the defensible source-near numeric comparator. It remains AMBIGUOUS solely on BELOW_CUP_MIDPOINT. Because the frozen source record does not publish numeric depth or handle landmarks, those dimensions are observations rather than scored mismatches.

Audit conclusion: **CWH_FAMILY_MATCH / PIVOT_NEAR_MATCH_1.23PCT / SOURCE_NEAR_STRUCTURE_FOUND / HANDLE_MIDPOINT_SEMANTICS_GAP**. This refines the prior blanket SOURCE_TARGET_CWH_NOT_RECONSTRUCTED wording.

### 018 RBLX 2025
IBD/MarketSurge oracle: CUP_WITH_HANDLE pivot 74.24, breakout 2025-05-13. Daily replay: O 73.93 / H 77.24 / L 73.38 / C 77.02; volume 12,375,800 vs prior50 8,210,696 (~1.507x); close +3.7446%. T+1 open 77.40, +4.2565%, inside 5% zone. Frozen engine emits nearby CWH candidates but the representative 75.74 pivot is AMBIGUOUS/DEEP_HANDLE_EXCEPTIONAL rather than an exact source-target reconstruction. Classification: **MORPHOLOGY_FIDELITY_GAP / CWH_PIVOT_AND_HANDLE_SEMANTICS**.


## CWH numeric audit 009 — RBLX 2025

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITH_HANDLE | CWH candidates emitted; one RECOGNIZED, source-near candidate AMBIGUOUS | family recognition is clearly present |
| Pivot | 74.24 | 75.73999786 on closest source-near candidate | +1.499998 / **+2.0205%** |
| Source-near right rim | source pivot area 74.24 | 2025-02-05 / 75.73999786 | near, not exact |
| Source-near handle low | not numerically frozen from source | 2025-03-10 or open-right-edge 2025-04-07 depending lineage | not scored |
| Source-near depth | no numeric source depth frozen | 12.976403% on narrower candidate; 22.568656% on broader lineage | not scored |
| Final state at source-near pivot | valid CWH per source | AMBIGUOUS | categorical mismatch |
| Source-near faults | source accepts structure | DEEP_HANDLE_EXCEPTIONAL on narrower candidate; broader variants also SHARP_V / FRAGMENTED_BOTTOM | morphology-semantics gap |
| Other engine CWH | n/a | RECOGNIZED pivot 55.09999847, no faults | proves CWH family can reach RECOGNIZED, but this is **not** the oracle structure |
| Breakout date | 2025-05-13 | high 77.24 / close 77.02 crossed 74.24 | **chronology corroborated** |
| Breakout volume | no source numeric ratio frozen | 1.50728x prior-50 | passes USSY 1.40 confirmation |
| Breakout close vs oracle pivot | breakout | +3.7446% | inside 5% zone |
| T+1 open vs oracle pivot | n/a to source morphology | +4.2565% | inside 5% zone |

Numeric adjudication: RBLX requires separating **family recognition** from **source-target recognition**. The frozen engine does produce a fully RECOGNIZED CWH with no faults, but its pivot is 55.10 and therefore it is not the IBD 74.24 setup. The closest source-relevant emitted pivot is 75.73999786, about **2.02% above** the oracle. That nearby structure remains AMBIGUOUS, commonly due to DEEP_HANDLE_EXCEPTIONAL, with broader lineages also carrying SHARP_V / FRAGMENTED_BOTTOM.

Thus RBLX is neither a blanket CWH failure nor a source-target positive control. It is evidence that the detector can recognize CWH on the same security while selecting different structural boundaries from the oracle setup.

Audit conclusion: **CWH_FAMILY_RECOGNIZED_ON_SECURITY / SOURCE_PIVOT_NEAR_MATCH_2.02PCT / SOURCE_TARGET_STRUCTURE_AMBIGUOUS / BOUNDARY_AND_HANDLE_SEMANTICS_GAP**.

### 019 DUOL 2024
IBD/MarketSurge oracle: CUP_WITH_HANDLE pivot 241.86; source documents the setup and later reporting confirms a brief move past the buy point. Daily replay uses 2024-05-06 as the completed daily crossing: O 242.245 / H 251.30 / L 241.156 / C 248.20; volume 863,700 vs prior50 839,762 (~1.029x); close +2.6213%. T+1 2024-05-07 open 246.19, +1.7903%, inside 5% zone. Frozen engine does not exactly reconstruct the 241.86 source-target CWH; representative candidates include pivot 231.89 with FRAGMENTED_BOTTOM + BELOW_CUP_MIDPOINT. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.

### CWH family adjudication after 10 valid cases
The CWH tranche is now closed at **10/10**: LRCX, EW, NVO, OLED, TSLA, TOL, URBN, SHOP, RBLX, DUOL. The accumulated evidence shows repeated source-fidelity gaps, but they are not explained by one universal terminal gate: observed mechanisms include BELOW_CUP_MIDPOINT, assembly/handle-recognition misses, DEEP_HANDLE_EXCEPTIONAL, source-target base/pivot mismatch, and nearby-but-nonidentical handle/pivot semantics. This is strong evidence that CWH source fidelity of the frozen engine is not robust across authoritative historical examples, but **does not authorize detector tuning**. Any engine revision requires a separate morphology-engine workstream with positive and negative controls.


## CWH numeric audit 010 — DUOL 2024

Status: **AUDITED / SOURCE-FIDELITY DECOMPOSED / NO ENGINE CHANGE**.

| Field | Source oracle | Frozen reconstruction | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITH_HANDLE | multiple CWH candidates emitted, including RECOGNIZED structures | family recognition clearly present |
| Pivot | 241.86 | 241.86000061 on source-near candidates | +0.00000061 / **~+0.00000025%**; practical exact match |
| Source-near right rim | pivot 241.86 | 2024-03-01 / 241.86000061 | **practical exact pivot reconstruction** |
| Source-near handle lows | not numerically frozen from source | 2024-03-06 or open-right-edge 2024-04-16 depending lineage | not scored |
| Source-near depth | no numeric source depth frozen | 24.852033% or 24.319319% depending lineage | not scored |
| Final source-near state | valid CWH per source | AMBIGUOUS | categorical mismatch |
| Source-near faults | source accepts structure | DEEP_HANDLE_EXCEPTIONAL; alternate open-right-edge lineage FRAGMENTED_BOTTOM + BELOW_CUP_MIDPOINT | morphology-semantics gap |
| Other engine CWH | n/a | RECOGNIZED pivots 179.83999634 and 174.69999695, no faults | proves CWH family can reach RECOGNIZED, but these are not the oracle structure |
| Breakout/crossing date used in reconstruction | 2024-05-06 | high 251.30 / close 248.20 crossed 241.86 | **daily crossing corroborated** |
| Breakout volume | no source numeric ratio frozen | 1.02851x prior-50 | below USSY 1.40 confirmation; separate from morphology fidelity |
| Breakout close vs oracle pivot | crossing | +2.6213% | inside 5% zone |
| T+1 open vs oracle pivot | n/a to source morphology | +1.7903% | inside 5% zone |

Numeric adjudication: DUOL is a major refinement over the earlier tranche shorthand. The frozen engine reconstructs the oracle pivot **241.86 essentially exactly**: emitted source-near CWH candidates use pivot 241.86000061 from the 2024-03-01 right rim. Therefore the prior SOURCE_TARGET_CWH_NOT_RECONSTRUCTED wording is not defensible at pivot level.

The remaining disagreement is categorical morphology semantics. The source-near candidate with exact pivot is AMBIGUOUS because of DEEP_HANDLE_EXCEPTIONAL; an alternate open-right-edge lineage at the same pivot is AMBIGUOUS because of FRAGMENTED_BOTTOM and BELOW_CUP_MIDPOINT. The engine also emits unrelated fully RECOGNIZED CWH structures on DUOL, confirming that the family detector itself is operational.

Audit conclusion: **CWH_FAMILY_RECOGNIZED_ON_SECURITY / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / HANDLE_AND_BOTTOM_SEMANTICS_GAP**.


# CWOH completion tranche — cases 020–025

Status: **COMPLETE / 10 OF 10 CWOH GOLDEN CASES NOW PRESENT / NO ENGINE TUNING**.

The six cases below complete the CUP_WITHOUT_HANDLE tranche. Oracle facts were rechecked against IBD/MarketSurge material before replay. The frozen detector remains `33-core-p8-frozen-v1`; oracle values are comparison evidence only and are not detector inputs.

## 020 JPM 2023 — CUP_WITHOUT_HANDLE

- Source oracle: IBD identifies JPMorgan's August–November 2023 cup base and breakout in the week ended 2023-12-15. The prior-high pivot is **159.38**.
- Daily reconstruction date: **2023-12-15**. Yahoo provider basis: O 163.08 / H 165.28 / L 162.39 / C 165.23.
- Breakout volume: 20,309,300 vs prior-50 average 9,526,808 = **2.1318x**.
- Frozen engine: source-target CWOH **RECOGNIZED**, pivot **159.38000488**, practical exact match; an alternate lineage at the same pivot is AMBIGUOUS from FRAGMENTED_BOTTOM.
- T+1 2023-12-18 open 165.92 = **+4.1034%** vs pivot, inside original 5% buy zone.
- Adjudication: **SOURCE_FIDELITY_MATCH / CWOH_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH**.
- Authoritative replay: workflow run **35472174644**, job **105974993887**.

## 021 COST 2024 — CUP_WITHOUT_HANDLE

- Source oracle: IBD/MarketSurge cup base, pivot **787.08**; initial clearance **2024-05-10**, with a later renewed breakout on May 16.
- Daily reconstruction 2024-05-10: O 779.04 / H 787.45 / L 778.16 / C 787.19.
- Breakout volume: 1,652,700 vs prior-50 average 2,090,694 = **0.7905x**; morphology fidelity is separate from volume confirmation.
- Frozen engine: source-target CWOH **RECOGNIZED**, pivot **787.08001709**, no faults — practical exact match.
- T+1 2024-05-13 open 788.00 = **+0.1169%**, inside 5% zone.
- Adjudication: **SOURCE_FIDELITY_MATCH / CWOH_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH**.
- Authoritative replay: workflow run **35471986323**, job **105974484713**.

## 022 AX 2024 — CUP_WITHOUT_HANDLE

- Source oracle: IBD/MarketSurge cup base pivot **60.00**; IBD later records the stock moving above the cup-base buy point on **2024-05-06**.
- Daily reconstruction 2024-05-06: O 58.15 / H 60.23 / L 57.78 / C 59.68. Intraday high crossed the pivot but the close finished below it.
- Breakout-day volume: 608,100 vs prior-50 average 492,006 = **1.2360x**.
- Frozen engine: source-target CWOH pivot **60.00 exactly**, but state **AMBIGUOUS** with `FRAGMENTED_BOTTOM`.
- T+1 2024-05-07 open 59.80 = **-0.3333%** vs pivot, below the original buy zone.
- Adjudication: **CWOH_FAMILY_MATCH / PIVOT_EXACT_MATCH / SOURCE_TARGET_AMBIGUOUS / FRAGMENTED_BOTTOM_SEMANTICS_GAP**.
- Authoritative replay: workflow run **35471986323**, job **105974484640**.

## 023 NFLX 2024 — CUP_WITHOUT_HANDLE

- Source oracle: IBD/MarketSurge six-week cup base, pivot **697.49**, breakout **2024-08-20**.
- Corporate-action adaptation: current Yahoo history reflects the later 2025 10-for-1 split; replay restores the contemporaneous 2024 basis by **x10 OHLC / ÷10 volume**.
- Daily reconstruction: O 688.86 / H 711.33 / L 688.25 / C 698.54.
- Breakout volume: 4,813,100 vs prior-50 average 3,348,412 = **1.4374x**, above the 1.40 USSY confirmation threshold.
- Frozen engine: source-target CWOH **RECOGNIZED**, pivot **697.49000549**, no faults — practical exact match.
- T+1 2024-08-21 open 697.00 = **-0.0703%** vs pivot, fractionally below pivot.
- Adjudication: **SOURCE_FIDELITY_MATCH / CWOH_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH**.
- Authoritative corrected replay: workflow run **35472064980**, job **105974698199**.

## 024 ALL 2024 — CUP_WITHOUT_HANDLE

- Source oracle: IBD identifies a cup-without-handle/cup-base entry at **168.05**; the stock reclaimed the pivot on **2024-04-18**.
- Daily reconstruction: O 165.10 / H 169.53 / L 164.68 / C 169.11.
- Breakout volume: 2,068,300 vs prior-50 average 1,747,922 = **1.1833x**.
- Frozen engine: source-target CWOH **RECOGNIZED**, pivot **168.05000305**, no faults — practical exact match. The engine also emits a CWH interpretation at the same pivot, so cross-pattern overlap is preserved rather than hidden.
- T+1 2024-04-19 open 170.01 = **+1.1663%**, inside 5% zone.
- Adjudication: **SOURCE_FIDELITY_MATCH / CWOH_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH / CROSS_PATTERN_OVERLAP_PRESENT**.
- Authoritative replay: workflow run **35471986323**, job **105974484898**.

## 025 NVDA 2023 — CUP_WITHOUT_HANDLE

- Source oracle: IBD historical teaching example identifies a six-week cup without handle with pivot **187.90** and breakout in the week ended 2023-01-27. Daily reconstruction establishes the first crossing on **2023-01-23**.
- Corporate-action adaptation: current Yahoo history reflects Nvidia's later 2024 10-for-1 split; replay restores contemporaneous basis by **x10 OHLC / ÷10 volume**.
- Daily crossing 2023-01-23: O 180.64 / H 192.45 / L 178.18 / C 191.93.
- Breakout volume: 65,516,300 vs prior-50 average 45,508,718 = **1.4396x**, above the 1.40 threshold.
- Frozen engine emits the exact oracle pivot **187.90000916**, but that narrow source-target lineage is **REJECTED / TOO_SHORT**. The detector also emits nearby fully RECOGNIZED CWOH structures, including pivot 191.63999557.
- The exact source base spans 2022-12-13 to 2023-01-23: approximately six calendar weeks but fewer than the detector's minimum-session gate. This isolates a duration-semantics disagreement rather than a pivot-generation miss.
- T+1 2023-01-24 open 188.27 = **+0.1969%**, inside 5% zone.
- Adjudication: **CWOH_FAMILY_MATCH / PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_TARGET_REJECTED_TOO_SHORT / CALENDAR_WEEK_VS_SESSION_DURATION_SEMANTICS_GAP**.
- Authoritative corrected replay: workflow run **35472174644**, job **105974994015**.

## CWOH tranche status after cases 020–025

CUP_WITHOUT_HANDLE golden reconstruction is now **10/10 complete**:

- existing: AMD 2019, AVTR 2021, SE 2019, AMZN 2023;
- completion tranche: JPM 2023, COST 2024, AX 2024, NFLX 2024, ALL 2024, NVDA 2023.

The completion tranche materially improves the evidence balance: **JPM, COST, NFLX and ALL are source-target positive controls with practical-exact pivots**; AX isolates `FRAGMENTED_BOTTOM`; NVDA isolates a `TOO_SHORT` duration-semantics disagreement despite an exact pivot. No detector threshold or frozen engine code was changed to obtain these outcomes.


# DOUBLE_BOTTOM completion tranche — cases 026–032

Status: **COMPLETE / 10 OF 10 DOUBLE_BOTTOM GOLDEN CASES NOW PRESENT / NO ENGINE TUNING**.

The seven cases below complete the DOUBLE_BOTTOM tranche. They use the frozen Pattern Engine at `c433cc1e35a5aa32a46f732cd8c5545935e36e40`. Oracle family/pivot values remain comparison evidence only and are never detector inputs. Corrected replay run **35474785663** is authoritative for this tranche. The replay boundary is the first completed daily close at or above the oracle pivot inside the source-bounded chronology window; this corrects the earlier intraday-high boundary and keeps the original/source layer distinct from USSY T+1 execution.

## 026 LLY 2024 — DOUBLE_BOTTOM

- Source oracle: DOUBLE_BOTTOM, pivot **793.67**.
- Corrected daily crossing: **2024-05-21**; close **+1.1970%** versus oracle pivot.
- Breakout volume: **1.6553x** prior-50-session mean.
- Frozen engine emits a source-target DOUBLE_BOTTOM **RECOGNIZED** at pivot **793.66998291**, practical exact match. Nearby alternate DB lineages at 795.50 and 800.78 are preserved rather than substituted for the source target.
- T+1 open: **+0.9236%** versus pivot, inside the original 5% buy zone.
- Adjudication: **SOURCE_FIDELITY_MATCH / DOUBLE_BOTTOM_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH**.

## 027 FIS 2024 — DOUBLE_BOTTOM

- Source oracle: stage-one DOUBLE_BOTTOM, pivot **77.83**.
- Corrected daily crossing: **2024-08-13**; close **+0.5525%** versus oracle pivot.
- Breakout volume: **1.2219x** prior-50-session mean.
- Frozen engine does not emit the exact 77.83 source-target DB as RECOGNIZED at the corrected cutoff. The closest observed DB pivot is **78.73000336**, about **+1.156%** versus oracle, and remains AMBIGUOUS.
- T+1 open: **+0.6553%** versus pivot, inside the original 5% buy zone.
- Adjudication: **DOUBLE_BOTTOM_FAMILY_CANDIDATE_PRESENT / SOURCE_PIVOT_NEAR_MATCH_1.16PCT / SOURCE_TARGET_NOT_RECOGNIZED / MORPHOLOGY_BOUNDARY_GAP**.

## 028 CAG 2024 — DOUBLE_BOTTOM

- Source oracle: DOUBLE_BOTTOM elements / entry **29.89**.
- Corrected daily crossing: **2024-04-04**; close **+2.5092%** versus oracle pivot.
- Breakout volume: **2.7902x** prior-50-session mean.
- Frozen engine's closest source-relevant DB candidate uses pivot **30.69000053**, about **+2.676%** versus oracle, and is AMBIGUOUS.
- T+1 open: **+2.7434%** versus pivot, inside the original 5% buy zone.
- Adjudication: **DOUBLE_BOTTOM_FAMILY_CANDIDATE_PRESENT / SOURCE_PIVOT_NEAR_MATCH_2.68PCT / SOURCE_TARGET_AMBIGUOUS / MORPHOLOGY_BOUNDARY_GAP**.

## 029 STRL 2024 — DOUBLE_BOTTOM

- Source oracle: first-stage DOUBLE_BOTTOM, pivot **130.89**.
- Corrected daily crossing: **2024-09-18**; close **+3.0942%** versus oracle pivot.
- Breakout volume: **1.3331x** prior-50-session mean.
- Frozen engine emits source-target DOUBLE_BOTTOM **RECOGNIZED** at pivot **130.88999939**, practical exact match, with no need to substitute a neighboring lineage.
- T+1 open: **+6.1884%** versus pivot, above the original 5% buy-zone ceiling.
- Adjudication: **SOURCE_FIDELITY_MATCH / DOUBLE_BOTTOM_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH / USSY_T1_EXTENDED_ABOVE_5PCT_ZONE**.

## 030 URI 2024 — DOUBLE_BOTTOM

- Source oracle: DOUBLE_BOTTOM, pivot **715.34**.
- Corrected daily crossing: **2024-07-16**; close **+3.8681%** versus oracle pivot.
- Breakout volume: **1.2151x** prior-50-session mean.
- Frozen engine emits source-target DOUBLE_BOTTOM **RECOGNIZED** at pivot **715.34002686**, practical exact match. Alternate nearby lineages are retained as detector output but do not replace the source target.
- T+1 open: **+2.2800%** versus pivot, inside the original 5% buy zone.
- Adjudication: **SOURCE_FIDELITY_MATCH / DOUBLE_BOTTOM_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH**.

## 031 UBS 2024 — DOUBLE_BOTTOM

- Source oracle: DOUBLE_BOTTOM, pivot **31.45**.
- Corrected daily crossing: **2024-10-09**; close **+0.4134%** versus oracle pivot.
- Breakout volume: **0.3699x** prior-50-session mean; volume confirmation is kept separate from morphology fidelity.
- Frozen engine emits DOUBLE_BOTTOM **RECOGNIZED** at pivot **31.45499992**, only about **+0.016%** versus oracle and therefore a practical pivot match. Other nearby DB lineages remain visible.
- T+1 open: **+0.4769%** versus pivot, inside the original 5% buy zone.
- Adjudication: **SOURCE_FIDELITY_MATCH / DOUBLE_BOTTOM_RECOGNIZED / PIVOT_PRACTICAL_MATCH**.

## 032 NXPI 2024 — DOUBLE_BOTTOM

- Source oracle: DOUBLE_BOTTOM, pivot **251.96**.
- Corrected daily crossing: **2024-05-02**; close **+0.9128%** versus oracle pivot.
- Breakout volume: **0.9718x** prior-50-session mean.
- Frozen engine emits source-target DOUBLE_BOTTOM **RECOGNIZED** at pivot **251.96000671**, practical exact match. Ambiguous/rejected alternate lineages at the same pivot are preserved as cross-lineage evidence.
- T+1 open: **+3.5879%** versus pivot, inside the original 5% buy zone.
- Adjudication: **SOURCE_FIDELITY_MATCH / DOUBLE_BOTTOM_RECOGNIZED / PIVOT_PRACTICAL_EXACT_MATCH / MULTI_LINEAGE_STATE_OVERLAP_PRESENT**.

## DOUBLE_BOTTOM tranche status after cases 026–032

DOUBLE_BOTTOM golden reconstruction is now **10/10 complete**: the prior three cases plus LLY, FIS, CAG, STRL, URI, UBS and NXPI.

The completion tranche provides five strong source-target pivot/family matches (LLY, STRL, URI, UBS, NXPI) and two informative source-target morphology/boundary gaps (FIS, CAG). These mismatches are retained as validation evidence and **do not authorize tuning** of the frozen detector. Breakout-volume observations and USSY T+1 observations remain separate layers and do not retroactively alter morphology adjudication.

Overall golden reconstruction progress after this freeze: **32/40 = 80%**. CWH **10/10**, CWOH **10/10**, DOUBLE_BOTTOM **10/10**, FLAT_BASE **2/10**. Per batch governance, stop here before starting the FLAT_BASE completion tranche.


## CWOH numeric audit 001 — AMD 2019

Status: **AUDITED / SOURCE-FIDELITY MATCH / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from authoritative replay run **35411908528** rather than relying on a representative candidate.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 35.55 | 35.54999924 | -0.00000076 / **~0.0000021%**; practical exact match |
| Source cup low | 27.43 | 27.43000031 on 2019-10-03 | **practical exact landmark match** |
| Cup depth | source numeric depth not frozen | 22.841066% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source comparable numeric duration not frozen | engine structure 2019-08-09 through 2019-11-04 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout | 2019-11-04 | H 36.45 / C 36.29 above 35.55 | **daily crossing confirmed** |
| Breakout volume | source context about +67% | 1.6855x prior-50 = +68.55% | **strong corroboration; ~+1.55 pp vs rounded source context** |
| T+1 open | n/a to source morphology | 36.56 = +2.8411% vs pivot | inside original 5% zone; operationalization only |

All frozen CWOH candidates were considered. The source-near candidate is not merely the first or a convenient RECOGNIZED candidate: it uses **LEFT_RIM 2019-08-09 / CUP_LOW 2019-10-03**, pivot **35.54999924**, depth **22.841066%**, status **RECOGNIZED**, and no detector faults. Other CWOH candidates exist at pivots including 34.86, 34.30, 32.05, 29.95 and 21.44, but they are not substituted for the oracle structure.

The source-reported cup low **27.43** is independently reconstructed at **27.43000031**, while the oracle pivot **35.55** is reconstructed essentially exactly. The source material frozen for this case does not provide a numeric cup-depth or directly comparable duration value, so the engine's depth and duration are retained as evidence but not scored.

Numeric adjudication: AMD is a clean positive control for CWOH. The engine finds the correct family, source-target structure, pivot and source-reported trough, reaches RECOGNIZED with no faults, and the reconstructed breakout-day volume closely corroborates the source's rounded strong-volume description.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH / CUP_LOW_PRACTICAL_EXACT_MATCH / RECOGNIZED_NO_FAULTS**.


## CWOH numeric audit 002 — AVTR 2021

Status: **AUDITED / PRIOR SHORTHAND SUPERSEDED / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from replay run **35439158198**. It supersedes the earlier statement that no emitted CWOH pivot was near the 33.99 oracle.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 33.99 | 33.99000168 | +0.00000168 / **~+0.0000049%**; practical exact match |
| Source-target landmarks | source numeric landmarks beyond pivot not frozen | LEFT_RIM 2021-04-29 / CUP_LOW 2021-05-11 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 12.974409% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source comparable numeric duration not frozen | source-near structure present through 2021-06-16 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout | 2021-06-16 | H 34.50 / C 34.05 above 33.99 | **daily crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 1.3773x prior-50 / +37.73% | separate breakout evidence; not morphology-scored |
| T+1 open | n/a to source morphology | 34.05 = +0.1765% vs pivot | inside original 5% zone; operationalization only |

All emitted CWOH candidates were inspected. The closest candidate is **RECOGNIZED** with LEFT_RIM **2021-04-29**, CUP_LOW **2021-05-11**, pivot **33.99000168**, depth **12.974409%**, and **no detector faults**. Other CWOH outputs at 31.05, 30.99, 30.73, 28.98, 25.70, 19.50 and 18.09 are alternate structures and must not replace the exact source-near candidate.

This materially changes the earlier adjudication. The prior wording `SOURCE_TARGET_BASE_NOT_RECONSTRUCTED` resulted from inspecting a representative recognized structure rather than the full candidate set. The frozen output itself contains a practically exact 33.99 source-target pivot and a clean RECOGNIZED CWOH candidate.

Numeric adjudication: AVTR is a second positive CWOH source-fidelity control at the fields the current oracle can score. Depth, duration and detailed landmark fidelity remain unscored because the frozen source oracle does not provide comparable numeric values for those fields.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH / RECOGNIZED_NO_FAULTS**.


## CWOH numeric audit 003 — SE 2019

Status: **AUDITED / PRIOR PIVOT-GEOMETRY SHORTHAND REFINED / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from replay run **35439712313**, using the IBD oracle pivot **38.10** and breakout date **2019-11-20** only for post-replay adjudication.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 38.10 | 38.00 | -0.10 / **-0.2625%**; near match |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_RIM 2019-08-02 / CUP_LOW 2019-10-21 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 30.5000% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source comparable numeric duration not frozen | source-near structure present through oracle date | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout | 2019-11-20 intraday pivot cross | H 38.98 > 38.10; C 37.27 < 38.10 | **intraday daily-bar cross corroborated; close faded below pivot** |
| Breakout volume | source numeric oracle not frozen | 1.2136x prior-50 / +21.36% | separate breakout evidence; not morphology-scored |
| T+1 open | n/a to source morphology | 37.28 = -2.1522% vs oracle pivot | below pivot; operationalization only |

All frozen CWOH candidates were inspected. The source-nearest candidate is **RECOGNIZED**, LEFT_RIM **2019-08-02**, CUP_LOW **2019-10-21**, pivot **38.00**, depth **30.50%**, with **no detector faults**. This candidate is materially closer to the 38.10 oracle than the previously highlighted 36.90000153 candidate. Other recognized CWOH pivots include 37.00, 36.90000153, 32.93, 32.00, 25.00 and 13.09.

The oracle-to-engine pivot delta is only **-0.10 (-0.2625%)**. Therefore the earlier characterization as a broad `CWOH_PIVOT_GEOMETRY_MISMATCH` was too coarse. The engine recognizes the correct family and contains a source-near, fault-free structure with a pivot within about 0.26% of the oracle. Because the frozen source does not supply numeric depth, duration, or defensible landmark dates, those dimensions remain NOT SCORED.

The breakout-day evidence remains distinct: the daily high **38.98** crossed the oracle pivot **38.10**, while the close **37.27** finished below it. This corroborates the source's intraday pivot-cross description without converting it into a close-confirmed breakout. T+1 open **37.28** remained below the oracle pivot and is an execution-layer observation only.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_NEAR_STRUCTURE_FOUND / PIVOT_NEAR_MATCH_0.26PCT / RECOGNIZED_NO_FAULTS / INTRADAY_ORACLE_BREAKOUT_CROSS_CORROBORATED**.


## CWOH numeric audit 004 — AMZN 2023

Status: **AUDITED / PRIOR SOURCE-TARGET-NOT-RECONSTRUCTED CLASSIFICATION SUPERSEDED / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from replay run **35439948453**. The oracle remains CWOH with buy point **145.86**; the daily-bar replay identifies the first actual oracle-pivot cross on **2023-11-20**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 145.86 | 145.86000061 | +0.00000061 / **~+0.00000042%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_RIM 2023-09-14 / CUP_LOW 2023-10-26 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 18.860553% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source comparable numeric duration not frozen | source-near structure present through oracle date | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | source identifies CWOH | AMBIGUOUS | **downstream morphology-state gap** |
| Faults | source accepts structure | SHARP_V; FRAGMENTED_BOTTOM | **bottom-shape semantics gap** |
| Breakout | first daily oracle-pivot cross 2023-11-20 | H 146.63 / C 146.13 above 145.86 | **daily crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 0.7554x prior-50 / -24.46% | separate breakout evidence; not morphology-scored |
| T+1 open | n/a to source morphology | 143.91 = -1.3369% vs pivot | below pivot; operationalization only |

All frozen CWOH candidates were inspected. Crucially, the frozen engine does contain a source-near candidate with **LEFT_RIM 2023-09-14**, **CUP_LOW 2023-10-26**, and pivot **145.86000061**. Its pivot is a practical exact match to the **145.86** oracle. The candidate is not RECOGNIZED, however: it is **AMBIGUOUS** because of **SHARP_V** and **FRAGMENTED_BOTTOM**. Other CWOH candidates at 143.63000488, 134.47999573, 114.00 and 110.86000061 are alternate structures and must not be substituted for this source-target candidate.

This materially supersedes the earlier `SOURCE_TARGET_BASE_NOT_RECONSTRUCTED` diagnosis, which arose from highlighting the recognized 110.86 structure. The source-target pivot and structure are in fact present; the disagreement occurs at morphology-state gating after candidate construction.

The breakout layer remains separate. On 2023-11-20 both high and close crossed 145.86, with close +0.1851% above pivot and inside the original 5% zone, but volume was only about **0.7554x** the prior-50 mean. T+1 open **143.91** fell back below the oracle pivot; that is a USSY execution observation, not an O'Neil morphology failure.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_TARGET_STRUCTURE_AMBIGUOUS / SHARP_V_AND_FRAGMENTED_BOTTOM_SEMANTICS_GAP**.


## CWOH numeric audit 005 — JPM 2023

Status: **AUDITED / SOURCE-FIDELITY MATCH / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from authoritative replay run **35472174644**, job **105974993887**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 159.38 | 159.38000488 | +0.00000488 / **~+0.0000031%**; practical exact match |
| Source-target landmarks | source describes Aug-Nov cup; exact numeric landmark dates not frozen | LEFT_RIM 2023-07-31 / CUP_LOW 2023-10-05 | **NOT SCORED / SOURCE LANDMARK BOUNDARIES NOT NUMERICALLY COMPARABLE** |
| Cup depth | source numeric depth not frozen | 11.638852% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source describes Aug-Nov base; exact comparable duration not frozen | source-near lineage through breakout | **NOT SCORED / SOURCE BOUNDARY NOT NUMERICALLY COMPARABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout | week ended 2023-12-15 | 2023-12-15 H 165.28 / C 165.23 above 159.38 | **daily crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 2.1318x prior-50 / +113.18% | strong separate breakout evidence |
| T+1 open | n/a to source morphology | 165.92 = +4.1034% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | provider basis unchanged; identity transform | **no corporate-action transform applied** |

All emitted CWOH candidates were inspected. The closest source-target lineage is **RECOGNIZED**, LEFT_RIM **2023-07-31**, CUP_LOW **2023-10-05**, pivot **159.38000488**, depth **11.638852%**, with no detector faults. A second lineage at the same exact-practical pivot is **AMBIGUOUS** with CUP_LOW **2023-10-27** and `FRAGMENTED_BOTTOM`; it does not displace the clean recognized source-near candidate. Other CWOH pivots include 153.11000061, 144.33999634 and 143.36999512.

The important component-level result is that both a clean RECOGNIZED lineage and an alternate ambiguous lineage exist at the oracle pivot. Therefore the alternate `FRAGMENTED_BOTTOM` candidate is evidence of boundary sensitivity, but it is not a source-fidelity failure because the engine independently emits a fault-free source-near CWOH at the same pivot.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH / RECOGNIZED_NO_FAULTS / ALTERNATE_SAME_PIVOT_BOUNDARY_SENSITIVE_LINEAGE_PRESENT**.


## CWOH numeric audit 006 — COST 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from authoritative replay run **35471986323**, job **105974484713**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 787.08 | 787.08001709 | +0.00001709 / **~+0.0000022%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_RIM 2024-03-07 / CUP_LOW 2024-04-03 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 11.410530% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source comparable numeric duration not frozen | source-near lineage through breakout | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Initial clearance | 2024-05-10 | H 787.45 / C 787.19 above 787.08 | **daily crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 0.7905x prior-50 / -20.95% | separate breakout evidence; not morphology-scored |
| T+1 open | n/a to source morphology | 788.00 = +0.1169% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | provider basis unchanged; identity transform | **no corporate-action transform applied** |

The complete frozen CWOH set contains only two unique CWOH structures: the source-near 2024 lineage at pivot **787.08001709**, and an older recognized structure at pivot **530.04998779**. The source-near candidate is unambiguous: LEFT_RIM **2024-03-07**, CUP_LOW **2024-04-03**, depth **11.410530%**, status **RECOGNIZED**, and no detector faults.

The pivot delta from oracle **787.08** is only **+0.00001709**, a practical exact match. No alternate same-era candidate competes with the source-target interpretation. Source numeric depth, exact landmark boundaries, and comparable duration are not frozen, so those dimensions remain NOT SCORED rather than inferred.

The 2024-05-10 daily high and close both clear the oracle pivot, but volume is only **0.7905x** the prior-50 mean. This is a breakout-volume observation separate from morphology fidelity. The later May 16 renewed breakout noted in the source does not change the morphology adjudication of the initial clearance.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH / RECOGNIZED_NO_FAULTS**.


## CWOH numeric audit 007 — AX 2024

Status: **AUDITED / SOURCE-TARGET STRUCTURE FOUND BUT AMBIGUOUS / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from authoritative replay run **35471986323**, job **105974484640**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 60.00 | 60.00 | **exact match** |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_RIM 2024-01-31 / CUP_LOW 2024-04-16 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 19.200001% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source comparable numeric duration not frozen | source-target lineage through oracle date | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | source identifies CWOH | AMBIGUOUS | **morphology-state gap** |
| Faults | source accepts structure | FRAGMENTED_BOTTOM | **bottom-shape semantics gap** |
| Breakout | 2024-05-06 intraday clearance | H 60.23 > 60.00; C 59.68 < 60.00 | **intraday daily-bar cross corroborated; close below pivot** |
| Breakout volume | source numeric oracle not frozen | 1.2360x prior-50 / +23.60% | separate breakout evidence |
| T+1 open | n/a to source morphology | 59.80 = -0.3333% vs pivot | below pivot; operationalization only |
| Price basis | contemporaneous oracle basis | provider basis unchanged; identity transform | **no corporate-action transform applied** |

All frozen CWOH candidates were inspected. The source-target candidate is explicit: LEFT_RIM **2024-01-31**, CUP_LOW **2024-04-16**, pivot **60.00 exactly**, depth **19.200001%**. It is **AMBIGUOUS** solely from `FRAGMENTED_BOTTOM`. Other same-era CWOH candidates at 57.11999893 and 55.63999939 are also ambiguous from `FRAGMENTED_BOTTOM`; a shorter structure at 54.63999939 is RECOGNIZED without faults but is not substituted for the oracle-pivot structure.

Therefore AX cleanly separates candidate construction from final morphology gating: the engine finds the oracle family and exact oracle pivot, but its bottom-shape semantics do not accept the source-target structure as RECOGNIZED.

The source's 2024-05-06 move above the buy point is corroborated as an intraday cross by H **60.23**, while C **59.68** finishes below the pivot. T+1 open **59.80** also remains below pivot. Neither observation changes the morphology classification.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_EXACT_MATCH / SOURCE_TARGET_STRUCTURE_AMBIGUOUS / FRAGMENTED_BOTTOM_SEMANTICS_GAP**.


## CWOH numeric audit 008 — NFLX 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH AFTER EXPLICIT BASIS NORMALIZATION / REPLAY-DIAGNOSTIC BASIS DEFECT FOUND / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from authoritative replay run **35471986323**, job **105974484601**. NFLX requires special handling because current Yahoo history is on the later 2025 10-for-1 split basis while the 2024 oracle is pre-split.

| Field | Source oracle | Frozen output / normalized comparison | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 697.49 pre-split | engine 69.74900055 split-adjusted = **697.4900055 x10** | **practical exact match after basis normalization** |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_RIM 2024-07-05 / CUP_LOW 2024-08-05 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 15.835355% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout 2024-08-20 | pivot 697.49 | raw Yahoo H 71.133 / C 69.853996; normalized H **711.33** / C **698.53996** | **high and close above oracle after x10 normalization** |
| Breakout volume | source numeric oracle not frozen | ratio **1.4374x prior-50**; ratio invariant to /10 volume normalization | separate breakout evidence |
| T+1 open | n/a to source morphology | raw 69.699997; normalized **696.99997**, about **-0.0703%** vs pivot | slightly below pivot; operationalization only |
| Price basis | contemporaneous 2024 pre-split | metadata declares `LATER_10_FOR_1_SPLIT_RESTORED`, x10 OHLC / ÷10 volume | **declared adaptation is correct, but diagnostics remain on raw provider basis** |

All frozen CWOH candidates were inspected. The source-nearest structure is unambiguous: LEFT_RIM **2024-07-05**, CUP_LOW **2024-08-05**, raw split-adjusted pivot **69.74900055**, depth **15.835355%**, status **RECOGNIZED**, no faults. Applying the replay's own declared x10 price-basis normalization yields **697.4900055**, a practical exact match to oracle **697.49**. Other CWOH pivots (63.90000153, 37.94300079, 34.97999954) are alternate structures.

The audit also finds an important replay-evidence defect. The run metadata correctly declares `price_transform: x10` and `volume_transform: /10`, but `breakout_day_assessment` and `ussy_t1_execution_observation` were calculated from the raw split-adjusted Yahoo OHLC while compared directly with the pre-split oracle pivot. Consequently the frozen diagnostic fields incorrectly report roughly **-90%** versus pivot and false crossing/buy-zone booleans. These diagnostic percentages/booleans must **not** be used as-is for NFLX.

On a common pre-split basis, 2024-08-20 becomes approximately O **688.86**, H **711.33**, L **688.25**, C **698.54**; both high and close clear 697.49. T+1 open normalizes to about **697.00**, only **-0.0703%** below pivot. The volume ratio remains **1.4374x** because the same volume transform applies to both numerator and historical average.

This is an evidence-pipeline basis-application defect, not a frozen pattern-engine morphology failure. The source-target CWOH remains a source-fidelity match after explicit basis normalization.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH_AFTER_BASIS_NORMALIZATION / RECOGNIZED_NO_FAULTS / REPLAY_DIAGNOSTIC_PRICE_BASIS_APPLICATION_DEFECT**.


## CWOH numeric audit 009 — ALL 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from authoritative replay run **35471986323**, job **105974484898**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 168.05 | 168.05000305 | +0.00000305 / **~+0.0000018%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_RIM 2024-02-08 / CUP_LOW 2024-03-04 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 8.437969% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Duration | source comparable numeric duration not frozen | source-near lineage through oracle date | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout | 2024-04-18 | H 169.53 / C 169.11 above 168.05 | **daily crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 1.1833x prior-50 / +18.33% | separate breakout evidence |
| T+1 open | n/a to source morphology | 170.01 = +1.1663% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | provider basis unchanged; identity transform | **no corporate-action transform applied** |

All frozen CWOH candidates were inspected. The 2024 source-target lineage is unique and clean: LEFT_RIM **2024-02-08**, CUP_LOW **2024-03-04**, pivot **168.05000305**, depth **8.437969%**, status **RECOGNIZED**, with no detector faults. The only other CWOH candidates are older 2023 structures at pivots 114.97000122 and 114.08999634, both recognized but unrelated to the oracle target.

The oracle-to-engine pivot delta is effectively zero. No competing same-era lineage or morphology fault complicates the source-target adjudication. Source numeric depth, exact landmark boundaries, and comparable duration are unavailable, so those dimensions remain NOT SCORED.

On 2024-04-18 both high and close clear the oracle pivot; close is +0.6308% above it and inside the original 5% zone. Volume is 1.1833x the prior-50 mean, retained as separate breakout evidence. T+1 open 170.01 is +1.1663% above pivot and remains inside the 5% zone.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH / RECOGNIZED_NO_FAULTS**.


## CWOH numeric audit 010 — NVDA 2023

Status: **AUDITED / SOURCE-TARGET MATCH AFTER EXPLICIT SPLIT-BASIS NORMALIZATION / REPLAY-DIAGNOSTIC BASIS DEFECT CONFIRMED / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen CWOH candidate set from authoritative replay run **35471986323**, job **105974484647**. NVDA requires explicit basis normalization because current Yahoo history reflects the later 2024 10-for-1 split while the 2023 oracle is pre-split.

| Field | Source oracle | Frozen output / normalized comparison | Delta / result |
|---|---:|---:|---|
| Pattern family | CUP_WITHOUT_HANDLE | CUP_WITHOUT_HANDLE | **family exact match** |
| Pivot | 187.90 pre-split | engine 18.79000092 split-adjusted = **187.9000092 x10** | **practical exact match after basis normalization** |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_RIM 2022-12-13 / CUP_LOW 2022-12-28 | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Cup depth | source numeric depth not frozen | 26.109637% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid CWOH | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout 2023-01-27 | pivot 187.90 | raw H 20.628 / C 20.365; normalized H **206.28** / C **203.65** | **high and close above oracle after x10 normalization** |
| Breakout volume | source numeric oracle not frozen | ratio **1.2080x prior-50**; invariant to /10 normalization | separate breakout evidence |
| T+1 open | n/a to source morphology | raw 19.950001; normalized **199.500008**, **+6.1735%** vs pivot | above original 5% zone; operationalization only |
| Price basis | contemporaneous 2023 pre-split | metadata declares `LATER_10_FOR_1_SPLIT_RESTORED`, x10 OHLC / ÷10 volume | **declared adaptation correct; diagnostics remain raw-provider-basis** |

All frozen CWOH candidates were inspected. Once candidates are compared on the oracle's pre-split basis, the source-nearest structure is the **RECOGNIZED** candidate LEFT_RIM **2022-12-13**, CUP_LOW **2022-12-28**, raw pivot **18.79000092**, depth **26.109637%**, with no detector faults. Normalized by x10, its pivot is **187.9000092**, a practical exact match to oracle **187.90**.

Several earlier lineages have raw pivots above 28–34 but are REJECTED as `TOO_DEEP`; other recognized historical structures exist below the target. They do not displace the source-target candidate after basis normalization.

As with NFLX 2024, the replay metadata declares the correct x10 OHLC / ÷10 volume adaptation, but the frozen `breakout_day_assessment` and `ussy_t1_execution_observation` compare raw post-split Yahoo prices directly with the pre-split oracle. Their roughly -89% diagnostic values and false crossing flags are therefore basis-invalid. On a common pre-split basis, 2023-01-27 is approximately O **194.62**, H **206.28**, L **194.05**, C **203.65**; both high and close clear 187.90. T+1 open normalizes to approximately **199.50**, or **+6.17%** above pivot, beyond the original 5% buy-zone upper bound.

This independently confirms that the price-basis application defect found in NFLX is systematic for these later-split replay diagnostics, while the frozen pattern candidate itself remains source-faithful after normalization.

Audit conclusion: **CWOH_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH_AFTER_BASIS_NORMALIZATION / RECOGNIZED_NO_FAULTS / REPLAY_DIAGNOSTIC_PRICE_BASIS_APPLICATION_DEFECT**.

### CWOH numeric-audit closure

All **10/10** reconstructed CUP_WITHOUT_HANDLE golden cases have now received full-candidate numeric adjudication. The audit repeatedly showed that representative-candidate shorthand can materially misclassify source fidelity; full candidate inspection is required before declaring a source-target structure absent. The CWOH numeric-audit tranche is therefore **CLOSED** without tuning or modifying the frozen engine.


## DOUBLE_BOTTOM numeric audit 001 — LLY 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH / NO ENGINE CHANGE**.

This begins the one-by-one numeric adjudication of the already-frozen DOUBLE_BOTTOM reconstruction tranche. It re-inspects the complete frozen DOUBLE_BOTTOM candidate set from corrected authoritative replay run **35474785663**, job **105982053877**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family exact match** |
| Pivot | 793.67 | 793.66998291 | -0.00001709 / **~-0.0000022%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | LEFT_HIGH 2024-03-04 / TROUGH_1 2024-03-11 / MIDDLE_PEAK 2024-03-28 / TROUGH_2 2024-04-25 | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | 10.299962% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid double bottom | RECOGNIZED | **categorical match** |
| Faults | source accepts structure | none | **match** |
| Breakout | source-bounded first close >= pivot | 2024-05-21 H 816.61 / C 803.17 | **daily close crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 1.6553x prior-50 | separate breakout evidence |
| T+1 open | n/a to source morphology | 801.00 = +0.9236% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo, auto_adjust=false; no replay transform indicated | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. The source-nearest candidate is **RECOGNIZED**, with LEFT_HIGH **2024-03-04**, TROUGH_1 **2024-03-11**, MIDDLE_PEAK **2024-03-28**, TROUGH_2 **2024-04-25**, pivot **793.66998291**, depth **10.299962%**, and no detector faults. The engine also emits alternate lineages near 795.50 and 800.78 that are AMBIGUOUS/REJECTED because of `NO_SECOND_TROUGH_UNDERCUT` (and in one case `TOO_SHORT`), but these do not displace the clean oracle-pivot lineage.

The oracle-to-engine pivot delta is effectively zero. Because the source evidence frozen for this case does not provide numeric trough/peak dates or source depth, those geometry dimensions remain NOT SCORED rather than inferred from the engine.

The corrected replay uses the first daily **close** >= oracle pivot inside the source-bounded chronology window, yielding 2024-05-21. Close **803.17** is +1.1970% above pivot and volume is **1.6553x** the prior-50 mean. T+1 open **801.00** is +0.9236% above pivot and inside the original 5% zone.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / PIVOT_PRACTICAL_EXACT_MATCH / RECOGNIZED_NO_FAULTS**.


## DOUBLE_BOTTOM numeric audit 002 — FIS 2024

Status: **AUDITED / FAMILY PRESENT / SOURCE-NEAR PIVOT / SOURCE-TARGET REMAINS AMBIGUOUS / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from corrected authoritative replay run **35474785663**, job **105982053823**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family present** |
| Pivot | 77.83 | 78.73000336 | +0.90000336 / **+1.1564%**; near match |
| Source-target landmarks | source numeric landmarks not frozen | nearest lineage includes MIDDLE_PEAK 2024-05-20 / TROUGH_2 2024-08-05; multiple left-side alternatives | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | multiple candidate depths for the 78.73 lineage | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | source accepts stage-one double bottom | AMBIGUOUS | **morphology-state gap** |
| Faults | source accepts structure | NO_SECOND_TROUGH_UNDERCUT | **double-bottom trough semantics gap** |
| Breakout | source-bounded first close >= 77.83 | 2024-08-13 H 78.37 / C 78.26 | **daily close crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 1.2219x prior-50 | separate breakout evidence |
| T+1 open | n/a to source morphology | 78.34 = +0.6553% vs oracle pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo, auto_adjust=false | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. There is **no exact 77.83 engine pivot**. The closest family-consistent cluster is pivot **78.73000336**, only **+1.1564%** above the oracle. Multiple lineages share this pivot and the same right-side MIDDLE_PEAK **2024-05-20** / TROUGH_2 **2024-08-05**, but all are AMBIGUOUS because of `NO_SECOND_TROUGH_UNDERCUT`. Their left-side choices differ, so no single engine lineage should be promoted as an exact oracle geometry match without source numeric landmark evidence.

A second cluster at pivot **74.75** is farther from the oracle and is likewise AMBIGUOUS with `NO_SECOND_TROUGH_UNDERCUT`. Other lower-pivot candidates mainly carry `WEAK_MIDDLE_REBOUND`. Thus full-candidate inspection confirms rather than overturns the earlier coarse diagnosis: the engine detects the DOUBLE_BOTTOM family and constructs a source-near pivot, but its second-trough undercut semantics prevent source-target recognition.

The corrected source-bounded breakout reconstruction is 2024-08-13: close **78.26** is +0.5525% above oracle pivot **77.83**, with volume **1.2219x** prior-50. T+1 open **78.34** is +0.6553% above the oracle pivot and remains inside the original 5% zone.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_PRESENT / SOURCE_NEAR_PIVOT_1.16PCT / SOURCE_TARGET_STRUCTURE_AMBIGUOUS / NO_SECOND_TROUGH_UNDERCUT_SEMANTICS_GAP**.


## DOUBLE_BOTTOM numeric audit 003 — CAG 2024

Status: **AUDITED / FAMILY PRESENT / SOURCE-NEAR PIVOT / SOURCE-TARGET REMAINS AMBIGUOUS / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from corrected authoritative replay run **35474785663**, job **105982053857**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family present** |
| Pivot | 29.89 | 30.69000053 | +0.80000053 / **+2.6765%**; near match |
| Source-target landmarks | source numeric landmarks not frozen | nearest cluster uses MIDDLE_PEAK 2023-12-14 / TROUGH_2 2024-02-14 with multiple left-side alternatives | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | 31.72%-39.08% across nearest-pivot lineages | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | source accepts double-bottom elements / 29.89 entry | AMBIGUOUS | **morphology-state gap** |
| Faults | source accepts structure | NO_SECOND_TROUGH_UNDERCUT + WEAK_MIDDLE_REBOUND | **trough/rebound semantics gap** |
| Breakout | source-bounded first close >= 29.89 | 2024-04-04 H 31.39 / C 30.64 | **daily close crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 2.7902x prior-50 | separate breakout evidence |
| T+1 open | n/a to source morphology | 30.71 = +2.7434% vs oracle pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo, auto_adjust=false | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. There is **no exact 29.89 engine pivot**. The closest cluster is pivot **30.69000053**, **+2.6765%** above the oracle. All lineages in that cluster are AMBIGUOUS and share MIDDLE_PEAK **2023-12-14** / TROUGH_2 **2024-02-14**, with both `NO_SECOND_TROUGH_UNDERCUT` and `WEAK_MIDDLE_REBOUND`; left-side selections vary.

The engine also emits RECOGNIZED DOUBLE_BOTTOM structures at pivots **38.93999863** and **41.29999924**, but these are materially different historical structures and must not be substituted for the oracle 29.89 target. Therefore full-candidate inspection confirms the source-near-but-not-reconstructed diagnosis for the source target.

The corrected source-bounded breakout reconstruction is 2024-04-04: close **30.64** is +2.5092% above oracle pivot **29.89**, with volume **2.7902x** prior-50. T+1 open **30.71** is +2.7434% above the oracle pivot and remains inside the original 5% zone.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_PRESENT / SOURCE_NEAR_PIVOT_2.68PCT / SOURCE_TARGET_STRUCTURE_AMBIGUOUS / SECOND_TROUGH_AND_MIDDLE_REBOUND_SEMANTICS_GAP**.


## DOUBLE_BOTTOM numeric audit 004 — STRL 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH / MULTIPLE SAME-PIVOT LINEAGES / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from corrected authoritative replay run **35474785663**, job **105982053838**.

| Field | Source oracle | Frozen source-near candidates | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family exact match** |
| Pivot | 130.89 | 130.88999939 | -0.00000061 / **~-0.0000005%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | exact-pivot cluster shares TROUGH_1 2024-07-09 / MIDDLE_PEAK 2024-07-15, with alternate left-high and second-trough boundaries | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | multiple exact-pivot lineages, including 7.96%, 9.54%, 15.35%, 18.24%, 19.65%, 23.52%, 32.06% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid first-stage double bottom | multiple RECOGNIZED exact-pivot lineages | **categorical match** |
| Faults | source accepts structure | clean lineages have none; alternate same-pivot candidates may be AMBIGUOUS/REJECTED | **clean source-pivot lineage exists** |
| Breakout | source-bounded first close >= 130.89 | 2024-09-18 H 139.28 / C 134.94 | **daily close crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 1.3331x prior-50 | separate breakout evidence |
| T+1 open | n/a to source morphology | 138.99 = +6.1884% vs pivot | **above original 5% zone**; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo, auto_adjust=false | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. The engine produces a large exact-pivot cluster at **130.88999939**. Several lineages are **RECOGNIZED with no faults**, including structures ending at TROUGH_2 **2024-09-04**; other same-pivot alternatives are AMBIGUOUS/REJECTED because of `NO_SECOND_TROUGH_UNDERCUT` and/or `TOO_SHORT`. Because source numeric landmark boundaries are not frozen, the audit does not choose among these exact-pivot clean lineages as the unique oracle geometry.

The important source-fidelity result is unambiguous at the supported level: the DOUBLE_BOTTOM family is present, the oracle pivot is reconstructed to floating-point precision, and clean RECOGNIZED same-pivot structures exist. A secondary recognized cluster at pivot **125.40000153** is a different middle-peak construction and does not supersede the exact-pivot cluster.

The corrected source-bounded breakout reconstruction is 2024-09-18: close **134.94** is +3.0942% above pivot and volume is **1.3331x** prior-50. T+1 open **138.99** is +6.1884% above pivot, therefore outside the original 5% buy zone. That is an execution/operationalization observation, not a morphology failure.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / CLEAN_RECOGNIZED_SAME_PIVOT_LINEAGE_PRESENT / SOURCE_LANDMARK_BOUNDARY_NOT_SCOREABLE / T1_ABOVE_ORIGINAL_5PCT_ZONE**.


## DOUBLE_BOTTOM numeric audit 005 — URI 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH / MULTIPLE SAME-PIVOT CLEAN LINEAGES / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from corrected authoritative replay run **35474785663**, job **105982053780**.

| Field | Source oracle | Frozen source-near candidates | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family exact match** |
| Pivot | 715.34 | 715.34002686 | +0.00002686 / **~+0.0000038%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | exact-pivot cluster centers on TROUGH_1 2024-05-02 / MIDDLE_PEAK 2024-05-15 with TROUGH_2 2024-06-04 or 2024-06-18 and alternate left highs | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | clean exact-pivot lineages approximately 14.88%-17.06% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid double bottom | multiple RECOGNIZED exact-pivot lineages | **categorical match** |
| Faults | source accepts structure | clean lineages have none; one same-pivot short lineage is REJECTED | **clean source-pivot lineage exists** |
| Breakout | source-bounded first close >= 715.34 | 2024-07-16 H 743.24 / C 743.01 | **daily close crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 1.2151x prior-50 | separate breakout evidence |
| T+1 open | n/a to source morphology | 731.65 = +2.2800% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo, auto_adjust=false | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. The source-pivot cluster at **715.34002686** contains several **RECOGNIZED** lineages with no faults. They share TROUGH_1 **2024-05-02** and MIDDLE_PEAK **2024-05-15**, while the engine varies the left-high boundary and selects TROUGH_2 **2024-06-04** or **2024-06-18**. One same-pivot candidate is REJECTED as `TOO_SHORT`, but multiple clean lineages remain.

Because source numeric landmark dates and depth are not frozen, the audit does not select one of those clean lineages as the unique oracle geometry. The supported fidelity result is nevertheless strong: family exact, pivot practical exact, and clean recognized same-pivot structures present. Nearby pivot **713.59002686** candidates are ambiguous under `NO_SECOND_TROUGH_UNDERCUT`; the **729.90997314** cluster is recognized but represents a different middle-peak construction.

The corrected source-bounded breakout reconstruction is 2024-07-16: close **743.01** is +3.8681% above pivot, with volume **1.2151x** prior-50. T+1 open **731.65** is +2.2800% above pivot and remains inside the original 5% zone.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / CLEAN_RECOGNIZED_SAME_PIVOT_LINEAGE_PRESENT / SOURCE_LANDMARK_BOUNDARY_NOT_SCOREABLE**.


## DOUBLE_BOTTOM numeric audit 006 — UBS 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH AT PIVOT LEVEL / MULTIPLE SAME-PIVOT LINEAGES / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from corrected authoritative replay run **35474785663**, job **105982053825**.

| Field | Source oracle | Frozen source-near candidates | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family exact match** |
| Pivot | 31.45 | 31.45499992 | +0.00499992 / **+0.0159%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | exact/near-pivot cluster contains multiple boundary choices | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | clean 31.45499992 lineages span about 9.76%-14.81% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid double bottom | multiple RECOGNIZED 31.45499992 lineages | **categorical match exists** |
| Faults | source accepts structure | clean lineages have none; alternate same-pivot lineages carry NO_SECOND_TROUGH_UNDERCUT | **clean source-pivot lineage exists** |
| Breakout | source-bounded first close >= 31.45 | 2024-10-09 H 31.59 / C 31.58 | **daily close crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 0.3699x prior-50 | weak volume; separate breakout evidence |
| T+1 open | n/a to source morphology | 31.60 = +0.4769% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo, auto_adjust=false | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. The closest cluster is **31.45499992**, only **+0.0159%** above the 31.45 oracle. Crucially, this cluster contains several **RECOGNIZED, fault-free** lineages, not merely ambiguous candidates. Clean examples use TROUGH_1 **2024-06-26** / MIDDLE_PEAK **2024-07-16**, with TROUGH_2 **2024-08-05** or **2024-09-10** and varying left-high boundaries. Other same-pivot lineages use a later TROUGH_1 **2024-08-05** / MIDDLE_PEAK **2024-08-27** and are AMBIGUOUS under `NO_SECOND_TROUGH_UNDERCUT`.

Because the source does not freeze numeric landmark dates, the audit cannot identify which same-pivot lineage is the unique oracle geometry. But the prior shorthand that focused on ambiguity is too coarse: at the supported fidelity level, the engine has both the correct family and a practical-exact pivot with clean RECOGNIZED structures.

Nearby **31.39500046** and **31.94499969** clusters are ambiguous and do not supersede the cleaner 31.45499992 cluster.

The corrected source-bounded breakout reconstruction is 2024-10-09: close **31.58** is +0.4134% above oracle pivot. Volume is only **0.3699x** prior-50, so breakout-volume evidence is weak and remains separate from morphology. T+1 open **31.60** is +0.4769% above pivot and inside the original 5% zone.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH_0.016PCT / CLEAN_RECOGNIZED_SAME_PIVOT_LINEAGE_PRESENT / SOURCE_LANDMARK_BOUNDARY_NOT_SCOREABLE / BREAKOUT_VOLUME_WEAK**.


## DOUBLE_BOTTOM numeric audit 007 — NXPI 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH / EXACT-PIVOT CLEAN LINEAGES PRESENT / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from corrected authoritative replay run **35474785663**, job **105982053723**.

| Field | Source oracle | Frozen source-near candidates | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family exact match** |
| Pivot | 251.96 | 251.96000671 | +0.00000671 / **~+0.0000027%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | exact-pivot cluster shares TROUGH_1 2024-03-15 / MIDDLE_PEAK 2024-04-09 / TROUGH_2 2024-04-19, with alternate left-high boundaries | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | exact-pivot candidates include ~5.56%, 10.60%, and 19.39% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid double bottom | RECOGNIZED clean exact-pivot lineages present | **categorical match** |
| Faults | source accepts structure | clean lineages none; alternates include TOO_SHORT or WEAK_MIDDLE_REBOUND | **clean source-pivot lineage exists** |
| Breakout | source-bounded first close >= 251.96 | 2024-05-02 H 255.39 / C 254.26 | **daily close crossing confirmed** |
| Breakout volume | source numeric oracle not frozen | 0.9718x prior-50 | near-average volume; separate breakout evidence |
| T+1 open | n/a to source morphology | 261.00 = +3.5879% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo, auto_adjust=false | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. The engine reconstructs the oracle pivot at **251.96000671** to floating-point precision. Two clean RECOGNIZED exact-pivot lineages are present, including LEFT_HIGH **2024-03-07** or **2023-12-15**, both sharing TROUGH_1 **2024-03-15**, MIDDLE_PEAK **2024-04-09**, and TROUGH_2 **2024-04-19**. Alternate exact-pivot candidates include one REJECTED `TOO_SHORT` and one AMBIGUOUS `WEAK_MIDDLE_REBOUND`, but they do not displace the clean lineages.

Because source numeric landmarks and depth are not frozen, the audit does not choose between the clean exact-pivot left-boundary alternatives. The nearby **264.26000977** cluster is broadly AMBIGUOUS under `NO_SECOND_TROUGH_UNDERCUT`, while lower **238.27000427** candidates are also alternate structures; neither supersedes the exact-pivot clean cluster.

The corrected source-bounded breakout reconstruction is 2024-05-02: close **254.26** is +0.9128% above pivot. Volume is **0.9718x** prior-50, approximately average and not strong confirmation. T+1 open **261.00** is +3.5879% above pivot and remains inside the original 5% zone.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / CLEAN_RECOGNIZED_EXACT_PIVOT_LINEAGE_PRESENT / SOURCE_LANDMARK_BOUNDARY_NOT_SCOREABLE / BREAKOUT_VOLUME_NEAR_AVERAGE**.


## DOUBLE_BOTTOM numeric audit 008 — TSM 2024

Status: **AUDITED / SOURCE-FIDELITY MATCH / EXACT-PIVOT CLEAN LINEAGES PRESENT / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from authoritative replay run **35420754613**, job **105837873681**.

| Field | Source oracle | Frozen source-near candidates | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family exact match** |
| Pivot | 148.43 | 148.42999268 | -0.00000732 / **~-0.0000049%**; practical exact match |
| Source-target landmarks | source numeric landmarks not frozen | exact-pivot candidates share TROUGH_1 2024-03-19 / MIDDLE_PEAK 2024-04-10 / TROUGH_2 2024-04-22; alternate LEFT_HIGH 2024-02-09 or 2024-03-08 | **NOT SCORED / SOURCE NUMERIC LANDMARKS NOT AVAILABLE** |
| Depth | source numeric depth not frozen | clean exact-pivot candidates include **6.946807%** and **20.593432%** | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | valid double bottom | RECOGNIZED clean exact-pivot lineages present | **categorical match** |
| Faults | source accepts structure | clean lineages none; one alternate exact-pivot candidate is REJECTED TOO_SHORT | **clean source-pivot lineage exists** |
| Breakout | source 2024-05-10 | H 150.50 / C 149.26 | **daily breakout corroborated** |
| Breakout volume | source contemporaneously reports breakout | **1.4645x prior-50** | strong corroboration |
| T+1 open | n/a to source morphology | 148.02 = **-0.2762%** vs pivot | below pivot; operationalization only |
| Price basis | contemporaneous oracle basis | Yahoo/yfinance, auto_adjust=false; identity transform | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. The oracle-pivot cluster at **148.42999268** contains two clean **RECOGNIZED** lineages. Both share TROUGH_1 **2024-03-19**, MIDDLE_PEAK **2024-04-10**, and TROUGH_2 **2024-04-22**; their LEFT_HIGH boundary differs (**2024-02-09** versus **2024-03-08**). A third exact-pivot candidate using the latter boundary is REJECTED as `TOO_SHORT`, showing boundary-sensitive duration adjudication, but a fault-free candidate with the same geometry/pivot is also emitted.

The source does not freeze numeric landmark dates or depth, so the audit does not select a unique oracle boundary between the clean exact-pivot alternatives. Other clusters at **158.3999939** and **135.16999817** are mostly AMBIGUOUS under `NO_SECOND_TROUGH_UNDERCUT`; they are different structures and do not displace the exact-pivot source-near cluster.

On 2024-05-10 the daily bar opened **147.22**, reached **150.50**, and closed **149.26**, so high and close both cleared 148.43; close was **+0.5592%** above pivot. Volume was **23,671,400** versus prior-50 mean **16,163,340**, or **1.4645x / +46.45%**. T+1 open on 2024-05-13 was **148.02**, **-0.2762%** below pivot. The frozen replay labels its strict original-buy-zone-at-open boolean false because open was below the pivot; this is an execution-layer observation, not a morphology failure.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / CLEAN_RECOGNIZED_EXACT_PIVOT_LINEAGE_PRESENT / SOURCE_LANDMARK_BOUNDARY_NOT_SCOREABLE / BREAKOUT_VOLUME_STRONG**.


## DOUBLE_BOTTOM numeric audit 009 — IPHI 2019

Status: **AUDITED / SOURCE-NEAR STRUCTURE FOUND / PIVOT NEAR MATCH / SECOND-TROUGH SEMANTICS GAP / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from authoritative lifecycle replay run **35413742554**, job **105818216871**.

| Field | Source oracle | Frozen source-near candidate | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM | **family present** |
| Pivot | 64.85 | 64.75 | -0.10 / **-0.1542%**; near match |
| Source-target landmarks | source numeric landmarks not separately frozen | LEFT_HIGH 2019-08-08 / TROUGH_1 2019-08-28 / MIDDLE_PEAK 2019-09-20 / TROUGH_2 2019-10-02 | source-near structural neighborhood; exact landmark scoring unavailable |
| Depth | source numeric depth not frozen | 11.688702% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | documented double bottom | AMBIGUOUS | **morphology-state gap** |
| Faults | source accepts structure | NO_SECOND_TROUGH_UNDERCUT | **second-trough semantics gap** |
| Breakout | source 2019-10-15 | H 66.20 / C 64.99 | **daily crossing corroborated** |
| Breakout volume | source numeric volume oracle not frozen | 1.1462x prior-50 / +14.62% | below frozen USSY 1.40 threshold; separate evidence |
| T+1 open | n/a to source morphology | 65.06 = +0.3238% vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | Tiingo fallback; identity transform; no corporate-action transform | **common basis** |

All emitted DOUBLE_BOTTOM candidates were inspected. The source-nearest candidate is unambiguous among the emitted structures: pivot **64.75**, only **-0.1542%** from the oracle 64.85, with LEFT_HIGH **2019-08-08**, TROUGH_1 **2019-08-28**, MIDDLE_PEAK **2019-09-20**, and TROUGH_2 **2019-10-02**. It is AMBIGUOUS solely under `NO_SECOND_TROUGH_UNDERCUT`.

Other DOUBLE_BOTTOM candidates do not overturn that adjudication. The **66.56** cluster is also AMBIGUOUS under `NO_SECOND_TROUGH_UNDERCUT` and represents older/wider structures; the **51.83** candidate is REJECTED as `TOO_SHORT`. No clean RECOGNIZED candidate near the 64.85 source pivot exists.

The breakout daily bar on 2019-10-15 reached **66.20** and closed **64.99**, +0.2159% above the oracle pivot. Volume was **1.1462x** prior-50, below the frozen USSY 1.40 confirmation threshold. T+1 open **65.06** was +0.3238% above the oracle pivot and remained inside the original 5% zone. The separately frozen lifecycle evidence later corroborates the documented failed-breakout character; it does not change the morphology adjudication.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_MATCH / SOURCE_NEAR_STRUCTURE_FOUND / PIVOT_NEAR_MATCH_0.15PCT / SOURCE_TARGET_STRUCTURE_AMBIGUOUS / NO_SECOND_TROUGH_UNDERCUT_SEMANTICS_GAP**.


## DOUBLE_BOTTOM numeric audit 010 — WMT 2024

Status: **AUDITED / SOURCE-TARGET STRUCTURE NOT EMITTED / LANDMARK-GENERATION MISS / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen DOUBLE_BOTTOM candidate set from authoritative diagnostic replay run **35428260263**, job **105857943569**.

| Field | Source oracle | Frozen engine | Delta / result |
|---|---:|---:|---|
| Pattern family | DOUBLE_BOTTOM | DOUBLE_BOTTOM exists only for an older unrelated structure | **family capability present, source-target absent** |
| Pivot | 60.89 | 56.64666748 (older unrelated candidate) | **NOT SCORED as source-near pivot** |
| Source landmarks | TROUGH_1 2024-04-19 / MIDDLE_PEAK 2024-05-03 / TROUGH_2 2024-05-10; source lows 58.88 / 58.55 | no source-target candidate; oracle_candidate_matches=[] | **source-target landmark-generation miss** |
| Depth | source numeric depth not frozen | older candidate 9.834184% | **NOT SCORED / unrelated structure** |
| Final source-target state | documented 2024 double bottom | no emitted source-target candidate | **upstream fidelity gap** |
| Faults | source accepts structure | no source-target morphology candidate exists to fault | **morphology gate not reached** |
| Breakout | source 2024-05-16 | H 64.42 / C 64.01 | crossing corroborated, but already extended |
| Breakout volume | source breakout | **3.9813x prior-50 / +298.13%** | very strong; separate evidence |
| T+1 open | n/a to source morphology | 64.24 = **+5.5017%** vs pivot | above original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | identity transform; no corporate-action transform | **common basis** |

Full-candidate inspection is decisive. The frozen replay emits only one DOUBLE_BOTTOM structure: LEFT_HIGH **2023-09-13**, TROUGH_1 **2023-10-06**, MIDDLE_PEAK **2023-11-15**, TROUGH_2 **2023-12-11**, pivot **56.64666748**, RECOGNIZED with no faults. This is an older unrelated structure and must not be substituted for the source-labelled April-May 2024 double bottom.

The oracle comparison layer explicitly records TROUGH_1 **2024-04-19**, MIDDLE_PEAK **2024-05-03**, TROUGH_2 **2024-05-10**, and `oracle_candidate_matches=[]`. The separately frozen boundary diagnosis already localizes the failure upstream: primary, auxiliary, and fused landmark vocabularies contain no April-May 2024 source-target landmarks, leaving downstream segmentation empty. Therefore this case does **not** test `NO_SECOND_TROUGH_UNDERCUT`; there is no source-target morphology candidate on which that gate could operate.

On 2024-05-16 the bar opened **64.22**, reached **64.42**, and closed **64.01**, which is **+5.1240%** above the 60.89 oracle pivot and slightly beyond the conventional 5% zone. Volume was **3.9813x** prior-50. T+1 open **64.24** was **+5.5017%** above pivot and also beyond the 5% zone. These strong breakout observations do not repair the upstream morphology miss.

Audit conclusion: **DOUBLE_BOTTOM_FAMILY_CAPABILITY_PRESENT / SOURCE_TARGET_STRUCTURE_NOT_EMITTED / SOURCE_TARGET_PIVOT_NOT_SCOREABLE / LANDMARK_GENERATION_MISS / BREAKOUT_VOLUME_VERY_STRONG / T1_ABOVE_ORIGINAL_5PCT_ZONE**.

### DOUBLE_BOTTOM numeric-audit closure

All **10/10** frozen DOUBLE_BOTTOM golden cases now have full-candidate numeric adjudication. The tranche contains both clean practical-exact source-pivot reconstructions and localized fidelity gaps at different layers: some cases reach DOUBLE_BOTTOM morphology but remain ambiguous under trough/rebound semantics, while WMT fails earlier at landmark generation. These outcomes do not support collapsing all discrepancies into one universal DOUBLE_BOTTOM gate failure, and no detector tuning or frozen-engine modification is authorized by this audit tranche.


## FLAT_BASE numeric audit 001 — AAPL 2019

Status: **AUDITED / SOURCE PIVOT EXACTLY RECOVERED / FLAT-BASE GEOMETRY-GATE GAP / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen FLAT_BASE candidate set from authoritative replay run **35417737472**, job **105829518703**.

| Field | Source oracle | Frozen source-near candidates | Delta / result |
|---|---:|---:|---|
| Pattern family | FLAT_BASE | FLAT_BASE | **family exact match** |
| Pivot | 221.37 | 221.36999512 | -0.00000488 / **~-0.0000022%**; practical exact match |
| Source-target landmarks | source numeric base-low not frozen | LEFT_HIGH 2019-07-31 / BASE_LOW 2019-08-05 | left-high/pivot exact; remaining geometry not independently scoreable |
| Depth | source numeric depth not frozen | 13.005373% | **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** |
| Final source-near state | documented flat base | REJECTED confirmed structure; AMBIGUOUS open-right-edge form | **morphology-state gap** |
| Faults | source accepts structure | TOO_SHORT + WIDE_LOOSE; alternate same structure WIDE_LOOSE | **duration/tightness geometry gap** |
| Breakout | source week ending 2019-09-13; daily replay 2019-09-11 | H 223.71 / C 223.59 | **daily crossing corroborated** |
| Breakout volume | source breakout | **1.7080x prior-50 / +70.80%** | strong corroboration |
| T+1 open | n/a to source morphology | 224.80 = **+1.5494%** vs pivot | inside original 5% zone; operationalization only |
| Price basis | contemporaneous 2019 basis | later AAPL 4-for-1 split restored: OHLC x4 / volume ÷4 | **basis normalized to oracle period** |

All emitted FLAT_BASE candidates were inspected. The source-target cluster is unmistakable: pivot **221.36999512**, LEFT_HIGH **2019-07-31**, BASE_LOW **2019-08-05**, depth **13.0054%**. The confirmed-structure candidate is REJECTED under `TOO_SHORT` + `WIDE_LOOSE`; the open-right-edge variant of the same structure is AMBIGUOUS under `WIDE_LOOSE`. Therefore the engine recovers the family neighborhood and oracle pivot essentially exactly, but its frozen duration/tightness geometry gates do not promote the source-labelled flat base to RECOGNIZED.

Other FLAT_BASE candidates are materially different structures: pivot **215.30999756** is REJECTED under `TOO_DEEP` + `WIDE_LOOSE`; older **158.8500061** structures are AMBIGUOUS under `WIDE_LOOSE` with one also carrying `BOUNDARY_CONTEXT`. None supersedes the exact source-pivot structure.

The replay explicitly restores AAPL's later 2020 4-for-1 split to contemporaneous 2019 basis before comparison. On 2019-09-11 the normalized bar reached **223.71** and closed **223.59**, +1.0028% above the 221.37 oracle pivot. Volume was **1.7080x** prior-50. T+1 open **224.80** was +1.5494% above pivot and inside the original 5% zone.

Audit conclusion: **FLAT_BASE_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_TARGET_STRUCTURE_FOUND / SOURCE_TARGET_NOT_RECOGNIZED / TOO_SHORT_AND_WIDE_LOOSE_GEOMETRY_GAP / BREAKOUT_VOLUME_STRONG**.


## FLAT_BASE numeric audit 002 — SNPS 2023

Status: **AUDITED / SOURCE PIVOT AND LEFT BOUNDARY EXACTLY RECOVERED / FLAT-BASE GEOMETRY-GATE GAP / NO ENGINE CHANGE**.

This audit re-inspects the complete frozen FLAT_BASE candidate set from authoritative corrected replay run **35418641005**, job **105832029466**.

| Field | Source oracle | Frozen source-near candidates | Delta / result |
|---|---:|---:|---|
| Pattern family | FLAT_BASE | FLAT_BASE | **family exact match** |
| Pivot | 392.79 | 392.79000854 | +0.00000854 / **~+0.0000022%**; practical exact match |
| Source left boundary | 2023-04-04 | LEFT_HIGH 2023-04-04 | **exact match** |
| Source duration | six weeks | source-target candidate present, but confirmed form fails TOO_SHORT while open-right-edge form does not | **duration adjudication gap** |
| Source range/depth | 8.0% | 8.253778% | **+0.2538 pp; near numeric match** |
| Final source-near state | documented flat base | REJECTED confirmed structure; AMBIGUOUS open-right-edge form | **morphology-state gap** |
| Faults | source accepts structure | TOO_SHORT + WIDE_LOOSE; alternate same structure WIDE_LOOSE | **duration/tightness geometry gap** |
| Breakout | 2023-05-18 | H 410.91 / C 409.71 | **daily crossing corroborated** |
| Breakout volume | source +163% above average | replay **+171.63% / 2.7163x prior-50** | **strong, directionally close but averaging definitions may differ** |
| T+1 open | n/a to source morphology | 413.03 = **+5.1529%** vs pivot | above original 5% zone; operationalization only |
| Price basis | contemporaneous oracle basis | identity transform; no corporate action documented for fixture | **common provider basis** |

All emitted FLAT_BASE candidates were inspected. The source-target structure is explicit: LEFT_HIGH **2023-04-04**, BASE_LOW **2023-04-25**, pivot **392.79000854**, depth **8.253778%**. This independently recovers the source's 2023-04-04 base high and 392.79 pivot essentially exactly, while the measured depth/range is only **+0.2538 percentage points** from the source-reported 8.0%.

As with AAPL, the source-target structure is not promoted to RECOGNIZED. The confirmed-structure candidate is REJECTED under `TOO_SHORT` + `WIDE_LOOSE`; the open-right-edge representation of the same structure is AMBIGUOUS under `WIDE_LOOSE`. This is particularly informative because the source explicitly calls the base **six weeks**, so the `TOO_SHORT` result is a direct duration-semantics discrepancy rather than merely an unavailable oracle dimension.

Other emitted FLAT_BASE structures do not supersede the source-target candidate: **391.17001343** structures are much deeper and REJECTED under `TOO_DEEP` + `WIDE_LOOSE`; **379.76000977**, **363.98999023**, **350.45001221**, **326.10998535**, and **304.80999756** represent different historical bases and mostly carry `WIDE_LOOSE` and/or depth/duration faults.

On 2023-05-18 the bar reached **410.91** and closed **409.71**, +4.3076% above pivot and still inside the original 5% zone. Replay volume was **2.7163x prior-50**, or **+171.63%**, versus the source's reported **+163%**; both strongly corroborate the breakout, while the exact difference should not be overinterpreted because the averaging definitions are not proven identical. T+1 open **413.03** was **+5.1529%** above pivot, just outside the original 5% zone.

Audit conclusion: **FLAT_BASE_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_LEFT_BOUNDARY_EXACT_MATCH / SOURCE_DEPTH_NEAR_MATCH_0.25PP / SOURCE_TARGET_NOT_RECOGNIZED / TOO_SHORT_AND_WIDE_LOOSE_GEOMETRY_GAP / BREAKOUT_VOLUME_STRONG / T1_ABOVE_ORIGINAL_5PCT_ZONE**.

### Current FLAT_BASE numeric-audit boundary

Both currently reconstructed FLAT_BASE golden cases now have full-candidate numeric adjudication. AAPL and SNPS independently recover the source pivot essentially exactly, yet neither source-target structure reaches RECOGNIZED because of frozen duration/tightness geometry gates. SNPS is the stronger duration diagnostic because its oracle explicitly states **six weeks**, while the engine still produces a confirmed candidate with `TOO_SHORT`. This is validation evidence only; no threshold change or detector tuning is authorized.


## FLAT_BASE completion tranche — cases 033–040

Authoritative batch replay: **35497962478** — **8/8 SUCCESS**. Frozen engine SHA remains `c433cc1e35a5aa32a46f732cd8c5545935e36e40`. These fixtures are source-fidelity evidence only; oracle values were comparison inputs and were not passed to the detector.

| Case | Oracle pivot | Source-nearest frozen FLAT_BASE | Frozen adjudication |
|---|---:|---|---|
| 033 META 2024 | 602.95 | 602.95001221, AMBIGUOUS, depth 8.9394%, WIDE_LOOSE | SOURCE_TARGET_FOUND / PIVOT_PRACTICAL_EXACT / WIDE_LOOSE_GAP |
| 034 TW 2024 | 136.13 | 136.13499451, AMBIGUOUS, depth 8.0618%, WIDE_LOOSE; same structure also REJECTED TOO_SHORT+WIDE_LOOSE | SOURCE_TARGET_FOUND / PIVOT_NEAR_EXACT_0.0037PCT / DURATION_TIGHTNESS_GAP |
| 035 NOW 2024 | 850.33 | nearest 815.31997681 REJECTED; nearer chronology candidate 806.52000427 AMBIGUOUS WIDE_LOOSE | SOURCE_TARGET_PIVOT_NOT_RECONSTRUCTED / BOUNDARY_OR_LANDMARK_GAP |
| 036 DECK 2023 | 568.47 | 568.47001648, AMBIGUOUS, depth 14.8557%, WIDE_LOOSE | SOURCE_TARGET_FOUND / PIVOT_PRACTICAL_EXACT / WIDE_LOOSE_GAP |
| 037 CROX 2021 | 109.91 | 109.91000366, AMBIGUOUS WIDE_LOOSE; same pivot confirmed candidate REJECTED TOO_SHORT+WIDE_LOOSE | SOURCE_TARGET_FOUND / PIVOT_PRACTICAL_EXACT / DURATION_TIGHTNESS_GAP |
| 038 CPRT 2020 | 92.51 | no source-near pivot; nearest emitted 83.69999695 AMBIGUOUS/REJECTED | SOURCE_TARGET_PIVOT_NOT_RECONSTRUCTED / BOUNDARY_OR_LANDMARK_GAP |
| 039 AMZN 2020 | 3344.39 | 3344.28985596, AMBIGUOUS WIDE_LOOSE; same pivot confirmed candidate REJECTED TOO_SHORT+WIDE_LOOSE | SOURCE_TARGET_FOUND / PIVOT_NEAR_MATCH_0.003PCT / DURATION_TIGHTNESS_GAP |
| 040 KKR 2024 | 103.48 | 103.48000336, AMBIGUOUS WIDE_LOOSE; same structure also REJECTED TOO_SHORT+WIDE_LOOSE | SOURCE_TARGET_FOUND / PIVOT_PRACTICAL_EXACT / DURATION_TIGHTNESS_GAP |

Breakout/T+1 evidence is kept separate from morphology. The source-bounded daily replay confirms the oracle-pivot close crossing for all eight fixtures. Breakout prior-50 volume ratios were approximately: META **1.2524x**, TW **1.0369x**, NOW **1.4729x**, DECK **5.1891x**, CROX **1.4620x**, CPRT **1.4822x**, AMZN **0.8414x**, KKR **1.3333x**. T+1 opens remained within the original 0–5% pivot zone for all eight replay fixtures.

Corporate-action normalization is explicit where required: NOW **x5**, DECK **x6**, CPRT **x4**, and AMZN **x20** for historical-price comparison, with inverse volume transforms. META, TW, CROX, and KKR use identity transforms.

### Historical reconstruction closure — 40/40

The historical golden reconstruction target is now **40/40 COMPLETE**: CUP_WITH_HANDLE 10/10, CUP_WITHOUT_HANDLE 10/10, DOUBLE_BOTTOM 10/10, FLAT_BASE 10/10. The eight new FLAT_BASE fixtures complete reconstruction coverage; they do not authorize detector tuning. Full one-by-one numeric adjudication remains complete for the original 32 fixtures and should proceed separately for FLAT_BASE cases 033–040 if required.


## FLAT_BASE numeric audit #003 — META 2024

Oracle evidence identifies META as a FLAT_BASE with **602.95** buy point and a 2024-12-03 breakout. The primary source also describes the setup as a new base/base-on-base, but the evidence frozen for this case does **not** provide an authoritative numeric base depth/range, exact left-boundary date, or duration value. Those dimensions are therefore **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE** rather than inferred from the oracle.

Full-candidate inspection of frozen replay **35497962478** finds the source-target FLAT_BASE independently. The confirmed candidate has structural start/pivot-source date **2024-10-07**, structural end/base low **2024-11-21**, pivot **602.95001221**, depth **8.939385%**, status **AMBIGUOUS**, and sole fault **WIDE_LOOSE**. An open-right-edge representation of the same source-target structure also carries pivot **602.95001221**, depth **8.939385%**, and **WIDE_LOOSE**. No source-target FLAT_BASE at this pivot reaches RECOGNIZED.

The pivot difference is only **+0.00001221** dollars, approximately **+0.0000020%**, so this is a practical exact pivot reconstruction. The engine-measured 8.9394% depth is retained as an observation only; it is not scored against the source because no authoritative source numeric depth/range was recovered for this case. Likewise, the 2024-10-07 left boundary and duration are engine observations, not oracle matches.

The replay breakout bar on **2024-12-03** opened **595.00**, reached **614.20**, and closed **613.65**, **+1.7746%** above the 602.95 pivot. Volume was **1.2524x** the replay prior-50 average, or about **+25.24%**. The primary IBD breakout report likewise describes volume about **25% above average**; this is close corroboration, while averaging definitions are not assumed identical. T+1 on **2024-12-04** opened **612.96**, **+1.6602%** above pivot and inside the original 5% buy zone.

Audit conclusion: **FLAT_BASE_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_LEFT_BOUNDARY_NOT_SCORED / SOURCE_DURATION_NOT_SCORED / SOURCE_DEPTH_NOT_SCORED / SOURCE_TARGET_NOT_RECOGNIZED / WIDE_LOOSE_GEOMETRY_GAP / BREAKOUT_VOLUME_NEAR_SOURCE_25PCT / T1_INSIDE_ORIGINAL_5PCT_ZONE**.

Numeric-audit progress after this freeze: **33/40 = 82.5% overall**; FLAT_BASE **3/10 = 30%**.


## FLAT_BASE numeric audit #004 — TW 2024

Primary IBD/MarketSurge evidence identifies Tradeweb Markets (TW) as a **six-week FLAT_BASE** with **136.13** buy point. A later IBD retrospective states that TW broke out from this **stage-two flat base** on **2024-11-20**. The daily replay uses a stricter close-crossing observation rule, so its first close >= pivot occurs later on 2024-11-26; that operational date must not overwrite the source breakout date.

Full-candidate inspection of frozen replay **35497962478** independently recovers the source-target pivot. The source-nearest OPEN_RIGHT_EDGE FLAT_BASE starts/pivots at **2024-10-15**, ends at replay as-of **2024-11-26**, pivot **136.13499451**, depth **8.061844%**, status **AMBIGUOUS**, sole fault **WIDE_LOOSE**. The corresponding CONFIRMED_STRUCTURE uses the same **2024-10-15** pivot and **136.13499451** level, ends/base-low at **2024-11-06**, has the same measured depth **8.061844%**, and is **REJECTED** under **TOO_SHORT + WIDE_LOOSE**.

The pivot difference is **+$0.00499451**, about **+0.00367%**, a near-exact reconstruction. IBD explicitly calls the base **six weeks**, while the frozen confirmed structure is rejected as **TOO_SHORT**. This is therefore a direct duration-semantics discrepancy, analogous to SNPS rather than an inference from unavailable oracle data. The engine depth 8.0618% is retained as an observation only because the retrieved source does not provide an equivalent numeric depth/range.

Source chronology and replay execution observation are deliberately separated. IBD says the breakout occurred **2024-11-20**, including intraday clearance of the 136.13 buy point; the frozen replay's first **daily close >= pivot** is **2024-11-26**, when high was **136.96** and close **136.32**, +0.1396% above pivot. Replay volume was **1.0369x prior-50** (+3.69%). T+1 after the replay close-crossing observation opened **137.45**, +0.9697% above pivot and inside the original 5% buy zone.

Audit conclusion: **FLAT_BASE_FAMILY_MATCH / SOURCE_PIVOT_NEAR_EXACT_MATCH_0.0037PCT / SOURCE_DURATION_SIX_WEEKS / CONFIRMED_STRUCTURE_TOO_SHORT_DURATION_SEMANTICS_GAP / SOURCE_DEPTH_NOT_SCORED / SOURCE_TARGET_NOT_RECOGNIZED / TOO_SHORT_AND_WIDE_LOOSE_GEOMETRY_GAP / SOURCE_BREAKOUT_2024-11-20_INTRADAY / REPLAY_CLOSE_CROSSING_2024-11-26 / T1_INSIDE_ORIGINAL_5PCT_ZONE**.

Numeric-audit progress after this freeze: **34/40 = 85% overall**; FLAT_BASE **4/10 = 40%**.


## FLAT_BASE numeric audit #005 — NOW 2024

Frozen oracle identifies ServiceNow (NOW) as a **FLAT_BASE** with **850.33** pivot and **2024-08-30** breakout. Full-candidate inspection of authoritative replay **35497962478** shows a materially different failure mode from AAPL, SNPS, META, and TW: the frozen engine does **not** emit a FLAT_BASE candidate at or near the source pivot.

The nearest emitted FLAT_BASE pivot is **815.31997681**, about **-$35.0100 / -4.117%** below the 850.33 oracle. That lineage is REJECTED in multiple confirmed structures: depth **21.7497%** with **TOO_DEEP + WIDE_LOOSE**, depth **10.4008%** with **TOO_SHORT + WIDE_LOOSE**, and depth **16.1200%** with **TOO_DEEP + WIDE_LOOSE**. A later chronology candidate beginning **2024-07-05** has pivot **806.52000427**, depth **9.5832%**, and is AMBIGUOUS under **WIDE_LOOSE**; its confirmed representation is REJECTED under **TOO_SHORT + WIDE_LOOSE**. None reconstructs 850.33.

Therefore this case must not be classified as the recurring “source pivot recovered but geometry gate blocks recognition” pattern. The source-target pivot itself is absent from FLAT_BASE output, so the discrepancy occurs **upstream at boundary/landmark/pivot construction** before final recognition gating. Oracle numeric left boundary, duration, and depth/range are not available in the frozen source evidence and are **NOT SCORED**.

Historical-price comparison uses an explicit **x5** pre-split normalization. This is necessary because ServiceNow's later 5-for-1 split became effective in December 2025; the 2024 oracle is on the pre-split basis. On the source breakout date **2024-08-30**, replay high was **857.25** and close **855.00**, +0.5492% above the 850.33 pivot. Replay volume was **1.4729x prior-50** (+47.29%); no source-equivalent numeric volume is frozen, so volume is observational rather than scored. T+1 operationalization on **2024-09-03** opened **856.40**, +0.7138% above pivot and inside the original 5% buy zone.

Audit conclusion: **FLAT_BASE_FAMILY_ORACLE / SOURCE_PIVOT_NOT_RECONSTRUCTED / NEAREST_ENGINE_PIVOT_815.32_MINUS_4.12PCT / SOURCE_LEFT_BOUNDARY_NOT_SCORED / SOURCE_DURATION_NOT_SCORED / SOURCE_DEPTH_NOT_SCORED / UPSTREAM_BOUNDARY_LANDMARK_PIVOT_GAP / BREAKOUT_2024-08-30_CONFIRMED / BREAKOUT_VOLUME_1.473X_OBSERVATIONAL / T1_INSIDE_ORIGINAL_5PCT_ZONE / PRICE_BASIS_X5_VALIDATED**.

Numeric-audit progress after this freeze: **35/40 = 87.5% overall**; FLAT_BASE **5/10 = 50%**.


## FLAT_BASE numeric audit #006 — DECK 2023

Frozen oracle identifies Deckers Outdoor (DECK) as a **FLAT_BASE** with **568.47** pivot and breakout in the week ending **2023-10-27**. Historical comparison uses explicit **x6** normalization to restore the pre-split price basis.

Full-candidate inspection of authoritative replay **35497962478** independently recovers the source pivot. The source-nearest FLAT_BASE is an OPEN_RIGHT_EDGE candidate with structural/pivot-source date **2023-08-08**, as-of end **2023-10-27**, pivot **568.47001648**, engine-measured depth **14.855670%**, status **AMBIGUOUS**, and sole fault **WIDE_LOOSE**. No source-target FLAT_BASE at 568.47 reaches RECOGNIZED. The next-nearest lineage pivots at **562.96998596** and is either AMBIGUOUS WIDE_LOOSE or REJECTED TOO_SHORT + WIDE_LOOSE, so it does not supersede the exact source-pivot lineage.

The pivot difference is only **+$0.00001648**, approximately **+0.0000029%**, a practical exact reconstruction. The retrieved source evidence does not freeze an authoritative numeric left boundary, duration, or base depth/range for this case, so those dimensions are **NOT SCORED / SOURCE NUMERIC VALUE NOT AVAILABLE**. Engine depth **14.8557%** is therefore observational only.

On **2023-10-27**, the replay bar opened **545.19**, reached **585.00**, and closed **576.37**, **+1.3897%** above the 568.47 pivot. Replay volume was **5.1891x prior-50** (+418.91%), a very strong breakout observation; no source-equivalent numeric volume is frozen, so it is not scored as an oracle match. T+1 on **2023-10-30** opened **580.20**, **+2.0634%** above pivot and inside the original 5% buy zone.

Audit conclusion: **FLAT_BASE_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_LEFT_BOUNDARY_NOT_SCORED / SOURCE_DURATION_NOT_SCORED / SOURCE_DEPTH_NOT_SCORED / SOURCE_TARGET_NOT_RECOGNIZED / WIDE_LOOSE_GEOMETRY_GAP / BREAKOUT_WEEK_ENDING_2023-10-27_CONFIRMED / BREAKOUT_VOLUME_5.189X_STRONG_OBSERVATIONAL / T1_INSIDE_ORIGINAL_5PCT_ZONE / PRICE_BASIS_X6**.

Numeric-audit progress after this freeze: **36/40 = 90% overall**; FLAT_BASE **6/10 = 60%**.


## FLAT_BASE numeric audit #007 — CROX 2021

Frozen MarketSmith oracle identifies Crocs (CROX) as a **FLAT_BASE** with **109.91** pivot. The frozen source note associates the historical breakout with **2021-06-15**; replay chronology begins 2021-06-14 and uses the stricter rule “first daily close >= oracle pivot”, which occurs one session earlier. Source chronology and replay close-crossing are therefore kept separate rather than forcing either date to replace the other.

Full-candidate inspection of authoritative replay **35497962478** independently reconstructs the source pivot. The CONFIRMED_STRUCTURE candidate starts/pivots **2021-05-10**, ends **2021-05-26**, pivot **109.91000366**, engine-measured depth **11.582206%**, status **REJECTED**, faults **TOO_SHORT + WIDE_LOOSE**. The OPEN_RIGHT_EDGE representation uses the same 2021-05-10 pivot and **109.91000366** level, extends through replay as-of 2021-06-14, measures depth **13.638436%**, and remains **AMBIGUOUS** under **WIDE_LOOSE**. No source-target candidate reaches RECOGNIZED.

The pivot difference is only **+$0.00000366**, approximately **+0.0000033%**, a practical exact reconstruction. The retrieved oracle does not freeze authoritative numeric left-boundary, duration, or depth/range values. Consequently the engine's 2021-05-10 boundary, 11.5822%/13.6384% depths, and TOO_SHORT flag are observations but **NOT SCORED** as source discrepancies. In particular, unlike SNPS and TW, TOO_SHORT cannot be promoted to a proven duration-semantics gap without a source duration.

On **2021-06-14**, replay high was **115.37** and close **112.58**, +2.4293% above the 109.91 pivot. Replay volume was **1.4620x prior-50** (+46.20%). The frozen oracle note labels 2021-06-15 as breakout, so this one-day chronology difference is recorded explicitly as **SOURCE_DATE_VS_REPLAY_CLOSE_CROSSING_DISCREPANCY**, not a morphology failure. T+1 relative to replay close-crossing, **2021-06-15**, opened **112.47**, +2.3292% above pivot and inside the original 5% buy zone.

Audit conclusion: **FLAT_BASE_FAMILY_MATCH / SOURCE_PIVOT_PRACTICAL_EXACT_MATCH / SOURCE_LEFT_BOUNDARY_NOT_SCORED / SOURCE_DURATION_NOT_SCORED / SOURCE_DEPTH_NOT_SCORED / SOURCE_TARGET_NOT_RECOGNIZED / TOO_SHORT_OBSERVATIONAL_ONLY / WIDE_LOOSE_GEOMETRY_GAP / SOURCE_BREAKOUT_NOTE_2021-06-15 / REPLAY_CLOSE_CROSSING_2021-06-14 / SOURCE_DATE_VS_REPLAY_CLOSE_CROSSING_DISCREPANCY / BREAKOUT_VOLUME_1.462X_OBSERVATIONAL / T1_INSIDE_ORIGINAL_5PCT_ZONE**.

Numeric-audit progress after this freeze: **37/40 = 92.5% overall**; FLAT_BASE **7/10 = 70%**.


## FLAT_BASE numeric audit #008 — CPRT 2020

Primary IBD Top Stocks evidence identifies Copart (CPRT) as a **five-week FLAT_BASE** with **92.51** buy point and states that the stock broke out on Thursday **2020-01-02**, closing **93.48**. This gives direct oracle support for family, pivot, duration, breakout date, and breakout close.

Full-candidate inspection of authoritative replay **35497962478** finds **no FLAT_BASE candidate at or near 92.51**. The nearest emitted pivot is **83.69999695**, about **-$8.8100 / -9.523%** below the oracle. Its OPEN_RIGHT_EDGE representation starts/pivots **2019-09-17**, extends through 2020-01-02, measures depth **8.781361%**, and is AMBIGUOUS under **WIDE_LOOSE**. The corresponding CONFIRMED_STRUCTURE ends **2019-10-03** and is REJECTED under **TOO_SHORT + WIDE_LOOSE**. Other emitted pivots (79.74, 67.08, 60.01, etc.) are still farther from the source target.

Because the source-target 92.51 pivot is absent, this is not principally a final geometry-gate failure. The discrepancy is upstream in **boundary/landmark/pivot construction**: the engine never constructs the source-target FLAT_BASE. The source explicitly says **five weeks**, but the emitted 83.70 structure is a different structure, so its TOO_SHORT flag must not be compared as if it adjudicated the oracle base.

Corporate-action handling requires a correction to the provisional source note. The authoritative replay uses **x4** historical price normalization, not x2. Copart had successive 2-for-1 splits after the 2020 oracle, yielding a cumulative x4 basis transformation for comparison to the 92.51 historical price. The replay therefore correctly uses prices x4 and volume /4; the stale “later 2-for-1 split restored” wording is insufficient if read as the cumulative transform.

On **2020-01-02**, replay high was **93.57** and close **93.48**, exactly corroborating the IBD-reported close and placing the close **+1.0485%** above the 92.51 pivot. Replay volume was **1.4822x prior-50** (+48.22%), observational because the source excerpt does not provide a numeric breakout-volume percentage. T+1 on **2020-01-03** opened **92.62**, only **+0.1189%** above pivot and inside the original 5% buy zone.

Audit conclusion: **FLAT_BASE_FAMILY_ORACLE / SOURCE_PIVOT_92.51_NOT_RECONSTRUCTED / SOURCE_DURATION_FIVE_WEEKS / NEAREST_ENGINE_PIVOT_83.70_MINUS_9.52PCT / NEAREST_STRUCTURE_NOT_ORACLE_STRUCTURE / UPSTREAM_BOUNDARY_LANDMARK_PIVOT_GAP / SOURCE_BREAKOUT_2020-01-02_CONFIRMED / SOURCE_CLOSE_93.48_EXACTLY_CORROBORATED / BREAKOUT_VOLUME_1.482X_OBSERVATIONAL / T1_INSIDE_ORIGINAL_5PCT_ZONE / PRICE_BASIS_CUMULATIVE_X4_VALIDATED**.

Numeric-audit progress after this freeze: **38/40 = 95% overall**; FLAT_BASE **8/10 = 80%**.


## FLAT_BASE numeric audit #009 — AMZN 2020

Frozen IBD Top Stocks oracle identifies Amazon (AMZN) as a **five-week FLAT_BASE** with **3344.39** buy point. Historical comparison explicitly restores the pre-2022-split basis using **x20** prices and inverse volume normalization.

Full-candidate inspection of authoritative replay **35497962478** independently reconstructs the source pivot. The CONFIRMED_STRUCTURE starts/pivots **2020-07-13**, ends **2020-07-21**, pivot **3344.28985596**, engine-measured depth **12.739921%**, status **REJECTED**, faults **TOO_SHORT + WIDE_LOOSE**. The OPEN_RIGHT_EDGE representation uses the same 2020-07-13 pivot and **3344.28985596** level, extends through replay as-of **2020-08-25**, measures depth **13.643853%**, and is **AMBIGUOUS** under **WIDE_LOOSE**. No source-target FLAT_BASE reaches RECOGNIZED.

The pivot difference is **-$0.10014404**, approximately **-0.002995%**, a near-exact reconstruction. The oracle explicitly states **five weeks**, whereas the engine's confirmed representation of the source-pivot lineage is rejected as **TOO_SHORT**. This is direct evidence of a duration-semantics gap, analogous to SNPS/TW, while the engine depth values are observational because no authoritative source numeric depth/range is frozen.

The replay's first daily close >= oracle pivot is **2020-08-25**: high **3357.40**, close **3346.49**, only **+0.0628%** above the 3344.39 pivot. Replay volume is **0.8414x prior-50** (-15.86%), so this close-crossing does **not** show strong volume confirmation under common O'Neil-style breakout-volume expectations; no source-equivalent numeric volume is frozen, so it remains an execution observation rather than an oracle mismatch. T+1 on **2020-08-26** opened **3351.11**, **+0.2009%** above pivot and inside the original 5% buy zone.

Audit conclusion: **FLAT_BASE_FAMILY_MATCH / SOURCE_PIVOT_NEAR_EXACT_MATCH_0.003PCT / SOURCE_DURATION_FIVE_WEEKS / CONFIRMED_STRUCTURE_TOO_SHORT_DURATION_SEMANTICS_GAP / SOURCE_DEPTH_NOT_SCORED / SOURCE_TARGET_NOT_RECOGNIZED / TOO_SHORT_AND_WIDE_LOOSE_GEOMETRY_GAP / REPLAY_CLOSE_CROSSING_2020-08-25 / BREAKOUT_VOLUME_0.841X_WEAK_OBSERVATIONAL / T1_INSIDE_ORIGINAL_5PCT_ZONE / PRICE_BASIS_X20_VALIDATED**.

Numeric-audit progress after this freeze: **39/40 = 97.5% overall**; FLAT_BASE **9/10 = 90%**.
