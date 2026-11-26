#!/usr/bin/env python3
"""Summarise model scope and compare FY estimates with known issuer benchmarks."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 cfg=json.loads((R/'configs/forecast_research.json').read_text());result=json.loads((R/'artifacts/three_statement_development/results.json').read_text());a=cfg['actuals'];rows=[]
 for name,c in cfg['scenarios'].items():
  p=result['scenarios'][name]['periods'][0];income=p['income_statement'];oct_pbt=a['pbt_10m_rounded']-a['pbt_9m'];fy_pbt=a['pbt_9m']+income['profit_before_tax']
  rows.append(dict(scenario=name,fy2026_revenue=c['periods'][0]['wc_revenue'],management_revenue_target=a['fy26_management_revenue_target'],revenue_difference_to_target=c['periods'][0]['wc_revenue']-a['fy26_management_revenue_target'],october_revenue_observed_approx=a['revenue_10m_rounded']-a['revenue_9m'],nov_dec_revenue_projected=income['revenue']-(a['revenue_10m_rounded']-a['revenue_9m']),october_pbt_observed_approx=oct_pbt,nov_dec_pbt_implied=income['profit_before_tax']-oct_pbt,fy2026_pbt=fy_pbt,management_pbt_target=a['fy26_management_pbt_target'],pbt_difference_to_target=fy_pbt-a['fy26_management_pbt_target'],fy2026_cash_capex=a['capex_9m']+p['cash_flow']['capex'],broader_investment_budget=a['fy26_management_investment_budget']))
 with (R/'outputs/fpt_development/prevaluation_benchmarks.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0],lineterminator="\n");w.writeheader();w.writerows(rows)
 (R/'outputs/fpt_development/prevaluation_benchmarks.json').write_text(json.dumps(dict(unit='VND billion',research_cutoff=cfg['research_cutoff'],october_rounding='10M management figures rounded; October amounts are approximate differences.',pbt_scope='October PBT is a benchmark; full Q4 PBT is modelled at quarterly level. Implied November–December is not reported actuals.',cases=rows),indent=2)+'\n')
 print('Built 3 scenario comparisons with October observations and management targets')
if __name__=='__main__':main()
