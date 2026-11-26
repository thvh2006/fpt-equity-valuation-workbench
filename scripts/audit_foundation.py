#!/usr/bin/env python3
"""Read-only workbook audit and reproducible next-step evidence. Standard library only."""
from __future__ import annotations

import csv
import hashlib
import json
import posixpath
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from equity_valuation.clock_b import load_inputs, value_business
from equity_valuation.intake import validate_opening

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS = {"m": MAIN}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def inspect_workbook(path: Path) -> dict:
    sheets = []
    all_values = {}
    with ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ["".join(t.itertext()) for t in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        for sheet in workbook.find("m:sheets", NS):
            target = rels[sheet.attrib[RID]]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            xml = ET.fromstring(archive.read(target))
            values, formulas, errors, labels = {}, {}, [], []
            for cell in xml.findall(".//m:sheetData/m:row/m:c", NS):
                address, kind = cell.attrib["r"], cell.attrib.get("t")
                val, formula = cell.find("m:v", NS), cell.find("m:f", NS)
                text = val.text if val is not None else None
                if kind == "s" and text is not None:
                    text = strings[int(text)]
                elif kind == "inlineStr":
                    node = cell.find("m:is", NS)
                    text = "".join(node.itertext()) if node is not None else None
                values[address] = text
                if formula is not None:
                    formulas[address] = formula.text
                if kind == "e":
                    errors.append({"cell": address, "error": text})
                if kind in {"str", "s", "inlineStr"} and formula is None and text:
                    labels.append({"cell": address, "label": text})
            all_values[sheet.attrib["name"]] = values
            sheets.append({"name": sheet.attrib["name"], "cell_count": len(values),
                           "formula_count": len(formulas), "cached_errors": errors,
                           "formula_samples": dict(list(formulas.items())[:5]), "labels": labels})
    base, rows = value_business(load_inputs(ROOT / "data/sample/clock_b_inputs.json"))
    mapping = {
        "blended_value": ("Clock B Valuation", "E39", base.blended_value_per_share),
        "sotp_value": ("Clock B Valuation", "E37", base.sotp_value_per_share),
        "pe_value": ("Clock B Valuation", "E38", base.pe_value_per_share),
        "forecast_2031_revenue": ("Clock B Build", "J6", rows[-1].revenue),
        "forecast_2031_fcff": ("Clock B Build", "J17", rows[-1].fcff),
    }
    comparison = []
    for metric, (sheet, cell, expected) in mapping.items():
        cached = float(all_values[sheet][cell])
        comparison.append({"metric": metric, "sheet": sheet, "cell": cell,
                           "python": expected, "excel_cached": cached,
                           "absolute_difference": abs(expected - cached),
                           "within_tolerance": abs(expected - cached) < 0.01})
    return {
        "path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sheet_count": len(sheets), "formula_count": sum(s["formula_count"] for s in sheets),
        "cached_error_count": sum(len(s["cached_errors"]) for s in sheets),
        "inspection_limit": "XML/cached-value inspection; not native Excel recalculation or visual QA",
        "sheets": sheets, "clock_b_base_cache_comparison": comparison,
    }


def audit_price_sample() -> dict:
    path = ROOT / "data/sample/fpt_monthly_price_history.csv"
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    dates = [r["month_end"] for r in rows]
    months = [d[:7] for d in dates]
    numeric = [float(r["cutoff_rebased_close_vnd"]) for r in rows]
    return {
        "sample_path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(rows), "assets": ["FPT"], "frequency": "monthly last-trading-date observations",
        "first_date": dates[0], "last_date": dates[-1],
        "ordered_unique_dates": dates == sorted(set(dates)),
        "unique_months": len(set(months)) == len(months), "positive_prices": all(p > 0 for p in numeric),
        "source_status": "Existing repository-derived sample inspected; external provider not re-fetched",
        "new_download_verified": False,
        "decision": "USABLE_FOR_PIPELINE_FIXTURE_ONLY",
        "blocked_research_uses": ["multi-asset cross-sectional ranking", "daily execution/capacity simulation",
                                  "point-in-time universe claims", "verified total-return claims"],
        "missing": ["multi-asset universe membership history", "daily OHLCV and tradability",
                    "corporate action/cash distribution contract", "point-in-time data vintages",
                    "benchmark total-return series", "redistribution and usage-rights review"],
    }


def main() -> None:
    output = ROOT / "docs/audit/2026-11-23"
    output.mkdir(parents=True, exist_ok=True)
    inventory = inspect_workbook(ROOT / "reports/fpt_equity_valuation_v0_8.xlsx")
    (output / "workbook_inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    with (output / "workbook_sheets.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sheet", "cells", "formulas", "cached_errors"])
        writer.writeheader()
        writer.writerows({"sheet": s["name"], "cells": s["cell_count"], "formulas": s["formula_count"],
                          "cached_errors": len(s["cached_errors"])} for s in inventory["sheets"])
    price = audit_price_sample()
    (output / "p2_data_feasibility.json").write_text(json.dumps(price, indent=2) + "\n")
    intake = json.loads((ROOT / "data/intake/clock_c_opening_pending.json").read_text())
    result = validate_opening(intake)
    (output / "clock_c_intake_status.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"workbook_sheets": inventory["sheet_count"], "formulas": inventory["formula_count"],
                      "cached_errors": inventory["cached_error_count"],
                      "base_cache_checks_pass": all(r["within_tolerance"] for r in inventory["clock_b_base_cache_comparison"]),
                      "clock_c_intake": result["status"], "intake_errors": len(result["errors"]),
                      "p2_sample": price["decision"]}, indent=2))


if __name__ == "__main__":
    main()
