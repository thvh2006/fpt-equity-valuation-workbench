#!/usr/bin/env python3
"""Run three illustrative linked-statement cases. No target price is produced."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from equity_valuation.three_statement import run_forecast


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development", action="store_true", help="Allow reviewed-text inputs pending original-file verification")
    args = parser.parse_args()
    opening_path = ROOT / "data/intake/clock_c_opening_pending.json"
    config_path = ROOT / "configs/forecast_research.json"
    opening, config = json.loads(opening_path.read_text()), json.loads(config_path.read_text())
    results = {name: run_forecast(opening, case, development=args.development) for name, case in config["scenarios"].items()}
    digest = hashlib.sha256(opening_path.read_bytes()+config_path.read_bytes()).hexdigest()
    out = ROOT / "artifacts/three_statement_development"
    out.mkdir(parents=True, exist_ok=True)
    payload = {"run_id": "dev-"+digest[:12], "input_sha256": digest,
               "model_status": "ANALYST_CASE_PREVALUATION", "scenarios": results}
    (out / "results.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"run_id": payload["run_id"], "scenarios": len(results),
        "periods_per_scenario": len(results["base"]["periods"]),
        "maximum_accounting_difference": max(abs(v) for result in results.values() for period in result["periods"] for v in period["checks"].values()),
        "valuation_published": False}, indent=2))


if __name__ == "__main__":
    main()
