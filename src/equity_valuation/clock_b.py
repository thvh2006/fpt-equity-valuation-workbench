"""Reproducible Clock B forecast and sum-of-parts valuation.

The module intentionally uses only the Python standard library so a reviewer can
audit the formulas without installing a financial modelling framework.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class ForecastYear:
    year: int
    revenue: float
    revenue_growth: float
    ebit: float
    ebit_margin: float
    nopat: float
    depreciation_amortisation: float
    capital_expenditure: float
    change_in_nwc: float
    fcff: float
    associate_profit: float
    net_financial_income: float
    parent_net_profit: float
    eps: float


@dataclass(frozen=True)
class ValuationResult:
    scenario: str
    wacc: float
    cost_of_equity: float
    cost_of_debt_after_tax: float
    operating_enterprise_value: float
    capitalised_associate_earnings: float
    equity_value: float
    sotp_value_per_share: float
    pe_value_per_share: float
    blended_value_per_share: float
    upside_to_market_price: float
    recommendation: str
    risk_label: str


def load_inputs(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def cost_of_capital(inputs: dict[str, Any], scenario: str) -> tuple[float, float, float]:
    actuals = inputs["actuals"]
    coc = inputs["cost_of_capital"]
    case = inputs["scenarios"][scenario]
    cost_of_equity = coc["risk_free_rate"] + coc["levered_beta"] * coc["equity_risk_premium"]
    after_tax_debt = coc["pre_tax_cost_of_debt"] * (1.0 - coc["tax_rate"])
    market_cap = actuals["market_price"] * actuals["shares_outstanding_million"] / 1000.0
    equity_weight = market_cap / (market_cap + actuals["debt"])
    base_wacc = equity_weight * cost_of_equity + (1.0 - equity_weight) * after_tax_debt
    return cost_of_equity, after_tax_debt, base_wacc + case["wacc_adjustment"]


def forecast(inputs: dict[str, Any], scenario: str = "base") -> list[ForecastYear]:
    if scenario not in inputs["scenarios"]:
        raise ValueError(f"Unknown scenario: {scenario}")
    case = inputs["scenarios"][scenario]
    actuals = inputs["actuals"]
    tax_rate = inputs["cost_of_capital"]["tax_rate"]
    pat_conversion = inputs["earnings"]["parent_pat_to_pbt"]
    shares = actuals["shares_outstanding_million"]
    years = list(range(2026, 2032))
    revenue = actuals["revenue_2026_anchor"]
    prior_revenue = actuals["revenue_2025_comparable"]
    associate_profit = actuals["associate_profit_2026"]
    rows: list[ForecastYear] = []

    for index, year in enumerate(years):
        if index:
            revenue *= 1.0 + case["revenue_growth"][index]
            associate_profit *= 1.0 + case["associate_profit_growth"][index]
        ebit = revenue * case["ebit_margin"][index]
        nopat = ebit * (1.0 - tax_rate)
        da = revenue * case["da_to_revenue"][index]
        capex = revenue * case["capex_to_revenue"][index]
        delta_revenue = revenue - prior_revenue
        change_nwc = delta_revenue * case["nwc_to_incremental_revenue"][index]
        fcff = nopat + da - capex - change_nwc
        net_financial_income = revenue * case["net_financial_income_to_revenue"][index]
        pbt = ebit + associate_profit + net_financial_income
        parent_pat = pbt * pat_conversion
        rows.append(
            ForecastYear(
                year=year,
                revenue=revenue,
                revenue_growth=case["revenue_growth"][index],
                ebit=ebit,
                ebit_margin=case["ebit_margin"][index],
                nopat=nopat,
                depreciation_amortisation=da,
                capital_expenditure=capex,
                change_in_nwc=change_nwc,
                fcff=fcff,
                associate_profit=associate_profit,
                net_financial_income=net_financial_income,
                parent_net_profit=parent_pat,
                eps=parent_pat * 1000.0 / shares,
            )
        )
        prior_revenue = revenue
    return rows


def value_business(inputs: dict[str, Any], scenario: str = "base") -> tuple[ValuationResult, list[ForecastYear]]:
    actuals = inputs["actuals"]
    case = inputs["scenarios"][scenario]
    valuation = inputs["valuation"]
    rows = forecast(inputs, scenario)
    cost_of_equity, after_tax_debt, wacc = cost_of_capital(inputs, scenario)
    explicit = rows[1:]
    timings = valuation["discount_timings"]
    explicit_pv = sum(row.fcff / (1.0 + wacc) ** timing for row, timing in zip(explicit, timings))
    terminal_value = explicit[-1].fcff * (1.0 + case["terminal_growth"]) / (wacc - case["terminal_growth"])
    terminal_pv = terminal_value / (1.0 + wacc) ** valuation["terminal_timing"]
    operating_ev = explicit_pv + terminal_pv
    associate_value = explicit[0].associate_profit * case["associate_multiple"]
    equity_value = (
        operating_ev
        + associate_value
        + actuals["cash"]
        + actuals["short_term_investments"]
        - actuals["debt"]
        - actuals["non_controlling_interests"]
    )
    shares = actuals["shares_outstanding_million"]
    sotp = equity_value * 1000.0 / shares
    pe_value = explicit[0].eps * case["pe_multiple"]
    blended = valuation["sotp_weight"] * sotp + valuation["pe_weight"] * pe_value
    upside = blended / actuals["market_price"] - 1.0
    recommendation = "BUY" if upside >= 0.20 else ("HOLD" if upside >= -0.10 else "SELL")
    result = ValuationResult(
        scenario=scenario,
        wacc=wacc,
        cost_of_equity=cost_of_equity,
        cost_of_debt_after_tax=after_tax_debt,
        operating_enterprise_value=operating_ev,
        capitalised_associate_earnings=associate_value,
        equity_value=equity_value,
        sotp_value_per_share=sotp,
        pe_value_per_share=pe_value,
        blended_value_per_share=blended,
        upside_to_market_price=upside,
        recommendation=recommendation,
        risk_label="HIGH",
    )
    return result, rows


def run_all_scenarios(inputs: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {"metadata": inputs["metadata"], "scenarios": {}}
    for scenario in ("downside", "base", "upside"):
        result, rows = value_business(inputs, scenario)
        output["scenarios"][scenario] = {
            "valuation": asdict(result),
            "forecast": [asdict(row) for row in rows],
        }
    return output
