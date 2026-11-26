#!/usr/bin/env python3
"""Build and execute the Clock C research walkthrough in ordinary Python."""
import json,io
from pathlib import Path
from contextlib import redirect_stdout
ROOT=Path(__file__).resolve().parents[1]

def main():
    cells=[]
    def md(s):cells.append(dict(cell_type='markdown',metadata={},source=s.splitlines(True)))
    def code(s):cells.append(dict(cell_type='code',metadata={},source=s.splitlines(True),execution_count=None,outputs=[]))
    md('''# FPT Clock C valuation and decision review

Information cutoff23November2026. Forward value31December2026E. This notebook
reproduces the valuation, its accounting scope, economic challenges and decision.
Saved outputs use a sequential ordinary-Python harness, not a Jupyter kernel.
The source/forecast walkthrough remains in02_three_statement_development.ipynb.
''')
    code('''from pathlib import Path
import json,sys
from copy import deepcopy
ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'src/equity_valuation').is_dir())
sys.path.insert(0,str(ROOT/'src'))
from equity_valuation.three_statement import run_forecast
from equity_valuation.clock_c import value_case,reverse_terminal_growth
opening=json.loads((ROOT/'data/intake/clock_c_opening_pending.json').read_text())
fc=json.loads((ROOT/'configs/forecast_research.json').read_text())
vc=json.loads((ROOT/'configs/valuation_clock_c.json').read_text())
forecasts={n:run_forecast(opening,c) for n,c in fc['scenarios'].items()}
values={n:value_case(f,vc['scenarios'][n],vc['common']) for n,f in forecasts.items()}
print('Value date:',vc['common']['valuation_date'],'Information cutoff:',vc['information_cutoff'])
''')
    md('## 1 Forward value and financing\nA policy shortfall remains visible. Cases are not probability intervals.')
    code('''for n,v in values.items():
    print(n,'VND/share',round(v['fair_value_vnd'],2),'WACC',round(v['wacc']*100,2),'funding',v['financing_status'])
assert values['downside']['max_funding_gap']>0
assert values['base']['market_price_vnd'] is None
''')
    md('## 2 Trace the parent equity bridge\nAssociate book value and CIP are excluded from asset additions. Future cash is not added a second time.')
    code('''v=values['base']
for k in ['operating_ev','associate_value','cash_net_of_reserve','investments','debt','nci_value','equity_value','diluted_shares_million']:
    print(k,round(v[k],3))
assert abs(v['checks']['equity_bridge'])<1e-6
print('Terminal share of EV:',round(v['terminal_share_of_ev']*100,2),'%')
''')
    md('## 3 Operating drivers reach valuation\nStress collections in the existing forecast, then recompute the forward equity bridge and FCFF.')
    code('''stress=deepcopy(fc['scenarios']['base'])
for p in stress['periods']:p['dso']+=30
sf=run_forecast(opening,stress)
sv=value_case(sf,vc['scenarios']['base'],vc['common'])
print('DSO plus30days fair value:',round(sv['fair_value_vnd'],2))
print('Base fair value:',round(v['fair_value_vnd'],2))
assert sv['fair_value_vnd']<v['fair_value_vnd']
assert sf['periods'][0]['balance_sheet']['cash']<forecasts['base']['periods'][0]['balance_sheet']['cash']
''')
    md('## 4 Terminal challenges and hypothetical reverse DCF\nHigher WACC reduces value. A solved hypothetical price is not an observed market expectation.')
    code('''higher=value_case(forecasts['base'],vc['scenarios']['base'],vc['common'],wacc_override=v['wacc']+.01)
assert higher['fair_value_vnd']<v['fair_value_vnd']
print('WACC plus100bp value:',round(higher['fair_value_vnd'],2))
r=reverse_terminal_growth(forecasts['base'],vc['scenarios']['base'],vc['common'],v['fair_value_vnd'])
assert abs(r['terminal_growth']-.03)<1e-9
assert abs(r['residual_vnd'])<1e-6
print('Recovered base g:',r['terminal_growth'],'Residual VND:',r['residual_vnd'])
''')
    md('## 5 Decision test\nDo not replace the cash gate with a mechanical valuation rating.')
    code('''reported=json.loads((ROOT/'data/intake/q3_2026_reported_schedules.json').read_text())
cfo9=next(g['reported_total_vnd']/1e9 for g in reported['groups'] if g['id']=='cfo')
q=forecasts['base']['periods'][0]
conversion=(cfo9+q['cash_flow']['cfo'])/(fc['actuals']['parent_pat_9m']+q['income_statement']['parent_pat'])
print('FY2026E CFO / parent PAT:',round(conversion*100,2),'%')
print('Cash gate:', 'PASS' if conversion>=.30 else 'FAIL')
print('Research stance: WATCHLIST. Same-cutoff quote is unavailable.')
assert conversion<.30
''')
    md('## 6 Independent engine receipts\nThese receipts describe numerical agreement, not empirical validation of assumptions.')
    code('''out=ROOT/'outputs/p1_final'
excel=json.loads((out/'excel_valuation_reconciliation.json').read_text())
js=json.loads((out/'javascript_valuation_reconciliation.json').read_text())
assert js['all_pass']
assert all(abs(r['excel']-r['python'])<1e-6 for r in excel['comparisons'])
print('Excel valuation comparisons:',len(excel['comparisons']))
print('Excel native sensitivity points:',excel['native_sensitivity_points'])
print('JavaScript valuation comparisons:',js['numeric_comparisons'])
''')
    env={'__name__':'__main__'};count=0
    for i,cell in enumerate(cells):
        cell['id']='clock-c-%02d'%i
        if cell['cell_type']=='code':
            count+=1;buf=io.StringIO()
            with redirect_stdout(buf):exec(compile(''.join(cell['source']),'<notebook-cell>','exec'),env)
            cell['execution_count']=count;cell['outputs']=[dict(output_type='stream',name='stdout',text=buf.getvalue().splitlines(True))]
    nb=dict(nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.12'),execution_method='ordinary Python sequential harness'),cells=cells)
    (ROOT/'notebooks/03_clock_c_valuation_and_decision.ipynb').write_text(json.dumps(nb,indent=2)+'\n')
    print('Clock C notebook:',count,'executed code cells')

if __name__=='__main__':main()
