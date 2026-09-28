"""Resolve every native REF/SEQ/PAGEREF, export, and close without rewriting XML."""
import argparse,hashlib,json,re,zipfile
from pathlib import Path
from lxml import etree
import pythoncom,win32com.client as win32
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('docx',type=Path);ap.add_argument('pdf',type=Path);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
    before=hashlib.sha256(a.docx.read_bytes()).hexdigest()
    with zipfile.ZipFile(a.docx) as z:root=etree.fromstring(z.read('word/document.xml'))
    print('starting Word automation',flush=True)
    pythoncom.CoInitialize();word=win32.DispatchEx('Word.Application');word.Visible=False;word.DisplayAlerts=0
    print('opening current DOCX read-only',flush=True)
    try:
        d=word.Documents.Open(FileName=str(a.docx.resolve()),ReadOnly=True,AddToRecentFiles=False,OpenAndRepair=False)
        try:
            print('repaginating',flush=True);d.Repaginate();resolved=[];pagerefs={}
            # Index access avoids a live COM enumerator changing while fields update.
            for index in range(1,d.Fields.Count+1):
                f=d.Fields.Item(index)
                code=f.Code.Text.strip();kind=code.split()[0] if code else ''
                if kind in {'REF','SEQ','PAGEREF'}:
                    previous=f.Result.Text;f.Update();result=f.Result.Text
                    assert not any(s in result for s in ['Error!','Lỗi!','Error:']), (code,result)
                    if kind!='PAGEREF':assert previous.strip()==result.strip(),(code,previous,result)
                    resolved.append({'type':kind,'code':code,'result':result.strip(),'absolute_page':int(f.Result.Information(3))})
            for n in root.iter(W+'instrText'):
                m=re.match(r'\s*PAGEREF\s+(\S+)',n.text or '')
                if m:
                    assert d.Bookmarks.Exists(m[1]),m[1]
                    pagerefs[m[1]]=str(d.Bookmarks(m[1]).Range.Information(1))
            assert len(pagerefs)==83
            counts={t:sum(x['type']==t for x in resolved) for t in ['REF','SEQ','PAGEREF']}
            assert counts=={'REF':14,'SEQ':30,'PAGEREF':83},counts
            print('exporting PDF',flush=True)
            d.ExportAsFixedFormat(OutputFileName=str(a.pdf.resolve()),ExportFormat=17,OpenAfterExport=False,OptimizeFor=0,
                CreateBookmarks=1,DocStructureTags=True,BitmapMissingFonts=True,UseISO19005_1=True)
            report={'status':'PASS','source_docx_sha256':before,'read_only':True,'open_and_repair':False,'word_saved_source':False,
                'reason_no_word_save':'Bảo toàn XML bullet/OMML; cập nhật field trong bộ nhớ và cache PAGEREF có kiểm soát bằng OOXML.',
                'word_math_count':d.OMaths.Count,'word_field_count':d.Fields.Count,'resolved_counts':counts,'resolved_fields':resolved,'pageref_results':pagerefs}
            assert d.OMaths.Count==827 and d.Fields.Count==400
            a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','resolved_counts':counts}),flush=True)
        finally:d.Close(SaveChanges=False)
    finally:word.Quit();pythoncom.CoUninitialize()
    assert hashlib.sha256(a.docx.read_bytes()).hexdigest()==before
if __name__=='__main__':main()
