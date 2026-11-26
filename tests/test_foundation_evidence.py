"""Cross-artifact checks on real audit evidence, without approving source provenance."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_original_file_reviewed_opening_passes_with_recorded_digest():
    from equity_valuation.intake import validate_opening
    payload = json.loads((ROOT / "data/intake/clock_c_opening_pending.json").read_text())
    result = validate_opening(payload)
    assert len(result["reconciliations"]) == 4
    assert all(abs(v) < 0.001 for v in result["reconciliations"].values())
    assert result["status"] == "PASS"
    assert result["errors"] == []
    receipt = json.loads((ROOT / "data/intake/source_verification_receipt.json").read_text())
    assert all(f["source_sha256"] == receipt["sha256"] for f in payload["facts"])
    binary = ROOT / receipt["local_binary"]
    if binary.exists():
        import hashlib
        assert hashlib.sha256(binary.read_bytes()).hexdigest() == receipt["sha256"]


def test_cached_workbook_outputs_match_python_base_case():
    import importlib.util
    spec = importlib.util.spec_from_file_location("audit_foundation", ROOT / "scripts/audit_foundation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.inspect_workbook(ROOT / "reports/fpt_equity_valuation_v0_8.xlsx")
    assert len(result["clock_b_base_cache_comparison"]) == 5
    assert all(row["within_tolerance"] for row in result["clock_b_base_cache_comparison"])


def test_original_workbook_is_preserved_byte_for_byte():
    import hashlib
    receipt = json.loads((ROOT / "docs/audit/2026-11-23/upstream_receipt.json").read_text())
    actual = hashlib.sha256((ROOT / receipt["workbook_path"]).read_bytes()).hexdigest()
    assert actual == receipt["workbook_sha256"]
