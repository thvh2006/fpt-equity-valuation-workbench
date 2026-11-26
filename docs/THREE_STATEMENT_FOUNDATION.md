> Historical implementation checkpoint. Superseded on24November2026 by [Pre-valuation review](PREVALUATION_REVIEW.md), which records completed original-file verification and the implemented analyst forecast schedules. Pending items below describe the earlier checkpoint.

# FPT Three Statement Foundation

Audit date: 23 November 2026. Upstream archive observed at commit `1196c95fe28076df6ff4fac34fcd974db0137bc3`. Local archive import is not a fetched copy of upstream Git history. This branch contains an additive foundation, not a reviewed Clock C valuation release.

## Verified local baseline

- Existing repository suite: 20 of 20 checks passed before changes; the README's 19-check description is outdated.
- Current workbook: 23 sheets and 1,555 formulas. XML inspection found no cached error cells.
- Five selected base-case Python calculations reconcile to saved Excel caches within VND0.01 per share or VND0.01 billion as applicable. This is not native Excel recalculation, scenario recalculation, or visual QA.
- Existing FCFF/SOTP and frozen Clock A/B files have not been changed.
- Historical financial facts and a partial static balance-sheet input are present. A fully linked forecast BS/CF, funding schedule and Q4-to-FY bridge are absent from the inspected implementation.

## First implemented module

`src/equity_valuation/intake.py` validates a grouped opening balance sheet. It checks finite values, missing/zero distinctions, duplicate metrics, date/cutoff, unit, accounting basis, provenance, component sums and the accounting identity. Passing it alone does not approve a forecast.

`data/intake/q3_2026_balance_lines.csv` contains primary filing amounts transcribed from the exchange-hosted Q3/2026 consolidated filing. `scripts/build_opening_intake.py` groups explicit statement codes into 18 lines and converts VND to VND billion. Grouped residual categories use explicit components, not a balancing plug.

Primary source: [HOSE Q3/2026 consolidated filing](https://staticfile.hsx.vn/Uploads/UploadDocuments/2508914/20261028%20-%20FPT%20-%20BCTC%20hop%20nhat%20Quy%203%20nam%202026.pdf), printed pp.2–5; disclosure dated 28 October 2026. Content was read through primary-source text retrieval. Binary PDF SHA-256 and a second visual review remain pending, so the intake deliberately stays BLOCKED. The old repository hash is not assumed to match this mirror.

The 30 September opening requires an explicit Q4 stub before a FY2027 forecast; it must not be relabelled as audited 31 December 2026 data. The grouped intake does not yet split trade/non-trade receivables, current/noncurrent prepaids, or all operating liabilities for forecast drivers. Disaggregate when building schedules.

## Backlog in dependency order

1. Obtain and hash the original binary; visually confirm columns, dates, grouping and accounting perimeter. Retain extraction receipt and review.
2. Extract IS/CF and note detail needed for Q4 stub, debt/interest, capex/D&A, working capital, associate cash dividends, NCI and equity movements.
3. Resolve 2026 perimeter changes separately from operational movements. Do not derive operating cash effects from cross-perimeter opening/closing BS differences without a bridge.
4. Build a Q4 scenario and FY2026 estimated closing BS/CF with explicit conventions. It is an estimate, not a reported actual.
5. Develop forecast schedules for receivables/payables, PP&E, debt and interest, tax, associate investment, distributions and cash. Model associate earnings as noncash in CFO with dividends separately under a documented policy.
6. Link IS, BS, CF; cash is the computed cash-flow result. A funding facility can be an explicit policy, never an unexplained equity/cash plug.
7. Connect valuation only after accounting reconciliation and source/assumption review. Preserve Clock B outputs.
8. Add independent Excel formulas and HTML scenario views; then verify cross-platform golden cases.

## Five golden cases for the next model build

| Case | Change | Required evidence |
|---|---|---|
| G1 Frozen Clock B baseline | None | Existing valuation and five cached-value checks unchanged |
| G2 Working-capital stress | Slower collection and higher inventory | CFO/cash worsen; funding response explicit; BS still reconciles |
| G3 Debt maturity | Repayment without sufficient cash | Facility policy or infeasibility displayed; interest cash/IS/BS coherent |
| G4 Associate distributions | Earnings and dividends diverge | Investment roll-forward and CFO/CFI classification do not double count |
| G5 Source failure | Missing, late or mismatched opening fact | Release blocked with the exact prerequisite; no zero imputation |

G1 and intake failure checks run now. G2–G4 remain acceptance cases until the forecast engine exists.

## Sector research scope

Primary sector: IT services/digital transformation, with revenue mix, delivery geography, talent/utilisation economics, contract demand, margins and capital intensity. Candidate operating peers: Accenture, Infosys, TCS, HCLTech and Cognizant. This is a research shortlist, not an approved current trading-comps set. Accounting dates, segment scope, currencies, lease treatment and rights need review before valuation comparison. Telecom associate exposure and education economics must be treated separately rather than blended into one sector multiple.

## Reproduce

```bash
python3 scripts/build_opening_intake.py
python3 scripts/audit_foundation.py
python3 scripts/run_checks.py
```

The audit writes JSON/CSV under `docs/audit/2026-11-23`. It reports the expected blocked intake separately from software test success. No external price/PDF fetch is performed by these commands. Scripts execute on this host's Python 3.9.6; the package's declared supported version remains Python 3.10+ and has not been changed.

## P2 data feasibility

The existing monthly FPT price sample has 70 rows over January 2020–October 2025 and is useful for pipeline fixtures only. It does not supply a cross-sectional universe, daily volumes/fills, a verified total-return contract, historical membership or data vintages. Provider access was attempted but not verified in this session. No multi-asset source is approved and no alpha backtest has been produced.

Next P2 gate: approve a source only after actual small multi-asset data retrieval, daily/corporate-action/benchmark schema checks and usage-rights review. Do not substitute current constituents and call them point-in-time. A failed provider retrieval is a session access result, not proof that the provider has no data.
