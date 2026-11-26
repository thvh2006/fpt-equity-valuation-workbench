#!/usr/bin/env python3
"""Build and sequentially execute a plain-Python notebook without Jupyter dependencies.

Execution method is recorded in the notebook. This is not a Jupyter-kernel smoke
test; the cells use ordinary Python and can be rerun in a Python 3.10+ kernel.
"""
from __future__ import annotations
from contextlib import redirect_stdout
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    cells = []

    def md(text):
        cells.append({"cell_type":"markdown","metadata":{},"source":text.splitlines(True)})

    def code(text):
        cells.append({"cell_type":"code","metadata":{},"source":text.splitlines(True),"execution_count":None,"outputs":[]})

    md("""# FPT linked statement development walkthrough

This notebook follows the opening statement, explicit Q4 stub, five annual forecasts,
cash/debt/equity schedules, economic challenges and cross-platform reconciliation.
Forward drivers are **documented analyst scenarios**, calibrated to verified opening facts and issuer updates available by23November2026. No target price is calculated.

The saved cells were evaluated sequentially in a plain-Python harness on Python 3.12.
Jupyter-kernel execution has not been verified on this host. Start a Python 3.10+
kernel from the repository or its notebooks directory to rerun the same cells.
""")
    code("""from pathlib import Path
import json, sys
from copy import deepcopy
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'src/equity_valuation').is_dir())
sys.path.insert(0, str(ROOT / 'src'))
from equity_valuation.intake import validate_opening
from equity_valuation.three_statement import run_forecast
opening = json.loads((ROOT / 'data/intake/clock_c_opening_pending.json').read_text())
configs = json.loads((ROOT / 'configs/forecast_research.json').read_text())['scenarios']
print('Units:', opening['unit'])
print('Opening:', opening['period_end'], '| information cutoff:', opening['information_cutoff'])
""")
    md("""## 1 Opening data and source status

The input contains 18 groups from reported statement codes. Component accounting
checks are separate from original-file provenance. The downloaded HOSE binary was hashed and visually reviewed. Passing the accounting
identity must not silently approve the source or forward assumptions.
""")
    code("""intake = validate_opening(opening)
print('Source intake:', intake['status'])
for name, difference in intake['reconciliations'].items():
    print(f'{name:25s} {difference:,.6f}')
print('Remaining issue types:', sorted({e['code'] for e in intake['errors']}))
print('Primary filing:', opening['source_url'])
""")
    md("""## Reported-note calibration references

Ten historical accounting bridges separate receivables, deposit principal and
accrued interest, associates, debt/perimeter, remaining loan maturities, cash
flows and financial income/expense. Every raw amount is integer VND and has a
printed-page locator. Original binary provenance is recorded separately from arithmetic agreement.
These are historical calibration references; future drivers remain analyst judgements.
""")
    code("""from equity_valuation.reported_schedules import analyse_reported_schedules
reported = json.loads((ROOT / 'data/intake/q3_2026_reported_schedules.json').read_text())
evidence = analyse_reported_schedules(reported)
assert evidence['all_accounting_bridges_pass']
for check in evidence['checks']:
    print(check['schedule'], 'difference VND:', check['difference_vnd'])
print('Historical associate dividend receipts / profit:',
      f"{evidence['metrics']['associate_received_dividends_to_profit']:.2%}")
print('Original binary verified:', evidence['source_verified'])
print('Important: FTEL perimeter movements and current-portion transfers are not cash repayments.')
""")
    md("""## 2 Periods and documented analyst assumptions

Q4 2026 is a 92/365 stub, not an actual or full-year 2026 forecast. For following
years, working-capital balances use the annual run rate. Trade DSO drives gross trade only. Vendor advances, contract receivables,
other balances and long deposits have separate schedules. October management
figures are held fixed across cases; November and December are forecast.
""")
    code("""print('Period       Annual run rate     EBIT margin      DSO     Capex ratio')
for p in configs['base']['periods']:
    print(f\"{p['label']:12s} {p['annual_revenue']:14,.1f} {p['ebit_margin']:14.1%} {p['dso']:8.1f} {p['capex_ratio']:14.1%}\")
""")
    md("""## 3 One linked build for all three cases

Operating profit, tax, earnings attribution, noncash associate earnings,
dividends, working capital, capex and debt flows feed the same cash account.
Cash is a cash-flow result; equity is rolled from earnings and distributions.
An explicit facility commitment can leave an infeasible funding gap.
""")
    code("""results = {name: run_forecast(opening, cfg, development=True) for name, cfg in configs.items()}
print('Case       Last cash     Last debt    Last CFO    Max accounting difference')
for name, result in results.items():
    last = result['periods'][-1]
    debt = last['balance_sheet']['short_term_debt'] + last['balance_sheet']['long_term_debt']
    difference = max(abs(v) for row in result['periods'] for v in row['checks'].values())
    print(f\"{name:10s} {last['balance_sheet']['cash']:11,.1f} {debt:13,.1f} {last['cash_flow']['cfo']:11,.1f} {difference:24.10f}\")
""")
    md("""## 4 Working capital challenge

Increase receivable days by 30 in the first period. The incremental cash use
must equal full-year sales times30/365, adjusted for the tax effect of incremental
receivable provisions. The provision charge changes profit; nontrade balances
are unchanged.. The financing or cash consequence is explicit.
""")
    code("""stress = deepcopy(configs['base'])
stress['periods'][0]['dso'] += 30
stressed = run_forecast(opening, stress, development=True)['periods'][0]
base = results['base']['periods'][0]
p = stress['periods'][0]
expected_cash_use = p['wc_revenue'] * 30 / 365 * (1-p['allowance_ratio']*p['tax_rate'])
observed_cash_use = base['cash_flow']['cfo'] - stressed['cash_flow']['cfo']
assert abs(expected_cash_use-observed_cash_use) < 1e-6
print('Expected additional cash use:', round(expected_cash_use, 3))
print('Observed additional cash use:', round(observed_cash_use, 3))
""")
    md("""## 5 Infeasible financing is not an accounting plug

A deliberately extreme receivable assumption and zero additional commitment
must surface a funding shortfall. Negative projected cash in this experiment
means the scenario cannot be financed under the specified policy.
""")
    code("""failure = deepcopy(configs['base'])
failure['facility_limit'] = 0
failure['periods'][0]['dso'] = 700
row = run_forecast(opening, failure, development=True)['periods'][0]
assert row['funding']['status'] == 'INFEASIBLE'
print('Funding status:', row['funding']['status'])
print('Cash-floor shortfall:', round(row['funding']['funding_gap'], 3))
print('Balance-sheet difference:', round(row['checks']['balance_sheet'], 8))
""")
    md("""## 6 Excel and browser reconciliation

Excel independently calculates the saved cases using formulas. The HTML model
is separately implemented in JavaScript. These checks support mathematical
agreement, not approval of assumptions or an investment recommendation.
""")
    code("""out = ROOT / 'outputs/fpt_development'
excel = json.loads((out / 'excel_python_reconciliation.json').read_text())
browser = json.loads((out / 'dashboard_reconciliation.json').read_text())
assert all(abs(r['difference']) < 1e-6 for r in excel['results'])
assert browser['all_pass']
print('Excel comparison points:', excel['checks'])
print('Browser comparison points:', browser['numeric_comparisons'])
print('Valuation published:', results['base']['valuation_published'])
""")
    md("""## 7 Stress captures and source/forecast boundary

The source receipt records the downloaded HOSE PDF digest and visually reviewed
pages. The assumption register documents every numeric period driver, including
analyst judgement and legacy inactive fields. It does not claim verification of
future outcomes. Stress captures are recalculated by the pipeline.
""")
    code("""stress_results = json.loads((ROOT / 'artifacts/research_stresses/results.json').read_text())['results']
print('Stress case               Minimum cash     Largest funding gap')
for name, item in stress_results.items():
    minimum = min(p['balance_sheet']['cash'] for p in item['periods'])
    gap = max(p['funding']['funding_gap'] for p in item['periods'])
    print(f'{name:28s} {minimum:12,.1f} {gap:22,.1f}')
assert stress_results['no_revolver_refinancing']['periods'][0]['funding']['status'] == 'INFEASIBLE'
print('A gap is relative to the fixed-deposit, zero-additional-facility policy; it is not an issuer insolvency claim.')
""")
    md("""## 8 Scope before valuation

The analyst model separates trade/nontrade receivables, provisions, prepaid
stocks, operating liabilities, deposit principal/accrual/receipts, term and
revolving debt, current/noncurrent classification, CIP and associate dividends.
Tax timing, capital mix, useful lives, refinancing, FX and dividend policies
remain explicit modelling judgements and limitations. Read the full assumption
register and `docs/PREVALUATION_REVIEW.md` before connecting a valuation.
No target price or academic findings report is generated here. No independent
human review, native Excel recalculation or Jupyter-kernel run is claimed.
""")
    env = {"__name__":"__main__"}
    count = 0
    for cell in cells:
        if cell['cell_type'] == 'code':
            count += 1
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exec(compile(''.join(cell['source']), '<notebook-cell>', 'exec'), env)
            cell['execution_count'] = count
            cell['outputs'] = [{"output_type":"stream", "name":"stdout", "text":buffer.getvalue().splitlines(True)}]
    nb = {"nbformat":4,"nbformat_minor":5,"metadata":{
        "kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
        "language_info":{"name":"python","version":"3.12"},
        "execution_method":"plain_python_sequential_harness; Jupyter kernel not tested"},"cells":cells}
    for i, cell in enumerate(cells):
        cell['id'] = 'fpt-dev-%02d' % i
    target = ROOT / 'notebooks/02_three_statement_development.ipynb'
    target.write_text(json.dumps(nb,ensure_ascii=False,indent=2)+'\n')
    print(f'Built notebook with {count} evaluated ordinary-Python cells')


if __name__ == '__main__':
    main()
