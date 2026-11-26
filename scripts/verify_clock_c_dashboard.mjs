// Execute the saved HTML application with a minimal DOM to exercise controls.
// This tests application behaviour, not browser layout or a browser session.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html=await fs.readFile(path.join(root,'outputs/p1_final/FPT_Research_Dashboard_Clock_C.html'),'utf8');
const golden=JSON.parse(await fs.readFile(path.join(root,'outputs/p1_final/clock_c_valuation.json'),'utf8'));
const elements={};
for(const match of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)){
 const id=match[1],tag=match[0],handlers={};
 let inputValue=id==='scenario'?'base':(tag.match(/\bvalue="([^"]*)"/)?.[1]??'');
 elements[id]={get value(){return inputValue;},set value(v){inputValue=String(v);},textContent:'',innerHTML:'',hidden:false,disabled:false,
  addEventListener:(name,fn)=>handlers[name]=fn,trigger:name=>handlers[name]?.()};
}
const tabs=[...html.matchAll(/<button role="tab"[^>]*data-view="([^"]+)"/g)].map(m=>({dataset:{view:m[1]},attributes:{},addEventListener(n,f){this[n]=f;},setAttribute(k,v){this.attributes[k]=v;}}));
const document={getElementById:id=>{if(!elements[id])throw Error('Missing DOM id '+id);return elements[id];},querySelectorAll:()=>tabs};
const context=vm.createContext({document,Intl,structuredClone,console,setTimeout,clearTimeout,Blob,URL});
for(const script of html.matchAll(/<script>([\s\S]*?)<\/script>/g))vm.runInContext(script[1].replace("$('error').textContent=e.message;","$('error').textContent=e.stack;"),context,{timeout:5000});
let checks=0;
function assert(ok,msg){if(!ok)throw Error(msg);checks++;}
function price(){return Number(elements.fairValue.textContent.replaceAll(',',''));}
assert(Math.abs(price()-golden.cases.base.fair_value_vnd)<.51,'Initial base fair value: '+elements.fairValue.textContent+'; '+elements.error.textContent+'; controls '+JSON.stringify(Object.fromEntries(['scenario','dso','capex','rate','facility','refinance','collection','wacc','growth'].map(k=>[k,elements[k].value]))));
for(const name of ['downside','upside','base']){
 elements.scenario.value=name;elements.scenario.trigger('input');
 assert(Math.abs(price()-golden.cases[name].fair_value_vnd)<.51,'Case control '+name);
 assert(elements.error.hidden,'Unexpected application error');
}
const initial=price();elements.wacc.value='1';elements.wacc.trigger('input');assert(price()<initial,'WACC control');
elements.reset.trigger('click');assert(price()===initial,'Reset restores base and WACC');
elements.dso.value='30';elements.dso.trigger('input');assert(price()<initial,'DSO reaches valuation');
elements.reset.trigger('click');
for(const tab of tabs){tab.click();assert(elements.tableContent.innerHTML.length>50,'Tab '+tab.dataset.view);}
elements.facility.value='';elements.facility.trigger('input');assert(!elements.error.hidden,'Missing facility rejected');
assert(elements.fairValue.textContent==='Unavailable','Invalid input clears stale valuation');
elements.reset.trigger('click');assert(elements.error.hidden&&price()===initial,'Error recovery');
assert(elements.sensitivity.innerHTML.includes('<table>'),'Sensitivity renders');
const receipt={status:'PASS',method:'saved HTML script execution in Node VM with minimal DOM; not browser visual verification',checks};
await fs.writeFile(path.join(root,'outputs/p1_final/dashboard_control_checks.json'),JSON.stringify(receipt,null,2));
console.log(receipt);
