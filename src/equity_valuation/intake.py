"""Fail-closed opening-statement intake; no valuation or missing-value imputation."""
from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

REQUIRED = (
    "cash", "short_term_investments", "receivables", "inventories", "prepaids",
    "ppe_net", "intangibles_net", "associates", "other_assets", "total_assets",
    "short_term_debt", "long_term_debt", "trade_payables", "other_liabilities",
    "total_liabilities", "parent_equity", "nci_equity", "total_equity",
)
ASSETS = REQUIRED[:9]
LIABILITIES = ("short_term_debt", "long_term_debt", "trade_payables", "other_liabilities")
ALLOWED_STATUS = {"missing", "repository_extracted_unverified",
                  "primary_text_reviewed_pending_checksum", "verified_original"}


def validate_opening(payload: dict[str, Any]) -> dict[str, Any]:
    """Check a grouped balance sheet and provenance. Zero is valid, missing is not.

    A valid return means this opening snapshot passes intake, not that a forecast
    model or a new recommendation is reviewed. `other_*` must be sourced grouped
    balances, never a plug computed to force the balance-sheet identity.
    """
    errors: list[dict[str, str]] = []
    values: dict[str, Decimal] = {}

    def error(code: str, metric: str, message: str) -> None:
        errors.append({"code": code, "metric": metric, "message": message})

    def parse_date(value: Any, field: str) -> date | None:
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            error("invalid_date", field, "Expected ISO calendar date")
            return None

    cutoff = parse_date(payload.get("information_cutoff"), "information_cutoff")
    period = parse_date(payload.get("period_end"), "period_end")
    if cutoff and period and period > cutoff:
        error("future_period", "period_end", "Opening date is later than information cutoff")
    if payload.get("currency") != "VND" or payload.get("unit") != "VND billion":
        error("unit_mismatch", "unit", "Opening snapshot requires VND billion")
    if not payload.get("accounting_basis"):
        error("missing_basis", "accounting_basis", "Specify consolidation perimeter")
    facts = payload.get("facts", [])
    if not isinstance(facts, list):
        facts = []
        error("invalid_facts", "facts", "Expected a list of financial facts")
    counts = Counter(f.get("metric") for f in facts if isinstance(f, dict))
    for metric, count in counts.items():
        if count > 1:
            error("duplicate_metric", str(metric), "Duplicate facts must be resolved explicitly")
    for metric in REQUIRED:
        if not counts.get(metric):
            error("missing_fact", metric, "Required grouped balance-sheet line is absent")
    for fact in facts:
        if not isinstance(fact, dict):
            error("invalid_fact", "facts", "Fact must be an object")
            continue
        metric = fact.get("metric", "")
        if metric not in REQUIRED:
            error("unknown_metric", metric, "Metric is outside this grouped-statement contract")
            continue
        if fact.get("status") not in ALLOWED_STATUS:
            error("invalid_status", metric, "Unknown verification status")
        if fact.get("status") != "verified_original":
            error("unverified_fact", metric, "Original statement has not been verified for this intake")
        value = fact.get("value")
        if value is None or isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            error("invalid_value", metric, "A finite numeric value is required; missing is not zero")
        else:
            try:
                number = Decimal(str(value))
                if not number.is_finite():
                    raise InvalidOperation
                if metric not in {"parent_equity", "nci_equity", "total_equity"} and number < 0:
                    error("negative_balance", metric, "Grouped asset/liability balances must be nonnegative")
                if counts[metric] == 1:
                    values[metric] = number
            except InvalidOperation:
                error("invalid_value", metric, "Non-finite financial amount")
        for field in ("source_id", "source_locator", "source_sha256", "reviewed_by", "grouping_note"):
            if not isinstance(fact.get(field), str) or not fact[field].strip():
                error("missing_provenance", metric, "Missing " + field)
        digest = fact.get("source_sha256", "")
        if digest and (len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest)):
            error("invalid_checksum", metric, "Expected a 64-character SHA-256")
        available = parse_date(fact.get("available_at"), metric + ".available_at")
        if available and cutoff and available > cutoff:
            error("post_cutoff_fact", metric, "Disclosure was unavailable at the selected cutoff")
        if available and period and available < period:
            error("availability_before_period", metric, "Statement availability precedes period end")
        if fact.get("period_end") != payload.get("period_end"):
            error("mixed_period", metric, "Do not mix opening balances from different reporting dates")
        if fact.get("accounting_basis") != payload.get("accounting_basis"):
            error("mixed_basis", metric, "Fact does not match the opening consolidation perimeter")

    differences: dict[str, float] = {}

    def reconcile(label: str, left: str, right: tuple[str, ...]) -> None:
        if all(k in values for k in (left,) + right):
            delta = values[left] - sum((values[k] for k in right), Decimal(0))
            differences[label] = float(delta)
            if abs(delta) > Decimal("0.001"):
                error("reconciliation_failure", label, "Difference exceeds VND0.001 billion")

    reconcile("asset_components", "total_assets", ASSETS)
    reconcile("liability_components", "total_liabilities", LIABILITIES)
    reconcile("equity_components", "total_equity", ("parent_equity", "nci_equity"))
    reconcile("balance_sheet", "total_assets", ("total_liabilities", "total_equity"))
    return {
        "status": "PASS" if not errors else "BLOCKED",
        "scope": "opening balance-sheet intake only; not a forecast release approval",
        "fact_count": len(facts), "required_count": len(REQUIRED),
        "reconciliations": differences, "errors": errors,
    }
