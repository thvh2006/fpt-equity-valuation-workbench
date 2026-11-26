#!/usr/bin/env python3
"""Build forward Clock C valuation, sensitivities and hypothetical reverse DCF."""
import json, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from equity_valuation.clock_c import value_case, sensitivity, reverse_terminal_growth
from equity_valuation.three_statement import run_forecast

def main():
    inputs=[ROOT/p for p in ['configs/forecast_research.json','configs/valuation_clock_c.json','data/intake/clock_c_opening_pending.json']]
    fc,vc,opening=[json.loads(p.read_text()) for p in inputs]
    cases={}
    for name,config in fc['scenarios'].items():
        f=run_forecast(opening,config)
        c=vc['scenarios'][name]
        v=value_case(f,c,vc['common'])
        v['sensitivity']=sensitivity(f,c,vc['common'])
        v['reverse_dcf_hypothetical']=[reverse_terminal_growth(f,c,vc['common'],p) for p in [60000,80000,100000]]
        cases[name]=v
    payload=dict(status='FORWARD_RESEARCH_VALUATION',version=vc['version'],
                 run_id=hashlib.sha256(b''.join(p.read_bytes() for p in inputs)).hexdigest()[:16],
                 information_cutoff=vc['information_cutoff'],valuation_date=vc['common']['valuation_date'],
                 unit='VND billion except per-share VND and million shares',
                 decision='WATCHLIST: require verified entry quote and cash-conversion recovery before adding exposure',
                 cases=cases)
    out=ROOT/'outputs/p1_final';out.mkdir(parents=True,exist_ok=True)
    (out/'clock_c_valuation.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    print(json.dumps({name:{k:v[k] for k in ['fair_value_vnd','wacc','terminal_share_of_ev','financing_status']} for name,v in cases.items()},indent=2))

if __name__=='__main__':main()
