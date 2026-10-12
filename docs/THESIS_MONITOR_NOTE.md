# FPT Thesis Monitor

## Purpose

The monitor converts the investment thesis into observable conditions. It separates three questions:

1. Is demand supporting the forecast?
2. Are reported earnings converting into cash?
3. Does the valuation still compensate for forecast and terminal-value risk?

The monitor does not change the forecast automatically. A breach tells the analyst which assumption to revisit and which evidence to collect.

## Indicator set

| Category | Indicators |
|---|---|
| Demand | group revenue growth, Global IT revenue growth, signed revenue growth, growth in clients with at least USD 1m revenue, growth in deals of at least USD 10m |
| Geography | Japan revenue growth, APAC revenue growth |
| Profitability | Global IT PBT margin |
| Cash | operating cash flow / PAT, post-capex cash conversion |
| Valuation | blended price gap, terminal value / enterprise value |

`Post-capex cash conversion = (operating cash flow - cash capex) / profit after tax`

## Threshold logic

For higher-is-better metrics:

- green: observed value is at or above the green threshold;
- amber: observed value is below green but at or above red;
- red: observed value is below the red threshold.

For lower-is-better metrics, the inequalities reverse.

Thresholds are editable inputs in the Assumptions sheet. Green and red levels must retain a valid ordering. The Checks sheet reports any ordering violation.

## Overall status

- **Red:** at least two indicators are red.
- **Amber:** at least one indicator is red, or at least four indicators are amber.
- **Green:** neither red condition nor amber condition is met.

This rule avoids turning one noisy quarter into an automatic thesis rejection while still forcing a review when a material indicator breaches.

## Clock A result

At the 31 October 2025 cutoff, the monitor is amber:

- 5 green;
- 6 amber;
- 1 red.

The red indicator is 9M2025 post-capex cash conversion at 23.1%, below the 30% red threshold. Operating cash flow / PAT is 73.2%, which remains amber. Together these show that earnings growth was not converting into post-investment cash at the preferred rate during the period.

This does not prove permanent deterioration. The next review should separate recurring working-capital use, one-off investment timing and the operating return expected from higher capex.

## Escalation map

- Demand breach: reduce Global IT growth assumptions and re-test the applied P/E.
- Margin breach: lower forecast EBIT margins and FCFF.
- Cash breach: raise capex or working-capital requirements and lower DCF value.
- Valuation breach: rerun DCF, comparable P/E and reverse DCF before adding exposure.

## Quarterly refresh workflow

1. Load the new earnings report and consolidated financial statements.
2. Update observed KPI inputs without changing thresholds.
3. Review status changes and explain each new amber or red result.
4. Decide whether the evidence is temporary, structural or a data-quality issue.
5. Change forecast assumptions only when the evidence supports it.
6. Save the prior forecast and monitor snapshot before producing a new valuation version.

## Limitations

- The monitor currently contains one operating snapshot, not a multi-quarter trend.
- Signed revenue and large-deal metrics use issuer definitions that may change between reports.
- Nine-month cash conversion can be seasonal. It should be compared with FY2025 actuals and later quarterly history before drawing a structural conclusion.
- Thresholds are analyst governance choices, not statistically estimated breakpoints.
