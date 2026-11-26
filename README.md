# FPT Equity Research Workbench

FPT (HOSE: FPT) research with linked three-statement forecasts, operating DCF, separate associate valuation and explicit cash-conversion decision rules.

**Clock C is the current package. Information cutoff: 23 November 2026. Forward value date: 31 December 2026E. Research stance: WATCHLIST.**

| Clock C | Base | Downside | Upside |
| --- | ---: | ---: | ---: |
| Forward fair value VND/share | 76,156 | 40,319 | 109,965 |
| WACC | 11.69% | 13.19% | 11.19% |
| Terminal growth | 3.0% | 2.0% | 4.0% |
| Financing under stated policy | Funded | Cash-floor shortfall | Funded |

These analyst scenarios are not a statistical price interval. No same-cutoff market quote is verified, so no spot upside is presented. Base FY2026E CFO / parent PAT is26.3%, below the30% add-exposure gate. Terminal value is72.5% of base operating EV. WACC, terminal economics, associate multiples and the NCI proxy remain explicit judgement risks.

## Review the research

- [Research report](outputs/p1_final/FPT_Equity_Research_Clock_C.pdf):12pages including sector discussion and primary sources.
- [Decision memo](outputs/p1_final/FPT_Decision_Memo_Clock_C.pdf):two pages.
- [Formula workbook](outputs/p1_final/FPT_Research_Model_Clock_C.xlsx):14sheets, one active forecast and native WACC/g sensitivity.
- [Interactive dashboard](index.html):download/open the HTML if viewing through GitHub's code viewer.
- [Stock pitch PDF](outputs/p1_final/FPT_Stock_Pitch_Clock_C.pdf) and [HTML pitch](outputs/p1_final/FPT_Stock_Pitch_Clock_C.html):ten slides.
- [Sector appendix](outputs/p1_final/FPT_Sector_Appendix_Clock_C.pdf):operating comparisons and sources, without claiming a contemporaneous peer valuation basket.
- [Valuation notebook](notebooks/03_clock_c_valuation_and_decision.ipynb) and [forecast notebook](notebooks/02_three_statement_development.ipynb).
- [Valuation JSON](outputs/p1_final/clock_c_valuation.json), [sensitivity CSV](outputs/p1_final/valuation_sensitivity.csv) and [final review](docs/CLOCK_C_FINAL_REVIEW.md).

## Reproduce

Python3.10+ and its standard library are sufficient for the financial engines and economic tests:

```bash
python scripts/run_three_statement.py
python scripts/run_clock_c.py
python scripts/run_checks.py
```

The suite has62checks. Excel reconciles378forecast points,15valuation outputs and75native sensitivity points across the cases. JavaScript reconciles1,584forecast and147valuation/sensitivity values. Saved-HTML tests exercise20control/error-recovery behaviours. The valuation notebook executes seven ordinary-Python code cells.

The full artifact build needs Node, `@oai/artifact-tool` and Python PDF dependencies. See [reproducibility](REPRODUCIBILITY.md). Bundled LibreOffice independently recalculates the workbook, including25base native sensitivity cells. Microsoft Excel interaction, Jupyter-kernel execution and independent human research review are not claimed.

## Valuation design

The original HOSE Q3 filing anchors18opening balance groups and ten exact reported-note bridges. Rounded10M management figures remain separate from exact9M statements. November–December and2027–2031 are documented forecasts.

Q4 cash movements enter the projected year-end bridge, so Q4 FCFF is excluded from the DCF. Operating FCFF excludes deposit interest and associate earnings. It deducts capex, working-capital investment and increases in required operating cash. Terminal reinvestment equals NOPAT × g / ROIC. Explicit and terminal mid-year discount conventions match.

The bridge adds associate equity and nonoperating cash/investments, subtracts debt and an NCI proxy, then divides by issued shares plus a1% dilution reserve. Associate book value, future dividends and CIP are not added again. The parent P/E cross-check receives no blending weight.

## Historical clocks

Clock A remains the frozen historical process and FY2025 forecast review. Clock B remains the9October2026 underwriting cycle. Its historical value and price are not a current recommendation. The [Clock B note](docs/CLOCK_B_VALUATION_NOTE.md) retains that evidence.

Prevaluation documents record the24November model stage. The [final review](docs/CLOCK_C_FINAL_REVIEW.md) supersedes their next-stage status statements. New actuals must be appended with publication dates without silently overwriting the frozen forecast.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/equity_valuation` | Financial engines |
| `configs` | Sources and dated assumptions |
| `data/intake` | Reported inputs and source receipt |
| `reports/plan` | Assumption and evidence registers |
| `dashboard` | Independent browser models |
| `outputs/p1_final` | Deliverables and verification receipts |
| `notebooks` | Executed walkthroughs |
| `tests` | Accounting and economic checks |

Original code is MIT-licensed. Third-party filings, market data and trademarks retain their own rights. See [NOTICE](NOTICE.md). Public author attribution uses only `thvh2006` or remains blank.
