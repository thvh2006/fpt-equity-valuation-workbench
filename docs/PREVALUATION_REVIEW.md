# FPT pre-valuation review

Research information cutoff: **23 November 2026**. Build reviewed: **24 November 2026**. Status: **documented analyst scenarios ready for a separate valuation stage**. This is technical model documentation; the academic/equity research findings report remains unwritten.

## Source verification completed

The original 54-page HOSE Q3 2026 consolidated filing was downloaded from the exchange URL. Its SHA-256 is `e32a7edba4e40fd08af58587abaf8b95c9c7b70cd120c14e5f33b6153b1c9e14` (3,210,883 bytes). The receipt is `data/intake/source_verification_receipt.json`. The raw extraction hash is checked before regenerating the opening statement; when the local binary is present its digest is also rechecked. The original PDF is excluded from public git assets and retained separately.

Printed balance-sheet pages 2–5 were visually compared with the downloaded PDF, along with the income statement, FTEL comparison, cash-flow statement, investment/associate notes and debt/finance notes used in the ten reported bridges. The source intake now passes all four accounting reconciliations with original-file provenance. This verifies provenance and transcription within that scope; it does not constitute an audit opinion or independent human sign-off.

Issuer releases dated 21 October and 18 November 2026 supply 9M and 10M business updates. These web amounts are rounded management figures, distinct from the exact financial-statement amounts. The source facts file records URLs, publication dates, review status and the rounding contract. The annual report's 2026 targets are comparison benchmarks, not enforced model outputs. No post-cutoff news or market price is used.

## Forecast inputs and reasoning completed

`configs/forecast_research.json` and `scripts/build_research_assumptions.py` own the three cases. `reports/plan/forecast_assumption_register.csv` records all 684 scenario-period numeric input records: 648 active driver records and 36 explicitly inactive legacy compatibility records. Each has a classification, source locator, rationale, date and reviewer. Forward assumptions are analyst judgements; none is labelled a verified future fact.

| Area | Implementation and evidence | What remains a judgement |
|---|---|---|
| Revenue | October observed revenue = rounded 10M issuer revenue less exact 9M filing revenue. Global IT, domestic IT and remaining education/other sectors reconcile. November–December are forecast separately; annual growth fades by segment through 2031 | The Nov–Dec run rate and future growth paths. AI revenue is included within global IT, not added again |
| Accounting perimeter | FTEL remains equity-accounted; pre-2026 fully consolidated telecom sales are not used as a like-for-like denominator | No new perimeter or ownership changes |
| Margins | Gross margin anchored to 9M31.95%; operating margin before finance/associate income anchored near14.74%. Incremental receivable provision charged explicitly | Delivery/mix improvements or compression, future credit coverage and unmodelled one-offs |
| Tax | Normalised current/cash tax rate on PBT excluding equity-accounted after-tax associate earnings. Base17%, downside20%, upside15% | Payment timing and tax incentives. Deferred credits are not perpetuated; existing tax balances remain fixed |
| Trade and other receivables | Gross trade DSO separated from vendor advances, contract assets, other short receivables, allowance and long deposits | Turnover ratios, coverage proxy and deposit growth. No write-offs assumed |
| Other operating capital | Inventory/AP days, short prepaids, long prepaid stock, payroll/accrual/customer advance/deferred revenue/other operating liabilities are explicit | Net prepaid stock and liability ratios replace unavailable contract-by-contract forecasts |
| Deposit investments | Principal, accrued interest, current-period collections and opening-interest collections roll separately. Only deposit principal earns the assumed yield | Undisclosed contractual rates/maturities, collection timing and reinvestment. No automatic deposit liquidation |
| Associates | Separate earnings and dividends; future earnings use `prior * (1 + growth)` and a test enforces the entire growth path | Aggregate earnings growth and cash payout policies. FTEL perimeter addition is not recurring profit or cash |
| Debt | Revolvers, term bank loans and leases separated. Source remaining-maturity buckets allocated by days; term/current reclassification creates no repayment cash | Uniform instalment timing, revolving-debt rollover, future rates. Additional uncommitted facility starts at zero |
| PP&E/CIP | Capex allocated to tangible assets, intangibles and CIP. Opening CIP transfers into PPE; D&A does not reduce CIP directly | Aggregate D&A/capital mix and commissioning timing substitute for an asset-level register |
| Equity/distributions | Parent/NCI earnings and distributions roll separately; prospective NCI share is0.2%, reflecting the changed perimeter | Payout, FX/OCI, ESOP, future issuance and ownership changes |

No other-investment dividends, nonrecurring other income, new M&A, disposals, impairment, FX gains/losses or OCI are forecast. These zero-event policies are simplifications, not assertions that the issuer will experience no such items. Financial income on cash and other non-deposit investments is excluded from the earnings scope. Interest uses opening debt; any new facility accrues interest from the next model period.

## Known October and management targets

The model fixes the observed October sales component across all cases. PBT is built for the whole Q4 from the linked accounting schedules because an October balance sheet and detailed cash-flow accounts are unavailable. The October PBT observation is used in an explicit reconciliation benchmark: Q4 projected PBT minus observed October PBT gives implied November–December PBT. Do not describe those implied months as reported results.

Base FY2026 sales are below the original management revenue target: the forecast follows the latest observed run rate instead of forcing an acceleration to the plan. The broader investment budget is not equated to cash fixed-asset capex. The generated pre-valuation summary quantifies both differences.

## Verification and challenge

- Source balances and ten historical bridges reconcile independently of forecast assumptions.
- The three saved cases have six contiguous forecast periods and pass all linked accounting checks.
- Trade-DSO stress changes gross trade only, including the allowance/tax consequence.
- Delayed interest collection changes cash and the accrued-interest asset while leaving accrued profit unchanged.
- No revolver rollover has a first-period cash cost equal to the source revolver principal; no balancing cash plug is introduced.
- Scheduled term-loan repayments total exactly the original source bank principal; current/noncurrent transfers do not double count repayment.
- The entire associate growth path has an independent economic test. A discovered missing `1 +` in scenario generation was corrected before this release; cross-engine mathematical agreement alone would not have detected it.
- Nine base/scenario/stress cases cover 54 period observations. Stress cases include delayed trade collection, +200bp borrowing rates, no rollover, delayed interest receipts, no associate dividends and combined stress.
- Python, spreadsheet formulas and JavaScript are independently calculated and compared. Notebook cells execute sequentially through Python; this is not a Jupyter-kernel certification.

Liquidity shortfalls are relative to the held-deposit, zero-new-facility policy. They do not assert issuer insolvency: deposit redemption or different financing could alter the result. No cash sweep, hypothetical bank commitment or unlimited emergency draw is assumed.

## Next stage: valuation only

The source/forecast work specified for this stage is complete as a documented analyst model. A valuation can now use its operating FCFF, separate associate treatment and explicitly scoped nonoperating assets without double counting interest or equity income. It still needs dated discount-rate and share-price inputs, valuation-date discount timings, a consistent treatment of CIP/prepaids, tax assumptions, NCI and associate investments, terminal economics and an independently checked EV-to-equity bridge. No target price or recommendation has been generated.

Native Microsoft Excel recalculation, Jupyter-kernel execution and independent human research review are not claimed. Dashboard hosting/publication and GitHub push are outside this local pre-valuation release. The report work remains an outline/evidence/figure plan.
