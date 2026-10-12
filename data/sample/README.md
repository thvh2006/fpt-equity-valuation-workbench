# Sample Data

## Files

### `reported_annual_core.csv`

Core audited consolidated facts for FY2020–FY2024. Values are raw VND integers. Each year uses a current-year audited filing where practical; FY2020 uses the reclassified comparative presented in the FY2021 audited filing.

`capex_purchase` and `dividends_paid` are stored as positive outflow magnitudes although the source cash-flow statement presents parentheses/negative signs.

### `eps_as_presented.csv`

EPS observations are deliberately stored by filing rather than collapsed into one history. Comparative EPS changes across later filings, demonstrating why per-share history must be normalized for stock dividends/corporate actions before valuation.

Do not select the latest number per year silently. Recompute a fully diluted, consistently adjusted series in the normalization layer.

### `share_count_bridge_reported.csv`

Reported roll-forward of beginning shares, employee/other issuance, share dividends and ending shares. It also records the latest weighted-average observation found for each fiscal year.

The five weighted-average observations do not yet form one common FY2024 share-basis series because each comparative was restated in a different subsequent filing.

### `operating_facts_9m2025.csv`

YTD operating and segment KPIs from the 9M2025 earnings report. Values use the displayed unit—mostly VND billion, with counts and VND/share explicitly labelled.

The file also stores issuer-presented year-on-year growth rates as numeric `ratio` observations for the thesis monitor. Consolidated 9M2025 operating cash flow and cash capex are taken from page 8 of the Q3 2025 consolidated financial statements. Capex is stored as a positive outflow magnitude.

Do not compare YTD values directly to annual figures without annualization/seasonality logic.

### `fy2025_actuals.csv`

Post-cutoff FY2025 audited consolidated statements, business-segment values and selected issuer operating facts. Financial statement values use VND billion and preserve signed cash-flow effects for working-capital lines. Capex and interest paid are stored as positive outflow magnitudes for analysis.

This file is validation evidence only. It must not feed Clock A assumptions or replace the frozen forecast. The workbook calculates EBIT, effective tax, working-capital use and FCFF in a separate derived section so reported inputs remain visible.

### `segment_history_reported.csv`

Reported segment revenue and profit before tax for FY2020-FY2024. The taxonomy is mapped to six consistent columns, including consolidation eliminations. Education, investment and other activities remain combined because the audited segment note reports them together.

### `fcff_history_reported.csv`

Historical inputs for a transparent FCFF build. `ebit_before_financial_items` equals gross profit less selling and general/administration expenses. `working_capital_cash_effect` is the sum of reported cash-flow changes in receivables, inventories, payables and prepaid expenses. A positive value is a cash inflow.

### `fpt_monthly_price_history.csv`

Month-end FPT price observations from the VNDirect Finfo stock-prices endpoint, January 2020 to 31 October 2025. The file preserves the raw close and the provider's currently served adjusted close.

Because a current adjusted-price series can incorporate corporate actions after the Clock A cutoff, the analytical series is rebased by:

`cutoff rebase factor = raw close at 31-Oct-2025 / provider-adjusted close at 31-Oct-2025`

`cutoff-rebased historical close = provider-adjusted close × cutoff rebase factor`

This removes uniform backward adjustments introduced after the cutoff while retaining pre-cutoff corporate-action continuity. It is a price-history control, not a total-return series.

## Status

- Extraction: manual-assisted from page-preserving PDF text.
- Visual verification: FY2024 and FY2025 audited statements plus key 9M2025 slides completed.
- Arithmetic validation: automated checks in `tests/test_reported_data.py`.
- Normalization: not yet applied.
- Investment conclusion: none.

## Known limitations

- Auditor report date is not automatically the public availability date.
- Annual report 2020 text extraction was weak; FY2020 uses reclassified comparative values from FY2021.
- Segment taxonomy and consolidation scope still require a cross-year bridge.
- EPS is not yet safe for trend or valuation use.
- The month-end price sample is factual public market data derived from a public endpoint; users should refresh it subject to the provider's current terms before production use.
- Historical P/E bands in the workbook use external broker benchmarks as diagnostics. They are not reconstructed from the sample price file because a point-in-time TTM EPS history is not yet available.
