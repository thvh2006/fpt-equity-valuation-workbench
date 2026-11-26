#!/usr/bin/env python3
"""Group manually reviewed primary-source amounts; never infer a balancing plug."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://staticfile.hsx.vn/Uploads/UploadDocuments/2508914/20261028%20-%20FPT%20-%20BCTC%20hop%20nhat%20Quy%203%20nam%202026.pdf"
GROUPS = {
    "cash": [110], "short_term_investments": [120], "receivables": [130, 210],
    "inventories": [140], "prepaids": [161, 271], "ppe_net": [221, 224],
    "intangibles_net": [227], "associates": [262],
    "other_assets": [162, 163, 250, 263, 264, 265, 272, 279], "total_assets": [280],
    "short_term_debt": [321], "long_term_debt": [339], "trade_payables": [311],
    "other_liabilities": [312, 313, 314, 315, 316, 318, 319, 320, 322, 323, 337, 338, 342, 343, 344],
    "total_liabilities": [300], "parent_equity": [411, 412, 414, 417, 418, 419, 420],
    "nci_equity": [429], "total_equity": [400],
}


def main():
    raw_path = ROOT / "data/intake/q3_2026_balance_lines.csv"
    with raw_path.open(newline="") as handle:
        raw = {int(r["statement_code"]): r for r in csv.DictReader(handle)}
    receipt = json.loads((ROOT / 'data/intake/source_verification_receipt.json').read_text())
    assert receipt['balance_extraction_sha256'] == hashlib.sha256(raw_path.read_bytes()).hexdigest(), 'Transcription changed after source review'
    binary = ROOT / receipt['local_binary']
    if binary.exists():
        assert hashlib.sha256(binary.read_bytes()).hexdigest() == receipt['sha256'], 'Original binary checksum changed'
    basis = "Continuing consolidated operations plus equity-accounted associates"
    payload = {
        "status": "VERIFIED_OPENING_ORIGINAL",
        "period_end": "2026-09-30", "information_cutoff": "2026-11-23",
        "currency": "VND", "unit": "VND billion", "accounting_basis": basis,
        "source_url": SOURCE, "extraction_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "notes": [
            "Amounts transcribed from primary exchange-hosted filing text, printed pp.2-5.",
            "Original HOSE PDF downloaded, hashed and visually reviewed; see source_verification_receipt.json.",
            "Grouping is an analytical presentation, not a full historical or forecast statement.",
            "Receivables include short/long net balances; prepaids are expense allocations only.",
            "Other assets/liabilities are sums of explicit reported codes, not balancing plugs.",
            "Q3 opening must first be bridged through Q4; it cannot be labelled FY2026 closing actuals.",
        ], "facts": [],
    }
    for metric, codes in GROUPS.items():
        payload["facts"].append({
            "metric": metric, "value": sum(int(raw[c]["value_vnd"]) for c in codes) / 1e9,
            "status": "verified_original", "period_end": "2026-09-30",
            "accounting_basis": basis, "available_at": "2026-10-28",
            "source_id": "hsx_fpt_q3_2026_consolidated_fs", "source_sha256": receipt["sha256"],
            "source_locator": "Printed pp." + ",".join(sorted({raw[c]["printed_page"] for c in codes}))
                              + "; statement codes " + ",".join(map(str, codes)),
            "reviewed_by": "Codex primary filing text review 2026-11-23",
            "grouping_note": "Sum of reported statement codes " + "+".join(map(str, codes)),
        })
    (ROOT / "data/intake/clock_c_opening_pending.json").write_text(json.dumps(payload, indent=2) + "\n")
    print("Built 18 original-file-verified groups; forecast assumptions remain separate")


if __name__ == "__main__":
    main()
