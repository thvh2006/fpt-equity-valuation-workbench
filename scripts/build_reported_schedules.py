#!/usr/bin/env python3
"""Validate reported schedules and export reproducible evidence tables."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from equity_valuation.reported_schedules import analyse_reported_schedules

def main():
    payload = json.loads((ROOT / 'data/intake/q3_2026_reported_schedules.json').read_text())
    result = analyse_reported_schedules(payload)
    out = ROOT / 'artifacts/reported_schedules'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'analysis.json').write_text(json.dumps(result, indent=2)+'\n')
    with (out / 'reported_facts.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(['schedule','fact','label','value_vnd','printed_page','source_url','status'])
        for group in payload['groups']:
            for row in group['rows']:
                writer.writerow([group['id'],row['id'],row['label'],row['value_vnd'],group['printed_page'],payload['source_url'],payload['status']])
    if not result['all_accounting_bridges_pass']:
        raise SystemExit(json.dumps(result['checks']))
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
