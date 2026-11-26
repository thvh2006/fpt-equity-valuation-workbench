#!/usr/bin/env python3
"""Package a private-path-free research release and record deliverable digests."""
import hashlib,json,subprocess,re,unicodedata
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/p1_final'
def normal(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def main():
    (ROOT/'index.html').write_bytes((OUT/'FPT_Research_Dashboard_Clock_C.html').read_bytes())
    previous=ROOT/'outputs/fpt_development/development_manifest.json'
    if previous.exists():
        current=json.loads(previous.read_text())
        for item in current['files']:
            b=(ROOT/item['path']).read_bytes();item.update(sha256=hashlib.sha256(b).hexdigest(),size_bytes=len(b))
        previous.write_text(json.dumps(current,indent=2)+'\n')
    files=[ROOT/p for p in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()]
    files=[p for p in files if p.is_file() and p.suffix!='.zip' and not p.name.endswith('.inspect.ndjson')]
    # Derive the private identity locally. Never embed it in repository code or receipts.
    home_id=normal(Path.home().name);private_path=str(Path.home())
    problems=[];checked=0
    for p in files:
        content=''
        try:
            if p.suffix in {'.xlsx','.docx','.pptx'}:
                with ZipFile(p) as z:content='\n'.join(z.read(n).decode('utf8','ignore') for n in z.namelist() if n.endswith(('.xml','.rels')))
            elif p.suffix=='.pdf':
                from pypdf import PdfReader
                r=PdfReader(p);content=str(r.metadata)+'\n'+'\n'.join(x.extract_text() for x in r.pages)
            elif p.suffix not in {'.png','.jpg','.jpeg','.ico'}:content=p.read_text(errors='ignore')
        except Exception as e:raise RuntimeError('Could not inspect '+str(p.relative_to(ROOT))) from e
        checked+=1
        if private_path in content or (len(home_id)>12 and home_id in normal(re.sub('<[^>]*>','',content))):problems.append(str(p.relative_to(ROOT)))
    if problems:raise ValueError('Public identity scan failed: '+', '.join(problems))
    receipt=dict(status='PASS',scanned_files=checked,scope='current public files, Office XML, PDF text and metadata; not Git history or remote caches',private_identity_matches=0,personal_home_path_matches=0)
    (OUT/'public_identity_scan.json').write_text(json.dumps(receipt,indent=2)+'\n')
    # Keep source and outputs together without private source binaries, logs or VCS metadata.
    paths=sorted(set(files+[OUT/'public_identity_scan.json']))
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if not p.is_file() or p.suffix=='.zip' or p.name.endswith('.inspect.ndjson') or p.name=='release_manifest.json':continue
        b=p.read_bytes();manifest.append(dict(path=str(p.relative_to(ROOT)),size_bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
    (OUT/'release_manifest.json').write_text(json.dumps(dict(version='1.1.0-clock-c',information_cutoff='2026-11-23',forward_value_date='2026-12-31',files=manifest),indent=2)+'\n')
    with ZipFile(OUT/'FPT_P1_Clock_C_Complete.zip','w',ZIP_DEFLATED) as z:
        for p in sorted(set(paths+[OUT/'release_manifest.json'])):
            z.write(p,'fpt-equity-valuation-workbench/'+str(p.relative_to(ROOT)))
    print(json.dumps(dict(public_files=checked,identity_scan='PASS',bundle_bytes=(OUT/'FPT_P1_Clock_C_Complete.zip').stat().st_size)))

if __name__=='__main__':main()
