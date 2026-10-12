# FPT Reported-Data Extraction Report v0.1

## Objective

Create a point-in-time, reviewable actuals base for an FPT valuation case. This release records reported facts; it does not yet normalize earnings, shares or cash flows and does not express an investment recommendation.

## Information boundary

- Forecast origin: 9M2025.
- Clock A information cutoff: 31 October 2025.
- Included primary sources: FPT annual reports FY2020–FY2024 and FPT Earnings Report 9M2025.
- FY2020 consolidated facts use the reclassified comparative disclosed in the FY2021 filing.
- Later FY2025 actual results remain outside Clock A and will be used only for out-of-sample validation.

## Data products

| Product | Grain | Purpose |
|---|---|---|
| `reported_annual_core.csv` | one row per fiscal year | Audited income statement, cash-flow and balance-sheet anchors |
| `operating_facts_9m2025.csv` | one row per metric and segment | YTD operating context available at forecast origin |
| `eps_as_presented.csv` | one row per filing-version observation | Preserve retrospective changes in per-share presentation |
| `share_count_bridge_reported.csv` | one row per fiscal year | Reconcile beginning shares, issuance, share dividends and ending shares |
| `fpt_actuals_v0_1.xlsx` | analyst review workbook | Review trends, controls, sources and unresolved scope |

Values in the annual CSV remain in raw VND. The workbook displays VND billion for readability. Units and source-page fields are explicit.

## Controls performed

All five annual observations passed the following formula tests within the defined tolerance:

1. total assets = total liabilities + total owners' equity;
2. profit after tax = parent profit after tax + non-controlling-interest profit;
3. reported sector totals reconcile to group values where the source provides a complete bridge;
4. filing-version EPS observations are retained rather than overwritten.

The workbook was recalculated, scanned for spreadsheet errors and visually reviewed sheet by sheet after rendering.

## Early analytical observations

- Revenue increased from VND 29.8 trillion in FY2020 to VND 62.8 trillion in FY2024 while the reported PBT margin stayed near 17%–18%.
- Operating cash flow less capital-expenditure purchases increased materially in FY2023–FY2024, but this is not yet normalized free cash flow.
- Cash and short-term investments less reported borrowings increased across the period; valuation treatment still requires checks for restricted cash, leases and other debt-like items.
- Comparative EPS changes between successive filings. This means a price-per-share model must use a corporate-action-adjusted share bridge rather than combine historical EPS values without adjustment.
- At 9M2025, issuer-reported Global IT Services growth, signed revenue and large-client/deal counts provide candidate drivers for the forecast, subject to definition and period-consistency checks.

These are descriptive observations, not conclusions about intrinsic value.

## Items deliberately unresolved

- one common-basis diluted weighted-average share history; the reported corporate-action roll-forward is captured, but successive EPS comparatives remain on different restatement vintages;
- a consistent FY2020–FY2025 segment taxonomy;
- working-capital classifications and non-recurring items;
- depreciation, amortization, leases, associates and capex normalization;
- market price, valuation date, beta, risk-free rate and equity-risk-premium convention;
- peer set and comparable-multiple definitions.

## Acceptance gate for v0.2

The next release may begin forecasting only after:

- the share-count bridge reconciles reported EPS and parent earnings;
- segment history has an explicit mapping table and documented breaks;
- normalized FCFF reconciles to reported cash flow;
- every manual adjustment has a source, rationale and reversible calculation;
- Clock A data is frozen before FY2025 actuals are opened for backtesting.
