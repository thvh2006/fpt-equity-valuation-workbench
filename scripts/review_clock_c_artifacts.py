#!/usr/bin/env python3
"""Render report pages and check the independently recalculated workbook."""
from pathlib import Path
import json,sys,hashlib
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageOps,ImageDraw
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/p1_final';QA=ROOT/'outputs/qa/clock_c';QA.mkdir(parents=True,exist_ok=True)
for name in ['FPT_Equity_Research_Clock_C','FPT_Stock_Pitch_Clock_C','FPT_Decision_Memo_Clock_C','FPT_Sector_Appendix_Clock_C']:
    pdf=pdfium.PdfDocument(OUT/(name+'.pdf'));images=[]
    for i,page in enumerate(pdf):
        im=page.render(scale=1.5).to_pil();im.save(QA/f'{name}_{i+1:02d}.png')
        small=im.copy();small.thumbnail((425,590));tile=Image.new('RGB',(445,615),'#d8e0e7');tile.paste(small,((445-small.width)//2,15));ImageDraw.Draw(tile).text((12,595),str(i+1),fill='black');images.append(tile)
    for first in range(0,len(images),6):
        canvas=Image.new('RGB',(445*3,615*2),'white')
        for j,im in enumerate(images[first:first+6]):canvas.paste(im,(j%3*445,j//3*615))
        canvas.save(QA/f'{name}_contact_{first//6+1}.png')
    texts=[p.extract_text() for p in PdfReader(OUT/(name+'.pdf')).pages]
    assert all(len(t)>100 for t in texts),'Empty PDF page'
    assert all('\u25a0' not in t for t in texts),'Missing glyph'
gold=json.loads((OUT/'clock_c_valuation.json').read_text())
source=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/p1-lo-check/FPT_Research_Model_Clock_C.xlsx')
if source.exists():
    wb=load_workbook(source,data_only=True);checks=[]
    for address,key in [('D35','fair_value_vnd'),('D25','operating_ev'),('D28','associate_value'),('D33','equity_value')]:
        got=wb['DCF'][address].value;want=gold['cases']['base'][key]
        assert isinstance(got,(int,float)) and abs(got-want)<1e-6,(address,got,want)
        checks.append({'cell':'DCF!'+address,'value':got,'difference':got-want})
    sensitivity=[]
    for i in range(5):
        for j in range(5):
            got=wb['Valuation Inputs'].cell(23+i,7+j).value;want=gold['cases']['base']['sensitivity'][i*5+j]['fair_value_vnd']
            assert isinstance(got,(int,float)) and abs(got-want)<1e-6,('LO sensitivity',i,j,got,want)
            sensitivity.append(got)
    errors=[f'{s.title}!{c.coordinate}' for s in wb for row in s for c in row if c.data_type=='e']
    assert not errors,errors
    receipt={'status':'PASS','engine':'bundled LibreOffice headless, independent XLSX recalculation; not Microsoft Excel','original_workbook_sha256':hashlib.sha256((OUT/'FPT_Research_Model_Clock_C.xlsx').read_bytes()).hexdigest(),'headline_checks':checks,'native_sensitivity_points':len(sensitivity),'cached_formula_errors':errors}
    (OUT/'office_engine_recalculation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Independent office engine checks:',len(checks)+len(sensitivity))
print('PDF pages rendered into outputs/qa/clock_c')
