> Historical implementation checkpoint. Superseded on24November2026 by [Pre-valuation review](PREVALUATION_REVIEW.md), which records completed original-file verification and the implemented analyst forecast schedules. Pending items below describe the earlier checkpoint.

# Reported schedules and forecast calibration

Research cutoff: 23 November 2026. Reported flows: 1 January–30 September 2026. Closing balances: 30 September 2026. Raw units: integer VND; workbook and dashboard: VND billion.

## Evidence boundary

`data/intake/q3_2026_reported_schedules.json` contains transcribed primary-text facts, printed-page locators, reported controls and interpretation notes. The original PDF binary checksum and visual review are pending. This supplement does not promote the source intake to verified or approve any forward driver. The existing opening-statement gate remains active.

Run `python scripts/build_reported_schedules.py` to reproduce the ten exact-integer accounting bridges and fact CSV. They reconcile receivables, short-term investments, associate investments, short/long debt, remaining loan repayment buckets, CFO, CFI, financial income and financial expense. No unexplained balancing item is introduced.

## Implemented cash-flow correction

Interest income is now removed from CFO and assumed interest receipts added to CFI. This follows the reported investing classification. The development model explicitly assumes cash interest received equals income, so the change affects CFO/CFI presentation equally and oppositely, leaving total cash unchanged. Python, spreadsheet and browser use the same policy. Interest timing, accruals and yield on principal still require a separate schedule. Other financial income and FX effects remain outside this simplified forecast.

## Calibration decisions that remain open

| Model area | Historical evidence | Required forecast implementation | Acceptance evidence |
|---|---|---|---|
| Receivables | Trade gross is distinct from vendor advances, contract progress, other receivables, provisions and long-term net deposits | Trade DSO drives trade gross only; advances and contract balances receive separate ratios or milestones; provision policy and nontrade balances are explicit | Components reproduce opening grouped receivables; trade DSO perturbation changes only the intended balance and cash |
| Investments | Term-deposit principal differs from accrued interest and other loans | Principal roll, maturity/reinvestment, accrued interest and receipts; yield uses an explicit exposure basis | Principal + accrual + loans reconcile to opening investments; income-to-cash bridge closes |
| Associates | Earnings, received dividends, contributions and FTEL perimeter addition are separate | Investment and dividend schedules; payout assumptions distinguish declaration and receipt timing | Historical roll matches; changes in dividends affect cash/investment without changing equity-accounted profit |
| Debt | FX and FTEL perimeter changes are separate from increases/decreases; current-portion transfers are reclassifications | Separate revolving debt, term-loan amortisation, lease, refinancing and FX policies | Current/noncurrent totals close; internal current-portion transfers cancel at total-debt level |
| Maturities | Within-one-year and second-year repayment buckets are explicit; years 3–5 are grouped | Allocate grouped later maturities only through a labelled analyst assumption; map Q4 timing separately | Repayment cannot exceed loan principal; bank-loan buckets do not incorrectly include revolvers or leases |
| Cash flows | Reported CFO/CFI have source controls and deconsolidation effects | Reconcile the actual cash-flow statement rather than infer it from perimeter-mismatched balance changes | Actual bridges reconcile independently of forward forecast |

The observed associate received-dividend/equity-income ratio is approximately 9.73% for this nine-month period. It is not a normalised payout target: receipt timing, investment timing and the FTEL change matter. The existing 50% development assumption is therefore flagged for underwriting, rather than silently replaced by 9.73%.

## Report plan amendment — no findings report drafted

1. Add a methods subsection on accounting perimeter and source verification.
2. Reserve an appendix table for the ten reported bridges, including units, dates and printed-page locators.
3. Reserve three research figures: associate earnings-to-dividends bridge; debt bridge separating cash, FX, current-portion transfers and FTEL; CFO-to-CFI interest classification.
4. Record each future driver as observed, derived or analyst scenario. Explain any conversion of a historical ratio into a forward assumption.
5. Keep valuation and investment conclusions blocked until source verification and driver underwriting are complete.
6. Reproduce tables from versioned inputs and scripts; do not manually paste unexplained model totals into the report.

## Verification scope

The repository check runner covers missing/duplicate reported facts, FTEL omission, dividend/earnings separation, maturity scope and cash-conserving interest reclassification. The workbook has formula-based reported controls and an independently checked historical distribution ratio. The notebook includes an evaluated evidence walkthrough. Native Excel recalculation, Jupyter-kernel execution and internet hosting remain unverified.
