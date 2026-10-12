# FPT Forecast and Valuation Model Note v0.7

## Purpose

Translate the Clock A evidence set into a reviewable FY2025E-FY2030E operating forecast and a point-in-time valuation at 31 October 2025. The workbook keeps operating assumptions, market inputs, WACC, DCF mechanics, the enterprise-to-equity bridge, comparable-company evidence and blended valuation visible as separate steps.

## Calculation flow

```text
selected case
-> segment revenue growth
-> consolidated revenue after eliminations
-> EBIT before financial items
-> NOPAT
-> D&A, capex and change in working capital
-> FCFF
-> WACC and discounting
-> enterprise value
-> enterprise-to-equity bridge
-> value per share, reverse DCF and sensitivity
-> FY2026E parent-earnings bridge
-> segment-mix peer multiple
-> DCF / comparable blended valuation
-> historical multiple context and corporate-action-safe price history
-> thesis-monitor indicators, thresholds and decision response
-> frozen Clock A forecast review against FY2025 audited actuals
-> summary and charts
```

All checks are terminal readers. No forecast or output formula depends on the Checks sheet.

## Segment taxonomy

The build preserves the audited disclosure categories:

1. Global IT;
2. Domestic IT;
3. Telecom;
4. Digital content;
5. Education, investment and other activities;
6. consolidation eliminations.

Education, investment and other activities remain combined because the audited segment note does not provide a complete separate history for all three components.

## EBIT definition

`EBIT before financial items = gross profit - selling expense - general and administration expense`

This definition excludes financial income, financial expense, profit from associates and other income/expense. It is more suitable for FCFF than FPT's reported “net operating profit,” which includes several financial and associate items.

## FCFF definition

`FCFF = EBIT × (1 - cash tax rate) + D&A - capex - change in working capital`

Historical change in working capital is the negative of the combined cash-flow effect from receivables, inventories, payables and prepaid expenses. Forecast change in working capital is tied to incremental revenue.

The workbook also presents:

`CFO-based unlevered FCF proxy = CFO + interest paid × (1 - cash tax rate) - capex`

The proxy is a comparison, not the primary FCFF calculation. Differences reflect classification and scope differences between the two approaches.

## Scenario design

- One numeric selector controls Base or Downside.
- Active assumptions link to the selected case.
- Historical actuals never depend on the selector.
- Forecast formulas refer to active assumptions rather than maintaining parallel forecast builds.
- Each material assumption has a concise rationale and evidence reference in the workbook.

## Validation performed

- audited balance-sheet and PAT identities;
- segment revenue and PBT reconciliation;
- reported share roll-forward;
- segment-to-FCFF and Summary-to-FCFF links;
- spreadsheet formula-error scan;
- Base/Downside recalculation test with FY2024 actual immutability;
- terminal-growth recalculation test with market-price immutability;
- peer-adjustment recalculation test with DCF and market-price immutability;
- historical-context recalculation test and cutoff-price rebase reconciliation;
- thesis-monitor threshold recalculation test with DCF immutability and Summary status linkage;
- Clock A freeze test: changing the live Base/Downside selector does not change frozen forecast, actual or backtest status;
- FY2025 segment-revenue, PAT-attribution and FCFF-variance reconciliations;
- revenue-only actual re-anchor reconciliation;
- valuation-method weight, comparable-value and Summary-to-blended-value checks;
- Q3 2025 balance-sheet, WACC-weight and enterprise-to-equity bridge checks;
- recalculation in an Excel-compatible engine;
- visual review of every worksheet;
- saved-file structure and chart-binding checks.

## Valuation conventions

- Valuation date: 31 October 2025.
- FY2025 is an operating forecast anchor, but the DCF discounts FY2026E-FY2030E FCFF so cash flows earned before the valuation date are not counted again.
- Discount timing uses approximate mid-year points for explicit FCFF and 31 December 2030 for terminal value.
- WACC uses the 31 October 2025 Vietnam 10-year government bond yield, a January 2025 Vietnam equity risk premium, an FPT-specific beta, observed borrowing cost and market-value capital weights.
- The equity bridge adds cash, short-term investments, associates and net other financial investments, and subtracts debt and non-controlling interests using the 30 September 2025 consolidated balance sheet.
- Cash and non-operating investment inclusion rates are editable to test whether reported balances are fully excess to operations.

## Comparable-valuation conventions

- Peer observations are point-in-time and were available before the 31 October 2025 cutoff.
- Global IT and telecom peers use Vietcap data at 21 October 2025. Education peers use Vietcap data at 12 August 2025 because the October table did not publish an education block.
- The model retains visible high-multiple observations and uses medians so outliers do not control the result.
- Segment peer medians are weighted by FPT's 9M2025 PBT mix: technology 45.4%, telecom 33.8%, and education, investment and other 20.7%.
- The resulting 21.2x mix-adjusted 2026F P/E receives a transparent 5% group comparability adjustment, producing a 20.2x applied multiple.
- FY2026E parent earnings are derived from the model's EBIT, the FY2024 PBT/EBIT relationship, the selected-case tax rate and the 9M2025 parent share of group PAT.
- The low P/E reference is FPT's observed 17.0x 2026F P/E in Vietcap's 22 October 2025 report. It is a market reference, not a statistical peer quartile.
- DCF receives a 60% weight and comparable valuation 40%. Both weights and the peer adjustment are editable.

## Historical-valuation conventions

- The monthly price series uses the VNDirect Finfo endpoint from January 2020 through the 31 October 2025 cutoff.
- Provider-adjusted prices as currently served may include corporate actions after the cutoff. The workbook rebases the full adjusted series so its cutoff observation equals the raw cutoff close. This neutralises uniform post-cutoff backward adjustments while retaining pre-cutoff continuity.
- The model price remains VND102,830 from the established HOSE-referenced source. VNDirect's raw close is VND103,900; the approximately 1% source difference is disclosed rather than silently overwritten.
- Vietcap's exact three-year average TTM P/E of 20.7x is treated as a recent-regime benchmark.
- The SHS / FiinProX January 2014-January 2025 P/E chart is used only for approximate long-run context: mean 14.5x, ±1 standard deviation 9.0x/20.0x and ±2 standard deviations 3.5x/25.5x.
- Historical benchmarks have zero additional weight in the blended valuation. Giving them a third weight would double-count P/E evidence already represented by the comparable method.

## Base outputs

- WACC: 10.23%.
- Terminal growth: 4.0%.
- DCF value: VND132,527 per share.
- Market price at the valuation date: VND102,830 per share.
- DCF price gap: 28.9%.
- Comparable value: VND116,754 per share.
- Blended value: VND126,218 per share.
- Blended price gap: 22.7%.
- FY2026E EPS: VND5,794 per share.
- Applied 2026F P/E: 20.2x.
- Current market-implied 2026F P/E: 17.7x.
- Recent three-year average TTM P/E: 20.7x.
- Market-implied terminal growth: 1.4%.
- Terminal value / enterprise value: 76.8%, disclosed as a key sensitivity rather than treated as a comfort metric.

## Thesis-monitor conventions

- Twelve indicators cover demand, geography, profitability, cash conversion and valuation.
- Observed operating metrics link to the 9M2025 input sheet. Valuation diagnostics link to the completed valuation schedules.
- Green and red thresholds are editable in Assumptions. Amber is the interval between them.
- The direction field supports both higher-is-better and lower-is-better metrics. Threshold ordering is checked independently on the Checks sheet.
- Overall status is red when at least two indicators are red. It is amber when any indicator is red or at least four are amber. Otherwise it is green.
- Monitor outputs do not feed the forecast or valuation. They identify when the analyst should change assumptions, but the change must be made explicitly in Assumptions.
- The base snapshot is amber: five green indicators, six amber indicators and one red indicator.
- The red indicator is post-capex cash conversion: `(9M2025 operating cash flow - cash capex) / PAT = 23.1%`, below the 30% red threshold.

## FY2025 forecast-review conventions

- The v0.6 Base-case snapshot is identified by SHA-256 and stored as immutable forecast evidence in `Forecast Review`.
- FY2025 results published after 31 October 2025 enter only `FY25 Actuals` and the validation layer. They do not overwrite Assumptions, Segment Build, FCFF Build or the original valuation.
- The primary tests are group revenue, EBIT margin and FCFF. Review tolerances are 2.0% for revenue, 0.5 percentage point for EBIT margin and 10.0% for FCFF.
- Revenue baselines are a repeat of FY2024 revenue growth and management's 20% FY2025 plan. They are evaluated on the same FY2025 actual.
- The revenue-only valuation diagnostic replaces the FY2025 segment-revenue anchor but retains the frozen Base-case ratios, WACC, terminal growth and equity bridge. It is not a revised target price.
- The result is mixed: revenue passes, while EBIT margin and FCFF miss their review tolerances.

## FY2025 backtest findings

- Group revenue was VND70,112.8 billion versus VND69,665.5 billion forecast, a 0.6% absolute error.
- EBIT margin was 15.7% versus 16.8% forecast, a 1.1 percentage-point miss.
- FCFF was VND6,029.8 billion versus VND8,429.7 billion forecast, a 28.5% miss.
- The FCFF miss comprised VND427.1 billion lower NOPAT, partly offset by VND57.9 billion higher D&A, plus VND918.0 billion additional capex and VND1,112.7 billion additional working-capital use.
- The driver revenue forecast outperformed both simple revenue baselines. The margin-expansion assumption did not outperform a stable FY2024 margin.
- Full-year operating cash flow / PAT recovered to 90.2%. Post-capex cash conversion improved from 23.1% at 9M2025 to 44.9% for FY2025, moving from red to amber under the frozen threshold framework.
- A revenue-only actual re-anchor changes DCF value by only 0.3%. The larger economic issue is not scale but profitability, capex and working-capital conversion, which require a separate Clock B re-underwrite.

## Not yet included

- common-basis historical diluted shares for EPS trend analysis;
- a fully point-in-time monthly TTM EPS series suitable for formal multiple backtesting;
- a separate operating lease adjustment beyond reported finance-lease borrowings;
- a Clock B forecast incorporating the FY2025 post-mortem;
- a completed initiation note and investment decision memo.
