"""Pre-valuation analyst cases with explicit operating and financing components."""
from copy import deepcopy
from datetime import date
import math
from .intake import validate_opening, REQUIRED

EXTRA = ('wc_revenue','vendor_advance_ratio','contract_receivable_ratio','other_receivable_ratio',
 'allowance_ratio','long_receivable_growth','long_prepaid_growth','other_op_liability_ratio',
 'cip_share','cip_transfer_rate','interest_collection_ratio','opening_interest_collection_ratio',
 'refinance_ratio','term_repayment','lease_repayment','current_term_next','current_lease_next')


def run_research_forecast(opening, config, *, development=False):
 from .three_statement import validate_assumptions
 intake=validate_opening(opening)
 if intake['status']!='PASS':raise ValueError('Verified original opening is required for research forecast')
 validate_assumptions(config)
 if not config.get('reviewed'):raise ValueError('Documented analyst review required')
 b={f['metric']:float(f['value']) for f in opening['facts'] if f['metric'] in REQUIRED}
 s=deepcopy(config['opening_components']);facility=0.
 if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or v<0 for v in s.values()):raise ValueError('Invalid opening component')
 rec=lambda z:sum(z[k] for k in ['trade_receivables','vendor_advances','contract_receivables','other_short_receivables','long_receivables'])-z['receivable_allowance']
 initial={'receivables':rec(s),'prepaids':s['short_prepaids']+s['long_prepaids'],'short_term_investments':s['deposit_principal']+s['interest_accrued']+s['investment_other_net'],'debt':s['revolver']+s['term_bank']+s['lease']}
 for k,v in initial.items():
  want=b['short_term_debt']+b['long_term_debt'] if k=='debt' else b[k]
  if abs(v-want)>1e-6:raise ValueError('Opening component mismatch: '+k)
 fixed_other_assets=b['other_assets']-s['cip'];fixed_other_liabs=b['other_liabilities']-s['operating_other_liabilities']
 if min(fixed_other_assets,fixed_other_liabs)<0:raise ValueError('Components exceed source group')
 previous_end=date.fromisoformat(opening['period_end']);rows=[]
 for p in config['periods']:
  for k in EXTRA:
   v=p.get(k)
   if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:raise ValueError('Invalid component driver: '+k)
   if (k.endswith('_ratio') or k in ['cip_share','cip_transfer_rate','long_receivable_growth','long_prepaid_growth']) and v>1:raise ValueError('Component ratio outside [0,1]: '+k)
  if p['cip_share']+p['intangible_share']>1:raise ValueError('Capex allocation exceeds100%')
  start,end=date.fromisoformat(p['start']),date.fromisoformat(p['end'])
  if (start-previous_end).days!=1:raise ValueError('Forecast must start immediately after prior close')
  previous_end=end;days=(date(end.year+1,1,1)-date(end.year,1,1)).days;fraction=((end-start).days+1)/days
  prior=deepcopy(b);prior_s=deepcopy(s);revenue=p['annual_revenue']*fraction;wc=p['wc_revenue'];cogs=revenue*(1-p['gross_margin'])
  s['trade_receivables']=wc*p['dso']/days
  s['vendor_advances']=wc*p['vendor_advance_ratio'];s['contract_receivables']=wc*p['contract_receivable_ratio'];s['other_short_receivables']=wc*p['other_receivable_ratio']
  s['receivable_allowance']=s['trade_receivables']*p['allowance_ratio'];s['long_receivables']*=1+p['long_receivable_growth']*fraction
  credit_loss=s['receivable_allowance']-prior_s['receivable_allowance']
  b['receivables']=rec(s);b['inventories']=wc*(1-p['gross_margin'])*p['dio']/days
  s['short_prepaids']=wc*p['prepaid_ratio'];s['long_prepaids']*=1+p['long_prepaid_growth']*fraction
  b['prepaids']=s['short_prepaids']+s['long_prepaids'];b['trade_payables']=wc*(1-p['gross_margin'])*p['dpo']/days
  s['operating_other_liabilities']=wc*p['other_op_liability_ratio'];b['other_liabilities']=fixed_other_liabs+s['operating_other_liabilities']
  delta_nwc=sum(b[k]-prior[k] for k in ['receivables','inventories','prepaids'])-(b['trade_payables']-prior['trade_payables'])-(s['operating_other_liabilities']-prior_s['operating_other_liabilities'])
  ebit=revenue*p['ebit_margin']-credit_loss;da=revenue*p['da_ratio'];capex=revenue*p['capex_ratio']
  assoc=p['associate_profit']*fraction;div=assoc*p['associate_payout']
  ii=prior_s['deposit_principal']*p['investment_yield']*fraction
  receipts=prior_s['interest_accrued']*p['opening_interest_collection_ratio']+ii*p['interest_collection_ratio']
  s['interest_accrued']=prior_s['interest_accrued']+ii-receipts;b['short_term_investments']=s['deposit_principal']+s['investment_other_net']+s['interest_accrued']
  ie=(prior['short_term_debt']+prior['long_term_debt'])*p['debt_rate']*fraction
  pbt=ebit+ii-ie+assoc;tax=max(pbt-assoc,0)*p['tax_rate'];pat=pbt-tax;nci=pat*p['nci_share'];parent=pat-nci
  pd=max(parent,0)*p['parent_payout'];nd=max(nci,0)*p['nci_payout']
  transfer=min(prior_s['cip'],prior_s['cip']*p['cip_transfer_rate']*fraction)
  s['cip']=prior_s['cip']+capex*p['cip_share']-transfer;b['other_assets']=fixed_other_assets+s['cip']
  b['ppe_net']=prior['ppe_net']+capex*(1-p['intangible_share']-p['cip_share'])+transfer-da*(1-p['intangible_share'])
  b['intangibles_net']=prior['intangibles_net']+(capex-da)*p['intangible_share'];b['associates']=prior['associates']+assoc-div
  if min(b['ppe_net'],b['intangibles_net'],b['associates']) < -1e-8:raise ValueError('Long-term asset exhausted')
  if p['term_repayment']>prior_s['term_bank']+1e-8 or p['lease_repayment']>prior_s['lease']+1e-8:raise ValueError('Debt repayment exceeds principal')
  revolver_repaid=prior_s['revolver']*(1-p['refinance_ratio']);s['revolver']=prior_s['revolver']-revolver_repaid
  s['term_bank']=max(prior_s['term_bank']-p['term_repayment'],0);s['lease']=max(prior_s['lease']-p['lease_repayment'],0)
  current_bank=min(s['term_bank'],p['current_term_next']);current_lease=min(s['lease'],p['current_lease_next'])
  short_repaid=revolver_repaid+p['term_repayment']+p['lease_repayment'];long_repaid=0.
  cfo=pat+da-assoc-ii-delta_nwc;cfi=-capex+div+receipts;pre_cff=-short_repaid-pd-nd
  before=prior['cash']+cfo+cfi+pre_cff;floor=wc*p['cash_floor_ratio'];required=max(floor-before,0);draw=min(required,max(config['facility_limit']-facility,0));gap=required-draw;facility+=draw
  cff=pre_cff+draw;b['cash']=prior['cash']+cfo+cfi+cff
  b['short_term_debt']=s['revolver']+current_bank+current_lease+facility;b['long_term_debt']=s['term_bank']+s['lease']-current_bank-current_lease
  b['parent_equity']=prior['parent_equity']+parent-pd;b['nci_equity']=prior['nci_equity']+nci-nd
  b['total_assets']=sum(b[k] for k in ['cash','short_term_investments','receivables','inventories','prepaids','ppe_net','intangibles_net','associates','other_assets'])
  b['total_liabilities']=sum(b[k] for k in ['short_term_debt','long_term_debt','trade_payables','other_liabilities']);b['total_equity']=b['parent_equity']+b['nci_equity']
  checks=dict(balance_sheet=b['total_assets']-b['total_liabilities']-b['total_equity'],cash_flow_to_cash=b['cash']-prior['cash']-cfo-cfi-cff,parent_equity_roll=b['parent_equity']-prior['parent_equity']-parent+pd,nci_equity_roll=b['nci_equity']-prior['nci_equity']-nci+nd,associate_roll=b['associates']-prior['associates']-assoc+div,debt_roll=b['short_term_debt']+b['long_term_debt']-prior['short_term_debt']-prior['long_term_debt']+short_repaid-draw,pat_attribution=pat-parent-nci,interest_receivable_roll=s['interest_accrued']-prior_s['interest_accrued']-ii+receipts,cip_roll=s['cip']-prior_s['cip']-capex*p['cip_share']+transfer)
  if any(abs(v)>1e-6 for v in checks.values()):raise ArithmeticError('Research model accounting reconciliation failed: '+str(checks))
  rows.append(dict(period=p['label'],start=p['start'],end=p['end'],year_fraction=fraction,income_statement=dict(revenue=revenue,cogs=cogs,gross_profit=revenue-cogs,opex=revenue-cogs-ebit,ebit=ebit,credit_loss_charge=credit_loss,interest_income=ii,interest_expense=ie,associate_profit=assoc,profit_before_tax=pbt,tax=tax,group_pat=pat,parent_pat=parent,nci_pat=nci),cash_flow=dict(opening_cash=prior['cash'],da=da,delta_nwc=delta_nwc,investment_income_removed=assoc+ii,interest_received=receipts,cfo=cfo,capex=capex,associate_dividend=div,cfi=cfi,short_repaid=short_repaid,long_repaid=long_repaid,parent_dividend=pd,nci_dividend=nd,facility_draw=draw,cff=cff,closing_cash=b['cash']),balance_sheet=deepcopy(b),component_schedules=dict(**s,credit_loss_charge=credit_loss,cip_transfer=transfer,current_bank=current_bank,current_lease=current_lease,revolver_repaid=revolver_repaid,term_repayment=p['term_repayment'],lease_repayment=p['lease_repayment']),funding=dict(cash_floor=floor,cash_before_funding=before,required_funding=required,facility_draw=draw,facility_outstanding=facility,funding_gap=gap,status='INFEASIBLE' if gap>1e-6 else 'FUNDED'),fcff=ebit*(1-p['tax_rate'])+da-capex-delta_nwc,checks=checks))
 return dict(status='ANALYST_CASE_PREVALUATION',scenario=config['name'],unit='VND billion',opening_period_end=opening['period_end'],information_cutoff=opening['information_cutoff'],source_intake_status=intake['status'],source_intake_error_count=0,assumptions_reviewed=True,independently_reviewed=False,valuation_published=False,opening_balances={f['metric']:f['value'] for f in opening['facts']},limitations=config['limitations'],periods=rows)
