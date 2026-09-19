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
- prior peak / base high: 392.79 on April 4
- source buy point: 392.79
- base duration: six weeks
- base trading range/depth characterization: tight 8% range
- breakout date: May 18
- breakout move: gap up 8.7%
- breakout volume: 163% above its 50-day average
- source buy-zone upper bound: 412.43
- prior context: an earlier cup-with-handle breakout occurred Feb. 1; this fact is context only and must not be used to force the flat-base detector

Year resolution:
- The source chronology is treated as the historical SNPS flat-base example whose April 4 peak and May 18 breakout are to be resolved against provider history before detector replay.
- The replay script must fail closed if historical OHLCV cannot uniquely corroborate the 392.79 April-4 high / May-18 breakout chronology. Do not silently guess a year.

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
