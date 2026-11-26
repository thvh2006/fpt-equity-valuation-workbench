"""Independent economic and failure-path tests for linked development statements."""
from copy import deepcopy
import json
from pathlib import Path
from equity_valuation.intake import REQUIRED
from equity_valuation.three_statement import run_forecast

ROOT = Path(__file__).resolve().parents[1]


def actual_development_case():
    opening = json.loads((ROOT / "data/intake/clock_c_opening_pending.json").read_text())
    config = json.loads((ROOT / "configs/three_statement_development.json").read_text())["scenarios"]["base"]
    return opening, config


def test_interest_receipts_move_to_investing_without_creating_cash():
    opening, config = actual_development_case()
    row = run_forecast(opening, config, development=True)['periods'][0]
    income, cf = row['income_statement'], row['cash_flow']
    assert income['interest_income'] > 0
    assert cf['interest_received'] == income['interest_income']
    assert abs(cf['cfo'] - (income['group_pat'] + cf['da'] -
               income['associate_profit'] - income['interest_income'] - cf['delta_nwc'])) < 1e-8
    assert abs(cf['cfi'] - (-cf['capex'] + cf['associate_dividend'] + cf['interest_received'])) < 1e-8
    # Relative to the old presentation, equal and opposite reclassification.
    old_cfo = income['group_pat'] + cf['da'] - income['associate_profit'] - cf['delta_nwc']
    old_cfi = -cf['capex'] + cf['associate_dividend']
    assert abs(cf['cfo'] + cf['cfi'] - old_cfo - old_cfi) < 1e-8


def test_independent_one_year_cash_and_equity_case():
    amounts = {k: 0 for k in REQUIRED}
    amounts.update(cash=100, ppe_net=100, total_assets=200, parent_equity=200, total_equity=200)
    opening = {"period_end":"2026-12-31", "information_cutoff":"2027-01-31", "currency":"VND",
               "unit":"VND billion", "accounting_basis":"synthetic", "facts":[
        {"metric":k,"value":v,"status":"verified_original","period_end":"2026-12-31",
         "accounting_basis":"synthetic","available_at":"2027-01-20","source_id":"synthetic",
         "source_locator":"hand calculation","source_sha256":"a"*64,"reviewed_by":"test",
         "grouping_note":"synthetic fixture only"} for k,v in amounts.items()]}
    _, config = actual_development_case()
    p = deepcopy(config["periods"][1])
    p.update(start="2027-01-01",end="2027-12-31",annual_revenue=100,gross_margin=.5,ebit_margin=.2,
             tax_rate=.2,dso=0,dio=0,dpo=0,prepaid_ratio=0,da_ratio=.1,capex_ratio=.1,
             intangible_share=0,associate_profit=0,parent_payout=.5,nci_share=0,cash_floor_ratio=0)
    config.update(periods=[p], reviewed=True)
    row = run_forecast(opening,config)["periods"][0]
    # Independently: profit=20*(1-.2)=16; CFO=16+10=26; CFI=-10; dividend=8.
    assert abs(row["income_statement"]["group_pat"]-16) < 1e-8
    assert abs(row["cash_flow"]["cfo"]-26) < 1e-8
    assert abs(row["balance_sheet"]["cash"]-108) < 1e-8
    assert abs(row["balance_sheet"]["parent_equity"]-208) < 1e-8


def test_working_capital_stress_has_economic_cash_cost():
    opening, config = actual_development_case()
    base = run_forecast(opening,config,development=True)["periods"][0]
    config["periods"][0]["dso"] += 30
    stressed = run_forecast(opening,config,development=True)["periods"][0]
    expected_use = config["periods"][0]["annual_revenue"]*30/365
    assert abs(base["cash_flow"]["cfo"]-stressed["cash_flow"]["cfo"]-expected_use) < 1e-7
    assert abs(base["income_statement"]["group_pat"]-stressed["income_statement"]["group_pat"]) < 1e-8


def test_facility_cap_exposes_infeasible_scenario_without_plug():
    opening, config = actual_development_case()
    config["facility_limit"] = 0
    config["periods"][0]["dso"] = 700
    row = run_forecast(opening,config,development=True)["periods"][0]
    assert row["funding"]["status"] == "INFEASIBLE"
    assert row["funding"]["funding_gap"] > 0
    assert row["balance_sheet"]["cash"] < 0
    assert abs(row["checks"]["balance_sheet"]) < 1e-6


def test_associate_dividend_changes_cash_and_investment_not_profit():
    opening, config = actual_development_case()
    config["periods"] = config["periods"][:1]
    a = run_forecast(opening,config,development=True)["periods"][0]
    config["periods"][0]["associate_payout"] = 0
    b = run_forecast(opening,config,development=True)["periods"][0]
    dividend = a["cash_flow"]["associate_dividend"]
    assert abs(a["income_statement"]["group_pat"]-b["income_statement"]["group_pat"]) < 1e-8
    assert abs(a["balance_sheet"]["cash"]-b["balance_sheet"]["cash"]-dividend) < 1e-7
    assert abs(b["balance_sheet"]["associates"]-a["balance_sheet"]["associates"]-dividend) < 1e-7


def test_incomplete_source_is_blocked_without_development_flag():
    opening, config = actual_development_case()
    opening["facts"][0]["status"] = "primary_text_reviewed_pending_checksum"
    opening["facts"][0]["source_sha256"] = ""
    try:
        run_forecast(opening,config)
    except ValueError as exc:
        assert "Original-source" in str(exc)
    else:
        raise AssertionError("Unreviewed source was accepted")


def test_missing_balance_and_noncontiguous_stub_fail_even_in_development():
    opening, config = actual_development_case()
    opening["facts"][0]["value"] = None
    try:
        run_forecast(opening,config,development=True)
    except ValueError:
        pass
    else:
        raise AssertionError("Missing balance accepted")
    opening, config = actual_development_case()
    config["periods"][0]["start"] = "2026-10-02"
    try:
        run_forecast(opening,config,development=True)
    except ValueError as exc:
        assert "immediately" in str(exc)
    else:
        raise AssertionError("Gap after opening accepted")


def test_all_scenarios_and_full_calendar_years_reconcile():
    opening, _ = actual_development_case()
    configs = json.loads((ROOT / "configs/three_statement_development.json").read_text())["scenarios"]
    for config in configs.values():
        result = run_forecast(opening,config,development=True)
        assert abs(result["periods"][0]["year_fraction"]-92/365) < 1e-10
        for row in result["periods"][1:]:
            assert row["year_fraction"] == 1
        assert all(abs(v)<1e-6 for row in result["periods"] for v in row["checks"].values())
        assert result["valuation_published"] is False
