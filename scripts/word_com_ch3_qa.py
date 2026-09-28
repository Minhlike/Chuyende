"""Render private read-only Word sessions; never let Word rewrite user lists."""
from __future__ import annotations
import argparse, json, re, sys, zipfile
from pathlib import Path
from lxml import etree
import pythoncom
import win32com.client as win32

ROOT=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('docx', type=Path)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--update-pagerefs',action='store_true')
    args=parser.parse_args()
    pythoncom.CoInitialize()
    word=win32.DispatchEx('Word.Application')
    word.Visible=False;word.DisplayAlerts=0;word.ScreenUpdating=False
    try:
        doc=word.Documents.Open(FileName=str(args.docx.resolve()),ConfirmConversions=False,
            ReadOnly=True,AddToRecentFiles=False,OpenAndRepair=False)
        try:
            assert doc.ReadOnly
            doc.Repaginate()
            pagerefs={}
            pending=list(doc.Fields)
            seen=set()
            while pending:
                field=pending.pop()
                identity=(field.Code.Start,field.Code.End,field.Type)
                if identity in seen:continue
                seen.add(identity)
                pending.extend(list(field.Result.Fields))
                code=field.Code.Text.strip()
                match=re.match(r'PAGEREF\s+(\S+)',code)
                if not match:continue
                if args.update_pagerefs:field.Update()
                pagerefs[match.group(1)]=field.Result.Text.strip()
            doc.Repaginate()
            # Word's Fields collection does not expose the nested PAGEREF
            # fields in this document. Resolve their original bookmark targets
            # directly using Word's actual adjusted page numbers instead.
            resolved_from_bookmarks=False
            if args.update_pagerefs and not pagerefs:
                with zipfile.ZipFile(args.docx) as archive:
                    xml=etree.fromstring(archive.read('word/document.xml'))
                ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
                for node in xml.iter(ns+'instrText'):
                    match=re.match(r'\s*PAGEREF\s+(\S+)',node.text or '')
                    if not match:continue
                    target=match.group(1)
                    assert doc.Bookmarks.Exists(target),target
                    pagerefs[target]=str(doc.Bookmarks(target).Range.Information(1))
                resolved_from_bookmarks=True
                assert len(pagerefs)==82,len(pagerefs)
            doc.ExportAsFixedFormat(OutputFileName=str(args.pdf.resolve()),ExportFormat=17,
                OpenAfterExport=False,OptimizeFor=0,CreateBookmarks=1,DocStructureTags=True,
                BitmapMissingFonts=True,UseISO19005_1=True)
            record={'status':'PASS','opened_without_repair_api':True,'read_only':True,
                'word_math_count':doc.OMaths.Count,'word_field_count':doc.Fields.Count,
                'pages_word':doc.ComputeStatistics(2),'pdf_bytes':args.pdf.stat().st_size,
                'source_docx':str(args.docx.resolve()),'pdf':str(args.pdf.resolve()),
                'pagination_fields_updated_in_memory_only':args.update_pagerefs,
                'pageref_values_resolved_from_original_bookmarks':resolved_from_bookmarks,
                'pageref_results':pagerefs,'document_saved_by_word':False}
            assert record['word_math_count']==827 and record['word_field_count']==386
            args.report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({k:v for k,v in record.items() if k!='pageref_results'},ensure_ascii=False),flush=True)
        finally:doc.Close(SaveChanges=False)
    finally:
        word.Quit();pythoncom.CoUninitialize()

if __name__=='__main__':main()
