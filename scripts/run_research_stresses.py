#!/usr/bin/env python3
"""Policy and liquidity stress captures, with no trading or valuation outputs."""
from copy import deepcopy
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from equity_valuation.three_statement import run_forecast

def main():
 o=json.loads((ROOT/'data/intake/clock_c_opening_pending.json').read_text());cfg=json.loads((ROOT/'configs/forecast_research.json').read_text())
 cases={k:deepcopy(v) for k,v in cfg['scenarios'].items()}
 for name in ['dso_plus_30','rates_plus_200bp','no_revolver_refinancing','interest_collection_delayed','no_associate_dividends','combined_stress']:
  c=deepcopy(cfg['scenarios']['base']);c['name']=name
  for p in c['periods']:
   if name in ['dso_plus_30','combined_stress']:p['dso']+=30
   if name in ['rates_plus_200bp','combined_stress']:p['debt_rate']+=.02
   if name=='no_revolver_refinancing':p['refinance_ratio']=0
   if name=='combined_stress':p['refinance_ratio']=.5;p['ebit_margin']-=.02;p['capex_ratio']+=.02
   if name=='interest_collection_delayed':p['interest_collection_ratio']=0;p['opening_interest_collection_ratio']=0
   if name=='no_associate_dividends':p['associate_payout']=0
  cases[name]=c
 results={name:run_forecast(o,c) for name,c in cases.items()};rows=[]
 for name,r in results.items():
  for p in r['periods']:
   rows.append(dict(scenario=name,period=p['period'],revenue=p['income_statement']['revenue'],parent_pat=p['income_statement']['parent_pat'],cfo=p['cash_flow']['cfo'],cfi=p['cash_flow']['cfi'],closing_cash=p['balance_sheet']['cash'],total_debt=p['balance_sheet']['short_term_debt']+p['balance_sheet']['long_term_debt'],funding_gap=p['funding']['funding_gap'],funding_status=p['funding']['status'],max_accounting_difference=max(abs(v) for v in p['checks'].values())))
 assert results['no_revolver_refinancing']['periods'][0]['funding']['status']=='INFEASIBLE'
 out=ROOT/'artifacts/research_stresses';out.mkdir(parents=True,exist_ok=True)
 (out/'results.json').write_text(json.dumps(dict(research_cutoff=cfg['research_cutoff'],interpretation='Liquidity gaps are relative to the fixed-deposit/no-new-facility policy. They do not assert issuer insolvency. Deposit redemption and refinancing are not guaranteed or automatically assumed.',results=results),indent=2)+'\n')
 with (out/'summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rows)
 print(json.dumps({'stress_cases':len(cases),'period_observations':len(rows),'all_accounting_checks_pass':all(r['max_accounting_difference']<1e-6 for r in rows)},indent=2))
if __name__=='__main__':main()
