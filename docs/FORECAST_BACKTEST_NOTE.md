# FY2025 Forecast Backtest Note

## Objective

Test whether the 31 October 2025 Clock A forecast explained FY2025 outcomes before any post-cutoff result was visible. The test separates forecast quality from later model updating.

## Anti-leakage control

- Frozen artifact: `fpt_equity_valuation_v0_6.xlsx`.
- SHA-256: `0cb2a73e4f6cef7b842821149e36340d6c4cdc377d03a148ee88322f1d37da25`.
- Information cutoff: 31 October 2025.
- Actual evidence: FPT Annual Report 2025 and the issuer's FY2025 business-results release.
- Post-cutoff actuals do not feed Assumptions, Segment Build, FCFF Build or the original DCF.
- Changing the live Base/Downside selector does not change the frozen review snapshot or backtest conclusion.

## Primary evaluation

| Metric | Frozen forecast | FY2025 actual | Error | Review tolerance | Result |
|---|---:|---:|---:|---:|---|
| Group revenue | VND69,665.5bn | VND70,112.8bn | 0.6% | 2.0% | Pass |
| EBIT margin | 16.8% | 15.7% | 1.1pp | 0.5pp | Miss |
| FCFF | VND8,429.7bn | VND6,029.8bn | 28.5% | 10.0% | Miss |

The overall result is mixed. The model estimated scale well but overestimated the conversion of revenue into operating profit and free cash flow.

## Revenue attribution

Global IT, Domestic IT and less-negative consolidation eliminations offset weaker Telecommunication and Education, Investment and Other revenue. The group-level error was small because material segment errors moved in opposite directions.

The Clock A driver forecast had a lower revenue error than both comparison baselines:

- repeat FY2024 revenue growth;
- management's FY2025 revenue plan of 20% growth.

This supports retaining the segment-driver structure. It does not validate every segment assumption.

## FCFF attribution

The VND2,399.9bn FCFF miss reconciles as follows:

- NOPAT: negative VND427.1bn;
- D&A: positive VND57.9bn;
- capex: negative VND918.0bn;
- change in working capital: negative VND1,112.7bn.

The result identifies two distinct forecast errors. Margin expansion did not occur, and capital intensity plus working-capital use were materially higher than assumed.

## Cash-signal post-mortem

The 9M2025 cash warning contained information, but the year-end outcome was less severe than the nine-month snapshot implied:

- operating cash flow / PAT improved from 73.2% to 90.2%;
- post-capex cash conversion improved from 23.1% to 44.9%;
- capex / revenue finished at 7.3% versus the frozen 6.0% FY2025 assumption.

The correct conclusion is not that the 9M warning was false. The red signal improved to amber as fourth-quarter cash flow recovered, while full-year capital intensity and working-capital use still caused a material FCFF miss.

## Valuation interpretation

Replacing only the FY2025 segment-revenue anchor and retaining all later frozen Base-case ratios increases DCF value by approximately 0.3%. FY2025 FCFF itself has no direct effect because the explicit DCF period begins in FY2026.

This diagnostic should not be treated as a revised target price. A proper Clock B valuation must re-underwrite:

1. EBIT-margin progression;
2. capex normalization;
3. working-capital intensity;
4. the timing and economics of AI Factory, data-center and content investment.

## Decision

Retain the revenue-driver architecture. Do not retain the old profitability and cash-conversion path without new evidence. Preserve Clock A unchanged and create Clock B as a new version.
