import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {computeScenario} from '../dashboard/research-model.mjs';
import {valueForward} from '../dashboard/valuation-model.mjs';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const opening=JSON.parse(await fs.readFile(path.join(root,'data/intake/clock_c_opening_pending.json'),'utf8'));
const config=JSON.parse(await fs.readFile(path.join(root,'configs/forecast_research.json'),'utf8'));
const results=JSON.parse(await fs.readFile(path.join(root,'artifacts/three_statement_development/results.json'),'utf8'));
const valuationConfig=JSON.parse(await fs.readFile(path.join(root,'configs/valuation_clock_c.json'),'utf8'));
const valuationGolden=JSON.parse(await fs.readFile(path.join(root,'outputs/p1_final/clock_c_valuation.json'),'utf8'));
let valuationPoints=0;
for(const name of Object.keys(config.scenarios)){
 const f=computeScenario(opening,config.scenarios[name]),v=valueForward(f,valuationConfig.scenarios[name],valuationConfig.common),want=valuationGolden.cases[name];
 for(const [k,n] of Object.entries(v))if(typeof n==='number'){if(Math.abs(n-want[k])>1e-6)throw Error('Valuation JS mismatch '+name+' '+k);valuationPoints++;}
 for(const point of want.sensitivity){const x=valueForward(f,valuationConfig.scenarios[name],valuationConfig.common,point.wacc-want.wacc,point.g-want.terminal_growth);if(Math.abs(x.fair_value_vnd-point.fair_value_vnd)>1e-6)throw Error('JS sensitivity mismatch');valuationPoints++;}
}
let checked=0;
function compare(got,want,trail=''){
 if(typeof want==='number'){if(!Number.isFinite(got)||Math.abs(got-want)>1e-6)throw Error(`${trail}: ${got} != ${want}`);checked++;}
 else if(want&&typeof want==='object')for(const [k,v] of Object.entries(want))compare(got?.[k],v,trail+'.'+k);
}
for(const name of Object.keys(config.scenarios))compare(computeScenario(opening,config.scenarios[name]).periods,results.scenarios[name].periods,name);
// Counterfactual: source changes must flow through the same browser model.
const stress=structuredClone(config.scenarios.base);stress.facility_limit=0;stress.periods[0].dso=700;
if(computeScenario(opening,stress).periods[0].funding.status!=='INFEASIBLE')throw Error('Browser liquidity failure not exposed');
let html=await fs.readFile(path.join(root,'dashboard/template.html'),'utf8');
const model=(await fs.readFile(path.join(root,'dashboard/research-model.mjs'),'utf8')).replace('export function','function')+'\n'+(await fs.readFile(path.join(root,'dashboard/valuation-model.mjs'),'utf8')).replace('export function','function');
const data=JSON.stringify({opening,config,valuationConfig,run_id:valuationGolden.run_id}).replaceAll('<','\\u003c');
html=html.replace('/* MODEL_SOURCE */',model).replace('/* MODEL_DATA */',`const DATA=${data};`);
const reported=JSON.parse(await fs.readFile(path.join(root,'data/intake/q3_2026_reported_schedules.json'),'utf8'));
const analysis=JSON.parse(await fs.readFile(path.join(root,'artifacts/reported_schedules/analysis.json'),'utf8'));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const number=v=>new Intl.NumberFormat('en-US',{minimumFractionDigits:3,maximumFractionDigits:3}).format(v/1e9);
const section=`<section class="panel"><h3>Reported notes: historical calibration</h3><p>9M 2026 flows and 30 Sep 2026 balances. VND billion. Forward driver choices and their rationale are recorded in the assumption register. Original HOSE PDF downloaded, hashed and visually reviewed.</p><p>Associate dividends received / equity-accounted profit: <strong>${(analysis.metrics.associate_received_dividends_to_profit*100).toFixed(2)}%</strong>. This is a historical receipt ratio, affected by distribution timing.</p>${reported.groups.map(g=>`<details><summary style="cursor:pointer;padding:12px 0;font-weight:600">${escape(g.title)} · printed p. ${escape(g.printed_page)}</summary><div class="table-wrap"><table><thead><tr><th>Reported component</th><th>Signed VND bn</th></tr></thead><tbody>${g.rows.map(r=>`<tr><td>${escape(r.label)}</td><td>${number(r.value_vnd)}</td></tr>`).join('')}<tr class="total"><td>Reported control total</td><td>${number(g.reported_total_vnd)}</td></tr><tr><td>Arithmetic difference</td><td>${number(g.rows.reduce((s,r)=>s+r.value_vnd,0)-g.reported_total_vnd)}</td></tr></tbody></table></div><p>${escape(g.note)}</p></details>`).join('')}<p><a href="${escape(reported.source_url)}" target="_blank" rel="noopener">Primary filing</a></p></section>`;
const register=JSON.parse(await fs.readFile(path.join(root,'artifacts/reported_schedules/assumption_register.json'),'utf8'));
const rationales=register.filter(r=>r.scenario==='base'&&r.period==='Q4 2026E');
const assumptionsSection=`<section class="panel"><h3>Assumption rationale and evidence</h3><p>All ${register.length} scenario-period inputs have a classification and rationale. The shared rationale below explains the policy; the Assumptions tab shows the selected case values. Source facts are historical. Future assumptions are analyst judgements.</p><details><summary style="cursor:pointer;padding:12px 0;font-weight:600">Read all ${rationales.length} driver rationales</summary><div class="table-wrap"><table><thead><tr><th>Driver</th><th>Classification</th><th>Rationale and source locator</th></tr></thead><tbody>${rationales.map(r=>`<tr><td>${escape(r.driver.replaceAll('_',' '))}</td><td>${escape(r.classification)}</td><td style="white-space:normal;min-width:360px;text-align:left">${escape(r.rationale)}<br><small>${escape(r.source_ids)}</small></td></tr>`).join('')}</tbody></table></div></details></section>`;
html=html.replace('<footer>',section+assumptionsSection+'<footer>');
// Add valuation to the same browser calculation and controls, never a second forecast.
html=html.replace('<title>FPT Statement Workbench</title>','<title>FPT Research and Valuation</title>');
html=html.replace('FPT Corporation · Pre-valuation research','FPT Corporation · Clock C research');
html=html.replace('Three statements. One set of assumptions.','FPT equity research and valuation');
html=html.replace('No target price is calculated.','Forward valuation updates with these controls.');
html=html.replace('<strong>Not published</strong>','<strong>Forward 31 Dec 2026E value</strong>');
html=html.replace('No valuation.','Forward valuation.');
html=html.replace('<button class="secondary" id="reset">',`<div class="control"><label for="wacc">WACC adjustment <output id="waccValue">0.0 pp</output></label><input id="wacc" type="range" min="-2" max="3" step="0.25" value="0"></div><div class="control"><label for="growth">Terminal g adjustment <output id="growthValue">0.0 pp</output></label><input id="growth" type="range" min="-1" max="1" step="0.25" value="0"></div><button class="secondary" id="reset">`);
const valuationSection=`<section class="panel" id="valuation"><h3>Forward valuation at 31 December 2026E</h3><p>Information cutoff 23 Nov 2026. Q4 forecast closing balances feed the equity bridge. WACC, multiples, NCI and terminal economics are analyst assumptions. Market upside is unavailable without a verified same-cutoff quote.</p><div class="metrics"><div class="metric"><label>Forward fair value · VND/share</label><strong id="fairValue"></strong><small id="waccNote"></small></div><div class="metric"><label>20% margin of safety price · VND</label><strong id="entryValue"></strong><small>Conditional research threshold, not an order</small></div><div class="metric"><label>Terminal value / operating EV</label><strong id="terminalShare"></strong><small>Stable tax20%; reinvestment = NOPAT × g / ROIC</small></div></div><div id="valueBridge" class="table-wrap"></div><p>Associate book value, future associate dividends and CIP are not added again. NCI is forecast book value times a case multiple. P/E is a separate analyst cross-check, never blended with DCF.</p><details><summary>WACC and terminal growth sensitivity</summary><div id="sensitivity" class="table-wrap"></div></details></section>`;
html=html.replace('<div class="metrics"><div class="metric"><label>2031',valuationSection+'<div class="metrics"><div class="metric"><label>2031');
const renderValuation=`function showValuation(){
 const v=valueForward(result,DATA.valuationConfig.scenarios[$('scenario').value],DATA.valuationConfig.common,Number($('wacc').value)/100,Number($('growth').value)/100);
 $('waccValue').textContent=format(Number($('wacc').value),2)+' pp';$('growthValue').textContent=format(Number($('growth').value),2)+' pp';
 $('fairValue').textContent=format(v.fair_value_vnd,0);$('entryValue').textContent=format(v.margin_of_safety_price_vnd,0);$('terminalShare').textContent=format(v.terminal_share_of_ev*100)+'%';$('waccNote').textContent='WACC '+format(v.wacc*100,2)+'%; terminal g '+format(v.terminal_growth*100,2)+'%';
 const rows=[['Operating EV',v.operating_ev],['Associates',v.associate_value],['Cash less operating reserve',v.cash_net_of_reserve],['Deposits and other investments',v.investments],['Debt',-v.debt],['NCI proxy',-v.nci_value],['Parent equity',v.equity_value],['2027 P/E cross-check VND/share',v.pe_crosscheck_vnd]];
 $('valueBridge').innerHTML='<table><thead><tr><th>Bridge component</th><th>VND bn except per share</th></tr></thead><tbody>'+rows.map(r=>'<tr><td>'+r[0]+'</td><td>'+format(r[1])+'</td></tr>').join('')+'</tbody></table>';
 const gs=[.02,.025,.03,.035,.04],shifts=[-.02,-.01,0,.01,.02];
 $('sensitivity').innerHTML='<table><thead><tr><th>WACC / g</th>'+gs.map(g=>'<th>'+format(g*100,1)+'%</th>').join('')+'</tr></thead><tbody>'+shifts.map(s=>'<tr><td>'+format((v.wacc+s)*100,2)+'%</td>'+gs.map(g=>'<td>'+format(valueForward(result,DATA.valuationConfig.scenarios[$('scenario').value],DATA.valuationConfig.common,Number($('wacc').value)/100+s,g-DATA.valuationConfig.scenarios[$('scenario').value].terminal_growth).fair_value_vnd,0)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
}
`;
html=html.replace('function update(){',renderValuation+'\nfunction update(){');
html=html.replace('drawChart();table();','drawChart();table();showValuation();');
html=html.replace("'facility','refinance','collection']","'facility','refinance','collection','wacc','growth']");
html=html.replace("'capex','rate','refinance','collection']","'capex','rate','refinance','collection','wacc','growth']");
html=html.replace("exported_at:new Date().toISOString(),status:'ANALYST_CASE_PREVALUATION'","exported_at:new Date().toISOString(),status:'FORWARD_RESEARCH_VALUATION',valuation:valueForward(result,DATA.valuationConfig.scenarios[$('scenario').value],DATA.valuationConfig.common,Number($('wacc').value)/100,Number($('growth').value)/100)");
html=html.replace("result=null;$('error')","result=null;$('fairValue').textContent='Unavailable';$('entryValue').textContent='Unavailable';$('terminalShare').textContent='Unavailable';$('valueBridge').innerHTML='';$('sensitivity').innerHTML='';$('error')");
const policies=`<section class="panel"><h3>Valuation assumptions and source register</h3>${Object.entries(valuationConfig.input_policy).map(([key,text])=>'<p><strong>'+escape(key.replaceAll('_',' '))+'</strong>. '+escape(text)+'</p>').join('')}<ul>${valuationConfig.sources.map(s=>'<li><a href="'+escape(s.url)+'">'+escape(s.id)+'</a> ('+s.published+'). '+escape(s.status)+'</li>').join('')}</ul></section>`;
html=html.replace('<footer>',policies+'<footer>');


const out=path.join(root,'outputs/fpt_development');await fs.mkdir(out,{recursive:true});
await fs.writeFile(path.join(out,'FPT_Three_Statement_Dashboard.html'),html);
await fs.writeFile(path.join(root,'outputs/p1_final/FPT_Research_Dashboard_Clock_C.html'),html);
await fs.writeFile(path.join(root,'outputs/p1_final/javascript_valuation_reconciliation.json'),JSON.stringify({numeric_comparisons:valuationPoints,all_pass:true},null,2));
await fs.writeFile(path.join(out,'dashboard_reconciliation.json'),JSON.stringify({numeric_comparisons:checked,tolerance:1e-6,all_pass:true,liquidity_failure_case_pass:true,run_id:results.run_id},null,2));
console.log(JSON.stringify({html:'FPT_Three_Statement_Dashboard.html',numeric_comparisons:checked,all_pass:true}));
