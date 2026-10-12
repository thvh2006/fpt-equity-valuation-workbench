import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_only_current_workbook_is_in_primary_reports_folder():
    current = sorted(path.name for path in (ROOT / "reports").glob("*.xlsx"))
    assert current == ["fpt_equity_valuation_v0_8.xlsx"]
    assert (ROOT / "reports/archive/fpt_equity_valuation_v0_7.xlsx").exists()


def test_readme_preview_assets_exist():
    for name in (
        "valuation-crosscheck.png",
        "operating-forecast.png",
        "scenario-range.png",
        "assumption-dashboard.svg",
    ):
        assert (ROOT / "assets/readme" / name).exists()


def test_live_source_baselines_are_versioned_sha256_hashes():
    config = json.loads((ROOT / "configs/live_sources.json").read_text())
    assert len(config["sources"]) >= 3
    for source in config["sources"]:
        assert len(source["baseline_sha256"]) == 64
        int(source["baseline_sha256"], 16)


def test_investment_outcome_starts_from_clock_b_decision_point():
    with (ROOT / "data/sample/investment_outcomes.csv").open(newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["observation_date"] == "2026-10-09"
    assert float(row["fpt_price_vnd"]) == 57_900
    assert round(float(row["clock_b_fair_value_vnd"]), 4) == 94_497.8158
    assert row["thesis_status"] == "OPEN_EVIDENCE_PENDING"
