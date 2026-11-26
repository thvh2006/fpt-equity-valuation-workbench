"""Economic checks on reported bridges, including noncash classification."""
from copy import deepcopy
import json
from pathlib import Path
from equity_valuation.reported_schedules import analyse_reported_schedules

def source():
    return json.loads((Path(__file__).resolve().parents[1] / 'data/intake/q3_2026_reported_schedules.json').read_text())

def test_reported_bridges_reconcile_to_integer_vnd():
    result = analyse_reported_schedules(source())
    assert len(result['checks']) == 10
    assert result['all_accounting_bridges_pass']

def test_ignoring_ftel_perimeter_causes_debt_bridge_failure():
    p = source()
    group = next(g for g in p['groups'] if g['id'] == 'short_debt')
    next(r for r in group['rows'] if r['id'] == 'perimeter')['value_vnd'] = 0
    result = analyse_reported_schedules(p)
    c = next(c for c in result['checks'] if c['schedule'] == 'short_debt')
    assert c['difference_vnd'] == 7359517303863 and not c['passed']

def test_dividends_are_not_associate_earnings():
    result = analyse_reported_schedules(source())
    assert .097 < result['metrics']['associate_received_dividends_to_profit'] < .098
    assert result['source_verified']
    assert result['forecast_integration'] == 'historical_calibration_reference'

def test_missing_fact_cannot_silently_become_zero():
    p = source()
    p['groups'][0]['rows'][0]['value_vnd'] = None
    try:
        analyse_reported_schedules(p)
    except ValueError:
        return
    raise AssertionError("Invalid reported fact was accepted")

def test_duplicate_fact_is_rejected():
    p = source()
    p['groups'][0]['rows'].append(deepcopy(p['groups'][0]['rows'][0]))
    try:
        analyse_reported_schedules(p)
    except ValueError:
        return
    raise AssertionError("Invalid reported fact was accepted")

def test_remaining_loan_buckets_do_not_include_revolving_short_debt():
    p = source()
    maturity = next(g for g in p['groups'] if g['id'] == 'loan_maturity')
    assert sum(r['value_vnd'] for r in maturity['rows']) == 2771180307634
    assert maturity['reported_total_vnd'] < next(g for g in p['groups'] if g['id'] == 'short_debt')['reported_total_vnd']
