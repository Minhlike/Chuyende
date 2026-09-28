"""Verify native caption fields and pagination with Word without saving its XML."""
from __future__ import annotations
import argparse,hashlib,json,re,zipfile
from pathlib import Path
from lxml import etree
import pythoncom
import win32com.client as win32
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('docx',type=Path);ap.add_argument('pdf',type=Path)
    ap.add_argument('--report',type=Path,required=True);ap.add_argument('--resolve',action='store_true');args=ap.parse_args()
    before=hashlib.sha256(args.docx.read_bytes()).hexdigest()
    with zipfile.ZipFile(args.docx) as z:root=etree.fromstring(z.read('word/document.xml'))
    pythoncom.CoInitialize();word=win32.DispatchEx('Word.Application')
    word.Visible=False;word.DisplayAlerts=0;word.ScreenUpdating=False
    try:
        doc=word.Documents.Open(FileName=str(args.docx.resolve()),ReadOnly=True,AddToRecentFiles=False,
                                ConfirmConversions=False,OpenAndRepair=False)
        try:
            assert doc.ReadOnly
            caption_values={};caption_pages={}
            for kind,last in [('TBL',10),('CODE',4),('FIG',1)]:
                for number in range(1,last+1):
                    name=f'BK_{kind}_3_{number:03d}';assert doc.Bookmarks.Exists(name),name
                    rng=doc.Bookmarks(name).Range
                    fields=[f for f in rng.Fields if f.Code.Text.strip().startswith('SEQ ')]
                    assert len(fields)==1,(name,len(fields))
                    if args.resolve:fields[0].Update()
                    value=fields[0].Result.Text.strip();assert value==str(number),(name,value)
                    caption_values[name]={'code':fields[0].Code.Text.strip(),'sequence_value':value,'label':rng.Text}
            for f in doc.Fields:
                code=f.Code.Text.strip()
                if code.startswith('REF ') and any(k in code for k in ['BK_TBL_3_008','BK_TBL_3_009','BK_TBL_3_010','BK_FIG_3_001']):
                    if args.resolve:f.Update()
                    assert not any(s in f.Result.Text for s in ['Error!','Lỗi!']),code
            doc.Repaginate();pagerefs={}
            for n in root.iter(W+'instrText'):
                m=re.match(r'\s*PAGEREF\s+(\S+)',n.text or '')
                if m:
                    assert doc.Bookmarks.Exists(m.group(1)),m.group(1)
                    pagerefs[m.group(1)]=str(doc.Bookmarks(m.group(1)).Range.Information(1))
            assert len(pagerefs)==83
            for name in caption_values:caption_pages[name]=doc.Bookmarks(name).Range.Information(3)
            doc.ExportAsFixedFormat(OutputFileName=str(args.pdf.resolve()),ExportFormat=17,OpenAfterExport=False,
                OptimizeFor=0,CreateBookmarks=1,DocStructureTags=True,BitmapMissingFonts=True,UseISO19005_1=True)
            report={'status':'PASS','open_and_repair':False,'read_only':True,'word_math_count':doc.OMaths.Count,
                'word_field_count':doc.Fields.Count,'caption_sequence_checks':caption_values,'caption_absolute_pages':caption_pages,
                'pageref_results':pagerefs,'source_docx':str(args.docx.resolve()),'document_saved_by_word':False,
                'caption_fields_updated_in_memory':args.resolve,'source_docx_sha256':before}
            assert doc.OMaths.Count==827
            args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({'status':'PASS','caption_sequences_verified':len(caption_values),'pagerefs_resolved':len(pagerefs),'word_field_count':doc.Fields.Count}),flush=True)
        finally:doc.Close(SaveChanges=False)
    finally:word.Quit();pythoncom.CoUninitialize()
    assert hashlib.sha256(args.docx.read_bytes()).hexdigest()==before

if __name__=='__main__':main()
