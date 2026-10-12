# Investment Outcome Log

## Current status

Clock B was opened on 9 October 2026 at VND57,900 per share with a blended fair value of VND94,498. Because the observation window is only three calendar days as of 12 October 2026, no investment-performance conclusion is yet statistically or economically meaningful.

The current classification is **OPEN — EVIDENCE PENDING**, not “successful” or “failed”. The next decision gate is FY2026 operating cash flow and its working-capital bridge.

## What is measured

The outcome log separates four questions:

1. **Price outcome** — FPT total price return since the research date.
2. **Relative outcome** — FPT return less the VN-Index return over the same period.
3. **Valuation outcome** — remaining gap between observed price and the frozen Clock B fair value.
4. **Thesis outcome** — whether operating evidence confirms, weakens or invalidates the original assumptions.

A price increase does not prove the thesis was correct, and a price decline does not by itself invalidate it.

## Review cadence

| Review | Timing | Required evidence | Decision |
|---|---|---|---|
| Event review | Material disclosure | Revenue, margin, signed revenue, capex or accounting change | Maintain or re-underwrite |
| Quarterly review | Each results release | Full monitor refresh and valuation rerun | Add, hold, reduce or exit |
| Six-month scorecard | 9 April 2027 | Absolute and relative return plus thesis evidence | Interim process assessment |
| Twelve-month scorecard | 9 October 2027 | Return attribution and realised thesis path | Final Clock B scorecard |

## Decision rules

- **Confirm:** cash conversion recovers, operating indicators remain within Base thresholds and refreshed fair value retains the required margin of safety.
- **Weakening:** one critical indicator turns red or the fair-value gap falls below 15% without a compensating reduction in risk.
- **Invalidate:** two critical indicators are red, FY2026 cash conversion fails to reverse materially, or refreshed fair value falls below market.
- **Close successfully:** the price converges toward fair value while the operating thesis is substantially confirmed.
- **Close unsuccessfully:** the thesis is invalidated before convergence, regardless of interim price movements.

## Data entry

Observations live in `data/sample/investment_outcomes.csv`. Add a row with:

```bash
python scripts/update_investment_outcome.py \
  --date 2027-04-09 \
  --fpt-price 72000 \
  --vnindex 1850 \
  --status CONFIRMING \
  --note "FY2026 cash conversion recovered"
```

Prices and benchmark levels must be point-in-time observations with a source URL. Never revise the initial row for subsequent corporate actions; add an adjustment note and preserve the original observation.
