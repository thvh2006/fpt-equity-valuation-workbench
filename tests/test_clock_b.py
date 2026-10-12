"""Checks for the reproducible Clock B model."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from equity_valuation.clock_b import load_inputs, value_business  # noqa: E402


INPUTS = load_inputs(PROJECT_ROOT / "data" / "sample" / "clock_b_inputs.json")


def test_base_case_reproduces_reviewed_workbook() -> None:
    result, rows = value_business(INPUTS, "base")
    assert abs(result.wacc - 0.1088727461) < 1e-9
    assert abs(rows[-1].revenue - 89460.4923) < 0.01
    assert abs(rows[-1].fcff - 11120.9733) < 0.01
    assert abs(result.sotp_value_per_share - 97510.7126) < 0.1
    assert abs(result.pe_value_per_share - 89978.4706) < 0.1
    assert abs(result.blended_value_per_share - 94497.8158) < 0.1


def test_scenarios_are_ordered() -> None:
    downside, _ = value_business(INPUTS, "downside")
    base, _ = value_business(INPUTS, "base")
    upside, _ = value_business(INPUTS, "upside")
    assert downside.blended_value_per_share < base.blended_value_per_share
    assert base.blended_value_per_share < upside.blended_value_per_share


def test_no_terminal_value_division_error() -> None:
    for scenario in INPUTS["scenarios"]:
        _, _, wacc = __import__(
            "equity_valuation.clock_b", fromlist=["cost_of_capital"]
        ).cost_of_capital(INPUTS, scenario)
        assert wacc > INPUTS["scenarios"][scenario]["terminal_growth"]


def test_forecast_cash_flow_identity() -> None:
    _, rows = value_business(INPUTS, "base")
    for row in rows:
        expected = (
            row.nopat
            + row.depreciation_amortisation
            - row.capital_expenditure
            - row.change_in_nwc
        )
        assert abs(row.fcff - expected) < 1e-9
