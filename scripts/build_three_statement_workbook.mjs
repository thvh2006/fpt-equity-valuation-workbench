import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const config=JSON.parse(await fs.readFile(path.join(root,'configs/forecast_research.json'),'utf8'));
const opening=JSON.parse(await fs.readFile(path.join(root,'data/intake/clock_c_opening_pending.json'),'utf8'));
const expected=JSON.parse(await fs.readFile(path.join(root,'artifacts/three_statement_development/results.json'),'utf8'));
const out=path.join(root,'outputs/fpt_development');
await fs.mkdir(out,{recursive:true});
await fs.mkdir(path.join(root,'outputs/previews'),{recursive:true});
const wb=Workbook.create();
const names=['Start Here','Valuation','Summary','Assumptions','DCF','Valuation Inputs','Opening','Schedules','Income Statement','Cash Flow','Balance Sheet','Checks'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const cols=['E','F','G','H','I','J'];
const numeric='#,##0.0;(#,##0.0);"-"';
const label=(s,cell,text)=>s.getRange(cell).values=[[text]];
const formula=(s,cell,text)=>{s.getRange(cell).formulas=[['='+text]];s.getRange(cell).format.font.color=text.includes('!')?'#238249':'#172133';};
const value=(s,cell,v)=>{s.getRange(cell).values=[[v]];s.getRange(cell).format.font.color='#1756C0';};
for(const [name,s] of Object.entries(sheets)){
 s.showGridLines=false;s.getRange('A1:K180').format.font={name:'Arial',size:10,color:'#172133'};
 s.getRange('A:B').format.columnWidth=2.5;s.getRange('C:C').format.columnWidth=38;
 s.getRange('D:D').format.columnWidth=14;s.getRange('E:J').format.columnWidth=17;
 s.getRange('C1:J180').format.rowHeight=21;s.getRange('C2').format.font={size:15,bold:true,color:'#172133'};
 label(s,'C2',name);label(s,'C3','Clock C. VND billion. Information cutoff 23 Nov 2026. Forward value at 31 Dec 2026E.');
 s.getRange('C3:J3').format.font={size:10,italic:true,color:'#616B79'};
 s.getRange('C3:J3').format.rowHeight=26;
 if(!['Start Here','Opening','Assumptions'].includes(name)){
  label(s,'C5','Case selected');formula(s,'D5',"CHOOSE(Assumptions!$D$5,\"Base\",\"Downside\",\"Upside\")");
  s.getRange('D5').format.font.color='#238249';
 }
 if(!['Start Here','Opening','Assumptions'].includes(name)){
  for(let i=0;i<6;i++)label(s,cols[i]+'5',config.scenarios.base.periods[i].label);
  s.getRange('E5:J5').format={fill:'#183553',font:{color:'#FFFFFF',bold:true},horizontalAlignment:'center'};
  s.getRange('E6:J180').setNumberFormat(numeric);
 }
 if(!['Start Here','Summary'].includes(name)){s.freezePanes.freezeRows(5);s.freezePanes.freezeColumns(4);}
}
const a=sheets.Assumptions;
label(a,'C5','Case selector');value(a,'D5',1);a.getRange('D5').dataValidation={rule:{type:'list',values:['1','2','3']}};
label(a,'F5','1 Base   2 Downside   3 Upside');label(a,'C6','Additional facility commitment');value(a,'D6',0);
label(a,'F6','VND billion. Fixed commitment. No automatic cash sweep.');
for(let i=0;i<6;i++){
 const p=config.scenarios.base.periods[i],y=+p.end.slice(0,4),days=y%4===0?366:365;
 label(a,cols[i]+'8',p.label);value(a,cols[i]+'9',i?1:92/365);value(a,cols[i]+'10',days);
}
label(a,'C9','Period year fraction');label(a,'C10','Days in fiscal year');
a.getRange('E9:J9').setNumberFormat('0.0000');a.getRange('E10:J10').setNumberFormat('0');
const drivers=Object.keys(config.scenarios.base.periods[0]).filter(k=>!['label','start','end','short_repayment_fraction','long_repayment_fraction'].includes(k));
const driverRows={};
for(let k=0;k<drivers.length;k++){
 const key=drivers[k],r=12+k*4;driverRows[key]=r;
 label(a,'C'+r,key.replaceAll('_',' '));label(a,'D'+r,'Active');
 a.getRange('C'+r+':J'+r).format.fill='#EAF0F6';a.getRange('C'+r+':J'+r).format.font.bold=true;
 ['base','downside','upside'].forEach((name,j)=>{
  label(a,'D'+(r+j+1),name);
  for(let i=0;i<6;i++)value(a,cols[i]+(r+j+1),config.scenarios[name].periods[i][key]);
 });
 for(const c of cols)formula(a,c+r,`IF(CHOOSE($D$5,ISBLANK(${c}${r+1}),ISBLANK(${c}${r+2}),ISBLANK(${c}${r+3})),"Missing case input",CHOOSE($D$5,${c}${r+1},${c}${r+2},${c}${r+3}))`);
 const fmt=/margin|rate|ratio|share|payout|yield|fraction|growth/.test(key)?'0.0%':numeric;
 a.getRange(`E${r}:J${r+3}`).setNumberFormat(fmt);
}
const A=(c,key)=>`Assumptions!${c}${driverRows[key]}`;
const o=sheets.Opening;
const openingRows={};label(o,'C5','Grouped balance');label(o,'D5','VND billion');label(o,'F5','Reported statement codes');
for(let i=0;i<opening.facts.length;i++){
 const f=opening.facts[i],r=6+i;openingRows[f.metric]=r;
 label(o,'C'+r,f.metric.replaceAll('_',' '));value(o,'D'+r,f.value);label(o,'F'+r,f.grouping_note.replace('Sum of reported statement codes ',''));
}
o.getRange('D6:D23').setNumberFormat(numeric);label(o,'C25','Opening date');label(o,'D25','30-Sep-2026');
label(o,'C27','Source: HOSE Q3 2026 filing, printed pages 2 to 5. Original PDF downloaded, hashed and visually reviewed.');
label(o,'C29','Grouped prepaids include short and long expense allocations. Other balances use explicit codes.');
label(o,'C31',opening.source_url);o.getRange('C27:J31').format.rowHeight=25;
const componentRows={};
label(o,'C34','Opening components from verified source');label(o,'D34','VND billion');
for(const [idx,[key,amount]] of Object.entries(config.scenarios.base.opening_components).entries()){
 const r=35+idx;componentRows[key]=r;label(o,'C'+r,key.replaceAll('_',' '));value(o,'D'+r,amount);o.getRange('D'+r).setNumberFormat(numeric);
}
const O=k=>`Opening!$D$${componentRows[k]}`;
const actualRows={};label(o,'C53','Historical and issuer benchmark inputs');label(o,'D53','VND billion');label(o,'F53','Source ID');
for(const [idx,[key,amount]] of Object.entries(config.actuals).entries()){
 const r=54+idx;actualRows[key]=r;label(o,'C'+r,key.replaceAll('_',' '));value(o,'D'+r,amount);o.getRange('D'+r).setNumberFormat(numeric);
 const source=key.includes('management')?'plan':key.includes('10m')?'m10':key.includes('global_9m')||key.includes('domestic_9m')?'m9':'fs';label(o,'F'+r,source);
}
let sourceRow=80;for(const [id,source] of Object.entries(config.sources)){label(o,'C'+sourceRow,id+' · '+source.published);o.mergeCells(`D${sourceRow}:J${sourceRow}`);label(o,'D'+sourceRow,source.url);o.getRange(`D${sourceRow}:J${sourceRow}`).format.font={name:'Arial',size:9,color:'#1756C0'};sourceRow++;}
const actual=k=>`Opening!$D$${actualRows[k]}`;
const S=(c,r)=>`Schedules!${c}${r}`,IS=(c,r)=>`'Income Statement'!${c}${r}`,CF=(c,r)=>`'Cash Flow'!${c}${r}`,BS=(c,r)=>`'Balance Sheet'!${c}${r}`;
const schedLabels={6:'Annual revenue run rate',7:'Period year fraction',8:'Opening cash',9:'Opening investments',10:'Opening receivables',11:'Opening inventories',12:'Opening prepaids',13:'Opening PPE',14:'Opening intangibles',15:'Opening associates',16:'Opening other assets',17:'Opening base short debt',18:'Opening long debt',19:'Opening facility',20:'Opening trade payables',21:'Opening other liabilities',22:'Opening parent equity',23:'Opening NCI equity',25:'Closing receivables',26:'Closing inventories',27:'Closing prepaids',28:'Closing trade payables',29:'Change in operating working capital',30:'Cash capex',31:'Depreciation and amortisation',32:'Tangible additions',33:'Intangible additions',34:'Tangible depreciation',35:'Intangible amortisation',36:'Share of associate profit',37:'Associate dividends received',38:'Base short debt repaid',39:'Long debt repaid',40:'Parent dividends paid',41:'NCI distributions paid',42:'Required cash floor',43:'Cash before new facility',44:'Funding required',45:'Facility drawn',46:'Closing base short debt',47:'Closing long debt',48:'Closing facility',49:'Unfunded cash requirement',50:'Closing PPE',51:'Closing intangibles',52:'Closing associates',53:'Closing parent equity',54:'Closing NCI equity',55:'Unlevered FCFF',56:'Closing total debt'};
Object.assign(schedLabels,{60:'Full-year sales for balance ratios',61:'Deposit principal held constant',62:'Opening accrued deposit interest',63:'Closing accrued deposit interest',64:'Cash interest received',65:'Opening gross trade receivables',66:'Closing gross trade receivables',67:'Closing supplier advances',68:'Closing contract receivables',69:'Closing other short receivables',70:'Opening receivable allowance',71:'Closing receivable allowance',72:'Incremental credit-loss expense',73:'Opening long receivables',74:'Closing long receivables',75:'Opening long prepaids',76:'Closing long prepaids',77:'Closing short prepaids',78:'Opening other operating liabilities',79:'Closing other operating liabilities',80:'Other nonoperating liabilities fixed',81:'Opening revolving bank debt',82:'Revolver principal repaid',83:'Closing revolving bank debt',84:'Opening term bank principal',85:'Closing term bank principal',86:'Opening lease principal',87:'Closing lease principal',88:'Term bank current portion',89:'Lease current portion',90:'Opening construction in progress',91:'Capex allocated to CIP',92:'CIP transferred to tangible PPE',93:'Closing construction in progress',94:'Other assets excluding CIP, fixed',95:'Other net investment principal fixed'});
for(const [r,l] of Object.entries(schedLabels))label(sheets.Schedules,'C'+r,l);
const il={6:'Revenue',7:'Cost of sales',8:'Gross profit',9:'Operating expenses',10:'EBIT',11:'Interest income',12:'Interest expense',13:'Associate profit',14:'Profit before tax',15:'Tax expense',16:'Group profit after tax',17:'NCI profit after tax',18:'Parent profit after tax'};
for(const [r,l] of Object.entries(il))label(sheets['Income Statement'],'C'+r,l);
const cl={6:'Opening cash',7:'Group profit after tax',8:'D&A add-back',9:'Remove associate profit and interest',10:'Operating working capital cash effect',11:'Cash from operations',13:'Capital expenditure',14:'Interest and associate dividends received',15:'Cash from investing',17:'Debt principal repaid',18:'Parent dividends paid',19:'NCI distributions paid',20:'New facility draw',21:'Cash from financing',23:'Closing cash'};
for(const [r,l] of Object.entries(cl))label(sheets['Cash Flow'],'C'+r,l);
opening.facts.forEach((f,i)=>label(sheets['Balance Sheet'],'C'+(6+i),f.metric.replaceAll('_',' ')));
for(let i=0;i<6;i++){
 const c=cols[i],prev=cols[i-1];
 const op=k=>i?BS(prev,openingRows[k]):`Opening!$D$${openingRows[k]}`;
 const sf={6:A(c,'annual_revenue'),7:`Assumptions!${c}9`,8:op('cash'),9:op('short_term_investments'),10:op('receivables'),11:op('inventories'),12:op('prepaids'),13:op('ppe_net'),14:op('intangibles_net'),15:op('associates'),16:op('other_assets'),17:i?S(prev,46):`Opening!$D$${openingRows.short_term_debt}`,18:i?S(prev,47):`Opening!$D$${openingRows.long_term_debt}`,19:i?S(prev,48):'0',20:op('trade_payables'),21:op('other_liabilities'),22:op('parent_equity'),23:op('nci_equity'),25:`${c}6*${A(c,'dso')}/Assumptions!${c}10`,26:`${c}6*(1-${A(c,'gross_margin')})*${A(c,'dio')}/Assumptions!${c}10`,27:`${c}6*${A(c,'prepaid_ratio')}`,28:`${c}6*(1-${A(c,'gross_margin')})*${A(c,'dpo')}/Assumptions!${c}10`,29:`${c}25-${c}10+${c}26-${c}11+${c}27-${c}12-(${c}28-${c}20)`,30:`${IS(c,6)}*${A(c,'capex_ratio')}`,31:`${IS(c,6)}*${A(c,'da_ratio')}`,32:`${c}30*(1-${A(c,'intangible_share')})`,33:`${c}30*${A(c,'intangible_share')}`,34:`${c}31*(1-${A(c,'intangible_share')})`,35:`${c}31*${A(c,'intangible_share')}`,36:`${A(c,'associate_profit')}*${c}7`,37:`${c}36*${A(c,'associate_payout')}`,38:`${c}17*${A(c,'short_repayment_fraction')}`,39:`${c}18*${A(c,'long_repayment_fraction')}`,40:`MAX(${IS(c,18)},0)*${A(c,'parent_payout')}`,41:`MAX(${IS(c,17)},0)*${A(c,'nci_payout')}`,42:`${c}6*${A(c,'cash_floor_ratio')}`,43:`${c}8+${CF(c,11)}+${CF(c,15)}-${c}38-${c}39-${c}40-${c}41`,44:`MAX(${c}42-${c}43,0)`,45:`MIN(${c}44,MAX(Assumptions!$D$6-${c}19,0))`,46:`${c}17-${c}38`,47:`${c}18-${c}39`,48:`${c}19+${c}45`,49:`${c}44-${c}45`,50:`${c}13+${c}32-${c}34`,51:`${c}14+${c}33-${c}35`,52:`${c}15+${c}36-${c}37`,53:`${c}22+${IS(c,18)}-${c}40`,54:`${c}23+${IS(c,17)}-${c}41`,55:`${IS(c,10)}*(1-${A(c,'tax_rate')})+${c}31-${c}30-${c}29`,56:`SUM(${c}46:${c}48)`};
 const componentOpen=(key,row)=>i?S(prev,row):O(key);
 Object.assign(sf,{
  60:A(c,'wc_revenue'),61:O('deposit_principal'),62:componentOpen('interest_accrued',63),63:`${c}62+${IS(c,11)}-${c}64`,64:`${c}62*${A(c,'opening_interest_collection_ratio')}+${IS(c,11)}*${A(c,'interest_collection_ratio')}`,
  65:componentOpen('trade_receivables',66),66:`${c}60*${A(c,'dso')}/Assumptions!${c}10`,67:`${c}60*${A(c,'vendor_advance_ratio')}`,68:`${c}60*${A(c,'contract_receivable_ratio')}`,69:`${c}60*${A(c,'other_receivable_ratio')}`,70:componentOpen('receivable_allowance',71),71:`${c}66*${A(c,'allowance_ratio')}`,72:`${c}71-${c}70`,73:componentOpen('long_receivables',74),74:`${c}73*(1+${A(c,'long_receivable_growth')}*${c}7)`,75:componentOpen('long_prepaids',76),76:`${c}75*(1+${A(c,'long_prepaid_growth')}*${c}7)`,77:`${c}60*${A(c,'prepaid_ratio')}`,
  78:componentOpen('operating_other_liabilities',79),79:`${c}60*${A(c,'other_op_liability_ratio')}`,80:`Opening!$D$${openingRows.other_liabilities}-${O('operating_other_liabilities')}`,
  81:componentOpen('revolver',83),82:`${c}81*(1-${A(c,'refinance_ratio')})`,83:`${c}81-${c}82`,84:componentOpen('term_bank',85),85:`MAX(${c}84-${A(c,'term_repayment')},0)`,86:componentOpen('lease',87),87:`MAX(${c}86-${A(c,'lease_repayment')},0)`,88:`MIN(${c}85,${A(c,'current_term_next')})`,89:`MIN(${c}87,${A(c,'current_lease_next')})`,
  90:componentOpen('cip',93),91:`${c}30*${A(c,'cip_share')}`,92:`MIN(${c}90,${c}90*${A(c,'cip_transfer_rate')}*${c}7)`,93:`${c}90+${c}91-${c}92`,94:`Opening!$D$${openingRows.other_assets}-${O('cip')}`,95:O('investment_other_net'),
  25:`SUM(${c}66:${c}69)+${c}74-${c}71`,26:`${c}60*(1-${A(c,'gross_margin')})*${A(c,'dio')}/Assumptions!${c}10`,27:`${c}76+${c}77`,28:`${c}60*(1-${A(c,'gross_margin')})*${A(c,'dpo')}/Assumptions!${c}10`,29:`${c}25-${c}10+${c}26-${c}11+${c}27-${c}12-(${c}28-${c}20)-(${c}79-${c}78)`,32:`${c}30*(1-${A(c,'intangible_share')}-${A(c,'cip_share')})+${c}92`,38:`${c}82+${A(c,'term_repayment')}+${A(c,'lease_repayment')}`,39:'0',42:`${c}60*${A(c,'cash_floor_ratio')}`,46:`${c}83+${c}88+${c}89`,47:`${c}85+${c}87-${c}88-${c}89`
 });
 for(const [r,f] of Object.entries(sf))formula(sheets.Schedules,c+r,f);
 const iff={6:`${S(c,6)}*${S(c,7)}`,7:`${c}6*(1-${A(c,'gross_margin')})`,8:`${c}6-${c}7`,9:`${c}8-${c}10`,10:`${c}6*${A(c,'ebit_margin')}-${S(c,72)}`,11:`${S(c,61)}*${A(c,'investment_yield')}*${S(c,7)}`,12:`(${S(c,17)}+${S(c,18)}+${S(c,19)})*${A(c,'debt_rate')}*${S(c,7)}`,13:S(c,36),14:`${c}10+${c}11-${c}12+${c}13`,15:`MAX(${c}14-${c}13,0)*${A(c,'tax_rate')}`,16:`${c}14-${c}15`,17:`${c}16*${A(c,'nci_share')}`,18:`${c}16-${c}17`};
 for(const [r,f] of Object.entries(iff))formula(sheets['Income Statement'],c+r,f);
 const cff={6:S(c,8),7:IS(c,16),8:S(c,31),9:`-${S(c,36)}-${IS(c,11)}`,10:`-${S(c,29)}`,11:`SUM(${c}7:${c}10)`,13:`-${S(c,30)}`,14:`${S(c,37)}+${S(c,64)}`,15:`SUM(${c}13:${c}14)`,17:`-${S(c,38)}-${S(c,39)}`,18:`-${S(c,40)}`,19:`-${S(c,41)}`,20:S(c,45),21:`SUM(${c}17:${c}20)`,23:`${c}6+${c}11+${c}15+${c}21`};
 for(const [r,f] of Object.entries(cff))formula(sheets['Cash Flow'],c+r,f);
 const bf={6:CF(c,23),7:`${S(c,61)}+${S(c,63)}+${S(c,95)}`,8:S(c,25),9:S(c,26),10:S(c,27),11:S(c,50),12:S(c,51),13:S(c,52),14:`${S(c,94)}+${S(c,93)}`,15:`SUM(${c}6:${c}14)`,16:`${S(c,46)}+${S(c,48)}`,17:S(c,47),18:S(c,28),19:`${S(c,80)}+${S(c,79)}`,20:`SUM(${c}16:${c}19)`,21:S(c,53),22:S(c,54),23:`SUM(${c}21:${c}22)`};
 for(const [r,f] of Object.entries(bf))formula(sheets['Balance Sheet'],c+r,f);
 const checks={6:`${BS(c,15)}-${BS(c,20)}-${BS(c,23)}`,7:`${CF(c,23)}-${BS(c,6)}`,8:`${S(c,56)}-${S(c,17)}-${S(c,18)}-${S(c,19)}+${S(c,38)}+${S(c,39)}-${S(c,45)}`,9:`${BS(c,13)}-${S(c,15)}-${S(c,36)}+${S(c,37)}`,10:`${BS(c,21)}-${S(c,22)}-${IS(c,18)}+${S(c,40)}`,11:S(c,49)};
 for(const [r,f] of Object.entries(checks))formula(sheets.Checks,c+r,f);
 const summary={6:IS(c,6),7:IS(c,10),8:IS(c,18),9:CF(c,11),10:S(c,30),11:BS(c,6),12:S(c,56),13:S(c,55),14:S(c,49),15:`Checks!${c}6`};
 for(const [r,f] of Object.entries(summary))formula(sheets.Summary,c+r,f);
}
const ck=sheets.Checks;
['Balance sheet difference','Cash flow to balance-sheet cash','Debt roll-forward difference','Associate roll-forward difference','Parent equity roll-forward difference','Unfunded cash requirement'].forEach((l,i)=>label(ck,'C'+(6+i),l));
ck.getRange('E6:J10').setNumberFormat('0.00;(0.00);0.00');
ck.getRange('E6:J11').format.font.color='#172133';
ck.getRange('E6:J10').conditionalFormats.addCustom('ABS(E6)>0.000001',{fill:'#FDE8E8',font:{color:'#B42318',bold:true}});
ck.getRange('E11:J11').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0.000001,format:{fill:'#FDE8E8',font:{color:'#B42318',bold:true}}});
label(ck,'C14','Source verification');label(ck,'E14','ORIGINAL PDF VERIFIED');
label(ck,'C15','Assumption review');label(ck,'E15','DOCUMENTED ANALYST CASES');label(ck,'C16','Valuation release');label(ck,'E16','NOT PUBLISHED');
const sm=sheets.Summary;
['Revenue','EBIT','Parent profit after tax','Cash from operations','Cash capex','Closing cash','Closing debt','Unlevered FCFF','Unfunded requirement','Balance sheet difference'].forEach((l,i)=>label(sm,'C'+(6+i),l));
sm.getRange('E6:J15').format.font.color='#172133';sm.tabColor='#183553';a.tabColor='#61809E';
sm.getRange('C11:J12').format.fill='#EAF0F6';
sm.getRange('C18:E24').values=[['Period','Cash','Debt'],...cols.map(c=>[null,null,null])];
cols.forEach((c,i)=>{label(sm,'C'+(19+i),config.scenarios.base.periods[i].label);formula(sm,'D'+(19+i),c+'11');formula(sm,'E'+(19+i),c+'12');});
sm.getRange('D19:E24').setNumberFormat(numeric);sm.getRange('D19:E24').format.font.color='#172133';
label(sm,'C36','FY2026 and observed October benchmarks');sm.getRange('C36:J36').format.font.bold=true;
label(sm,'C38','FY2026 sales');formula(sm,'D38',`${actual('revenue_9m')}+'Income Statement'!E6`);label(sm,'F38','Mgmt target');formula(sm,'G38',actual('fy26_management_revenue_target'));label(sm,'H38','Gap');formula(sm,'I38','D38-G38');
label(sm,'C39','FY2026 profit before tax');formula(sm,'D39',`${actual('pbt_9m')}+'Income Statement'!E14`);label(sm,'F39','Mgmt target');formula(sm,'G39',actual('fy26_management_pbt_target'));label(sm,'H39','Gap');formula(sm,'I39','D39-G39');
label(sm,'C40','Implied November–December sales');formula(sm,'D40',`'Income Statement'!E6-(${actual('revenue_10m_rounded')}-${actual('revenue_9m')})`);
label(sm,'C41','Implied November–December PBT');formula(sm,'D41',`'Income Statement'!E14-(${actual('pbt_10m_rounded')}-${actual('pbt_9m')})`);
label(sm,'C42','FY2026 cash fixed-asset capex');formula(sm,'D42',`${actual('capex_9m')}+Schedules!E30`);
sm.getRange('D38:I42').setNumberFormat(numeric);sm.mergeCells('C44:J46');label(sm,'C44','October observations use rounded 10M issuer figures less exact9M statements. PBT is built at quarterly level; Nov–Dec PBT is implied, not reported. Management targets are benchmarks, not forced outcomes. The broader7,200bn investment budget has a different scope from cash fixed-asset capex.');sm.getRange('C44:J46').format.wrapText=true;
const chart=sm.charts.add('line',sm.getRange('C18:E24'));chart.title='Closing cash and debt (VND billion)';chart.setPosition('F18','K33');
chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=12;chart.legend={position:'top',textStyle:{typeface:'Arial',fontSize:10}};
chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};chart.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
chart.series.items[0].line={fill:'#1756C0',style:'solid',width:2};chart.series.items[1].line={fill:'#B7791F',style:'solid',width:2};
const start=sheets['Start Here'];start.tabColor='#8895A5';label(start,'C2','FPT three statement development model');
const instructions=[
 ['Status','Documented analyst scenarios. No investment valuation or recommendation.'],
 ['Scope','Q4 2026 stub followed by five annual forecasts, 2027 to 2031.'],
 ['Step 1','Read Summary. All amounts are VND billion.'],
 ['Step 2','Change Assumptions D5: 1 Base, 2 Downside, 3 Upside.'],
 ['Step 3','Edit blue case inputs; Active rows feed the same calculation build.'],
 ['Step 4','Review Schedules, Income Statement, Cash Flow and Balance Sheet.'],
 ['Step 5','Checks shows accounting differences and any unfunded cash requirement.'],
 ['Input colours','Blue inputs. Green cross-sheet links. Black same-sheet formulas.'],
 ['Opening data','Original HOSE PDF downloaded, hashed and visually reviewed.'],
 ['Model limits','Component working capital, debt maturity, deposit accrual and CIP schedules.'],
 ['Reset','Restore case values from configs/forecast_research.json.'],
 ['Research status','No target price. Analyst assumptions and their rationale are versioned in the register.'],
];
start.getRange('C6:D17').values=instructions;start.getRange('D6:D17').format.columnWidth=93;start.getRange('C6:D17').format.rowHeight=28;
for(const name of ['Income Statement','Cash Flow','Balance Sheet','Schedules']){
 const s=sheets[name];for(const r of (name==='Income Statement'?[10,16,18]:name==='Cash Flow'?[11,15,21,23]:name==='Balance Sheet'?[15,20,23]:[29,45,49,55,56])){s.getRange(`C${r}:J${r}`).format.fill='#EAF0F6';s.getRange(`C${r}:J${r}`).format.font.bold=true;}
}
// Reported-note history is a separate calibration reference, never a forecast override.
const reported=JSON.parse(await fs.readFile(path.join(root,'data/intake/q3_2026_reported_schedules.json'),'utf8'));
const evidence=wb.worksheets.add('Reported Notes');evidence.showGridLines=false;
evidence.getRange('C1:H160').format.font={name:'Arial',size:10,color:'#172133'};
evidence.getRange('C:C').format.columnWidth=54;
evidence.getRange('D:F').format.columnWidth=19;evidence.getRange('G:G').format.columnWidth=13;evidence.getRange('H:H').format.columnWidth=66;
evidence.getRange('C1:H160').format.rowHeight=22;evidence.getRange('D6:F160').setNumberFormat('#,##0.000;(#,##0.000);"-"');
label(evidence,'C2','FPT reported notes and calibration');evidence.getRange('C2:H2').format.font={name:'Arial',size:15,bold:true,color:'#172133'};
evidence.mergeCells('C3:H3');label(evidence,'C3','9M 2026 and 30 Sep 2026 balances. VND billion. Original HOSE PDF verified.');
evidence.mergeCells('C4:H4');label(evidence,'C4',reported.source_url);evidence.getRange('C4:H4').format.font={name:'Arial',size:9,color:'#1756C0'};
let er=6;const evidenceChecks=[];const factRefs={};
for(const group of reported.groups){
 const top=er;label(evidence,'C'+er,group.title);label(evidence,'D'+er,'Signed amount');label(evidence,'E'+er,'Reported control');label(evidence,'F'+er,'Difference');label(evidence,'G'+er,'Printed page');
 evidence.getRange(`C${er}:H${er}`).format={fill:'#183553',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:29,wrapText:true};er++;
 const first=er;
 for(const row of group.rows){label(evidence,'C'+er,row.label);value(evidence,'D'+er,row.value_vnd/1e9);label(evidence,'G'+er,group.printed_page);factRefs[group.id+'.'+row.id]='D'+er;er++;}
 label(evidence,'C'+er,'Reconstructed total and reported control');formula(evidence,'D'+er,`SUM(D${first}:D${er-1})`);value(evidence,'E'+er,group.reported_total_vnd/1e9);formula(evidence,'F'+er,`D${er}-E${er}`);
 evidence.getRange(`C${er}:H${er}`).format.fill='#EAF0F6';evidence.getRange(`C${er}:F${er}`).format.font.bold=true;evidenceChecks.push('F'+er);
 label(evidence,'H'+(top+1),group.note);evidence.getRange('H'+(top+1)).format.wrapText=true;evidence.getRange(`C${top+1}:H${top+1}`).format.rowHeight=62;er+=2;
}
label(evidence,'C'+er,'Associate cash dividends / equity income');formula(evidence,'D'+er,`-${factRefs['associates.dividends']}/${factRefs['associates.profit']}`);evidence.getRange('D'+er).setNumberFormat('0.00%');
evidence.mergeCells(`E${er}:H${er}`);label(evidence,'E'+er,'Historical receipt ratio. Distribution timing prevents automatic use as forecast payout.');er++;
evidence.freezePanes.freezeRows(5);evidence.tabColor='#61809E';
wb.recalculate();
for(const address of evidenceChecks){if(Math.abs(evidence.getRange(address).values[0][0])>1e-8)throw Error('Reported bridge failed '+address);}
const dividendRatio=evidence.getRange('D'+(er-1)).values[0][0];
if(Math.abs(dividendRatio-0.09727712771851216)>1e-12)throw Error('Historical dividend ratio mismatch');
for(let first=1;first<er;first+=27){const preview=await wb.render({sheetName:'Reported Notes',range:`C${first}:H${Math.min(er,first+26)}`,scale:1,format:'png'});await fs.writeFile(path.join(root,'outputs/previews/Reported_Notes_'+first+'.png'),new Uint8Array(await preview.arrayBuffer()));}

const noteRows=JSON.parse(await fs.readFile(path.join(root,'artifacts/reported_schedules/assumption_register.json'),'utf8')).filter(r=>r.scenario==='base'&&r.period==='Q4 2026E');
const notes=wb.worksheets.add('Assumption Notes');notes.showGridLines=false;notes.tabColor='#61809E';
notes.getRange('C1:J45').format.font={name:'Arial',size:10,color:'#172133'};notes.getRange('C:C').format.columnWidth=30;notes.getRange('D:D').format.columnWidth=24;notes.getRange('E:E').format.columnWidth=26;notes.getRange('F:J').format.columnWidth=18;
notes.mergeCells('C2:J2');label(notes,'C2','Analyst assumption rationale and source locators');notes.getRange('C2:J2').format.font={name:'Arial',size:15,bold:true,color:'#172133'};
notes.mergeCells('C3:J3');label(notes,'C3','Research cutoff:23 Nov2026. Values are selected in Assumptions. Future outcomes are not verified facts. No independent human sign-off.');notes.getRange('C3:J3').format.rowHeight=28;
notes.getRange('C5:E5').values=[['Driver','Classification','Source ID and printed page']];notes.mergeCells('F5:J5');label(notes,'F5','Rationale shared across cases; case values remain separately editable');notes.getRange('C5:J5').format={fill:'#183553',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:28};
for(const [idx,row] of noteRows.entries()){const r=6+idx;label(notes,'C'+r,row.driver.replaceAll('_',' '));label(notes,'D'+r,row.classification.replaceAll('_',' '));label(notes,'E'+r,row.source_ids);notes.mergeCells(`F${r}:J${r}`);label(notes,'F'+r,row.rationale);notes.getRange(`C${r}:J${r}`).format.wrapText=true;notes.getRange(`C${r}:J${r}`).format.rowHeight=Math.max(42,Math.ceil(row.rationale.length/110)*14+12);notes.getRange(`C${r}:J${r}`).format.verticalAlignment='center';if(idx%2===0)notes.getRange(`C${r}:J${r}`).format.fill='#F5F8FA';}
notes.freezePanes.freezeRows(5);
for(let first=1;first<44;first+=9){const image=await wb.render({sheetName:'Assumption Notes',range:`C${first}:J${Math.min(44,first+8)}`,scale:1,format:'png'});await fs.writeFile(path.join(root,'outputs/previews/Assumption_Notes_'+first+'.png'),new Uint8Array(await image.arrayBuffer()));}
const reconciliations=[];
for(const [index,name] of ['base','downside','upside'].entries()){
 a.getRange('D5').values=[[index+1]];wb.recalculate();
 for(let i=0;i<6;i++){
  const c=cols[i],r=expected.scenarios[name].periods[i];
  for(const [metric,sh,address,v] of [
   ['revenue','Income Statement',c+'6',r.income_statement.revenue],['group_pat','Income Statement',c+'16',r.income_statement.group_pat],
   ['parent_pat','Income Statement',c+'18',r.income_statement.parent_pat],['cfo','Cash Flow',c+'11',r.cash_flow.cfo],
   ['closing_cash','Balance Sheet',c+'6',r.balance_sheet.cash],['total_assets','Balance Sheet',c+'15',r.balance_sheet.total_assets],
   ['total_equity','Balance Sheet',c+'23',r.balance_sheet.total_equity],['funding_gap','Schedules',c+'49',r.funding.funding_gap],['deposit_interest_income','Income Statement',c+'11',r.income_statement.interest_income],['interest_receipts','Schedules',c+'64',r.cash_flow.interest_received],['trade_gross','Schedules',c+'66',r.component_schedules.trade_receivables],['allowance','Schedules',c+'71',r.component_schedules.receivable_allowance],['credit_loss','Schedules',c+'72',r.income_statement.credit_loss_charge],['long_prepaids','Schedules',c+'76',r.component_schedules.long_prepaids],['other_op_liabilities','Schedules',c+'79',r.component_schedules.operating_other_liabilities],['bank_principal','Schedules',c+'85',r.component_schedules.term_bank],['current_bank','Schedules',c+'88',r.component_schedules.current_bank],['closing_cip','Schedules',c+'93',r.component_schedules.cip],['interest_accrual','Schedules',c+'63',r.component_schedules.interest_accrued],['short_debt','Balance Sheet',c+'16',r.balance_sheet.short_term_debt],['long_debt','Balance Sheet',c+'17',r.balance_sheet.long_term_debt]]){
    const got=sheets[sh].getRange(address).values[0][0];
    if(typeof got!=='number'||Math.abs(got-v)>1e-6)throw new Error(`${name} ${metric} ${address}: ${got} != ${v}`);
    reconciliations.push({scenario:name,period:r.period,metric,excel:got,python:v,difference:got-v});
  }
 }
}
a.getRange('D5').values=[[1]];wb.recalculate();
const baseCFO=sheets['Cash Flow'].getRange('E11').values[0][0];
const dsoCell='E'+(driverRows.dso+1),savedDSO=a.getRange(dsoCell).values[0][0];
a.getRange(dsoCell).values=[[savedDSO+30]];wb.recalculate();
const stressedCFO=sheets['Cash Flow'].getRange('E11').values[0][0];
const firstPeriod=config.scenarios.base.periods[0];
const cashUse=firstPeriod.wc_revenue*30/365*(1-firstPeriod.allowance_ratio*firstPeriod.tax_rate);
if(Math.abs(baseCFO-stressedCFO-cashUse)>1e-6)throw Error('Excel working-capital perturbation failed');
a.getRange(dsoCell).values=[[savedDSO]];wb.recalculate();
const lastCash=sheets['Balance Sheet'].getRange('J6').values[0][0];
const capexCell='J'+(driverRows.capex_ratio+1),savedCapex=a.getRange(capexCell).values[0][0];
a.getRange(capexCell).values=[[savedCapex+.01]];wb.recalculate();
const changedCash=sheets['Balance Sheet'].getRange('J6').values[0][0];
if(Math.abs(lastCash-changedCash-config.scenarios.base.periods[5].annual_revenue*.01)>1e-6)throw Error('Excel later-period capex perturbation failed');
a.getRange(capexCell).values=[[savedCapex]];wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:1500})).ndjson);
await fs.writeFile(path.join(out,'excel_python_reconciliation.json'),JSON.stringify({checks:reconciliations.length,input_perturbations:2,results:reconciliations},null,2));
const ranges={'Start Here':'C2:J18',Summary:'C2:K47',Assumptions:'C2:J29',Opening:'C2:J52',Schedules:'C2:J29','Income Statement':'C2:J19','Cash Flow':'C2:J24','Balance Sheet':'C2:J24',Checks:'C2:J17'};
for(const [name,range] of Object.entries(ranges)){
 const image=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(root,'outputs/previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await image.arrayBuffer()));
}
for(const [name,range] of [['Assumptions','C30:J62'],['Assumptions','C63:J95'],['Assumptions','C96:J127'],['Assumptions','C128:J163'],['Schedules','C30:J56'],['Schedules','C60:J77'],['Schedules','C78:J95'],['Opening','C53:J83']]){
 const image=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(root,'outputs/previews',name+'_'+range.split(':')[0]+'.png'),new Uint8Array(await image.arrayBuffer()));
}
// Extend the existing single forecast build with forward year-end DCF/SOTP.
const valuationConfig=JSON.parse(await fs.readFile(path.join(root,'configs/valuation_clock_c.json'),'utf8'));
const golden=JSON.parse(await fs.readFile(path.join(root,'outputs/p1_final/clock_c_valuation.json'),'utf8'));
const vi=sheets['Valuation Inputs'],dc=sheets.DCF,vo=sheets.Valuation;
const commonRows={},caseRows={};let vr=8;
for(const [key,amount] of Object.entries(valuationConfig.common)){
 if(typeof amount!=='number')continue;
 commonRows[key]=vr;label(vi,'C'+vr,key.replaceAll('_',' '));value(vi,'D'+vr,amount);
 vi.getRange('D'+vr).setNumberFormat(key.includes('shares')?numeric:'0.00%');vr++;
}
vr=23;
for(const key of Object.keys(valuationConfig.scenarios.base)){
 caseRows[key]=vr;label(vi,'C'+vr,key.replaceAll('_',' '));
 for(const [j,name] of ['base','downside','upside'].entries()){label(vi,'C'+(vr+j+1),name);value(vi,'D'+(vr+j+1),valuationConfig.scenarios[name][key]);}
 formula(vi,'D'+vr,`IF(CHOOSE(Assumptions!$D$5,ISBLANK(D${vr+1}),ISBLANK(D${vr+2}),ISBLANK(D${vr+3})),"Missing case input",CHOOSE(Assumptions!$D$5,D${vr+1},D${vr+2},D${vr+3}))`);
 vi.getRange(`D${vr}:D${vr+3}`).setNumberFormat(/growth|roic|adjustment/.test(key)?'0.00%':'0.00');
 vi.getRange(`C${vr}:D${vr}`).format.fill='#EAF0F6';vr+=5;
}
const V=k=>`'Valuation Inputs'!$D$${commonRows[k]}`,K=k=>`'Valuation Inputs'!$D$${caseRows[k]}`;
label(vi,'F8','Cost of equity');formula(vi,'G8',`${V('risk_free_anchor')}+${K('beta')}*${V('total_equity_premium')}`);
label(vi,'F9','Calculated WACC');formula(vi,'G9',`G8*(1-${V('target_debt_weight')})+${V('cost_of_debt')}*(1-${V('debt_tax_rate')})*${V('target_debt_weight')}+${K('wacc_adjustment')}`);
label(vi,'F10','WACC used');formula(vi,'G10','G9');label(vi,'F11','Terminal growth used');formula(vi,'G11',K('terminal_growth'));
vi.getRange('G8:G11').setNumberFormat('0.00%');
label(vi,'F13','WACC and growth used are the actual Data Table inputs.');label(vi,'F14','Restore G10 = G9 and G11 = active terminal growth after manual edits.');
label(vi,'F16','Discount assumptions are analyst judgements, not verified market closes.');
for(const [i,[key,text]] of Object.entries(valuationConfig.input_policy).entries()){
 const r=66+i*3;label(vi,'C'+r,key.replaceAll('_',' '));vi.mergeCells(`D${r}:J${r+2}`);label(vi,'D'+r,text);vi.getRange(`D${r}:J${r+2}`).format.wrapText=true;
}
for(const [i,source] of valuationConfig.sources.entries()){const r=106+i*3;label(vi,'C'+r,source.id);vi.mergeCells(`D${r}:J${r+1}`);label(vi,'D'+r,source.url);vi.getRange(`D${r}:J${r+1}`).format.wrapText=true;label(vi,'D'+(r+2),source.status);}
const dl={6:'EBIT',7:'Explicit cash tax rate',8:'NOPAT',9:'Depreciation and amortisation',10:'Capital expenditure',11:'Change in operating working capital',12:'Change in operating cash reserve',13:'FCFF including cash reserve',14:'Discount time in years',15:'Discount factor',16:'Present value of FCFF'};
for(const [r,t] of Object.entries(dl))label(dc,'C'+r,t);
for(let i=1;i<6;i++){
 const c=cols[i],prev=cols[i-1];formula(dc,c+'6',IS(c,10));formula(dc,c+'7',A(c,'tax_rate'));
 formula(dc,c+'8',`${c}6*(1-${c}7)`);formula(dc,c+'9',S(c,31));formula(dc,c+'10',S(c,30));formula(dc,c+'11',S(c,29));
 formula(dc,c+'12',`${S(c,42)}-${S(prev,42)}`);formula(dc,c+'13',`${c}8+${c}9-${c}10-${c}11-${c}12`);
 value(dc,c+'14',i-.5);formula(dc,c+'15',`(1+'Valuation Inputs'!$G$10)^(-${c}14)`);formula(dc,c+'16',`${c}13*${c}15`);
}
label(dc,'E13','In closing BS');
const dr={19:'2032 normalised NOPAT',20:'2032 reinvestment',21:'2032 FCFF',22:'Terminal value at 2031 mid-year',23:'Present value of terminal',24:'Present value of explicit FCFF',25:'Operating enterprise value',27:'2027 associate earnings',28:'Associate equity value',29:'Cash less operating reserve',30:'Deposits accrued interest and other investments',31:'Debt including leases',32:'NCI valuation proxy',33:'Parent equity value',34:'Diluted million shares',35:'Forward fair value VND per share',36:'2027 P E cross check VND per share',37:'Margin of safety price VND',38:'Terminal share of EV'};
for(const [r,t] of Object.entries(dr))label(dc,'C'+r,t);
const f={19:`J6*(1+'Valuation Inputs'!G11)*(1-${V('terminal_tax')})`,20:`D19*'Valuation Inputs'!G11/${K('terminal_roic')}`,21:'D19-D20',22:`D21/('Valuation Inputs'!G10-'Valuation Inputs'!G11)`,23:`D22/(1+'Valuation Inputs'!G10)^J14`,24:'SUM(F16:J16)',25:'SUM(D23:D24)',27:IS('F',13),28:`D27*${K('associate_pe')}`,29:`${BS('E',6)}-${S('E',42)}`,30:`${S('E',61)}+${S('E',63)}+${S('E',95)}`,31:`${BS('E',16)}+${BS('E',17)}`,32:`${BS('E',22)}*${K('nci_book_multiple')}`,33:'D25+D28+D29+D30-D31-D32',34:`${V('issued_shares_million')}*(1+${V('incremental_dilution')})`,35:'D33/D34*1000',36:`${IS('F',18)}/D34*1000*${K('parent_pe')}`,37:`D35*(1-${V('margin_of_safety')})`,38:'D23/D25'};
for(const [r,text] of Object.entries(f))formula(dc,'D'+r,text);
dc.getRange('D19:D37').setNumberFormat(numeric);dc.getRange('D38').setNumberFormat('0.0%');dc.getRange('F7:J7').setNumberFormat('0.0%');dc.getRange('F14:J15').setNumberFormat('0.0000');
const or={7:['Forward fair value VND per share','DCF!D35'],8:['2027 P E cross check VND','DCF!D36'],9:['Margin of safety price VND','DCF!D37'],11:['Operating enterprise value VND bn','DCF!D25'],12:['Associate equity value','DCF!D28'],13:['Cash less operating reserve','DCF!D29'],14:['Deposits and other investments','DCF!D30'],15:['Debt including leases','-DCF!D31'],16:['NCI valuation proxy','-DCF!D32'],17:['Parent equity value','DCF!D33'],18:['Diluted million shares','DCF!D34'],20:['WACC',"'Valuation Inputs'!G10"],21:['Terminal growth',"'Valuation Inputs'!G11"],22:['Terminal share of EV','DCF!D38']};
for(const [r,[name,text]] of Object.entries(or)){label(vo,'C'+r,name);formula(vo,'D'+r,text);}
vo.getRange('D7:D18').setNumberFormat(numeric);vo.getRange('D20:D22').setNumberFormat('0.00%');vo.getRange('C7:D9').format.font={name:'Arial',size:14,bold:true,color:'#183553'};
label(vo,'C24','Market upside unavailable: no verified same-cutoff closing quote.');label(vo,'C25','Forward value at 31 Dec 2026E. Q4 FCFF is excluded after Q4 cash enters the equity bridge.');
label(vo,'C27','Watchlist: cash conversion and financing must support any entry decision.');
label(vo,'C29','Sensitivity is on Valuation Inputs. Change Assumptions D5 for one live case.');
label(vo,'C31','NCI uses a book multiple proxy. Associate P E is an analyst assumption.');
// Two actual inputs, one native two-variable table linked to the owning DCF.
label(vi,'F20','Fair value sensitivity VND. Rows WACC, columns terminal g.');formula(vi,'F22','DCF!D35');
for(let j=0;j<5;j++)value(vi,['G','H','I','J','K'][j]+'22',[.02,.025,.03,.035,.04][j]);
for(let i=0;i<5;i++)formula(vi,'F'+(23+i),`G9+${[-.02,-.01,0,.01,.02][i]}`);
vi.dataTables.add('F22:K27',{rowInput:'G11',columnInput:'G10'});
vi.getRange('G22:K22').setNumberFormat('0.0%');vi.getRange('F23:F27').setNumberFormat('0.00%');vi.getRange('G23:K27').setNumberFormat('#,##0');
const valuationChecks=[];
label(dc,'C30','Deposits and other investments');
vo.getRange('E5:J5').clear({applyTo:'all'});vi.getRange('E5:J5').clear({applyTo:'all'});
vo.getRange('D7:D22').format.font.color='#183553';
for(const [i,name] of ['base','downside','upside'].entries()){
 value(a,'D5',i+1);wb.recalculate();
 for(const [cell,key] of [['D35','fair_value_vnd'],['D25','operating_ev'],['D28','associate_value'],['D33','equity_value'],['D36','pe_crosscheck_vnd']]){
  const got=dc.getRange(cell).values[0][0],want=golden.cases[name][key];
  if(typeof got!=='number'||Math.abs(got-want)>1e-6)throw Error(`DCF ${name} ${key}: ${got} != ${want}`);
  valuationChecks.push({case:name,key,excel:got,python:want});
 }
 const grid=vi.getRange('G23:K27').values;
 for(let r=0;r<5;r++)for(let col=0;col<5;col++)if(Math.abs(grid[r][col]-golden.cases[name].sensitivity[r*5+col].fair_value_vnd)>1e-6)throw Error('Native sensitivity mismatch '+name+' '+r+' '+col);
}
value(a,'D5',1);wb.recalculate();
const originalPrice=dc.getRange('D35').values[0][0];value(vi,'G10',golden.cases.base.wacc+.01);wb.recalculate();
if(!(dc.getRange('D35').values[0][0]<originalPrice))throw Error('WACC edit does not affect value');
formula(vi,'G10','G9');wb.recalculate();
start.getRange('D6').values=[['Clock C forward research valuation. Open Valuation, then Summary.']];
start.getRange('D17').values=[['Cutoff 23 Nov 2026. Forward value at 31 Dec 2026E. No same-cutoff market return.']];
label(start,'C2','FPT equity research and valuation');
console.log((await wb.inspect({kind:'table',range:'Valuation!C7:D22',include:'values,formulas',tableMaxRows:16,tableMaxCols:2,maxChars:1800})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
for(const [name,range,suffix] of [['Valuation','C2:J32',''],['DCF','C2:J38',''],['Valuation Inputs','C2:K27',''],['Valuation Inputs','C28:D58','cases']]){
 const preview=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(root,'outputs/previews',name.replaceAll(' ','_')+suffix+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
await fs.writeFile(path.join(root,'outputs/p1_final/excel_valuation_reconciliation.json'),JSON.stringify({comparisons:valuationChecks,native_sensitivity_points:75,wacc_perturbation_pass:true},null,2));
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'outputs/p1_final/FPT_Research_Model_Clock_C.xlsx'));
console.log(JSON.stringify({workbook:'FPT_Three_Statement_Development.xlsx',scenario_reconciliations:reconciliations.length}));
