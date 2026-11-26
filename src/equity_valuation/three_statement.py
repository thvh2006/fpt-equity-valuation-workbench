"""Development-only linked IS/BS/CF with explicit quarter stub and financing.

No investment valuation is produced. Original-source and assumption review are
separate from mathematical reconciliation. All amounts are VND billion.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
import math
from typing import Any

from .intake import REQUIRED, validate_opening

DRIVERS = (
    "annual_revenue", "gross_margin", "ebit_margin", "tax_rate", "dso", "dio", "dpo",
    "prepaid_ratio", "da_ratio", "capex_ratio", "intangible_share", "associate_profit",
    "associate_payout", "investment_yield", "debt_rate", "short_repayment_fraction",
    "long_repayment_fraction", "parent_payout", "nci_share", "nci_payout", "cash_floor_ratio",
)
RATIOS = {"gross_margin", "ebit_margin", "tax_rate", "prepaid_ratio", "da_ratio", "capex_ratio",
          "intangible_share", "associate_payout", "investment_yield", "debt_rate",
          "short_repayment_fraction", "long_repayment_fraction", "parent_payout", "nci_share",
          "nci_payout", "cash_floor_ratio"}


def validate_assumptions(config: dict[str, Any]) -> None:
    for name in ("facility_limit",):
        value = config.get(name)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
            raise ValueError("Invalid " + name)
    periods = config.get("periods", [])
    if not periods:
        raise ValueError("At least one forecast period is required")
    end = None
    for p in periods:
        start, closing = date.fromisoformat(p["start"]), date.fromisoformat(p["end"])
        if start > closing or (end is not None and (start - end).days != 1):
            raise ValueError("Periods must be non-overlapping and contiguous")
        end = closing
        for k in DRIVERS:
            value = p.get(k)
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
                raise ValueError("Invalid or missing driver: " + k)
            if k in RATIOS and value > 1:
                raise ValueError("Ratio outside [0,1]: " + k)
        if p["annual_revenue"] <= 0 or p["ebit_margin"] > p["gross_margin"]:
            raise ValueError("Revenue must be positive and EBIT margin cannot exceed gross margin")


def run_forecast(opening: dict[str, Any], config: dict[str, Any], *, development: bool = False) -> dict[str, Any]:
    """Return a fully linked development scenario, without disguising source gaps."""
    if config.get('model_mode') == 'research_components':
        from .research_forecast import run_research_forecast
        return run_research_forecast(opening, config, development=development)
    intake = validate_opening(opening)
    hard_errors = [e for e in intake["errors"] if e["code"] not in {"unverified_fact", "missing_provenance"}]
    if hard_errors:
        raise ValueError("Opening statement fails accounting/data checks: " + hard_errors[0]["code"])
    if intake["status"] != "PASS" and not development:
        raise ValueError("Original-source review incomplete; explicit development mode required")
    validate_assumptions(config)
    if not config.get("reviewed", False) and not development:
        raise ValueError("Assumptions have not been reviewed")
    if not config.get("periods") or (date.fromisoformat(config["periods"][0]["start"]) - date.fromisoformat(opening["period_end"])).days != 1:
        raise ValueError("First forecast must start immediately after the opening statement")
    balances = {f["metric"]: float(f["value"]) for f in opening["facts"] if f["metric"] in REQUIRED}
    base_short, long_debt, facility = balances["short_term_debt"], balances["long_term_debt"], 0.0
    rows = []
    for p in config["periods"]:
        prior = deepcopy(balances)
        start, end = date.fromisoformat(p["start"]), date.fromisoformat(p["end"])
        year_days = 366 if (date(end.year, 12, 31) - date(end.year, 1, 1)).days == 365 else 365
        fraction = ((end - start).days + 1) / year_days
        revenue = p["annual_revenue"] * fraction
        cogs = revenue * (1 - p["gross_margin"])
        ebit = revenue * p["ebit_margin"]
        opex = revenue - cogs - ebit
        da = revenue * p["da_ratio"]
        capex = revenue * p["capex_ratio"]
        assoc_profit = p["associate_profit"] * fraction
        assoc_dividend = assoc_profit * p["associate_payout"]
        interest_income = prior["short_term_investments"] * p["investment_yield"] * fraction
        interest_expense = (base_short + long_debt + facility) * p["debt_rate"] * fraction
        pbt = ebit + interest_income - interest_expense + assoc_profit
        # Associate share of profit is after-tax; no second group tax imposed here.
        tax = max(pbt - assoc_profit, 0) * p["tax_rate"]
        pat = pbt - tax
        nci_pat = pat * p["nci_share"]
        parent_pat = pat - nci_pat
        parent_dividend = max(parent_pat, 0) * p["parent_payout"]
        nci_dividend = max(nci_pat, 0) * p["nci_payout"]
        balances["receivables"] = p["annual_revenue"] * p["dso"] / year_days
        balances["inventories"] = p["annual_revenue"] * (1-p["gross_margin"]) * p["dio"] / year_days
        balances["prepaids"] = p["annual_revenue"] * p["prepaid_ratio"]
        balances["trade_payables"] = p["annual_revenue"] * (1-p["gross_margin"]) * p["dpo"] / year_days
        delta_nwc = sum(balances[k]-prior[k] for k in ("receivables", "inventories", "prepaids")) - (balances["trade_payables"]-prior["trade_payables"])
        tangible_additions = capex * (1-p["intangible_share"])
        intangible_additions = capex * p["intangible_share"]
        balances["ppe_net"] = prior["ppe_net"] + tangible_additions - da * (1-p["intangible_share"])
        balances["intangibles_net"] = prior["intangibles_net"] + intangible_additions - da * p["intangible_share"]
        balances["associates"] = prior["associates"] + assoc_profit - assoc_dividend
        if min(balances[k] for k in ("ppe_net", "intangibles_net", "associates")) < -1e-8:
            raise ValueError("Scenario creates a negative long-term asset balance; revise schedules")
        short_repaid = base_short * p["short_repayment_fraction"]
        long_repaid = long_debt * p["long_repayment_fraction"]
        cfo = pat + da - assoc_profit - interest_income - delta_nwc
        # Development timing assumption: interest receipts equal accrued income.
        # Reclassification follows the reported CFI presentation, not a cash-timing estimate.
        cfi = -capex + assoc_dividend + interest_income
        pre_facility_cff = -short_repaid - long_repaid - parent_dividend - nci_dividend
        cash_before_funding = prior["cash"] + cfo + cfi + pre_facility_cff
        floor = p["annual_revenue"] * p["cash_floor_ratio"]
        required_funding = max(floor - cash_before_funding, 0)
        facility_available = max(config["facility_limit"] - facility, 0)
        draw = min(required_funding, facility_available)
        funding_gap = required_funding - draw
        base_short -= short_repaid
        long_debt -= long_repaid
        facility += draw
        cff = pre_facility_cff + draw
        balances["cash"] = prior["cash"] + cfo + cfi + cff
        balances["short_term_debt"] = base_short + facility
        balances["long_term_debt"] = long_debt
        balances["parent_equity"] = prior["parent_equity"] + parent_pat - parent_dividend
        balances["nci_equity"] = prior["nci_equity"] + nci_pat - nci_dividend
        balances["total_assets"] = sum(balances[k] for k in ("cash", "short_term_investments", "receivables", "inventories", "prepaids", "ppe_net", "intangibles_net", "associates", "other_assets"))
        balances["total_liabilities"] = sum(balances[k] for k in ("short_term_debt", "long_term_debt", "trade_payables", "other_liabilities"))
        balances["total_equity"] = balances["parent_equity"] + balances["nci_equity"]
        checks = {
            "balance_sheet": balances["total_assets"]-balances["total_liabilities"]-balances["total_equity"],
            "cash_flow_to_cash": balances["cash"]-prior["cash"]-cfo-cfi-cff,
            "parent_equity_roll": balances["parent_equity"]-prior["parent_equity"]-parent_pat+parent_dividend,
            "nci_equity_roll": balances["nci_equity"]-prior["nci_equity"]-nci_pat+nci_dividend,
            "associate_roll": balances["associates"]-prior["associates"]-assoc_profit+assoc_dividend,
            "debt_roll": balances["short_term_debt"]+balances["long_term_debt"]-prior["short_term_debt"]-prior["long_term_debt"]+short_repaid+long_repaid-draw,
            "pat_attribution": pat-parent_pat-nci_pat,
        }
        if any(abs(v) > 1e-6 for v in checks.values()):
            raise ArithmeticError("Linked statement reconciliation failed")
        rows.append({
            "period": p["label"], "start": p["start"], "end": p["end"], "year_fraction": fraction,
            "income_statement": {"revenue": revenue, "cogs": cogs, "gross_profit": revenue-cogs,
                "opex": opex, "ebit": ebit, "interest_income": interest_income,
                "interest_expense": interest_expense, "associate_profit": assoc_profit,
                "profit_before_tax": pbt, "tax": tax, "group_pat": pat,
                "parent_pat": parent_pat, "nci_pat": nci_pat},
            "cash_flow": {"opening_cash": prior["cash"], "da": da, "delta_nwc": delta_nwc,
                "investment_income_removed": assoc_profit + interest_income, "interest_received": interest_income,
                "cfo": cfo, "capex": capex, "associate_dividend": assoc_dividend, "cfi": cfi,
                "short_repaid": short_repaid, "long_repaid": long_repaid,
                "parent_dividend": parent_dividend, "nci_dividend": nci_dividend,
                "facility_draw": draw, "cff": cff, "closing_cash": balances["cash"]},
            "balance_sheet": deepcopy(balances),
            "funding": {"cash_floor": floor, "cash_before_funding": cash_before_funding,
                "required_funding": required_funding, "facility_draw": draw,
                "facility_outstanding": facility, "funding_gap": funding_gap,
                "status": "INFEASIBLE" if funding_gap > 1e-6 else "FUNDED"},
            "fcff": ebit*(1-p["tax_rate"])+da-capex-delta_nwc,
            "checks": checks,
        })
    return {
        "status": "DEVELOPMENT_NOT_REVIEWED" if development else "REVIEW_REQUIRED",
        "scenario": config["name"], "unit": "VND billion", "opening_period_end": opening["period_end"],
        "information_cutoff": opening["information_cutoff"], "source_intake_status": intake["status"],
        "source_intake_error_count": len(intake["errors"]), "assumptions_reviewed": config.get("reviewed", False),
        "valuation_published": False, "opening_balances": {f["metric"]: f["value"] for f in opening["facts"]},
        "limitations": config.get("limitations", []), "periods": rows,
    }
