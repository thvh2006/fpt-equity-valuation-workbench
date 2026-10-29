# Clock C source review — 29 October 2026

## Status

**Material new evidence confirmed. Clock C re-underwriting is required.**

The scheduled monitor correctly opened a review after FPT published its 9M2026 earnings release on 21 October and Q3 consolidated financial statements on 28 October. Both dates are after Clock B's 9 October information cutoff. Clock B and release v1.0 remain frozen and auditable; they are not silently overwritten.

## Evidence reviewed

- FPT 9M2026 earnings release: revenue of VND40.023tn and profit before tax of VND8.770tn, up 12.4% and 17.0% year on year on the issuer's restated comparable basis.
- Global IT revenue of VND28.538tn grew 11.6%; Japan grew 17.2% in VND terms; signed Global IT revenue of VND36.137tn grew 23.1%.
- Q3 consolidated financial statements: nine-month parent profit after tax of VND7.778tn, operating cash flow of VND0.952tn and capex cash outflow of VND2.029tn.
- Q3 balance sheet: cash of VND7.377tn, short-term financial investments of VND21.450tn, interest-bearing debt and finance leases of approximately VND16.596tn, and non-controlling interests of VND1.166tn.

The official Q3 PDF SHA-256 is `d4bbb4fd3fc1fdc93a54aeaa0a6091ac2f93f3ea893ecf61db274a34e818ed32`.

## Decision impact

The operating thesis is mixed rather than broken:

- Revenue, profit, signed demand and associate contribution remain positive.
- Nine-month cash conversion is only **12.24% of parent profit after tax** (`0.952 / 7.778`), below the model's explicit 30% add-exposure threshold.
- Receivables and inventories consumed cash, while payables and deferred expenses also moved against operating cash flow.

Therefore:

1. retain the existing position only within its current risk budget;
2. do not add exposure while cash conversion remains below 30%;
3. do not reuse Clock B's VND94,498 fair value as a fresh recommendation;
4. complete a Clock C rebuild using the Q3 balance sheet, nine-month cash flow, updated market price and cost of capital before publishing a new valuation;
5. keep v1.0 as the last reviewed release until the workbook, report, Python engine and checks reconcile under the new cutoff.

## Monitoring disposition

The H1 and 8M source pages remain available and their reported operating facts are unchanged. Their full-page fingerprints changed after an issuer-site redesign, so the verified 29 October fingerprints become the new availability baselines. The disclosure-register change is substantive and is preserved through this note and the new source entries rather than dismissed as a false positive.

## Release gate

Release v1.1 is blocked until all of the following pass:

- Clock C data manifest and point-in-time market inputs are complete;
- Excel and Python produce the same Base, Downside and Upside values;
- cash-conversion and working-capital scenarios are re-underwritten;
- the investment outcome log preserves Clock B without backfilling;
- the executed notebook and committee report are refreshed;
- all automated checks pass.
