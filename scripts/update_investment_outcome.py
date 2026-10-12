#!/usr/bin/env python3
"""Append a point-in-time investment outcome observation."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = PROJECT_ROOT / "data" / "sample" / "investment_outcomes.csv"


def optional_float(value: str) -> float | None:
    return None if value.strip() == "" else float(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, type=date.fromisoformat)
    parser.add_argument("--fpt-price", required=True, type=float)
    parser.add_argument("--vnindex", type=float)
    parser.add_argument("--status", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    args = parser.parse_args()

    with args.log.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
        fieldnames = list(rows[0].keys())
    if any(row["observation_date"] == args.date.isoformat() for row in rows):
        raise SystemExit(f"Observation already exists for {args.date}")

    initial = rows[0]
    initial_price = float(initial["fpt_price_vnd"])
    initial_index = optional_float(initial["vnindex_level"])
    fair_value = float(initial["clock_b_fair_value_vnd"])
    fpt_return = args.fpt_price / initial_price - 1.0
    benchmark_return = None if initial_index is None or args.vnindex is None else args.vnindex / initial_index - 1.0
    active_return = None if benchmark_return is None else fpt_return - benchmark_return

    row = {
        "observation_date": args.date.isoformat(),
        "fpt_price_vnd": f"{args.fpt_price:.2f}",
        "vnindex_level": "" if args.vnindex is None else f"{args.vnindex:.4f}",
        "fpt_return": f"{fpt_return:.8f}",
        "benchmark_return": "" if benchmark_return is None else f"{benchmark_return:.8f}",
        "active_return": "" if active_return is None else f"{active_return:.8f}",
        "clock_b_fair_value_vnd": f"{fair_value:.4f}",
        "fair_value_gap": f"{fair_value / args.fpt_price - 1.0:.8f}",
        "thesis_status": args.status,
        "evidence_note": args.note,
        "source_url": args.source_url,
    }
    with args.log.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writerow(row)
    print(f"Added {args.date}: FPT return {fpt_return:.1%}; status {args.status}")


if __name__ == "__main__":
    main()
