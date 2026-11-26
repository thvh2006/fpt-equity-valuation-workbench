"""Economic tests beyond cross-engine numerical agreement."""
import json
from copy import deepcopy
from pathlib import Path
from equity_valuation.clock_c import value_case,reverse_terminal_growth
from equity_valuation.three_statement import run_forecast
ROOT=Path(__file__).resolve().parents[1]

def inputs():
    o=json.loads((ROOT/'data/intake/clock_c_opening_pending.json').read_text())
    fc=json.loads((ROOT/'configs/forecast_research.json').read_text())
    vc=json.loads((ROOT/'configs/valuation_clock_c.json').read_text())
    return run_forecast(o,fc['scenarios']['base']),vc['scenarios']['base'],vc['common']

def test_clock_c_discount_timing_and_no_stub_double_count():
    f,c,a=inputs();v=value_case(f,c,a)
    assert [r['timing'] for r in v['periods']]==[.5,1.5,2.5,3.5,4.5]
    f['periods'][0]['fcff']+=100000
    assert value_case(f,c,a)['fair_value_vnd']==v['fair_value_vnd']
    assert abs(v['terminal_pv']-v['terminal_fcff']/(v['wacc']-v['terminal_growth'])/(1+v['wacc'])**4.5)<1e-8

def test_clock_c_cash_floor_investment_and_financial_scope():
    f,c,a=inputs();v=value_case(f,c,a)
    assert abs(v['periods'][0]['fcff']-(f['periods'][1]['fcff']-f['periods'][1]['funding']['cash_floor']+f['periods'][0]['funding']['cash_floor']))<1e-8
    f['periods'][0]['balance_sheet']['associates']+=10000
    assert value_case(f,c,a)['fair_value_vnd']==v['fair_value_vnd']
    f['periods'][1]['income_statement']['associate_profit']+=100
    changed=value_case(f,c,a)
    assert abs(changed['equity_value']-v['equity_value']-100*c['associate_pe'])<1e-7

def test_clock_c_wacc_growth_roic_and_dilution_direction():
    f,c,a=inputs();v=value_case(f,c,a)
    assert value_case(f,c,a,wacc_override=v['wacc']+.01)['fair_value_vnd']<v['fair_value_vnd']
    assert value_case(f,c,a,growth_override=.04)['fair_value_vnd']>v['fair_value_vnd']
    c['terminal_roic']+=.02
    assert value_case(f,c,a)['fair_value_vnd']>v['fair_value_vnd']
    c['terminal_roic']-=.02;a['incremental_dilution']+=.01
    assert value_case(f,c,a)['fair_value_vnd']<v['fair_value_vnd']

def test_clock_c_reverse_solver_recovery_and_outside_range():
    f,c,a=inputs();v=value_case(f,c,a)
    r=reverse_terminal_growth(f,c,a,v['fair_value_vnd'])
    assert r['status']=='SOLVED' and abs(r['terminal_growth']-.03)<1e-9 and abs(r['residual_vnd'])<1e-6
    assert reverse_terminal_growth(f,c,a,1)['status']=='OUTSIDE_NONNEGATIVE_GROWTH_RANGE'

def test_clock_c_invalid_terminal_and_unreviewed_gate():
    f,c,a=inputs()
    for change in ['growth','source']:
        bad=deepcopy(f);case=deepcopy(c)
        if change=='growth':case['terminal_growth']=.2
        else:bad['source_intake_status']='BLOCKED'
        try:value_case(bad,case,a)
        except ValueError:pass
        else:raise AssertionError('Invalid valuation accepted')

def test_clock_c_cash_and_debt_bridge_marginal_effect():
    f,c,a=inputs();v=value_case(f,c,a)
    f['periods'][0]['balance_sheet']['cash']+=100
    assert abs(value_case(f,c,a)['equity_value']-v['equity_value']-100)<1e-7
    f['periods'][0]['balance_sheet']['short_term_debt']+=100
    assert abs(value_case(f,c,a)['equity_value']-v['equity_value'])<1e-7

def test_clock_c_nci_proxy_and_no_market_upside():
    f,c,a=inputs();v=value_case(f,c,a)
    c['nci_book_multiple']+=1
    assert abs(v['equity_value']-value_case(f,c,a)['equity_value']-f['periods'][0]['balance_sheet']['nci_equity'])<1e-7
    assert v['upside'] is None and v['market_price_vnd'] is None
