#!/usr/bin/env python3
"""Archive public-source evidence and analyst assumptions, excluding credentials/code/UI captures."""
import hashlib,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
R=Path(__file__).resolve().parents[1]
def main():
 paths=['data/private_sources/FPT_Q3_2026_HOSE.pdf','data/intake/source_verification_receipt.json','data/intake/q3_2026_balance_lines.csv','data/intake/clock_c_opening_pending.json','data/intake/q3_2026_reported_schedules.json','data/intake/forecast_source_facts.json','configs/forecast_research.json','reports/plan/forecast_assumption_register.csv','artifacts/reported_schedules/revenue_forecast_bridge.csv','artifacts/reported_schedules/analysis.json','artifacts/research_stresses/summary.csv','outputs/fpt_development/prevaluation_benchmarks.csv','outputs/fpt_development/run_all_verification.json','docs/PREVALUATION_REVIEW.md','reports/plan/clock_c_report_outline.md','reports/plan/figure_register.csv']
 receipt=json.loads((R/'data/intake/source_verification_receipt.json').read_text())
 assert hashlib.sha256((R/paths[0]).read_bytes()).hexdigest()==receipt['sha256']
 target=R/'outputs/fpt_development/FPT_Prevaluation_Evidence_2026-11-24.zip'
 with ZipFile(target,'w',ZIP_DEFLATED,compresslevel=9) as z:
  manifest=[]
  for name in paths:
   data=(R/name).read_bytes();z.writestr(name,data);manifest.append(dict(path=name,sha256=hashlib.sha256(data).hexdigest(),size_bytes=len(data)))
  z.writestr('SHA256_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
 with ZipFile(target) as z:assert z.testzip() is None
 print('Packaged',len(paths),'evidence files,',target.stat().st_size,'bytes')
if __name__=='__main__':main()
