/** Independent JavaScript implementation of documented pre-valuation analyst cases. */
export function computeScenario(opening,config){
 const b=Object.fromEntries(opening.facts.map(f=>[f.metric,Number(f.value)])),s=structuredClone(config.opening_components);
 if(opening.facts.some(f=>f.value===null||!Number.isFinite(Number(f.value))))throw Error('Incomplete opening statement');
 const sum=(o,keys)=>keys.reduce((n,k)=>n+o[k],0),rec=z=>sum(z,['trade_receivables','vendor_advances','contract_receivables','other_short_receivables','long_receivables'])-z.receivable_allowance;
 const fixedAssets=b.other_assets-s.cip,fixedLiabs=b.other_liabilities-s.operating_other_liabilities;
 let facility=0;const periods=[];
 for(const p of config.periods){
  for(const [k,v] of Object.entries(p))if(typeof v==='number'&&(!Number.isFinite(v)||v<0))throw Error('Invalid driver '+k);
  if(p.ebit_margin>p.gross_margin||p.cip_share+p.intangible_share>1)throw Error('Invalid margin or capex allocation');
  const prior={...b},ps={...s},start=new Date(p.start+'T00:00:00Z'),end=new Date(p.end+'T00:00:00Z'),year=end.getUTCFullYear(),days=(Date.UTC(year+1,0,1)-Date.UTC(year,0,1))/86400000,fraction=((end-start)/86400000+1)/days;
  const revenue=p.annual_revenue*fraction,wc=p.wc_revenue,cogs=revenue*(1-p.gross_margin);
  s.trade_receivables=wc*p.dso/days;s.vendor_advances=wc*p.vendor_advance_ratio;s.contract_receivables=wc*p.contract_receivable_ratio;s.other_short_receivables=wc*p.other_receivable_ratio;
  s.receivable_allowance=s.trade_receivables*p.allowance_ratio;s.long_receivables*=1+p.long_receivable_growth*fraction;
  const creditLoss=s.receivable_allowance-ps.receivable_allowance;
  b.receivables=rec(s);b.inventories=wc*(1-p.gross_margin)*p.dio/days;
  s.short_prepaids=wc*p.prepaid_ratio;s.long_prepaids*=1+p.long_prepaid_growth*fraction;b.prepaids=s.short_prepaids+s.long_prepaids;b.trade_payables=wc*(1-p.gross_margin)*p.dpo/days;
  s.operating_other_liabilities=wc*p.other_op_liability_ratio;b.other_liabilities=fixedLiabs+s.operating_other_liabilities;
  const deltaNwc=b.receivables-prior.receivables+b.inventories-prior.inventories+b.prepaids-prior.prepaids-(b.trade_payables-prior.trade_payables)-(s.operating_other_liabilities-ps.operating_other_liabilities);
  const ebit=revenue*p.ebit_margin-creditLoss,da=revenue*p.da_ratio,capex=revenue*p.capex_ratio,assoc=p.associate_profit*fraction,div=assoc*p.associate_payout;
  const ii=ps.deposit_principal*p.investment_yield*fraction,receipts=ps.interest_accrued*p.opening_interest_collection_ratio+ii*p.interest_collection_ratio;
  s.interest_accrued=ps.interest_accrued+ii-receipts;b.short_term_investments=s.deposit_principal+s.investment_other_net+s.interest_accrued;
  const ie=(prior.short_term_debt+prior.long_term_debt)*p.debt_rate*fraction,pbt=ebit+ii-ie+assoc,tax=Math.max(pbt-assoc,0)*p.tax_rate,pat=pbt-tax,nci=pat*p.nci_share,parent=pat-nci,pd=Math.max(parent,0)*p.parent_payout,nd=Math.max(nci,0)*p.nci_payout;
  const transfer=Math.min(ps.cip,ps.cip*p.cip_transfer_rate*fraction);s.cip=ps.cip+capex*p.cip_share-transfer;b.other_assets=fixedAssets+s.cip;
  b.ppe_net=prior.ppe_net+capex*(1-p.intangible_share-p.cip_share)+transfer-da*(1-p.intangible_share);b.intangibles_net=prior.intangibles_net+(capex-da)*p.intangible_share;b.associates=prior.associates+assoc-div;
  if(Math.min(b.ppe_net,b.intangibles_net,b.associates)<-1e-8)throw Error('Long-term asset exhausted');
  if(p.term_repayment>ps.term_bank+1e-8||p.lease_repayment>ps.lease+1e-8)throw Error('Repayment exceeds principal');
  const revolverRepaid=ps.revolver*(1-p.refinance_ratio);s.revolver=ps.revolver-revolverRepaid;s.term_bank=Math.max(ps.term_bank-p.term_repayment,0);s.lease=Math.max(ps.lease-p.lease_repayment,0);
  const currentBank=Math.min(s.term_bank,p.current_term_next),currentLease=Math.min(s.lease,p.current_lease_next),shortRepaid=revolverRepaid+p.term_repayment+p.lease_repayment,longRepaid=0;
  const cfo=pat+da-assoc-ii-deltaNwc,cfi=-capex+div+receipts,preCff=-shortRepaid-pd-nd,before=prior.cash+cfo+cfi+preCff,floor=wc*p.cash_floor_ratio,required=Math.max(floor-before,0),draw=Math.min(required,Math.max(config.facility_limit-facility,0)),gap=required-draw;facility+=draw;
  const cff=preCff+draw;b.cash=prior.cash+cfo+cfi+cff;b.short_term_debt=s.revolver+currentBank+currentLease+facility;b.long_term_debt=s.term_bank+s.lease-currentBank-currentLease;
  b.parent_equity=prior.parent_equity+parent-pd;b.nci_equity=prior.nci_equity+nci-nd;b.total_assets=sum(b,['cash','short_term_investments','receivables','inventories','prepaids','ppe_net','intangibles_net','associates','other_assets']);b.total_liabilities=sum(b,['short_term_debt','long_term_debt','trade_payables','other_liabilities']);b.total_equity=b.parent_equity+b.nci_equity;
  const checks={balance_sheet:b.total_assets-b.total_liabilities-b.total_equity,cash_flow_to_cash:b.cash-prior.cash-cfo-cfi-cff,parent_equity_roll:b.parent_equity-prior.parent_equity-parent+pd,nci_equity_roll:b.nci_equity-prior.nci_equity-nci+nd,associate_roll:b.associates-prior.associates-assoc+div,debt_roll:b.short_term_debt+b.long_term_debt-prior.short_term_debt-prior.long_term_debt+shortRepaid-draw,pat_attribution:pat-parent-nci,interest_receivable_roll:s.interest_accrued-ps.interest_accrued-ii+receipts,cip_roll:s.cip-ps.cip-capex*p.cip_share+transfer};
  if(Object.values(checks).some(v=>Math.abs(v)>1e-6))throw Error('Accounting reconciliation failed');
  periods.push({period:p.label,start:p.start,end:p.end,year_fraction:fraction,income_statement:{revenue,cogs,gross_profit:revenue-cogs,opex:revenue-cogs-ebit,ebit,credit_loss_charge:creditLoss,interest_income:ii,interest_expense:ie,associate_profit:assoc,profit_before_tax:pbt,tax,group_pat:pat,parent_pat:parent,nci_pat:nci},cash_flow:{opening_cash:prior.cash,da,delta_nwc:deltaNwc,investment_income_removed:assoc+ii,interest_received:receipts,cfo,capex,associate_dividend:div,cfi,short_repaid:shortRepaid,long_repaid:longRepaid,parent_dividend:pd,nci_dividend:nd,facility_draw:draw,cff,closing_cash:b.cash},balance_sheet:{...b},component_schedules:{...s,credit_loss_charge:creditLoss,cip_transfer:transfer,current_bank:currentBank,current_lease:currentLease,revolver_repaid:revolverRepaid,term_repayment:p.term_repayment,lease_repayment:p.lease_repayment},funding:{cash_floor:floor,cash_before_funding:before,required_funding:required,facility_draw:draw,facility_outstanding:facility,funding_gap:gap,status:gap>1e-6?'INFEASIBLE':'FUNDED'},fcff:ebit*(1-p.tax_rate)+da-capex-deltaNwc,checks});
 }
 return {scenario:config.name,status:'ANALYST_CASE_PREVALUATION',valuation_published:false,periods};
}
