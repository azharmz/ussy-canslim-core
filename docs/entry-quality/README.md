# Entry Quality & Execution (E0-E6)

This workstream exists because an operationally realistic H+1 fill can still be a poor-quality entry. It is **separate** from C/A fundamental selection.

## Questions

| ID | Study | Core variable |
|---|---|---|
| E0 | Independent expanded technical baseline | baseline candidate/entry logic |
| E1 | Signal-day shock | `T0 / T-1 - 1` |
| E2 | H+1 execution gap | `Open(H+1) / Close(T0) - 1` |
| E3 | Signal pivot extension | `Close(T0) / Pivot - 1` with 3%/5%/8% variants |
| E4 | Actual-fill pivot extension | `Open(H+1) / Pivot - 1` |
| E5 | Interaction | shock + gap + extension |
| E6 | Outcome diagnostics | MAE, MFE, realized return, PF, DD, exits, concentration |

## Origin

Legacy TrendFoll walk-forward contained examples of very large T-1->T0 moves followed by retracement, plus cases where H+1 itself gapped materially above the signal price. These observations generate hypotheses only; they must not dictate post-hoc thresholds.

## Rule

Pivot-extension variants 3%, 5%, and 8% are pre-specified. Other thresholds are exploratory unless separately justified and validated on untouched evidence.

CAN SLIM may eventually use a different entry/execution policy from TrendFoll. Any such rule belongs to this independent project and does not automatically modify TrendFoll production.
