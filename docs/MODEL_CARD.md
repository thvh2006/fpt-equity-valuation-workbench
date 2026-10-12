# Model Card

## Model identity

| Field | Definition |
|---|---|
| Model | FPT Clock B equity valuation |
| Version | 1.0 |
| Valuation date | 9 October 2026 |
| Issuer | FPT Corporation, HOSE: FPT |
| Primary decision | Whether valuation upside compensates for cash-conversion and accounting-transition risk |
| Primary method | Continuing-operations FCFF DCF plus capitalised associate earnings |
| Cross-check | 2027E parent earnings at an explicit P/E multiple |
| Base output | VND94,498 per share, 63.2% above the observed market price |
| Intended user | Equity analyst or investment committee reviewer |

## Intended use

The model supports point-in-time equity research, scenario comparison, assumption review and thesis monitoring. It is designed to demonstrate an auditable research process rather than to produce an automated trading signal.

The model is suitable for:

- reviewing the economic effect of FPT Telecom's move to equity-method accounting;
- testing revenue, margin, reinvestment and cost-of-capital assumptions;
- separating source facts from analyst judgement;
- framing a measured position and defining evidence that would invalidate the thesis;
- comparing a frozen historical forecast with later actual results.

It is not suitable for:

- high-frequency or execution decisions;
- statutory reporting;
- use without verifying source updates after the valuation cutoff;
- treating the mechanical BUY output as advice;
- comparing 2025 and 2026 group revenue without adjusting for the accounting perimeter.

## Research-clock design

Clock A is frozen at 31 October 2025. FY2025 results published later are loaded only into the backtest layer and cannot alter the original forecast or valuation.

Clock B is the current research view at 9 October 2026. It uses H1 reviewed financial statements, 8M operating evidence, the post-bonus share count, current market price and an updated risk-free rate. Clock A and Clock B are deliberately separate artifacts.

## Inputs

### Reported and market inputs

- H1 2026 revenue, EBIT, associate profit, parent profit and cash flow;
- H1 cash, short-term investments, debt and non-controlling interests;
- 8M2026 revenue and profit-before-tax growth;
- H1 signed-revenue, Japan and AI growth indicators;
- 1,885.7 million post-bonus shares;
- VND57,900 market price at the cutoff;
- 4.58% Vietnam 10-year government-bond yield.

### Analyst assumptions

- revenue growth by scenario;
- EBIT margin recovery;
- D&A, capex and working-capital intensity;
- associate-profit growth and capitalisation multiple;
- beta, equity risk premium and terminal growth;
- 2027E P/E cross-check multiple;
- 60% SOTP and 40% earnings-cross-check weighting.

Editable assumptions are separated from reported source facts in both the workbook and the JSON input file.

## Calculation sequence

1. Forecast continuing-operation revenue and EBIT from 2026E to 2031E.
2. Convert EBIT to NOPAT using a normalised tax rate.
3. Calculate FCFF as NOPAT plus D&A less capex and change in working capital.
4. Discount 2027E–2031E FCFF using mid-year timing.
5. Calculate terminal value at 31 December 2031.
6. Capitalise 2027E associate and joint-venture earnings separately.
7. Add cash and short-term investments; subtract debt and NCI.
8. Divide by post-bonus shares to obtain SOTP value per share.
9. Cross-check against 2027E EPS and blend the two methods.

Associate book value is disclosed but not added because associate earnings are already capitalised. This prevents double counting.

## Scenario governance

| Driver | Downside | Base | Upside |
|---|---:|---:|---:|
| 2031E revenue growth | 5.0% | 9.0% | 12.0% |
| 2031E EBIT margin | 14.6% | 16.3% | 17.5% |
| WACC | 11.89% | 10.89% | 10.14% |
| Terminal growth | 3.0% | 4.0% | 4.5% |
| Associate multiple | 11.0x | 14.0x | 17.0x |
| 2027E P/E | 12.0x | 15.0x | 18.0x |
| Blended value | VND62,635 | VND94,498 | VND128,650 |

One authoritative selector drives the operating forecast and valuation. Reported actuals remain unchanged when the scenario changes.

## Validation

- The independent Python engine reproduces Base SOTP, P/E and blended value to within VND0.1 per share of the reviewed workbook.
- Fifteen accounting, extraction, cash-flow and valuation tests pass.
- Six Clock B terminal checks equal zero within tolerance.
- The Base, Downside and Upside results are monotonically ordered.
- The final workbook and report were rendered and visually reviewed.
- GitHub Actions runs the model and checks on each push and pull request.

## Monitoring and outcome policy

The primary live risk is cash conversion. H1 operating cash flow was negative VND1.15tn versus VND5.05tn of parent net profit.

Re-underwrite when revenue growth falls below 10%, EBIT margin falls below 14%, capex exceeds 6.5% of revenue, or two monitored indicators are red. Do not increase exposure before FY2026 operating cash flow shows a substantial second-half reversal.

Investment outcomes are recorded separately from the model in `data/sample/investment_outcomes.csv`. The outcome log must preserve the original market price and fair value, record subsequent prices and benchmark levels, and explain whether thesis evidence—not price alone—changed the decision.

## Limitations

- The 2026 revenue anchor annualises eight months of reported evidence.
- The associate line includes entities beyond FPT Telecom.
- Current licensed peer forecasts are not redistributed.
- H1 cash flow is not annualised because working-capital timing can reverse.
- Page-change monitoring identifies new evidence but does not automatically change assumptions or recommendations.

## Ownership and update cadence

Refresh after results releases, material disclosures or a monitor breach. Each refresh requires a new information cutoff, source record, assumption-change note, model output and investment-outcome observation. Historical clocks must never be overwritten.
