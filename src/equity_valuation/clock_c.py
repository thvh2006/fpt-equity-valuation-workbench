"""Forward year-end SOTP from the reviewed Clock C linked statements.

Financial amounts: VND billion. Share count: million. No market-data dependency.
"""
from copy import deepcopy
from math import isfinite


def value_case(forecast, case, common, *, wacc_override=None, growth_override=None):
    ps = forecast['periods']
    if forecast['source_intake_status'] != 'PASS' or not forecast['assumptions_reviewed']:
        raise ValueError('Reviewed source intake and forecast required')
    if ps[0]['end'] != common['valuation_date'] or len(ps) != 6:
        raise ValueError('Year-end valuation requires Q4 closing plus five annual periods')
    rf, erp, beta = common['risk_free_anchor'], common['total_equity_premium'], case['beta']
    ke = rf + beta * erp
    wacc = ke*(1-common['target_debt_weight']) + common['cost_of_debt']*(1-common['debt_tax_rate'])*common['target_debt_weight']
    wacc += case['wacc_adjustment']
    if wacc_override is not None:
        wacc = wacc_override
    g = case['terminal_growth'] if growth_override is None else growth_override
    roic = case['terminal_roic']
    if not 0 <= g < min(wacc, roic) or wacc <= 0:
        raise ValueError('Require 0 <= g < WACC and terminal ROIC')
    if not 0 <= common['incremental_dilution'] < 1:
        raise ValueError('Invalid dilution reserve')
    rows, pv = [], 0.0
    prev_floor = ps[0]['funding']['cash_floor']
    for i, p in enumerate(ps[1:], 1):
        reserve_change = p['funding']['cash_floor'] - prev_floor
        fcff = p['fcff'] - reserve_change
        # Full-year FCFF spread evenly within year. Mid-year discount convention.
        timing = i - .5
        discounted = fcff / (1+wacc)**timing
        rows.append(dict(period=p['period'], operating_fcff=p['fcff'],
                         operating_cash_investment=reserve_change, fcff=fcff,
                         timing=timing, discount_factor=(1+wacc)**-timing, pv=discounted))
        pv += discounted
        prev_floor = p['funding']['cash_floor']
    # Stable-state tax and reinvestment explicitly replace high-growth ratios.
    terminal_nopat = ps[-1]['income_statement']['ebit'] * (1+g) * (1-common['terminal_tax'])
    reinvestment = terminal_nopat*g/roic
    terminal_fcff = terminal_nopat-reinvestment
    tv = terminal_fcff/(wacc-g)
    # Mid-year stream begins in 2032. Gordon formula value at 2031.5.
    tv_timing = 4.5
    terminal_pv = tv/(1+wacc)**tv_timing
    ev = pv+terminal_pv
    q4 = ps[0]
    bs, cs = q4['balance_sheet'], q4['component_schedules']
    # Equity-accounted earnings are already FPT's attributable share. No second ownership haircut.
    associate_earnings = ps[1]['income_statement']['associate_profit']
    associate_value = associate_earnings*case['associate_pe']
    cash_net_of_reserve = bs['cash']-q4['funding']['cash_floor']
    investments = cs['deposit_principal']+cs['interest_accrued']+cs['investment_other_net']
    debt = bs['short_term_debt']+bs['long_term_debt']
    nci_value = bs['nci_equity']*case['nci_book_multiple']
    equity = ev+associate_value+cash_net_of_reserve+investments-debt-nci_value
    shares = common['issued_shares_million']*(1+common['incremental_dilution'])
    price = equity/shares*1000
    pe_value = ps[1]['income_statement']['parent_pat']/shares*1000*case['parent_pe']
    max_gap = max(p['funding']['funding_gap'] for p in ps)
    result = dict(valuation_date=common['valuation_date'], information_cutoff=forecast['information_cutoff'],
                  basis='31 Dec 2026E forward value; not a spot target or quoted return',
                  cost_of_equity=ke,wacc=wacc,terminal_growth=g,terminal_roic=roic,
                  periods=rows,explicit_pv=pv,terminal_nopat=terminal_nopat,
                  terminal_reinvestment=reinvestment,terminal_fcff=terminal_fcff,
                  terminal_value=tv,terminal_timing=tv_timing,terminal_pv=terminal_pv,
                  operating_ev=ev,terminal_share_of_ev=terminal_pv/ev,
                  associate_earnings=associate_earnings,associate_value=associate_value,
                  cash_net_of_reserve=cash_net_of_reserve,investments=investments,
                  debt=debt,nci_value=nci_value,equity_value=equity,
                  diluted_shares_million=shares,fair_value_vnd=price,
                  pe_crosscheck_vnd=pe_value,margin_of_safety_price_vnd=price*(1-common['margin_of_safety']),
                  market_price_vnd=None,upside=None,max_funding_gap=max_gap,
                  financing_status='POLICY_SHORTFALL' if max_gap>1e-6 else 'FUNDED',
                  nci_method='Forecast NCI book equity times explicit valuation proxy; not an observed market value',
                  checks={'equity_bridge':equity-(ev+associate_value+cash_net_of_reserve+investments-debt-nci_value),
                          'terminal_reinvestment':terminal_fcff-(terminal_nopat-reinvestment)})
    if not all(isfinite(v) for v in result.values() if isinstance(v,(float,int))):
        raise ValueError('Nonfinite valuation')
    return result


def reverse_terminal_growth(forecast, case, common, price):
    """Solve a hypothetical entry price; never label that price a market observation."""
    if price <= 0:
        raise ValueError('Positive hypothetical price required')
    v=value_case(forecast,case,common)
    low, high=0.0,min(v['wacc'],case['terminal_roic'])-1e-7
    vlo=value_case(forecast,case,common,growth_override=low)['fair_value_vnd']
    vhi=value_case(forecast,case,common,growth_override=high)['fair_value_vnd']
    if not vlo <= price <= vhi:
        return dict(status='OUTSIDE_NONNEGATIVE_GROWTH_RANGE',hypothetical_price=price,minimum_price=vlo)
    for _ in range(100):
        mid=(low+high)/2
        if value_case(forecast,case,common,growth_override=mid)['fair_value_vnd']<price:
            low=mid
        else:
            high=mid
    solved=(low+high)/2
    return dict(status='SOLVED',hypothetical_price=price,terminal_growth=solved,
                residual_vnd=value_case(forecast,case,common,growth_override=solved)['fair_value_vnd']-price)


def sensitivity(forecast, case, common):
    w=value_case(forecast,case,common)['wacc']
    return [dict(wacc=w+dw,g=g,fair_value_vnd=value_case(forecast,case,common,wacc_override=w+dw,growth_override=g)['fair_value_vnd'])
            for dw in [-.02,-.01,0,.01,.02] for g in [.02,.025,.03,.035,.04]]
