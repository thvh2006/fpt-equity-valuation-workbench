"""Economic and data-scope tests for source-calibrated analyst cases."""
from copy import deepcopy
import csv,json
from pathlib import Path
from equity_valuation.three_statement import run_forecast
ROOT=Path(__file__).resolve().parents[1]
def inputs():
 return json.loads((ROOT/'data/intake/clock_c_opening_pending.json').read_text()),json.loads((ROOT/'configs/forecast_research.json').read_text())['scenarios']['base']
def test_trade_dso_is_separate_from_advances_and_deposits():
 o,c=inputs();base=run_forecast(o,c)['periods'][0];c['periods'][0]['dso']+=30;stress=run_forecast(o,c)['periods'][0];p=c['periods'][0]
 delta=p['wc_revenue']*30/365
 assert abs(stress['component_schedules']['trade_receivables']-base['component_schedules']['trade_receivables']-delta)<1e-8
 for key in ['vendor_advances','contract_receivables','other_short_receivables','long_receivables']:
  assert stress['component_schedules'][key]==base['component_schedules'][key]
 assert abs(base['cash_flow']['cfo']-stress['cash_flow']['cfo']-delta*(1-p['tax_rate']*p['allowance_ratio']))<1e-7

def test_interest_accrual_is_asset_when_cash_collection_is_delayed():
 o,c=inputs();base=run_forecast(o,c)['periods'][0];c['periods'][0]['interest_collection_ratio']=0;c['periods'][0]['opening_interest_collection_ratio']=0
 stress=run_forecast(o,c)['periods'][0]
 assert stress['income_statement']['interest_income']==base['income_statement']['interest_income']
 assert stress['income_statement']['group_pat']==base['income_statement']['group_pat']
 assert stress['cash_flow']['interest_received']==0
 assert abs(base['balance_sheet']['cash']-stress['balance_sheet']['cash']-base['cash_flow']['interest_received'])<1e-8
 assert abs(stress['balance_sheet']['short_term_investments']-base['balance_sheet']['short_term_investments']-base['cash_flow']['interest_received'])<1e-8

def test_no_rollover_has_cash_cost_equal_to_revolver_principal():
 o,c=inputs();base=run_forecast(o,c)['periods'][0];c['periods'][0]['refinance_ratio']=0
 stress=run_forecast(o,c)['periods'][0];principal=c['opening_components']['revolver']
 assert abs(base['balance_sheet']['cash']-stress['balance_sheet']['cash']-principal)<1e-8
 assert stress['component_schedules']['revolver']==0
 assert stress['funding']['status']=='INFEASIBLE'

def test_term_maturities_repay_exact_source_principal_and_do_not_double_count_reclassification():
 o,c=inputs();result=run_forecast(o,c)
 paid=sum(p['component_schedules']['term_repayment'] for p in result['periods'])
 assert abs(paid-2771.180307634)<1e-8
 assert result['periods'][-1]['component_schedules']['term_bank']<1e-8
 for row in result['periods']:
  assert abs(row['checks']['debt_roll'])<1e-8

def test_source_gate_still_blocks_unverified_research_inputs():
 o,c=inputs();o['facts'][0]['status']='primary_text_reviewed_pending_checksum'
 try:run_forecast(o,c,development=True)
 except ValueError as e:
  assert 'Verified original' in str(e);return
 raise AssertionError('Source gate bypassed')

def test_historical_october_is_shared_across_cases():
 with (ROOT/'artifacts/reported_schedules/revenue_forecast_bridge.csv').open() as f:
  rows=[r for r in csv.DictReader(f) if r['period']=='Q4 2026E']
 assert len(rows)==3
 assert len({r['october_observed'] for r in rows})==1
 assert abs(float(rows[0]['october_observed'])-(44959-40022.659671369))<1e-8
 for r in rows:
  assert abs(float(r['global_it'])+float(r['domestic_it'])+float(r['education_other'])-float(r['period_revenue']))<1e-8

def test_documented_assumption_register_covers_each_period_driver():
 with (ROOT/'reports/plan/forecast_assumption_register.csv').open() as f: rows=list(csv.DictReader(f))
 ids={(r['scenario'],r['period'],r['driver']) for r in rows};assert len(ids)==len(rows)
 config=json.loads((ROOT/'configs/forecast_research.json').read_text())
 for name,c in config['scenarios'].items():
  for p in c['periods']:
   for k,v in p.items():
    if isinstance(v,(int,float)):assert (name,p['label'],k) in ids
 assert all(r['rationale'] and r['classification']!='verified_future_fact' for r in rows)

def test_all_three_cases_have_finite_reconciled_component_schedules():
 o,_=inputs();config=json.loads((ROOT/'configs/forecast_research.json').read_text())
 for c in config['scenarios'].values():
  r=run_forecast(o,c)
  assert r['source_intake_status']=='PASS' and not r['valuation_published']
  for row in r['periods']:
   assert max(abs(v) for v in row['checks'].values())<1e-6
   assert min(row['component_schedules'][k] for k in ['interest_accrued','term_bank','lease','cip'])>=-1e-8

def test_associate_growth_means_one_plus_growth_not_a_fraction_of_profit():
 config=json.loads((ROOT/'configs/forecast_research.json').read_text())
 facts=config['actuals']
 for name,q4factor,growths in [('base',1.05,[.12,.10,.09,.08,.06]),('downside',.9,[.05,.05,.06,.06,.05]),('upside',1.15,[.18,.15,.13,.11,.08])]:
  prior=facts['associate_9m']+facts['associate_q3']*q4factor
  for p,g in zip(config['scenarios'][name]['periods'][1:],growths):
   assert abs(p['associate_profit']/prior-1-g)<1e-10
   prior=p['associate_profit']
