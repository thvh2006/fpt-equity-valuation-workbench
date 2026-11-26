> Current release: [Pre-valuation review](PREVALUATION_REVIEW.md). Original-file verification and the documented analyst forecast upgrade are complete as of24November2026. The development history below is retained for context.

# Linked Statement Development Build

Date: 23 November 2026. This is an implemented development prototype, not the reviewed Clock C release.

## Implemented

- Explicit Q4 2026 stub and annual 2027–2031 forecasts in three cases.
- Linked income statement, balance sheet and cash flow, including working capital, capex/D&A, associates, parent/NCI equity, dividends, debt, opening-balance interest and a capped additional facility.
- Missing/inconsistent opening data fails validation. Original-source and assumption review remain separate gates. Development mode must be requested explicitly.
- Unfunded requirements are exposed as infeasible. Projected negative cash is not concealed with a cash/equity plug.
- Ten-sheet independent formula workbook with a case selector, editable drivers, linked statements, audit checks and native chart.
- Standalone HTML with case/DSO/capex/rate/facility controls, statement tabs, source/method view, chart, CSV/JSON downloads, invalid-input state and financing warning.
- A walkthrough notebook with eight evaluated ordinary-Python cells. Execution used a plain-Python sequential harness, not a Jupyter kernel.

## Evidence

Python 3.12.14: 46 of 46 repository checks pass. The legacy Clock B workbook is unchanged byte for byte. All three development cases reconcile across six periods; maximum accounting difference is below VND0.000001 billion.

The independent Excel formulas reconcile to Python at 144 saved output points. Two additional input perturbations test a 30-day receivable delay and a later-period capex change. All ten sheets were visually reviewed with the artifact renderer, including lower assumptions/schedules. The exported workbook was inspected for cached errors. Native Microsoft Excel recalculation is not yet verified.

The browser calculator reconciles to Python at 1,116 numerical values. Native Chrome was used to verify Base/Downside selection, invalid facility input, an infeasible zero-facility scenario, reset and balance-sheet navigation. Desktop layout was reviewed. CSV/JSON buttons are implemented but their downloaded files were not UI-verified. Mobile layout has responsive CSS but has not been visually verified on this host.

## Outputs

- `outputs/fpt_development/FPT_Three_Statement_Development.xlsx`
- `outputs/fpt_development/FPT_Three_Statement_Dashboard.html`
- `notebooks/02_three_statement_development.ipynb`
- `artifacts/three_statement_development/results.json`

The HTML is self-contained and opens directly in a browser; no server, market-data connection or credentials are needed. It is not an internet-hosted deployment or live market-data service.

## Reproduce

Run the full local pipeline with `python scripts/run_all.py` (or pass `--node /path/to/node`). It stops at the first failed stage, keeps diagnostic logs under ignored `outputs/qa/run_all/`, and writes `outputs/fpt_development/run_all_verification.json`. This does not publish, push, trade or approve research assumptions.

```bash
python scripts/build_opening_intake.py
python scripts/build_reported_schedules.py
python scripts/audit_foundation.py
python scripts/run_three_statement.py --development
python scripts/run_checks.py
node scripts/build_three_statement_workbook.mjs
node scripts/build_three_statement_dashboard.mjs
python scripts/build_three_statement_notebook.py
```

Python model code uses the standard library. Workbook building needs the bundled `@oai/artifact-tool` runtime. The ignored `node_modules` link on this machine points to the configured cached runtime, not a committed dependency tree. The existing package still declares Python 3.10+; this build was checked using the bundled Python 3.12.14.

## Still required for the reviewed research release

1. Original binary source verification and visual source checks.
2. Reviewed revenue/segment drivers and supporting sector/peer evidence.
3. Disaggregated working capital, detailed debt maturity/interest, capex/D&A, tax timing and associate distributions; account for perimeter changes/FX/disposals where material.
4. Replace all illustrative drivers with dated evidence or reasoned reviewed assumptions.
5. Native Excel and mobile/download UI verification.
6. Independently reviewed valuation integration, then report/pitch findings and hosted dashboard publication.

No new target price, investment recommendation, academic report or realised-performance claim is produced by this build. The report outline, claim register and figure plan remain under `reports/plan/`.

## Reported-note evidence supplement

Ten reported accounting bridges now reconcile exactly in integer VND. See [Reported schedules and calibration](REPORTED_SCHEDULES_AND_CALIBRATION.md). Excel includes Reported Notes, the HTML includes expandable historical tables, and the notebook evaluates the source evidence. Interest receipts have been reclassified to CFI in all three engines with an explicit equal-income timing assumption. Forecast underwriting and binary source verification remain pending.
