#!/usr/bin/env python3
"""Rebuild and verify local FPT development artifacts; no publishing or trading."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default=shutil.which('node'))
    args = parser.parse_args()
    if not args.node:
        parser.error('Node runtime required; pass --node /absolute/path/to/node')
    logdir = ROOT / 'outputs/qa/run_all'
    logdir.mkdir(parents=True, exist_ok=True)
    steps = [
        ('opening_intake', [sys.executable, 'scripts/build_opening_intake.py']),
        ('reported_schedules', [sys.executable, 'scripts/build_reported_schedules.py']),
        ('research_assumptions', [sys.executable, 'scripts/build_research_assumptions.py']),
        ('foundation_audit', [sys.executable, 'scripts/audit_foundation.py']),
        ('legacy_clock_b_regression', [sys.executable, 'scripts/run_clock_b.py', '--output', str(logdir / 'clock_b_regression.json')]),
        ('research_forecast', [sys.executable, 'scripts/run_three_statement.py']),
        ('clock_c_valuation', [sys.executable, 'scripts/run_clock_c.py']),
        ('research_stresses', [sys.executable, 'scripts/run_research_stresses.py']),
        ('prevaluation_benchmarks', [sys.executable, 'scripts/build_prevaluation_summary.py']),
        ('repository_checks', [sys.executable, 'scripts/run_checks.py']),
        ('excel_build_and_reconciliation', [args.node, 'scripts/build_three_statement_workbook.mjs']),
        ('html_build_and_reconciliation', [args.node, 'scripts/build_three_statement_dashboard.mjs']),
        ('notebook_build_and_execution', [sys.executable, 'scripts/build_three_statement_notebook.py']),
        ('dashboard_controls', [args.node, 'scripts/verify_clock_c_dashboard.mjs']),
        ('valuation_notebook', [sys.executable, 'scripts/build_clock_c_notebook.py']),
        ('research_report', [sys.executable, 'scripts/build_clock_c_report.py']),
    ]
    completed = []
    checks_passed = None
    for name, command in steps:
        print('Running:', name, flush=True)
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        output = result.stdout + result.stderr
        (logdir / (name + '.log')).write_text(output)
        if result.returncode:
            print(output[-5000:])
            raise SystemExit('Failed: ' + name)
        completed.append(name)
        if name == 'repository_checks':
            match = re.search(r'(\d+)/(\d+) checks passed', output)
            assert match and match[1] == match[2], 'Incomplete repository check run'
            checks_passed = int(match[1])
        print('Passed:', name, flush=True)

    # Verification uses the exported workbook bytes, not only in-memory cells.
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    workbook = ROOT / 'outputs/p1_final/FPT_Research_Model_Clock_C.xlsx'
    with ZipFile(workbook) as archive:
        book = ET.fromstring(archive.read('xl/workbook.xml'))
        assert len(book.find('m:sheets', ns)) == 14
        for name in archive.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                sheet = ET.fromstring(archive.read(name))
                assert not sheet.findall('.//m:c[@t="e"]', ns), 'Cached Excel error: ' + name
    html_path = ROOT / 'outputs/fpt_development/FPT_Three_Statement_Dashboard.html'
    html = html_path.read_text()
    assert html.count('<details>') == 12
    assert '/* MODEL_SOURCE */' not in html and '/* MODEL_DATA */' not in html
    scripts = re.findall(r'<script>(.*?)</script>', html, re.S)
    assert scripts, 'No dashboard scripts'
    for i, source in enumerate(scripts):
        target = logdir / ('dashboard_script_%d.js' % i)
        target.write_text(source)
        subprocess.run([args.node, '--check', str(target)], check=True, capture_output=True)

    out = ROOT / 'outputs/fpt_development'
    excel = json.loads((out / 'excel_python_reconciliation.json').read_text())
    browser = json.loads((out / 'dashboard_reconciliation.json').read_text())
    evidence = json.loads((ROOT / 'artifacts/reported_schedules/analysis.json').read_text())
    notebook = json.loads((ROOT / 'notebooks/02_three_statement_development.ipynb').read_text())
    code_cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
    assert all(c['execution_count'] and not any(o['output_type'] == 'error' for o in c['outputs']) for c in code_cells)
    assert all(abs(r['difference']) < 1e-6 for r in excel['results'])
    assert browser['all_pass'] and evidence['all_accounting_bridges_pass']
    summary = dict(completed_at_utc=datetime.now(timezone.utc).isoformat(),
                   status='LOCAL_BUILD_AND_CHECKS_PASSED', steps=completed,
                   repository_checks_passed=checks_passed,
                   reported_bridges=len(evidence['checks']), excel_comparisons=excel['checks'],
                   excel_input_perturbations=excel['input_perturbations'],
                   javascript_comparisons=browser['numeric_comparisons'],
                   evaluated_notebook_cells=len(code_cells),
                   exported_workbook_sheets=14, exported_cached_errors=0,
                   release_status='FORWARD_RESEARCH_VALUATION',
                   not_verified=['independent human research review',
                                 'native Microsoft Excel recalculation', 'Jupyter kernel',
                                 'new browser UI session', 'internet hosting'])
    (out / 'run_all_verification.json').write_text(json.dumps(summary, indent=2)+'\n')
    manifest_path = out / 'development_manifest.json'
    manifest = {'status':'FORWARD_RESEARCH_VALUATION','research_cutoff':'2026-11-23','valuation_date':'2026-12-31','files':[]}
    for relative in ['outputs/p1_final/FPT_Research_Model_Clock_C.xlsx','outputs/p1_final/FPT_Research_Dashboard_Clock_C.html','outputs/p1_final/FPT_Equity_Research_Clock_C.pdf','outputs/p1_final/clock_c_valuation.json','notebooks/03_clock_c_valuation_and_decision.ipynb']:
        data=(ROOT/relative).read_bytes()
        manifest['files'].append(dict(path=relative,sha256=hashlib.sha256(data).hexdigest(),size_bytes=len(data)))
    forecast=json.loads((ROOT / 'artifacts/three_statement_development/results.json').read_text())
    manifest.update(reported_source_verified=evidence['source_verified'],run_id=forecast['run_id'],repository_checks_passed=checks_passed,excel_output_comparisons=excel['checks'],javascript_numeric_comparisons=browser['numeric_comparisons'],analyst_assumption_rows=684,stress_cases=9)
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    (ROOT/'outputs/p1_final/build_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
