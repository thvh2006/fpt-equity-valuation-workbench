# Research Log

## 2026-10-08 — Reported actuals v0.1

### Question

Can the public FPT filings support a point-in-time historical base suitable for a driver forecast and reverse DCF?

### Work completed

- Registered and checksum-locked annual reports FY2020–FY2024 and the 9M2025 earnings report.
- Extracted consolidated financial anchors and selected segment/operating facts.
- Preserved EPS by filing version after observing retrospective changes.
- Reconciled balance-sheet and profit-attribution identities.
- Built and visually reviewed the analyst workbook.

### Decision

Proceed to normalization, but do not forecast per-share value until the corporate-action and diluted-share bridge is complete.

### Main risk discovered

Historical EPS is not stable across successive filings. Treating the latest displayed EPS for each year as if every observation had the same share basis could produce a false growth path.

### Next research query

Build the corporate-action/share-count bridge, then determine whether segment reclassifications permit a consistent Global IT, Domestic IT, Telecom and Education history.

## 2026-10-08 — Reported share roll-forward

### Evidence

The FY2020–FY2024 share roll-forward reconciles beginning shares plus employee/other issuance plus share dividends to ending shares for every year. Ending shares increased from 783,905,110 at FY2020 to 1,471,069,183 at FY2024.

Successive annual reports restate only the comparative weighted-average share count for the latest bonus issue. The latest observed weighted-average number for each historical year therefore does not automatically form one common-basis time series.

### Decision

Use the reported roll-forward as the control ledger. Do not mechanically combine EPS vintages or apply a single 15%/20% factor across all years. Build an explicit common-basis adjustment table before using per-share growth or producing target value per share.

## 2026-10-08 — Segment and FCFF model v0.2

### Build completed

- Mapped audited segment revenue and PBT for FY2020-FY2024 into a consistent six-column taxonomy including consolidation eliminations.
- Added one Base/Downside selector that drives segment growth, EBIT margin, tax, D&A, capex and working-capital assumptions.
- Defined EBIT before financial items as gross profit less selling and general/administration expenses.
- Calculated historical and forecast FCFF as NOPAT plus D&A less capex less change in working capital.
- Added a separate CFO-based unlevered FCF proxy for historical comparison.
- Added formula-linked revenue/EBIT and FCFF charts.

### Validation

- Seven data-integrity tests pass.
- All displayed model checks are zero within tolerance.
- No spreadsheet formula errors were found.
- The saved XLSX contains two charts with live cell bindings and the intended series colors.
- Changing the selector from Base to Downside changes forecast revenue and FCFF while FY2024 actual revenue remains unchanged; the workbook is restored to Base before export.

### Base-case output before valuation

The operating model produces FY2025E revenue of VND 69.7 trillion and FY2030E revenue of VND 120.1 trillion. FCFF is VND 8.4 trillion in FY2025E and VND 16.1 trillion in FY2030E. These are scenario outputs, not intrinsic-value conclusions.

### Open questions

- WACC and terminal-value conventions are not yet selected.
- Cash, investments, debt, leases, minority interests and associates still need an explicit enterprise-to-equity bridge.
- Weighted-average shares are not yet on one common basis across the complete history.
- Later FY2025 actuals remain excluded until the Clock A forecast is frozen for backtesting.

## 2026-10-09 — Historical valuation context v0.5

### Question

Can FPT's own trading history add useful valuation context without introducing corporate-action lookahead or double-counting the comparable P/E method?

### Work completed

- Derived 70 month-end observations from January 2020 through the 31 October 2025 cutoff.
- Preserved raw and provider-adjusted prices and created a cutoff-rebased analytical price series.
- Added the exact 20.7x Vietcap three-year average TTM P/E as a recent-regime benchmark.
- Visually reviewed SHS's FiinProX-sourced January 2014-January 2025 P/E chart and labelled its long-run mean and standard-deviation levels as approximate chart reads.
- Added implied-price references, two native charts, two terminal checks and a market-price sensitivity test.

### Anti-lookahead decision

Do not construct a monthly historical P/E series from calendar-year actual EPS. That would give early months earnings that were not yet known. Until a point-in-time TTM EPS history is available, historical P/E statistics remain external diagnostics.

The provider's currently served adjusted-price series is rebased so its 31 October 2025 observation equals the raw close on that date. This cancels uniform backward adjustments caused by corporate actions after the cutoff.

### Valuation decision

Give historical benchmarks zero incremental weight. The 60% DCF / 40% comparable P/E blend remains unchanged because a separate historical-P/E weight would count the same multiple signal twice.

### Main finding

The market price implies roughly 17.7x the model's FY2026E EPS, below the recent three-year average of 20.7x and around SHS's approximate long-run +1 standard-deviation region. The applied comparable multiple of roughly 20.2x is within the recent regime but above the current quote.

### Next research query

Translate the operating thesis into measurable monitor triggers, define green/amber/red thresholds, and surface them on a decision dashboard before freezing Clock A for the FY2025 actual backtest.

## 2026-10-11 — Thesis monitor v0.6

### Question

Which observable indicators would confirm, weaken or invalidate the Clock A thesis, and what model action should follow each breach?

### Work completed

- Added twelve indicators across demand, geography, profitability, cash conversion and valuation.
- Added editable green and red thresholds with explicit higher-is-better or lower-is-better direction.
- Extracted 9M2025 operating cash flow of VND6,027.6 billion and cash capex of VND4,125.6 billion from the Q3 2025 consolidated cash-flow statement.
- Added formula-driven indicator statuses, an overall escalation rule and a status-mix chart.
- Added a “what changes the thesis” table linking each red trigger to evidence, model response and decision implication.
- Confirmed that monitor threshold changes update the dashboard and Summary without changing the DCF.

### Clock A result

The monitor is amber: five green indicators, six amber indicators and one red indicator. Post-capex cash conversion is 23.1% and breaches the 30% red threshold. Operating cash flow / PAT is 73.2% and remains amber.

### Decision

Keep the valuation under review. Do not reduce the forecast automatically from a single nine-month cash observation. The FY2025 actual backtest must determine whether the cash-conversion weakness came from timing, recurring working-capital use or a structurally higher investment requirement.

### Next research query

Freeze the v0.6 Clock A forecast, load post-cutoff FY2025 actuals into a separate validation layer, and attribute forecast error by revenue, margin, cash conversion and valuation impact.

## 2026-10-11 — FY2025 Clock A backtest v0.7

### Question

Did the point-in-time segment model forecast FY2025 better than simple revenue baselines, and which assumptions caused the free-cash-flow error?

### Controls

- Frozen v0.6 workbook recorded with SHA-256 `0cb2a73e4f6cef7b842821149e36340d6c4cdc377d03a148ee88322f1d37da25`.
- FY2025 audited results loaded into a separate validation layer.
- Post-cutoff evidence does not update Clock A assumptions or valuation.
- Live case-selector changes leave the frozen forecast, actuals and backtest status unchanged.

### Results

- Revenue: VND70,112.8bn actual versus VND69,665.5bn forecast; 0.6% absolute error and a pass against the 2.0% review threshold.
- EBIT margin: 15.7% actual versus 16.8% forecast; 1.1 percentage-point miss.
- FCFF: VND6,029.8bn actual versus VND8,429.7bn forecast; 28.5% miss.
- The FCFF variance was driven mainly by VND918.0bn additional capex and VND1,112.7bn additional working-capital use.
- The Clock A revenue forecast outperformed a repeated-FY2024-growth baseline and the 20% management plan.
- Post-capex cash conversion improved from 23.1% at 9M2025 to 44.9% at FY2025, moving from red to amber rather than fully resolving the cash concern.
- A revenue-only actual re-anchor changes DCF value by approximately 0.3%; the material valuation question is the future margin and reinvestment path.

### Decision

Classify the backtest as mixed. Retain the segment-driver framework, but create a new Clock B forecast with revised EBIT margin, capex and working-capital assumptions. Do not overwrite Clock A.

### Next research query

Write the initiation note and decision memo using the frozen valuation, the FY2025 post-mortem and an explicit list of Clock B changes.

## 2026-10-11 — Clock B live valuation v0.8

### Question

How should FPT be valued after the 2026 deconsolidation of FPT Telecom, and does the current market price compensate for the resulting cash-conversion and comparability risks?

### Accounting decision

FPT Telecom moved from full consolidation to the equity method from 1 January 2026. Clock B does not extend the old consolidated revenue and FCFF series. It values continuing consolidated operations with FCFF and capitalises associate earnings separately. The associate book value is not added to the bridge because doing so would double count the same economic interest.

### Current evidence

- H1 revenue: VND26,268.5bn.
- H1 EBIT before financial items: VND3,880.3bn; margin 14.8%.
- H1 share of associate and JV profit: VND1,423.4bn.
- H1 parent net profit: VND5,055.0bn.
- H1 operating cash flow: negative VND1,145.7bn.
- 8M revenue and PBT: VND35,408bn and VND7,648bn, up 13.5% and 17.5% year on year.
- Shares outstanding: 1,885.7 million.
- Market price at 9 October 2026: VND57,900.

### Valuation result

- Base WACC: 10.9%; terminal growth: 4.0%.
- Operating enterprise value: VND130.7tn.
- Capitalised associate earnings: VND43.8tn.
- SOTP value: VND97,511 per share.
- 2027E P/E cross-check: VND89,978 per share.
- Blended fair value: VND94,498 per share, or 63.2% above the market price.
- Mechanical recommendation: BUY; risk label: HIGH.

### Validation

- Base-to-Downside selector testing reduced 2031 revenue and blended fair value while source actuals remained unchanged.
- Six Clock B terminal checks equal zero within tolerance.
- The workbook formula-error scan returned no matches.
- All six new Clock B sheets were rendered and visually reviewed.

### Decision

The valuation gap is large enough for a BUY classification, but the thesis is not confirmed by cash flow. Treat FY2026 operating cash flow and working-capital reversal as the next gating evidence. Keep Clock A frozen and preserve Clock B as a separate current-research artifact.

### Next research query

Draft the Clock B research update note, explain the valuation delta versus Clock A and convert the monitor into a concise investment-committee action plan.

## 2026-10-11 — Portfolio release v1.0

### Outputs

- Published the eight-page Clock B equity-research update in editable DOCX and PDF formats.
- Added a dependency-free Python valuation engine that independently reproduces the reviewed Excel Base result.
- Added a machine-readable three-scenario output, repository checks and GitHub Actions quality workflow.
- Reframed the README around reviewer sequence, analytical differentiation, falsification rules and reproducibility.

### Quality gates

- All 15 reported-data, accounting, cash-flow and valuation checks passed.
- The Base Python output matches workbook v0.8 to less than VND0.1 per share on SOTP, P/E and blended value.
- All eight report pages were rendered and visually inspected.
- The document accessibility audit reported zero high, medium or low findings.
- Personal Word metadata and revision-session identifiers were scrubbed.

### Release decision

Mark Clock B as portfolio-ready. The next research update should occur after FY2026 cash-flow disclosure; no pre-emptive refresh is required.
