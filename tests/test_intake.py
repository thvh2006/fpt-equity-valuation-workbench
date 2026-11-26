"""Economic and provenance failure cases for the new opening-statement gate."""
from copy import deepcopy
from equity_valuation.intake import REQUIRED, validate_opening


def fixture():
    # Synthetic grouped balance sheet ONLY for testing. No issuer factual claims.
    amounts = dict(cash=10, short_term_investments=5, receivables=20, inventories=5,
                   prepaids=0, ppe_net=30, intangibles_net=5, associates=15, other_assets=10,
                   total_assets=100, short_term_debt=15, long_term_debt=10, trade_payables=15,
                   other_liabilities=10, total_liabilities=50, parent_equity=45,
                   nci_equity=5, total_equity=50)
    return {"period_end": "2026-09-30", "information_cutoff": "2026-10-29",
            "currency": "VND", "unit": "VND billion", "accounting_basis": "synthetic test group",
            "facts": [{"metric": k, "value": amounts[k], "status": "verified_original",
                       "source_id": "synthetic_test_only", "source_locator": "fixture",
                       "source_sha256": "a" * 64, "reviewed_by": "unit test",
                       "grouping_note": "synthetic test amount, not issuer data",
                       "available_at": "2026-10-28", "period_end": "2026-09-30",
                       "accounting_basis": "synthetic test group"} for k in REQUIRED]}


def codes(payload):
    return {e["code"] for e in validate_opening(payload)["errors"]}


def test_verified_balanced_intake_accepts_legitimate_zero():
    assert validate_opening(fixture())["status"] == "PASS"


def test_missing_balance_is_not_coerced_to_zero():
    payload = fixture()
    payload["facts"][0]["value"] = None
    assert "invalid_value" in codes(payload)


def test_unverified_balanced_amounts_cannot_pass():
    payload = fixture()
    payload["facts"][0]["status"] = "repository_extracted_unverified"
    assert "unverified_fact" in codes(payload)


def test_post_cutoff_source_is_rejected():
    payload = fixture()
    payload["facts"][0]["available_at"] = "2026-10-30"
    assert "post_cutoff_fact" in codes(payload)


def test_mixed_opening_dates_and_accounting_perimeters_are_rejected():
    payload = fixture()
    payload["facts"][0]["period_end"] = "2025-12-31"
    payload["facts"][0]["accounting_basis"] = "different group"
    assert {"mixed_period", "mixed_basis"}.issubset(codes(payload))


def test_components_must_reconcile_not_just_headline_totals():
    payload = fixture()
    payload["facts"][0]["value"] = 11
    result = validate_opening(payload)
    assert result["reconciliations"]["balance_sheet"] == 0
    assert "reconciliation_failure" in codes(payload)


def test_duplicate_missing_and_nonfinite_values_fail():
    payload = fixture()
    payload["facts"].append(deepcopy(payload["facts"][0]))
    assert "duplicate_metric" in codes(payload)
    payload = fixture()
    payload["facts"].pop()
    assert "missing_fact" in codes(payload)
    payload = fixture()
    payload["facts"][0]["value"] = float("nan")
    assert "invalid_value" in codes(payload)


def test_units_invalid_dates_and_false_provenance_fail():
    payload = fixture()
    payload["unit"] = "VND"
    payload["facts"][0]["source_sha256"] = "not-a-hash"
    payload["facts"][0]["available_at"] = "not-a-date"
    assert {"unit_mismatch", "invalid_checksum", "invalid_date"}.issubset(codes(payload))


def test_validation_does_not_mutate_input():
    payload = fixture()
    before = deepcopy(payload)
    validate_opening(payload)
    assert payload == before
