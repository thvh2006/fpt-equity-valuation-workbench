#!/usr/bin/env python3
"""Build dated analyst scenarios from verified reported facts and explicit choices."""
import csv
from datetime import date,timedelta
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'fs':{'url':'https://staticfile.hsx.vn/Uploads/UploadDocuments/2508914/20261028%20-%20FPT%20-%20BCTC%20hop%20nhat%20Quy%203%20nam%202026.pdf','published':'2026-10-28','status':'downloaded_sha256_and_visual_review'},
 'm9':{'url':'https://fpt.com/en/news/fpt-s-9-months-2026-revenue-and-pbt-increase-12-4-and-17-0','published':'2026-10-21','status':'primary_web_content_reviewed'},
 'm10':{'url':'https://fpt.com/en/news/fpt-s-profit-before-tax-rises-16-8-in-first-10-months-of-2026-overseas-it-services-revenue-grows-12-2','published':'2026-11-18','status':'primary_web_content_reviewed'},
 'plan':{'url':'https://bctn2025.fpt.com/wp-content/uploads/2026/04/Annual-Report-2025.pdf','published':'2026-04','status':'primary_web_pdf_text_reviewed','locator':'Plan for 2026, printed p.54–55; investment budget is not cash capex guidance'}}
ACTUALS={'revenue_9m':40022.659671369,'cogs_9m':27233.683805181,'gross_profit_9m':12788.975866188,'selling_9m':3209.266638509,'admin_9m':3679.874559932,'pbt_9m':8770.160739433,'current_tax_9m':1083.828799171,'deferred_tax_9m':-90.110530089,'group_pat_9m':7776.442470351,'parent_pat_9m':7778.081180761,'nci_pat_9m':-1.638710410,'associate_9m':2220.302808436,'associate_q3':796.904312086,'da_9m':1292.850889343,'capex_9m':2028.801162827,'revenue_10m_rounded':44959.,'pbt_10m_rounded':9954.,'global_9m_rounded':28538.,'domestic_9m_rounded':6977.,'global_10m_rounded':32079.,'technology_10m_rounded':39917.,'fy26_management_revenue_target':58580.,'fy26_management_pbt_target':11629.,'fy26_management_investment_budget':7200.}
COMP={'trade_receivables':10847.235916673,'vendor_advances':1461.744848593,'contract_receivables':280.491632591,'other_short_receivables':821.495010836,'receivable_allowance':346.643599150,'long_receivables':566.684790000,'short_prepaids':1164.843298969,'long_prepaids':1758.483230080,'deposit_principal':20878.556627776,'interest_accrued':512.862972132,'investment_other_net':58.231563068,'revolver':13824.257149723,'term_bank':2771.180307634,'lease':1.002606729,'cip':1130.986988296,'operating_other_liabilities':sum([761.185251149,3633.275734501,969.039203819,156.498540977,2164.614328538,546.789521169])}
RULES={
 'annual_revenue':('analyst_derived','m9,m10','Segment Q4 = observed October plus forecast November/December. Annual periods = prior segment forecast times explicitly declining growth. Revenue parameter is period revenue divided by year fraction, not FY revenue for the Q4 stub.'),
 'wc_revenue':('analyst_derived','fs,m10','Full-year 2026 revenue = 9M actual + Q4 estimate. Full annual revenue thereafter; prevents quarter annualisation from distorting balance-day ratios.'),
 'gross_margin':('analyst_scenario','fs pp.6','9M margin 31.95%; base 32%, downside 30%, upside 33%. Mix and delivery costs determine scenario spreads.'),
 'ebit_margin':('analyst_scenario','fs pp.6','9M operating EBIT before finance/associates is 14.74%. Base begins 14.75%, fades toward 16%; downside 13%; upside up to 18%. Margin is before incremental receivable allowance charge.'),
 'tax_rate':('analyst_scenario','fs pp.6','9M current tax / PBT excluding associate income is 16.55%. Base 17%, downside 20%, upside 15%. No indefinite extrapolation of the 9M deferred-tax credit.'),
 'dso':('analyst_scenario','fs pp.2,6','Trade gross / annualised 9M sales implies about 74 days. Base 75, downside 95, upside 70. Applies to gross trade only.'),
 'dio':('analyst_scenario','fs pp.2,6','Net inventory / annualised 9M COGS implies about 20 days. Base20/down28/up18. Mix/allowance timing remains a sensitivity.'),
 'dpo':('analyst_scenario','fs pp.4,6','Trade AP / annualised 9M COGS implies about 19 days. Base20/down18/up22; excludes payroll and other operating liabilities.'),
 'prepaid_ratio':('analyst_scenario','fs pp.2,6','Short prepaid / annualised 9M sales is about2.18%. Base2.2%, down2.5%, up2.0%. Long prepaids rolled separately.'),
 'vendor_advance_ratio':('analyst_scenario','fs p.2','Opening advances about2.74% of annualised sales; base2.7%, down3.2%, up2.5%.'),
 'contract_receivable_ratio':('analyst_scenario','fs p.2','Opening contract-progress receivables about0.53% of annualised sales; base0.55%, down0.8%, up0.5%.'),
 'other_receivable_ratio':('analyst_scenario','fs pp.2,33','Opening other short receivables about1.54% of annualised sales; base1.55%, down1.8%, up1.4%. Includes nontrade items; separate from DSO.'),
 'allowance_ratio':('analyst_scenario','fs p.2','Opening short receivable allowance / gross trade is3.20%; base3.2%, down4%, up3%. Coverage proxy across short receivables, not a reported trade-only allowance. No write-offs; change charged to operating earnings.'),
 'long_receivable_growth':('analyst_scenario','fs pp.3,33','Long balances largely deposits. Hold at0% growth in all cases rather than apply trade DSO. Review when contract data become available.'),
 'long_prepaid_growth':('analyst_scenario','fs p.3','Contract durations not granular enough for an asset-by-asset forecast. Net stock grows5% base/up,8% down; prepaid expense amortisation is embedded in operating margin and net additions affect CFO.'),
 'other_op_liability_ratio':('analyst_scenario','fs p.4','Source-defined payroll, accruals, customer advances, contract payables, short deferred revenue and other short payables total about15.43% of annualised sales. Base15.4%, down14%, up16%; remaining nonoperating liabilities fixed.'),
 'da_ratio':('analyst_scenario','fs p.9','9M cash-flow D&A / sales3.23%; base3.3% Q4, then3.4–3.8% as assets enter service. No depreciation on CIP; capex-transfer schedule is explicit. Aggregate ratio remains a useful-life sensitivity.'),
 'capex_ratio':('analyst_scenario','fs p.9,plan','9M cash capex2,028.8bn. Q4 cash spend base1,500/down1,800/up1,700bn. Annual base7% declining to5.5%; down8% to7%; up8% to6%. The7,200bn investment budget includes broader investment and is not forced into cash capex.'),
 'intangible_share':('analyst_scenario','fs pp.3,34–35','Allocate10% cash capex and D&A to intangibles, with a separate30% capex-to-CIP allocation. Simplified capital mix, not issuer capex guidance.'),
 'cip_share':('analyst_scenario','fs pp.3,21','30% of capex initially in CIP. Remaining60% in tangible PPE and10% intangibles. No depreciation allocated directly to CIP.'),
 'cip_transfer_rate':('analyst_scenario','fs pp.3,21','Transfer50% of opening CIP per full year, prorated for Q4. No same-period depreciation beyond the underwritten aggregate D&A budget.'),
 'associate_profit':('analyst_scenario','fs pp.6–7,32','Q4 equity income = Q3 times0.9/1.05/1.15. Next year grows5%/12%/18%, fading thereafter. FTEL remains equity accounted; no telecom revenue consolidation.'),
 'associate_payout':('analyst_scenario','fs pp.9,32','9M received dividends / earnings9.73% is timing-dependent. Q4 cash dividends150/250/350bn; annual payout10/25/35% down/base/up. No assumed100% earnings-to-cash conversion.'),
 'investment_yield':('analyst_scenario','fs pp.30–31,44','4/5/6% down/base/up applied only to term-deposit principal. Contract-specific rates not disclosed. These are analyst rates, not current bank quotes. Other cash/loans earn zero in this conservative scope.'),
 'interest_collection_ratio':('analyst_scenario','fs pp.9,31,44','Current-period interest collected75/90/95% down/base/up. Uncollected income accumulates in the investment interest receivable.'),
 'opening_interest_collection_ratio':('analyst_scenario','fs p.31','Collect50% of opening accrued interest in Q4,100% in each full annual period. Timing assumption, not a contractual maturity claim.'),
 'debt_rate':('analyst_scenario','fs pp.9,39–41,44','Base5.5%,down7%,up4.5% on opening total debt. Nine-month expense and debt bridges support a mid-single-digit blended proxy; intraperiod draws/FX and hedges prevent an exact inferred contractual rate.'),
 'refinance_ratio':('analyst_scenario','fs pp.39–40','100% base/up and95% downside of opening revolver retained each period. Assumed rollover, not a bank commitment. Separate zero-refinancing stress is mandatory.'),
 'term_repayment':('analyst_allocation','fs p.40','Source maturity buckets allocated uniformly by days over Oct26–Sep27, Oct27–Sep28, Oct28–Sep31. Actual instalment dates undisclosed.'),
 'lease_repayment':('analyst_allocation','fs pp.39–40','Current lease amount allocated over first12months; remaining lease allocated over following3years. No new leases assumed.'),
 'current_term_next':('analyst_allocation','fs p.40','Next12months of the same source-bucket calendar, capped by remaining bank principal. Internal current/noncurrent transfer has no cash effect.'),
 'current_lease_next':('analyst_allocation','fs pp.39–40','Next12months of the same lease calendar, capped by remaining lease principal.'),
 'short_repayment_fraction':('legacy_inactive','fs p.40','Zero. Replaced by explicit revolver refinancing and term/lease repayment schedules in the research model.'),
 'long_repayment_fraction':('legacy_inactive','fs p.40','Zero. Replaced by explicit maturity schedule; retained only for legacy API compatibility.'),
 'parent_payout':('analyst_scenario','fs pp.6,10','25% of positive parent PAT base/up;20% downside. The9M combined dividend outflow is1,716.4bn. Forecast payout is an analyst capital-allocation policy, not a declared future dividend.'),
 'nci_share':('analyst_scenario','fs pp.6–7','9M NCI profit slightly negative, Q3 positive6.19bn. Use0.2% of group PAT prospectively, avoiding old1% assumption and pre-FTEL historical NCI ratio.'),
 'nci_payout':('analyst_scenario','fs pp.5–6','30% of positive NCI earnings; analyst policy. No ownership changes or minority capital issuance modelled.'),
 'cash_floor_ratio':('analyst_scenario','fs p.2','Hold5% of annual sales base/up and7% downside. Internal liquidity policy, not a covenant.'),
}
def allocation(start,end,buckets):
 total=0
 for a,b,amount in buckets:
  a,b=date.fromisoformat(a),date.fromisoformat(b);days=max(0,(min(end,b)-max(start,a)).days+1)
  total+=amount*days/((b-a).days+1)
 return total

def main():
 bank=[('2026-10-01','2027-09-30',491.980478973),('2027-10-01','2028-09-30',932.166999020),('2028-10-01','2031-09-30',1347.032829641)]
 lease=[('2026-10-01','2027-09-30',.233257231),('2027-10-01','2030-09-30',.769349498)]
 # Rounding residual assigned to the remaining sector, explicitly disclosed.
 oct_segments=[3541.,861.,ACTUALS['revenue_10m_rounded']-ACTUALS['revenue_9m']-3541.-861.]
 segment9=[28538.,6977.,ACTUALS['revenue_9m']-28538.-6977.]
 cases={};rows=[];revenue_build=[]
 for name,j in [('base',0),('downside',1),('upside',2)]:
  q4segments=[v*(1+2*[1.02,.90,1.10][j]) for v in oct_segments]
  fysegments=[a+b for a,b in zip(segment9,q4segments)]
  assocfy=ACTUALS['associate_9m']+ACTUALS['associate_q3']*[1.05,.9,1.15][j]
  c=dict(name=name,reviewed=True,review_status='documented_analyst_review_not_independent',model_mode='research_components',assumption_class='Dated analyst scenarios calibrated to verified opening and issuer updates',facility_limit=0.,opening_components=COMP,periods=[],limitations=[
   'Forecasts are analyst scenarios, not verified future facts, issuer guidance or an investment recommendation. No independent human sign-off is claimed.',
   '9M2026 and opening facts visually verified against the downloaded HOSE binary; 10M issuer web figures are rounded management updates, not audited October accounts.',
   'FTEL remains equity accounted. Historical FY2025 consolidated sales are not used as a like-for-like growth denominator.',
   'No new M&A, equity issuance, disposal, impairment, FX/OCI or ownership/perimeter change. Foreign-currency exposures remain unhedged in this forecast abstraction; rate/margin stresses address only part of that risk.',
   'Deposit principal and other net investment principal are held constant, implying maturity reinvestment. Collection ratios govern interest cash timing; contract rates are undisclosed.',
   'Current tax equals cash tax under a normalised effective rate excluding after-tax associate earnings. Deferred tax balances and opening current-tax payable remain fixed. This is a timing simplification, not a tax-return forecast.',
   'Trade receivables, vendor advances, contract receivables, other short receivables, allowances and long deposits are separate. Coverage provision changes affect EBIT; no write-offs assumed.',
   'Long prepaid net growth is a contract-stock proxy. Net operating-liability ratios replace a frozen liability balance; nonoperating balances remain fixed.',
   'Capex splits into PPE, intangible and CIP. CIP transfers have no cash effect. Aggregate D&A and10% intangible allocation substitute for unavailable asset-level useful lives.',
   'Bank/lease maturity buckets use explicit uniform-day allocation. Revolver rollover is assumed, not committed; the additional facility cap is zero unless changed by the user.',
   'Interest uses opening debt; financing is not circular. Interest on any new funding starts next period. No automatic cash or deposit sweep.',
   'Historical associate cash receipts do not determine a normalised payout. Future payout, NCI and parent distributions are analyst policies.',
   'A mathematically balanced scenario can be economically infeasible. Review the no-refinancing, working-capital and rate stress outputs before valuation.'
  ])
  for k in range(6):
   year=2026+k;start=date(year,10,1) if k==0 else date(year,1,1);end=date(year,12,31);days=(date(year+1,1,1)-date(year,1,1)).days;frac=((end-start).days+1)/days
   if k==0: rev=sum(q4segments);wcrev=sum(fysegments);ap=ACTUALS['associate_q3']*[1.05,.9,1.15][j];ad=[250,150,350][j]
   else:
    growth=([.13,.12,.11,.10,.08],[.06,.06,.07,.07,.06],[.18,.17,.15,.13,.10])[j][k-1]
    # Domestic/other growth are lower than global IT. No AI-revenue double count.
    rates=[growth,growth-.02,max(0,growth-.06)]
    fysegments=[v*(1+g) for v,g in zip(fysegments,rates)];rev=wcrev=sum(fysegments)
    assocfy*=1+([.12,.10,.09,.08,.06],[.05,.05,.06,.06,.05],[.18,.15,.13,.11,.08])[j][k-1];ap=assocfy;ad=ap*[.25,.10,.35][j]
   nextstart=end+timedelta(days=1);nextend=date(year+1,12,31)
   p=dict(label='Q4 2026E' if k==0 else f'{year}E',start=start.isoformat(),end=end.isoformat(),annual_revenue=rev/frac,wc_revenue=wcrev,gross_margin=[.32,.30,.33][j],ebit_margin=([.1475,.15,.152,.155,.158,.16],[.13]*6,[.155,.16,.165,.17,.175,.18])[j][k],tax_rate=[.17,.20,.15][j],dso=[75,95,70][j],dio=[20,28,18][j],dpo=[20,18,22][j],prepaid_ratio=[.022,.025,.020][j],vendor_advance_ratio=[.027,.032,.025][j],contract_receivable_ratio=[.0055,.008,.005][j],other_receivable_ratio=[.0155,.018,.014][j],allowance_ratio=[.032,.04,.03][j],long_receivable_growth=0.,long_prepaid_growth=[.05,.08,.05][j],other_op_liability_ratio=[.154,.14,.16][j],da_ratio=[.033,.034,.035,.036,.037,.038][k],capex_ratio=([1500,1800,1700][j]/rev if k==0 else ([.07,.065,.06,.055,.055],[.08,.08,.075,.07,.07],[.08,.075,.07,.065,.06])[j][k-1]),intangible_share=.10,cip_share=.30,cip_transfer_rate=.50,associate_profit=ap/frac,associate_payout=ad/ap,investment_yield=[.05,.04,.06][j],interest_collection_ratio=[.90,.75,.95][j],opening_interest_collection_ratio=.5 if k==0 else 1.,debt_rate=[.055,.07,.045][j],refinance_ratio=[1.,.95,1.][j],term_repayment=allocation(start,end,bank),lease_repayment=allocation(start,end,lease),current_term_next=allocation(nextstart,nextend,bank),current_lease_next=allocation(nextstart,nextend,lease),short_repayment_fraction=0.,long_repayment_fraction=0.,parent_payout=[.25,.20,.25][j],nci_share=.002,nci_payout=.30,cash_floor_ratio=[.05,.07,.05][j])
   c['periods'].append(p)
   revenue_build.append(dict(scenario=name,period=p['label'],global_it=q4segments[0] if k==0 else fysegments[0],domestic_it=q4segments[1] if k==0 else fysegments[1],education_other=q4segments[2] if k==0 else fysegments[2],period_revenue=rev,fy_revenue=wcrev,october_observed=sum(oct_segments) if k==0 else None,unknown_months='Nov–Dec' if k==0 else 'full year',source_ids='fs,m9,m10'))
   for driver,value in p.items():
    if driver in RULES:
     cls,source,rationale=RULES[driver];rows.append(dict(scenario=name,period=p['label'],driver=driver,value=value,classification=cls,source_ids=source,rationale=rationale,reviewed_on='2026-11-23',reviewer='Codex analytical review',independent_review=False))
  cases[name]=c
 out=dict(version='0.3.0-prevaluation-analyst',research_cutoff='2026-11-23',sources=SOURCES,actuals=ACTUALS,scenarios=cases)
 (ROOT/'configs/forecast_research.json').write_text(json.dumps(out,indent=2)+'\n')
 (ROOT/'data/intake/forecast_source_facts.json').write_text(json.dumps(dict(sources=SOURCES,actuals=ACTUALS,rounding_note='10M web amounts rounded to nearest VND billion. Remaining-sector residual explicitly reconciles rounded segments to exact9M group sales. Management targets are benchmarks, not enforced forecasts.'),indent=2)+'\n')
 for path,items in [('reports/plan/forecast_assumption_register.csv',rows),('artifacts/reported_schedules/revenue_forecast_bridge.csv',revenue_build)]:
  with (ROOT/path).open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=items[0].keys(),lineterminator="\n");w.writeheader();w.writerows(items)
 (ROOT/'artifacts/reported_schedules/assumption_register.json').write_text(json.dumps(rows,indent=2)+'\n')
 print('Built',len(rows),'documented scenario-period assumptions and',len(revenue_build),'segment revenue bridges')
if __name__=='__main__':main()
