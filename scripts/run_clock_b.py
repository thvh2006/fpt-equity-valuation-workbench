#!/usr/bin/env python3
"""Run all Clock B scenarios and write a reviewable JSON result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from equity_valuation.clock_b import load_inputs, run_all_scenarios  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inputs",
        type=Path,
        default=PROJECT_ROOT / "data" / "sample" / "clock_b_inputs.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "clock_b_summary.json",
    )
    args = parser.parse_args()
    output = run_all_scenarios(load_inputs(args.inputs))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    base = output["scenarios"]["base"]["valuation"]
    print(
        f"Base blended value: VND {base['blended_value_per_share']:,.0f} | "
        f"upside: {base['upside_to_market_price']:.1%} | {base['recommendation']}"
    )


if __name__ == "__main__":
    main()
