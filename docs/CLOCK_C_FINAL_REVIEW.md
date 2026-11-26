# Clock C final research review

Completed26November2026. Information cutoff23November2026. Forward value date **31December2026E**. Scope: documented forward research valuation and reproducible portfolio package.

## Completed

- Verified opening data, ten exact reported-note bridges, component schedules and three linked forecast cases.
- Operating DCF with operating-cash reinvestment, terminal tax/ROIC economics and consistent mid-year discount timing.
- Associate capitalisation, cash/investment/debt bridge, NCI proxy and issued-plus-dilution denominator.
- Case valuation, WACC/g sensitivity, P/E cross-check and hypothetical reverse DCF.
- Twelve-page report, two-page memo, compact sector appendix and ten-slide PDF/HTML pitch.
- Fourteen-sheet formula workbook and interactive dashboard using one active forecast build.
- Source/forecast walkthrough plus an executed valuation-and-decision notebook.

## Result and decision

Base forward value is VND76,156/share, downside VND40,319 and upside VND109,965. Base WACC11.69%, terminal g3%, ROIC15% and terminal tax20% are analyst assumptions. Terminal contribution is72.5% of base operating EV. Associates use14times2027 attributable earnings and NCI1.5times forecast book equity. Neither is an observed market multiple.

Base FY2026E CFO / parent PAT is26.3%, below the30% add-exposure gate. Stance: WATCHLIST. The20% margin-of-safety screen is approximately VND60,925/share, conditional on cash evidence and a consistent quote/value-date bridge. No spot upside is fabricated.

## Verification

| Check | Scope |
| --- | --- |
| Python | 62/62 data and economics tests |
| Excel forecast | 378 points and two input perturbations |
| Excel valuation | 15 golden outputs,75 native sensitivity points, WACC perturbation |
| JavaScript | 1,584 forecast and147 valuation/sensitivity values |
| Saved HTML controls | 20 initialisation, case, WACC, DSO, tab, reset and recovery checks |
| Notebook | Seven valuation cells and nine forecast cells in ordinary Python |
| Independent office engine | LibreOffice:four headline values,25 native sensitivity cells,no cached formula errors |
| Presentation | PDF pages and affected Excel views rendered and reviewed |

Receipts are in `outputs/p1_final`. The forecast-only engine retains its prevaluation status because valuation is a separate layer.

## Explicit limits

1. No verified closing quote at cutoff. A current return needs a dated quote and dividend/corporate-action bridge.
2. Risk-free anchor, premium, beta and target financing mix are analyst choices. HNX traded-yield ranges are not an exact par curve.
3. NCI is a book-value proxy. Associate and parent P/E inputs are not a peer median.
4. Terminal economics transition directly to a stable state. Tax incentives, asset useful lives, FX and new M&A are simplified.
5. Downside needs a feasible financing policy before supporting an entry decision. No hypothetical commitment is inserted.
6. Microsoft Excel UI, Jupyter kernel and independent human research review are not claimed.

These qualifications must remain visible when publishing. Clock A/B economics remain frozen.
