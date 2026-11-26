"""Reported accounting bridges; arithmetic checks never approve provenance."""
from math import isfinite


def analyse_reported_schedules(payload):
    if payload.get('unit') != 'VND':
        raise ValueError('Raw reported schedules must use integer VND')
    groups = {}
    checks = []
    for group in payload['groups']:
        key = group['id']
        if key in groups:
            raise ValueError('Duplicate schedule: ' + key)
        rows = {}
        for row in group['rows']:
            value = row['value_vnd']
            if row['id'] in rows or isinstance(value, bool) or not isinstance(value, int):
                raise ValueError('Duplicate or non-integer reported fact: ' + key)
            rows[row['id']] = value
        total = group['reported_total_vnd']
        if isinstance(total, bool) or not isinstance(total, int):
            raise ValueError('Missing or invalid reported control total: ' + key)
        difference = sum(rows.values()) - total
        checks.append(dict(schedule=key, difference_vnd=difference, passed=difference == 0))
        groups[key] = rows
    a, r, i = groups['associates'], groups['receivables'], groups['short_investments']
    metrics = {
        'associate_received_dividends_to_profit': -a['dividends'] / a['profit'],
        'trade_gross_share_of_grouped_net_receivables': r['trade_gross'] / sum(r.values()),
        'accrued_interest_share_of_short_investments': i['accrued_interest'] / sum(i.values()),
        'debt_perimeter_change_vnd': groups['short_debt']['perimeter'] + groups['long_debt']['perimeter'],
        'debt_fx_change_vnd': groups['short_debt']['fx'] + groups['long_debt']['fx'],
    }
    assert all(isfinite(v) for v in metrics.values())
    return dict(status=payload['status'], source_verified=(payload.get('status') == 'verified_original' and isinstance(payload.get('source_sha256'), str) and len(payload['source_sha256']) == 64),
                forecast_integration=payload['forecast_integration'],
                all_accounting_bridges_pass=all(c['passed'] for c in checks),
                checks=checks, metrics=metrics,
                interpretation='Historical observations only. No forward assumption is approved by these ratios.')
