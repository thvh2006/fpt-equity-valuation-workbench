/** Browser review calculator, independently reconciled to the Python engine. */
export function computeScenario(opening,config){
 let b=Object.fromEntries(opening.facts.map(f=>[f.metric,Number(f.value)]));
 if(opening.facts.some(f=>f.value===null||!Number.isFinite(Number(f.value))))throw Error('Opening balances are incomplete.');
 let baseShort=b.short_term_debt,longDebt=b.long_term_debt,facility=0;
 const periods=[];
 for(const p of config.periods){
  const prior={...b},start=new Date(p.start+'T00:00:00Z'),end=new Date(p.end+'T00:00:00Z');
  const year=end.getUTCFullYear(),days=(Date.UTC(year+1,0,1)-Date.UTC(year,0,1))/86400000;
  const fraction=((end-start)/86400000+1)/days;
  for(const key of Object.keys(p))if(typeof p[key]==='number'&&(!Number.isFinite(p[key])||p[key]<0))throw Error('Invalid assumption: '+key);
  if(p.ebit_margin>p.gross_margin)throw Error('EBIT margin exceeds gross margin.');
  const revenue=p.annual_revenue*fraction,cogs=revenue*(1-p.gross_margin),ebit=revenue*p.ebit_margin;
  const da=revenue*p.da_ratio,capex=revenue*p.capex_ratio;
  const assocProfit=p.associate_profit*fraction,assocDividend=assocProfit*p.associate_payout;
  const interestIncome=prior.short_term_investments*p.investment_yield*fraction;
  const interestExpense=(baseShort+longDebt+facility)*p.debt_rate*fraction;
  const pbt=ebit+interestIncome-interestExpense+assocProfit,tax=Math.max(pbt-assocProfit,0)*p.tax_rate;
  const pat=pbt-tax,nciPat=pat*p.nci_share,parentPat=pat-nciPat;
  const parentDividend=Math.max(parentPat,0)*p.parent_payout,nciDividend=Math.max(nciPat,0)*p.nci_payout;
  b.receivables=p.annual_revenue*p.dso/days;b.inventories=p.annual_revenue*(1-p.gross_margin)*p.dio/days;
  b.prepaids=p.annual_revenue*p.prepaid_ratio;b.trade_payables=p.annual_revenue*(1-p.gross_margin)*p.dpo/days;
  const deltaNwc=b.receivables-prior.receivables+b.inventories-prior.inventories+b.prepaids-prior.prepaids-(b.trade_payables-prior.trade_payables);
  b.ppe_net=prior.ppe_net+(capex-da)*(1-p.intangible_share);
  b.intangibles_net=prior.intangibles_net+(capex-da)*p.intangible_share;
  b.associates=prior.associates+assocProfit-assocDividend;
  if(Math.min(b.ppe_net,b.intangibles_net,b.associates)<-1e-8)throw Error('Scenario exhausts a long-term asset balance. Revise the asset schedules.');
  const shortRepaid=baseShort*p.short_repayment_fraction,longRepaid=longDebt*p.long_repayment_fraction;
  const cfo=pat+da-assocProfit-interestIncome-deltaNwc,cfi=-capex+assocDividend+interestIncome;
  const preCff=-shortRepaid-longRepaid-parentDividend-nciDividend;
  const cashBefore=prior.cash+cfo+cfi+preCff,cashFloor=p.annual_revenue*p.cash_floor_ratio;
  const required=Math.max(cashFloor-cashBefore,0),draw=Math.min(required,Math.max(config.facility_limit-facility,0)),gap=required-draw;
  baseShort-=shortRepaid;longDebt-=longRepaid;facility+=draw;
  const cff=preCff+draw;b.cash=prior.cash+cfo+cfi+cff;
  b.short_term_debt=baseShort+facility;b.long_term_debt=longDebt;
  b.parent_equity=prior.parent_equity+parentPat-parentDividend;b.nci_equity=prior.nci_equity+nciPat-nciDividend;
  b.total_assets=['cash','short_term_investments','receivables','inventories','prepaids','ppe_net','intangibles_net','associates','other_assets'].reduce((s,k)=>s+b[k],0);
  b.total_liabilities=b.short_term_debt+b.long_term_debt+b.trade_payables+b.other_liabilities;
  b.total_equity=b.parent_equity+b.nci_equity;
  periods.push({period:p.label,start:p.start,end:p.end,year_fraction:fraction,
   income_statement:{revenue,cogs,gross_profit:revenue-cogs,opex:revenue-cogs-ebit,ebit,interest_income:interestIncome,interest_expense:interestExpense,associate_profit:assocProfit,profit_before_tax:pbt,tax,group_pat:pat,parent_pat:parentPat,nci_pat:nciPat},
   cash_flow:{opening_cash:prior.cash,da,delta_nwc:deltaNwc,investment_income_removed:assocProfit+interestIncome,interest_received:interestIncome,cfo,capex,associate_dividend:assocDividend,cfi,short_repaid:shortRepaid,long_repaid:longRepaid,parent_dividend:parentDividend,nci_dividend:nciDividend,facility_draw:draw,cff,closing_cash:b.cash},
   balance_sheet:{...b},funding:{cash_floor:cashFloor,cash_before_funding:cashBefore,required_funding:required,facility_draw:draw,facility_outstanding:facility,funding_gap:gap,status:gap>1e-6?'INFEASIBLE':'FUNDED'},
   fcff:ebit*(1-p.tax_rate)+da-capex-deltaNwc,
   checks:{balance_sheet:b.total_assets-b.total_liabilities-b.total_equity,cash_flow_to_cash:b.cash-prior.cash-cfo-cfi-cff,parent_equity_roll:b.parent_equity-prior.parent_equity-parentPat+parentDividend,nci_equity_roll:b.nci_equity-prior.nci_equity-nciPat+nciDividend,associate_roll:b.associates-prior.associates-assocProfit+assocDividend,debt_roll:b.short_term_debt+b.long_term_debt-prior.short_term_debt-prior.long_term_debt+shortRepaid+longRepaid-draw,pat_attribution:pat-parentPat-nciPat}});
 }
 return {scenario:config.name,status:'DEVELOPMENT_NOT_REVIEWED',valuation_published:false,periods};
}
