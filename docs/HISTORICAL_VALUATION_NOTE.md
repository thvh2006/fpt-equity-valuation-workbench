# Historical Valuation Note

## Decision use

The historical-valuation page answers a narrow question: does the current market-implied multiple look unusual relative to FPT's own recent and long-run trading regimes?

It is a diagnostic layer, not a third valuation method. The final blended value remains 60% DCF and 40% comparable P/E so the same multiple signal is not counted twice.

## Benchmark hierarchy

1. **Current model-implied 2026F P/E** — market price divided by the model's FY2026E parent EPS.
2. **Applied comparable P/E** — segment-mix peer median after the disclosed group adjustment.
3. **Recent-regime benchmark** — Vietcap's exact three-year average TTM P/E of 20.7x at 21 October 2025.
4. **Long-run benchmark** — approximate levels read from SHS's FiinProX-sourced January 2014-January 2025 P/E chart: 14.5x mean, 9.0x/20.0x at ±1 standard deviation and 3.5x/25.5x at ±2 standard deviations.

Approximate chart-read levels are labelled as such and are not presented as database-precision observations.

## Price-history treatment

The public sample contains one observation per trading month from January 2020 to 31 October 2025. It preserves:

- raw close;
- the provider's currently served adjusted close;
- an analytical close rebased to the Clock A cutoff.

The rebase is:

`factor = raw close at cutoff / provider-adjusted close at cutoff`

`cutoff-basis close = provider-adjusted historical close × factor`

A corporate action after the cutoff normally changes all earlier backward-adjusted observations by a common factor. Anchoring the series to the raw cutoff close cancels that later factor and prevents the historical chart from inheriting post-cutoff corporate-action information.

## Anti-lookahead controls

- Operating forecasts use information available by 31 October 2025.
- The price series stops at the cutoff.
- Post-cutoff changes embedded in the provider's current adjusted series are neutralised through the cutoff rebase.
- No monthly historical P/E series is manufactured from full-year EPS. Doing so would leak future intra-year earnings into earlier months.
- The SHS and Vietcap benchmarks were both published before the cutoff.

## Interpretation

The market price implies roughly 17.7x the model's FY2026E EPS. This is below Vietcap's recent three-year TTM average of 20.7x and near the long-run +1 standard-deviation region shown by SHS. The applied comparable multiple of roughly 20.2x is therefore aggressive relative to the current quote but not outside the recent valuation regime.

The conclusion is conditional on the model's EPS. A historical multiple cannot compensate for an earnings forecast that is wrong, so thesis monitoring should focus next on signed revenue conversion, Global IT growth, EBIT margin and cash conversion.

## Limitations

- The long-run SHS levels are approximate chart reads rather than an exported time series.
- The current workbook does not contain point-in-time monthly TTM EPS, so it does not claim to backtest valuation percentiles.
- The VNDirect raw cutoff close differs from the model's established HOSE-referenced price by approximately 1%; both are disclosed and the existing valuation input is preserved.
- The rebased series is price-only and excludes dividends.
