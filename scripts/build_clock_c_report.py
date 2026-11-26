#!/usr/bin/env python3
"""Generate the Clock C research report, sector appendix, memo and pitch.

All valuation and forecast tables come from the engines, not transcribed targets.
"""
from pathlib import Path
import json,html,csv,re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Drawing,Rect,String,Line,PolyLine

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/p1_final';OUT.mkdir(parents=True,exist_ok=True)
v=json.loads((OUT/'clock_c_valuation.json').read_text());base=v['cases']['base']
fc=json.loads((ROOT/'artifacts/three_statement_development/results.json').read_text())['scenarios']
cfg=json.loads((ROOT/'configs/forecast_research.json').read_text())
vc=json.loads((ROOT/'configs/valuation_clock_c.json').read_text())
bench=json.loads((ROOT/'outputs/fpt_development/prevaluation_benchmarks.json').read_text())['cases']
reported=json.loads((ROOT/'data/intake/q3_2026_reported_schedules.json').read_text())
num=lambda x:f'{x:,.0f}'
pct=lambda x:f'{x:.1%}'
bn=lambda x:f'{x:,.1f}'
INK=colors.HexColor('#172d46');BLUE=colors.HexColor('#245c90');MUTED=colors.HexColor('#5e7082');LIGHT=colors.HexColor('#edf2f7')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyC',fontName='Helvetica',fontSize=10.2,leading=15.1,spaceAfter=10,textColor=INK))
styles.add(ParagraphStyle(name='TitleC',fontName='Helvetica-Bold',fontSize=26,leading=30,spaceAfter=15,textColor=colors.black))
styles.add(ParagraphStyle(name='HeadC',fontName='Helvetica-Bold',fontSize=17,leading=21,spaceAfter=13,textColor=colors.black))
styles.add(ParagraphStyle(name='SubC',fontName='Helvetica-Bold',fontSize=11,leading=15,spaceAfter=7,textColor=colors.black))
styles.add(ParagraphStyle(name='SmallC',fontName='Helvetica',fontSize=8.4,leading=11.5,spaceAfter=8,textColor=MUTED))
styles.add(ParagraphStyle(name='CellC',fontName='Helvetica',fontSize=8.5,leading=11,textColor=INK))
pages=[]
def page(title,paras,tables=(),chart=None):pages.append(dict(title=title,paras=paras,tables=list(tables),chart=chart))
def table(headers,rows):return dict(headers=headers,rows=rows)
q=fc['base']['periods'][0];annual=fc['base']['periods'][1:];last=annual[-1]
cfo9=next(g['reported_total_vnd']/1e9 for g in reported['groups'] if g['id']=='cfo')
fy26pat=cfg['actuals']['parent_pat_9m']+q['income_statement']['parent_pat'];fy26cfo=cfo9+q['cash_flow']['cfo']

page('FPT equity research Clock C',[
 f'<b>Decision: WATCHLIST.</b> The base forward equity value is VND{num(base["fair_value_vnd"])} per share at 31 December 2026E. The downside and upside values are VND{num(v["cases"]["downside"]["fair_value_vnd"])} and VND{num(v["cases"]["upside"]["fair_value_vnd"])}. These are conditional model outcomes, not a probability interval. The base value is materially below the frozen Clock B blended value, but the clocks use different dates, forecasts and methods, so the difference is not a realised investment loss.',
 'The investment question is whether growing IT demand converts into distributable cash after working capital and investment. The refreshed forecast improves sales and profits, yet the base FY2026 cash-conversion ratio remains below the existing add-exposure threshold. A balanced model alone does not justify increasing exposure.',
 f'Information is frozen at 23 November 2026. Valuation uses the projected 31 December 2026 closing balance sheet and cash flows from 2027 onward. This avoids treating a 30 September balance sheet as a current balance sheet or discounting already elapsed Q4 cash flows. Q4 dividends and financing movements are included in the projected closing balances. No same-cutoff market quote has been verified, so price upside and a current BUY rating are unavailable.',
 f'The research entry threshold is VND{num(base["margin_of_safety_price_vnd"])} after a 20% margin of safety, conditional on updated evidence. It is not a trade instruction. Terminal value contributes {pct(base["terminal_share_of_ev"])} of operating EV. Discount rates, terminal returns, associate capitalisation and NCI valuation are the main judgement risks.'
],[table(['Case','WACC','Forward value VND','Financing policy'],[[n.title(),pct(x['wacc']),num(x['fair_value_vnd']),x['financing_status'].replace('_',' ').title()] for n,x in v['cases'].items()])])

page('Accounting perimeter and evidence',[
 'FPT Telecom is equity-accounted from 2026. Consolidated revenue, EBIT, cash, debt and non-controlling interests therefore have a different perimeter from the fully consolidated 2025 accounts. Historical reconstruction and issuer-restated comparisons remain separate from the new forecast. A change in a balance-sheet account is not automatically a cash flow when a subsidiary leaves consolidation.',
 'The starting point is the 54-page Q3 consolidated filing hosted by HOSE, published 28 October 2026. The original PDF was downloaded, hashed and visually reviewed in the prior source-intake stage. Its 18 grouped opening balances and ten reported-note bridges reconcile. The extraction retains exact integer VND amounts. Forecasts and presentation tables use VND billion. Original-file provenance verifies the source and transcription within that scope, not the future assumptions.',
 'The model separates gross trade receivables from contract balances, supplier advances, other receivables, allowances and long receivables. Deposits are separated into principal and accrued interest. Associates have separate earnings and cash-dividend schedules. Term bank debt, revolvers, leases and current/noncurrent reclassification are distinct. Capital expenditure is allocated to tangible assets, intangibles and construction in progress.',
 'The 9M accounts and the 10M management update are different data types. The management figures are rounded. Their difference gives an approximate October observation. November and December are forecast. October PBT is used as a benchmark rather than an artificial monthly balance-sheet observation. Sources [1]-[4] and the full assumption register permit tracing these distinctions.'
],[table(['Evidence','Period','Control'],[['Original financial statement','30 Sep / 9M 2026','18 groups; four opening checks'],['Reported-note reconstruction','9M / 30 Sep 2026','10 exact VND bridges'],['Issuer update','10M 2026','Rounded management data'],['Forward assumptions','Q4 2026 and 2027-2031','648 active; 36 compatibility records']])])

page('Operating thesis and forecast',[
 'The base operating thesis is continued international delivery growth with a gradual improvement in efficiency. Domestic IT and education/other remain separate drivers. AI and data services are included in the existing segment forecast. Adding AI revenue as a new independent revenue stream would overstate the business.',
 'The 18 November issuer update reports 10M revenue of VND44,959bn and overseas IT sales of VND32,079bn. Signed overseas contract value grew 20.8%. Those observations support a continuing demand pipeline, but contract value is not immediately recognised sales or cash. Japan exposure also makes local-currency and VND growth comparisons sensitive to exchange rates. The model does not claim that the pipeline guarantees the forecast. [3]',
 f'The base FY2026 revenue forecast is VND{bn(bench[0]["fy2026_revenue"])}bn, {bn(abs(bench[0]["revenue_difference_to_target"]))}bn below the original management target. PBT is VND{bn(bench[0]["fy2026_pbt"])}bn. The original VND7,200bn investment budget has a broader scope than cash fixed-asset capex and is not forced into the capex schedule.',
 'Forward segment growth fades through 2031. Margin expansion remains an analyst assumption rather than a consequence of a company announcement. The downside case combines weaker execution, slower collections, larger working-capital balances and financing friction. The upside combines stronger delivery and collections. The case names do not imply statistical confidence or likelihood.'
],[table(['VND bn','2027E','2029E','2031E'],[[label,*[bn(fc['base']['periods'][i][sec][key]) for i in [1,3,5]]] for label,sec,key in [('Revenue','income_statement','revenue'),('EBIT','income_statement','ebit'),('Parent PAT','income_statement','parent_pat'),('Operating cash flow','cash_flow','cfo'),('Cash capex','cash_flow','capex')]])],chart='revenue')

page('Cash conversion and financing',[
 f'The 9M reported operating cash flow of VND{bn(cfo9)}bn equals only {pct(cfo9/cfg["actuals"]["parent_pat_9m"])} of parent profit. This is the central challenge to the earnings thesis. In the base forecast, Q4 operating cash flow is VND{bn(q["cash_flow"]["cfo"])}bn. FY2026 operating cash flow reaches VND{bn(fy26cfo)}bn against parent PAT of VND{bn(fy26pat)}bn, a ratio of {pct(fy26cfo/fy26pat)}. That still falls below the existing 30% add-exposure threshold.',
 'The cash-conversion ratio is a research gate, not an accounting standard. It compares consolidated operating cash with parent profit and is affected by associates, interest classification and NCI. The additional monitoring tests therefore inspect receivable days, associate distributions, capex and cash after scheduled repayments. A single ratio cannot establish cash quality across a changing perimeter.',
 'The model does not liquidate deposits automatically to meet every shortfall. It also assumes no new uncommitted emergency facility. The downside violates the cash-floor policy even while statements balance. This is a conditional policy shortfall, not evidence of insolvency. A documented deposit redemption, confirmed borrowing commitment or revised distribution plan would require a new funded scenario before an entry decision.',
 'Nine saved scenario/stress runs cover delayed trade collection, higher borrowing rates, loss of revolver rollover, delayed interest receipts, reduced associate dividends and combined stress. A 30-day DSO change must affect gross trade receivables and the associated provision/tax effect. A refinancing reduction must create a repayment cash cost rather than an unexplained balance-sheet adjustment.'
],[table(['Base closing balances VND bn','2026E','2028E','2031E'],[[label,*[bn(fc['base']['periods'][i]['balance_sheet'][key]) for i in [0,2,5]]] for label,key in [('Cash','cash'),('Short debt','short_term_debt'),('Long debt','long_term_debt')]])],chart='cash')

page('Discount rate and terminal economics',[
 f'The base WACC is {pct(base["wacc"])}. Cost of equity is {pct(base["cost_of_equity"])} from a 4.50% VND long-duration anchor, a judgemental beta of 1.0 and an 8% total equity premium. Target debt weight is 10%. Marginal debt cost is 5.50%, with a 20% normalised tax shield. The premium already includes local equity/country risk; no second country premium is added.',
 'These are explicit analyst assumptions. The HNX 9 November traded-yield statistics provide pre-cutoff interest-rate context, but a range of trades is not a clean par-yield curve or a verified closing risk-free rate. No historical beta regression or empirical 8% premium estimate is claimed. An exogenous target capital structure avoids using an unverified share price to calculate market-value WACC weights. [5]',
 'The operating DCF excludes deposit interest and equity-accounted earnings. Annual operating FCFF equals after-tax EBIT plus D&A less capex and operating working-capital investment. The valuation also deducts increases in the required operating-cash reserve, because that cash is retained in the business rather than distributed. Initial required cash is excluded from the equity cash addition.',
 f'The terminal year normalises tax to20%. NOPAT grows by the case terminal g and reinvestment equals NOPAT multiplied by g/ROIC. Base g is3% and ROIC15%, giving a20% reinvestment rate. This avoids perpetuating high-growth capex or assuming perpetual growth with no reinvestment. The immediate move to stable economics is still a simplification. A gradual fade, changing tax incentives or lower returns would change the result.',
 'Mid-year convention discounts annual FCFF at0.5,1.5,2.5,3.5 and4.5 years from31December2026. The Gordon stream begins with2032 cash at5.5years, so the terminal perpetuity is discounted from4.5years. Discounting that terminal at5.0 while using an unadjusted mid-year perpetuity would mix conventions.'
],[table(['Base terminal build','VND bn'],[['2032 normalised NOPAT',bn(base['terminal_nopat'])],['Reinvestment',bn(base['terminal_reinvestment'])],['2032 FCFF',bn(base['terminal_fcff'])],['PV explicit FCFF',bn(base['explicit_pv'])],['PV terminal',bn(base['terminal_pv'])]])])

page('Enterprise to parent equity',[
 'Associates are valued separately using 2027 FPT-attributable associate earnings and an analyst P/E assumption. Those earnings already reflect FPT ownership, so there is no second ownership haircut. Capitalising earnings includes the value of earnings retained inside the associates. Adding the associates book investment or future dividends again would double count that claim.',
 'The bridge adds projected year-end cash less the operating reserve, deposit principal, accrued interest and other short investments. Debt includes leases. CIP and operating prepaid balances remain within operating value. They are not added again as nonoperating assets. No cash accumulated after the valuation date is added to a DCF that already values the cash-generating operations.',
 f'Non-controlling interests require a separate equity claim. The base uses1.5times projected NCI book equity, worth VND{bn(base["nci_value"])}bn. That is a valuation proxy rather than an observed market value. A0.2% profit share alone would ignore the substantial opening NCI capital. The downside uses2.0times book and upside1.0times. A subsidiary-level valuation would improve this estimate.',
 f'The issued-share baseline is1,885.727648million after the September2026 bonus issue. A separate1% unissued dilution reserve gives{bn(base["diluted_shares_million"])}million shares. The reserve is an analyst allowance, not an announced security. Future bonus issues are neutral to aggregate equity value and require a corresponding per-share denominator adjustment. [4]',
 f'The independent parent-earnings cross-check gives VND{num(base["pe_crosscheck_vnd"])} using15times2027 parent earnings. That multiple is a judgement, not a contemporaneous peer median. It is shown alongside SOTP and receives no mechanical blending weight.'
],[table(['Base bridge','VND bn'],[[label,bn(amount)] for label,amount in [('Operating EV',base['operating_ev']),('Associate equity',base['associate_value']),('Cash less reserve',base['cash_net_of_reserve']),('Deposits and other investments',base['investments']),('Debt',-base['debt']),('NCI proxy',-base['nci_value']),('Parent equity',base['equity_value'])]])])

grid=base['sensitivity']
page('Sensitivity and reverse valuation',[
 f'The base valuation is highly sensitive to long-duration assumptions. Terminal value contributes{pct(base["terminal_share_of_ev"])} of operating EV. The grid varies WACC by two percentage points in either direction and terminal growth from2% to4%. It keeps the active operating forecast, terminal ROIC and equity bridge fixed. It is a conditional valuation sensitivity, not a new operating scenario.',
 'The Excel workbook implements a native two-input What-If Data Table connected to the actual WACC and terminal-growth cells. The browser recomputes the valuation from the same active forecast when a control changes. The Python engine supplies independent comparison cases. Changing DSO or capex changes the operating forecast before valuation rather than selecting a static precomputed target.',
 'Reverse DCF solves terminal growth for an explicitly hypothetical share price while preserving the other assumptions. It does not infer market expectations without a verified quote. A price below the value at zero terminal growth is reported outside the nonnegative-growth range. The solver does not fabricate a negative-growth answer or hide a failure as zero.',
 'The case range includes simultaneous changes in operations and valuation judgement. It should not be probability-weighted without a defensible probability assessment. High upside in a favourable case is not compensation for an unfinanceable downside. Review the cash policy and sources before interpreting a single fair-value number.'
],[table(['WACC / g','2.0%','2.5%','3.0%','3.5%','4.0%'],[[pct(grid[i*5]['wacc']),*[num(grid[i*5+j]['fair_value_vnd']) for j in range(5)]] for i in range(5)]),table(['Hypothetical VND price','Result','Implied terminal g'],[[num(r['hypothetical_price']),r['status'].replace('_',' ').title(),pct(r['terminal_growth']) if r['status']=='SOLVED' else 'Outside range'] for r in base['reverse_dcf_hypothetical']])])

page('Decision and monitoring protocol',[
 'The current research stance is WATCHLIST. A current recommendation requires both an attributable dated entry quote and refreshed evidence of cash quality. The model is complete enough to examine valuation and financing assumptions. It does not establish an executable opportunity at an unverified price.',
 f'For the research mandate, no new exposure is added while the cash-conversion gate fails. The base forecast ratio of{pct(fy26cfo/fy26pat)} remains below30%. The VND{num(base["margin_of_safety_price_vnd"])} entry threshold is a conditional screen. It also needs a valuation-date roll and any dividends/corporate actions between the quote and the forward-value date. A future year-end value cannot be presented as a same-day return.',
 'At the FY2026 filing, compare actual revenue, EBIT, capex, DSO, deposit receipts and debt repayments with the frozen forecast. Attribute misses to volume/mix, margins, collections, investment timing and financing. Append actual observations with publication dates. Preserve the forecast and its source hashes for later review. Do not silently overwrite a failed thesis with a revised forecast.',
 'Re-underwrite the thesis if collection deteriorates for two reports, if the model needs unsupported refinancing, if associate distributions fail to support cash needs, or if capital deployment materially reduces returns. Conversely, realised collections, completed higher-value contracts and disciplined reinvestment can support a new clock. Monitoring thresholds below are analyst decision rules rather than issuer guidance.'
],[table(['Trigger','Research response'],[['FY CFO / parent PAT below30%','No additional exposure under existing gate'],['Trade DSO above base by15days for two reports','Review collection assumptions and credit risk'],['Capex / sales above base by2pp','Rebuild returns and terminal reinvestment'],['Unfunded cash-floor requirement','Document a feasible financing policy'],['New issued shares or changed ownership','Update per-share and NCI bridge'],['Verified quote with date and adjustment basis','Calculate dated return only after value roll']])])

page('Sector economics and competition',[
 'IT-services firms convert client technology budgets into delivery revenue through consulting, implementation, software development and managed operations. Economics depend on billable capacity, skill mix, utilisation, pricing, delivery location and retention. In this research those relationships motivate the revenue and margin cases. A detailed utilisation/headcount build is not estimated because a complete comparable dataset is unavailable.',
 'AI can create integration, data, cloud and governance work while reducing labour required for some coding tasks. The net margin effect depends on contract terms and whether clients retain productivity gains. This is a causal hypothesis rather than a measured forecast variable. It argues for testing margins and collections separately from announced AI activity.',
 'FPT combines international IT, domestic technology and education/other activities. It also owns equity-accounted investments. That mix makes a consolidated P/E an imperfect comparison with a purer global IT supplier. VND growth incorporates exchange-rate effects, whereas peers often highlight USD and constant-currency growth. No common-currency revenue total or growth ranking is fabricated.',
 'TCS and Infosys provide operating reference points rather than a traded valuation basket. TCS reports a24.0% operating margin and2.4% USD year-on-year revenue growth for the quarter ending30September2026. Infosys reports a21.0% operating margin and1.3% USD revenue growth for that quarter. FPT9M EBIT margin on the continuing perimeter is approximately14.7%. Different period lengths, service mix, currencies and accounting treatments prevent a direct margin-target transplant. [6]-[7]'
],[table(['Reference','Period','Operating margin','Use'],[['FPT continuing group','9M2026','Approx14.7%','Own forecast anchor'],['TCS','Quarter Sep2026','24.0%','Delivery economics context'],['Infosys','Quarter Sep2026','21.0%','Delivery economics context']])])

page('Sector risks and valuation discipline',[
 'Client budget cycles and contract ramps affect recognition and utilisation. A strong signed-contract pipeline can coexist with delayed revenue or collections. Fixed-price work exposes delivery cost overruns. Higher-value work requires specialist talent and may raise wage costs before utilisation improves. These mechanisms connect demand evidence to downside margin and working-capital assumptions.',
 'Japan exposure introduces translation and commercial concentration risk. A stronger VND against contract currencies can reduce reported growth without a decline in local delivery. Geographical expansion can reduce concentration over time but adds delivery and compliance costs. The current model expresses these risks through scenario growth and margins rather than an unobserved hedging gain or loss.',
 'Education and infrastructure require cash investment before full earnings contribution. CIP commissioning can change depreciation and cash returns. The model transfers CIP into service and keeps construction additions distinct from depreciation. It does not assume that a broad investment-budget headline becomes productive cash capex immediately.',
 'Cybersecurity, data protection, intellectual-property obligations and cross-border delivery rules can alter contract costs or access. No new legal interpretation is embedded here. These are monitoring categories whose financial consequences should enter a subsequent clock when an attributable event or contract change is disclosed.',
 'A quoted peer P/E comparison would require same-date prices, diluted shares, net-debt definitions and matched earnings periods. That dataset is not present, so the cross-check multiples are labelled analyst assumptions. Sector observations challenge the operating thesis but do not turn the14times associate capitalisation or15times parent multiple into observed market facts. This limits the strength of any relative-value conclusion.'
],[table(['Risk channel','Model variable','Evidence to monitor'],[['Client budget or contract ramp','Segment sales / EBIT margin','Recognised sales and delivery commentary'],['Collections and milestones','Trade DSO / contract balances','Ageing and cash receipts'],['Talent and pricing','Gross margin / operating margin','Cost and utilisation disclosures'],['Infrastructure commissioning','Capex / CIP / D&A','Asset additions and in-service dates'],['Investment returns','Terminal ROIC / associate value','Cash distributions and capital allocation']])])

sources=[
 ('1','HOSE Q3 2026 consolidated filing','2026-10-28',cfg['sources']['fs']['url']),
 ('2','FPT 9M business update','2026-10-21',cfg['sources']['m9']['url']),
 ('3','FPT 10M business update','2026-11-18',cfg['sources']['m10']['url']),
 ('4','FPT outstanding-share notice','2026-09-25',vc['sources'][0]['url']),
 ('5','HNX traded-yield statistics context','2026-11-09',vc['sources'][1]['url']),
 ('6','TCS September quarter results','2026-10-08',vc['sources'][3]['url']),
 ('7','Infosys September quarter results','2026-10-23','https://www.infosys.com/about/last-quarter.html'),
 ('8','FPT annual report and 2026 plan','2026-04-08',cfg['sources']['plan']['url'])]
page('Sources and reproducibility',[
 'The research engines use standard-library Python for forecast and valuation. The independent spreadsheet is built with formulas, while the browser has a separate JavaScript implementation. The report reads generated result files so that its headline values and tables cannot drift through manual transcription. All new author metadata uses the repository username or is blank.',
 'Run scripts/run_clock_c.py and scripts/run_checks.py with Python3.10or later. The complete artifact build uses scripts/run_all.py plus the workbook/dashboard/report builders and the execution notebook. The quality workflow checks source/model economics and regenerates the Clock C result. Runtime-specific packages are needed to regenerate Excel/PDF outputs, but not to reproduce the financial calculations.',
 'New checks cover discount timing, absence of Q4 cash double counting, associate scope, operating-cash reserve investment, debt/cash marginal effects, WACC/growth/ROIC/dilution direction, NCI claim sensitivity, reverse-solver recovery and rejection of unreviewed or invalid inputs. Cross-engine agreement supplements those economic checks. It cannot establish that assumptions are true.',
 'Native Microsoft Excel interaction and a Jupyter kernel are separate application checks. Sequential ordinary-Python notebook execution and an independent office-engine recalculation must be described by their actual method. No independent human investment-research review is claimed. The forward value remains a conditional research result with the limitations recorded above.'
])
page('Primary source register',[
 'All publication dates below precede the information cutoff. Retrieval and report completion took place on26November2026. No post-cutoff business announcement or current market price is fed into the frozen forecast. Mutable landing pages can contain newer navigation or unrelated news; only the dated disclosures listed here are used.',
 'The original financial-statement receipt retains SHA-256 e32a7edba4e40fd08af58587abaf8b95c9c7b70cd120c14e5f33b6153b1c9e14. The share notice has prior visual verification and a checksum in configs/sources.yaml. Its fresh web retrieval was unavailable in this pass. HNX indexed pre-cutoff trade ranges were retrieved, while a fresh direct PDF fetch timed out. The risk-free anchor therefore remains explicitly judgemental.',
 *[f'<b>[{i}] {name}</b>. Published {date}.<br/><link href="{html.escape(url,quote=True)}" color="#245c90">'+ '<br/>'.join(html.escape(url[k:k+76]) for k in range(0,len(url),76))+'</link>' for i,name,date,url in sources]
])

def draw_chart(kind):
    d=Drawing(465,165);points=[];yrs=['2026E','2027E','2028E','2029E','2030E','2031E']
    if kind=='revenue':series=[('Revenue',[cfg['actuals']['revenue_9m']+q['income_statement']['revenue']]+[p['income_statement']['revenue'] for p in annual],BLUE)]
    else:series=[('Cash',[p['balance_sheet']['cash'] for p in fc['base']['periods']],BLUE),('Debt',[p['balance_sheet']['short_term_debt']+p['balance_sheet']['long_term_debt'] for p in fc['base']['periods']],colors.HexColor('#ac7a35'))]
    mx=max(max(vals) for _,vals,_ in series)*1.12
    for k in range(4):
        y=30+k*35;d.add(Line(42,y,450,y,strokeColor=LIGHT));d.add(String(38,y-3,num(mx*k/3),textAnchor='end',fontSize=7,fillColor=MUTED))
    for title,values,color in series:
        coords=[]
        for i,x in enumerate(values):coords.extend([50+i*78,30+x/mx*105])
        d.add(PolyLine(coords,strokeColor=color,strokeWidth=2));d.add(String(55+series.index((title,values,color))*100,151,title,fontSize=9,fillColor=color))
    for i,y in enumerate(yrs):d.add(String(50+i*78,12,y,textAnchor='middle',fontSize=8,fillColor=MUTED))
    return d

def spaced(t):return re.sub(r'\b(The|the|on|below|by|to|is|a|uses|times|from|at|of|g|ROIC|WACC|cutoff|Forward|date|November|September|December|October|Nov|Sep|Dec|Oct|Q4|FPT)(?=\d)',r'\1 ',t)
def P(t,style='BodyC'):return Paragraph(spaced(t) if '<link' not in t else t,styles[style])
def make_table(t,width=465):
    n=len(t['headers']);rows=[[P(html.escape(str(x)),'CellC') for x in t['headers']]]+[[P(html.escape(str(x)),'CellC') for x in r] for r in t['rows']]
    widths=[width/n]*n
    if n==2:widths=[width*.68,width*.32]
    tb=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT');tb.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LINEBELOW',(0,0),(-1,0),.6,BLUE),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#dce3ea'))]))
    return tb
def footer(canvas,doc):
    canvas.setAuthor('thvh2006');canvas.setTitle('FPT equity research Clock C');canvas.setSubject('Forward year-end valuation; information cutoff 23 Nov 2026')
    canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED);w,h=doc.pagesize
    canvas.drawString(54,28,'FPT Clock C | VND billion except per-share VND | 23 Nov 2026 cutoff');canvas.drawRightString(w-54,28,str(doc.page))
def build_pdf(path,selected):
    story=[]
    for i,p in enumerate(selected):
        if i:story.append(PageBreak())
        story.append(P(p['title'],'TitleC' if i==0 else 'HeadC'))
        for text in p['paras']:story.append(P(text))
        for t in p['tables']:story.extend([Spacer(1,6),make_table(t),Spacer(1,10)])
        if p['chart']:story.extend([Spacer(1,9),draw_chart(p['chart'])])
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=47,bottomMargin=48).build(story,onFirstPage=footer,onLaterPages=footer)

def markdown(selected):
    result=[]
    import re
    for p in selected:
        result.append('# '+p['title']+'\n')
        result.extend(spaced(re.sub('<[^>]+>','',x))+'\n' for x in p['paras'])
        for t in p['tables']:
            result.extend(['| '+' | '.join(map(str,t['headers']))+' |','| '+' | '.join(['---']*len(t['headers']))+' |'])
            result.extend('| '+' | '.join(map(str,r))+' |' for r in t['rows']);result.append('')
    return '\n'.join(result).rstrip()+'\n'

build_pdf(OUT/'FPT_Equity_Research_Clock_C.pdf',pages)
(ROOT/'reports/FPT_Equity_Research_Clock_C.md').write_text(markdown(pages))
build_pdf(OUT/'FPT_Decision_Memo_Clock_C.pdf',[pages[0],pages[7]])
(ROOT/'reports/FPT_Decision_Memo_Clock_C.md').write_text(markdown([pages[0],pages[7]]))
build_pdf(OUT/'FPT_Sector_Appendix_Clock_C.pdf',[pages[8],pages[9],pages[11]])

pitch=[
 ('FPT Clock C investment view',f'WATCHLIST. Base forward value VND{num(base["fair_value_vnd"])} per share.','The decision depends on cash conversion and a verified entry quote. Information cutoff23Nov2026. Value date31Dec2026E.'),
 ('The research question','Does earnings growth become distributable cash?','Revenue and profit can grow while receivables, capex and associate retained earnings absorb cash. Follow the cash statement as well as the income statement.'),
 ('Accounting changes the valuation','FPT Telecom is equity accounted.','Operating FCFF excludes associate profit and deposit interest. Associate equity and nonoperating cash investments enter separately. Do not reuse the fully consolidated revenue perimeter.'),
 ('Demand supports a conditional growth thesis','Keep contract pipeline separate from recognised cash.','The10M update and segment observations inform the forecast. AI is within existing segment sales. Delivery, collections and margins remain separate assumptions. Source: FPT18Nov2026 update.'),
 ('Cash is the decision constraint',f'FY2026E CFO / parent PAT is{pct(fy26cfo/fy26pat)}.','The base forecast remains below the30% add-exposure gate. Downside financing violates the held-deposit and zero-new-facility policy. That requires re-underwriting, not a cash plug.'),
 ('The DCF has a traceable operating build',f'Base WACC{pct(base["wacc"])}. Terminal g3%. ROIC15%.','Annual FCFF includes required operating-cash investment. Stable tax is20%. Mid-year discount convention is consistent across explicit cash and the terminal stream.'),
 ('Bridge enterprise value to parent equity',f'Parent equity value VND{bn(base["equity_value"])}bn.','Add associates and cash/deposits, subtract debt and the NCI proxy, then divide by issued shares plus a1% dilution reserve. No associate book, dividend or CIP double count.'),
 ('Valuation is assumption sensitive',f'Downside VND{num(v["cases"]["downside"]["fair_value_vnd"])}. Upside VND{num(v["cases"]["upside"]["fair_value_vnd"])}. ',f'Terminal value is{pct(base["terminal_share_of_ev"])} of base operating EV. The case range is not a statistical interval. P/E is an analyst cross-check, without a blending weight.'),
 ('What would change the decision','Collections, funding and investment returns must improve.','Track actual versus forecast DSO, CFO, capex, associate receipts and refinancing. Preserve frozen forecasts when new actuals arrive. Add a dated quote and corporate-action bridge before calculating return.'),
 ('Review the complete evidence chain','One forecast feeds independent valuation engines.','Source receipt, assumption register, Python economics tests, Excel native sensitivities and JavaScript golden cases accompany the report. WACC, NCI and terminal assumptions remain judgement risks.')]
pitchpath=OUT/'FPT_Stock_Pitch_Clock_C.pdf'
c=Canvas(str(pitchpath),pagesize=landscape(A4));w,h=landscape(A4)
for i,(title,takeaway,body) in enumerate(pitch):
    c.setFillColor(colors.white);c.rect(0,0,w,h,fill=1,stroke=0);c.setFillColor(BLUE);c.setFont('Helvetica-Bold',11);c.drawString(54,h-54,'FPT CORPORATION  /  CLOCK C')
    for text,y,font,size,lead in [(title,h-125,'Helvetica-Bold',29,35),(takeaway,h-225,'Helvetica-Bold',22,29),(body,h-320,'Helvetica',16,24)]:
        st=ParagraphStyle('slide',fontName=font,fontSize=size,leading=lead,textColor=INK)
        p=Paragraph(spaced(text),st);pw,ph=p.wrap(w-110,250);p.drawOn(c,54,y-ph)
    c.setFont('Helvetica',9);c.setFillColor(MUTED);c.drawString(54,35,'Forward31Dec2026E value. Information cutoff23Nov2026. thvh2006');c.drawRightString(w-54,35,f'{i+1} / 10');c.showPage()
c.setAuthor('thvh2006');c.setTitle('FPT stock pitch Clock C');c.save()
pitch_html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FPT Clock C stock pitch</title><style>body{margin:0;background:#edf2f7;font-family:Arial;color:#172d46}section{background:white;max-width:1100px;min-height:600px;margin:32px auto;padding:64px;box-sizing:border-box}h1{font-size:38px}h2{font-size:29px;line-height:1.4}p{font-size:23px;line-height:1.6}small{color:#5e7082}@media print{section{break-after:page;margin:0;box-shadow:none;min-height:0}}</style>'+''.join(f'<section><small>FPT CLOCK C · {i+1}/10</small><h1>{html.escape(t)}</h1><h2>{html.escape(a)}</h2><p>{html.escape(b)}</p><small>Forward31Dec2026E. Cutoff23Nov2026. thvh2006</small></section>' for i,(t,a,b) in enumerate(pitch))+'</html>'
(OUT/'FPT_Stock_Pitch_Clock_C.html').write_text(pitch_html)
with (OUT/'valuation_sensitivity.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=['scenario','wacc','g','fair_value_vnd'],lineterminator='\n');writer.writeheader()
    for name,case in v['cases'].items():
        for point in case['sensitivity']:writer.writerow(dict(scenario=name,**point))
print(json.dumps({'report_sections':len(pages),'pitch_slides':len(pitch),'base_fy26_cfo_to_parent_pat':fy26cfo/fy26pat}))
