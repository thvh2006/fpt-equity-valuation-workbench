// Independent browser implementation. VND billion and million shares.
export function valueForward(forecast, c, a, waccShift=0, growthShift=0){
 const p=forecast.periods,q=p[0],last=p.at(-1),ke=a.risk_free_anchor+c.beta*a.total_equity_premium;
 const wacc=ke*(1-a.target_debt_weight)+a.cost_of_debt*(1-a.debt_tax_rate)*a.target_debt_weight+c.wacc_adjustment+waccShift;
 const g=c.terminal_growth+growthShift;
 if(!(g>=0&&g<wacc&&g<c.terminal_roic))throw Error('Require 0 <= terminal growth < WACC and ROIC');
 let previous=q.funding.cash_floor;
 const periods=p.slice(1).map((r,i)=>{
  const operating_cash_investment=r.funding.cash_floor-previous;previous=r.funding.cash_floor;
  const fcff=r.fcff-operating_cash_investment,timing=i+.5,discount_factor=(1+wacc)**-timing;
  return {period:r.period,operating_fcff:r.fcff,operating_cash_investment,fcff,timing,discount_factor,pv:fcff*discount_factor};
 });
 const explicit_pv=periods.reduce((s,r)=>s+r.pv,0),terminal_nopat=last.income_statement.ebit*(1+g)*(1-a.terminal_tax);
 const terminal_reinvestment=terminal_nopat*g/c.terminal_roic,terminal_fcff=terminal_nopat-terminal_reinvestment;
 const terminal_value=terminal_fcff/(wacc-g),terminal_pv=terminal_value/(1+wacc)**4.5,operating_ev=explicit_pv+terminal_pv;
 const associate_earnings=p[1].income_statement.associate_profit,associate_value=associate_earnings*c.associate_pe;
 const cash_net_of_reserve=q.balance_sheet.cash-q.funding.cash_floor;
 const investments=q.component_schedules.deposit_principal+q.component_schedules.interest_accrued+q.component_schedules.investment_other_net;
 const debt=q.balance_sheet.short_term_debt+q.balance_sheet.long_term_debt,nci_value=q.balance_sheet.nci_equity*c.nci_book_multiple;
 const equity_value=operating_ev+associate_value+cash_net_of_reserve+investments-debt-nci_value;
 const diluted_shares_million=a.issued_shares_million*(1+a.incremental_dilution),fair_value_vnd=equity_value/diluted_shares_million*1000;
 const max_funding_gap=Math.max(...p.map(r=>r.funding.funding_gap));
 return {cost_of_equity:ke,wacc,terminal_growth:g,terminal_roic:c.terminal_roic,periods,explicit_pv,terminal_nopat,terminal_reinvestment,terminal_fcff,terminal_value,terminal_pv,operating_ev,terminal_share_of_ev:terminal_pv/operating_ev,associate_earnings,associate_value,cash_net_of_reserve,investments,debt,nci_value,equity_value,diluted_shares_million,fair_value_vnd,pe_crosscheck_vnd:p[1].income_statement.parent_pat/diluted_shares_million*1000*c.parent_pe,margin_of_safety_price_vnd:fair_value_vnd*(1-a.margin_of_safety),max_funding_gap,financing_status:max_funding_gap>1e-6?'POLICY_SHORTFALL':'FUNDED'};
}
