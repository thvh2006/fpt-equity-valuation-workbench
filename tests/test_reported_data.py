"""Integrity checks for manually extracted reported facts."""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_DIR = Path(__file__).parents[1]
DATA_DIR = PROJECT_DIR / "data" / "sample"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def test_annual_accounting_identities() -> None:
    rows = read_csv("reported_annual_core.csv")
    assert len(rows) == 5

    for row in rows:
        assets = int(row["total_assets"])
        liabilities = int(row["total_liabilities"])
        equity = int(row["total_owners_equity"])
        pat = int(row["profit_after_tax"])
        parent_pat = int(row["parent_profit_after_tax"])
        nci_pat = int(row["nci_profit_after_tax"])

        assert assets == liabilities + equity, row["period_end"]
        assert pat == parent_pat + nci_pat, row["period_end"]


def test_annual_periods_are_unique_and_sorted() -> None:
    rows = read_csv("reported_annual_core.csv")
    periods = [row["period_end"] for row in rows]
    assert periods == sorted(set(periods))


def test_9m2025_sector_reconciliation() -> None:
    rows = read_csv("operating_facts_9m2025.csv")

    def value(metric: str, segment: str) -> int:
        matches = [
            int(row["value"])
            for row in rows
            if row["metric"] == metric and row["segment"] == segment
        ]
        assert len(matches) == 1, (metric, segment, matches)
        return matches[0]

    assert value("revenue", "group") == sum(
        value("revenue", segment)
        for segment in (
            "technology_sector",
            "telecommunications_sector",
            "education_investment_other",
        )
    )
    assert value("profit_before_tax", "group") == sum(
        value("profit_before_tax", segment)
        for segment in (
            "technology_sector",
            "telecommunications_sector",
            "education_investment_other",
        )
    )

    # One-billion rounding difference is visible in the issuer's presentation.
    assert abs(
        value("revenue", "technology_sector")
        - value("revenue", "global_it_services")
        - value("revenue", "domestic_it_services")
    ) <= 1
    assert value("profit_before_tax", "technology_sector") == (
        value("profit_before_tax", "global_it_services")
        + value("profit_before_tax", "domestic_it_services")
    )
    assert value("revenue", "telecommunications_sector") == (
        value("revenue", "telecom_services")
        + value("revenue", "online_advertising")
    )


def test_eps_history_preserves_restatements() -> None:
    rows = read_csv("eps_as_presented.csv")
    by_observation: dict[str, set[int]] = {}
    for row in rows:
        by_observation.setdefault(row["observation_year"], set()).add(
            int(row["basic_eps_vnd"])
        )

    assert len(by_observation["2021"]) > 1
    assert len(by_observation["2022"]) > 1
    assert len(by_observation["2023"]) > 1


def test_reported_share_bridge_rolls_forward() -> None:
    rows = read_csv("share_count_bridge_reported.csv")
    assert len(rows) == 5

    prior_ending = None
    for row in rows:
        beginning = int(row["beginning_shares_in_circulation"])
        new_shares = int(row["new_employee_or_other_shares"])
        dividend_shares = int(row["share_dividend_shares"])
        ending = int(row["ending_shares_in_circulation"])

        assert beginning + new_shares + dividend_shares == ending
        if prior_ending is not None:
            assert beginning == prior_ending
        prior_ending = ending


def test_segment_history_reconciles_to_group() -> None:
    rows = read_csv("segment_history_reported.csv")
    assert len(rows) == 5
    for row in rows:
        revenue_parts = sum(
            int(row[key])
            for key in (
                "global_it_revenue",
                "domestic_it_revenue",
                "telecom_revenue",
                "digital_content_revenue",
                "education_investment_other_revenue",
                "consolidation_elimination_revenue",
            )
        )
        pbt_parts = sum(
            int(row[key])
            for key in (
                "global_it_pbt",
                "domestic_it_pbt",
                "telecom_pbt",
                "digital_content_pbt",
                "education_investment_other_pbt",
                "consolidation_elimination_pbt",
            )
        )
        assert abs(revenue_parts - int(row["group_revenue"])) <= 1_000_000
        assert abs(pbt_parts - int(row["group_pbt"])) <= 1_000_000


def test_fcff_history_ebit_definition() -> None:
    rows = read_csv("fcff_history_reported.csv")
    assert len(rows) == 5
    for row in rows:
        expected = (
            int(row["gross_profit"])
            - int(row["selling_expense"])
            - int(row["general_admin_expense"])
        )
        assert expected == int(row["ebit_before_financial_items"])


def test_monthly_price_history_reconciles_to_cutoff() -> None:
    rows = read_csv("fpt_monthly_price_history.csv")
    assert len(rows) == 70

    dates = [row["month_end"] for row in rows]
    assert dates == sorted(set(dates))
    assert dates[0] == "2020-01-31"
    assert dates[-1] == "2025-10-31"

    factors = {round(float(row["cutoff_rebase_factor"]), 9) for row in rows}
    assert len(factors) == 1

    cutoff = rows[-1]
    assert abs(
        int(cutoff["cutoff_rebased_close_vnd"])
        - int(cutoff["raw_close_vnd"])
    ) <= 1

    factor = float(cutoff["cutoff_rebase_factor"])
    for row in rows:
        expected = round(float(row["provider_adjusted_close_current_vnd"]) * factor)
        assert abs(expected - int(row["cutoff_rebased_close_vnd"])) <= 1


def test_9m2025_monitor_cash_inputs() -> None:
    rows = read_csv("operating_facts_9m2025.csv")

    def values(metric: str, segment: str) -> list[float]:
        return [
            float(row["value"])
            for row in rows
            if row["metric"] == metric and row["segment"] == segment
        ]

    operating_cash_flow = values("operating_cash_flow", "group")
    capex_purchase = values("capex_purchase", "group")
    group_pat = values("profit_after_tax", "group")

    assert len(operating_cash_flow) == 1
    assert len(capex_purchase) == 1
    assert len(group_pat) == 1
    assert operating_cash_flow[0] > capex_purchase[0] > 0

    post_capex_conversion = (
        operating_cash_flow[0] - capex_purchase[0]
    ) / group_pat[0]
    assert 0.23 < post_capex_conversion < 0.24

    required_growth_metrics = {
        ("revenue_growth_yoy", "group"),
        ("revenue_growth_yoy", "global_it_services"),
        ("signed_revenue_growth_yoy", "global_it_services"),
        ("revenue_growth_yoy", "global_it_japan"),
        ("revenue_growth_yoy", "global_it_apac"),
    }
    for metric, segment in required_growth_metrics:
        assert len(values(metric, segment)) == 1


def test_fy2025_actuals_reconcile() -> None:
    rows = read_csv("fy2025_actuals.csv")

    def value(metric_id: str, segment: str = "group") -> float:
        matches = [
            float(row["value_2025"])
            for row in rows
            if row["metric_id"] == metric_id and row["segment"] == segment
        ]
        assert len(matches) == 1, (metric_id, segment, matches)
        return matches[0]

    segment_revenue = sum(
        value("segment_revenue", segment)
        for segment in (
            "global_it",
            "domestic_it",
            "telecom",
            "digital_content",
            "education_investment_other",
            "elimination",
        )
    )
    assert abs(segment_revenue - value("net_revenue")) < 0.001
    assert abs(
        value("profit_after_tax")
        - value("parent_profit_after_tax")
        - value("nci_profit_after_tax")
    ) < 0.001


def test_fy2025_same_definition_fcff() -> None:
    rows = read_csv("fy2025_actuals.csv")

    def value(metric_id: str) -> float:
        matches = [
            float(row["value_2025"])
            for row in rows
            if row["metric_id"] == metric_id and row["segment"] == "group"
        ]
        assert len(matches) == 1, (metric_id, matches)
        return matches[0]

    ebit = (
        value("gross_profit")
        - value("selling_expense")
        - value("general_admin_expense")
    )
    tax_expense = value("current_tax") + value("deferred_tax")
    tax_rate = tax_expense / value("profit_before_tax")
    change_nwc = -sum(
        value(metric)
        for metric in (
            "receivables_cash_effect",
            "inventories_cash_effect",
            "payables_cash_effect",
            "prepaids_cash_effect",
        )
    )
    fcff = (
        ebit * (1 - tax_rate)
        + value("depreciation_amortisation")
        - value("capex_purchase")
        - change_nwc
    )

    assert 6029 < fcff < 6031
    assert 0.90 < value("operating_cash_flow") / value("profit_after_tax") < 0.91
    assert 0.44 < (
        value("operating_cash_flow") - value("capex_purchase")
    ) / value("profit_after_tax") < 0.46
