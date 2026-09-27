from __future__ import annotations
import json,sys,time
sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
from pathlib import Path
import pythoncom
import win32com.client as win32
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'Chuyên đề chuyên sâu.docx'
outdir=ROOT/'.tmp';outdir.mkdir(exist_ok=True)
outdoc=outdir/'wordqa.docx';outpdf=outdir/'wordqa.pdf';reopened_pdf=outdir/'wordqa-reopened.pdf'
for p in (outdoc,outpdf,reopened_pdf):
    if p.exists():p.unlink()
pythoncom.CoInitialize()
word=win32.DispatchEx('Word.Application')
word.Visible=False;word.DisplayAlerts=0;word.ScreenUpdating=False
try:
    print('OPEN',flush=True)
    doc=word.Documents.Open(FileName=str(source),ConfirmConversions=False,ReadOnly=False,AddToRecentFiles=False,OpenAndRepair=False)
    try:
        print('OPENED',doc.Name,'fields',doc.Fields.Count,'math',doc.OMaths.Count,flush=True)
        doc.EmbedTrueTypeFonts=True
        doc.DoNotEmbedSystemFonts=False
        doc.SaveSubsetFonts=True
        # Dynamic references are refreshed in the private QA copy.
        print('FIELD_UPDATE',flush=True)
        for field in list(doc.Fields):
            if not field.Code.Text.strip().upper().startswith('TOC'):
                field.Update()
        for toc in doc.TablesOfContents:toc.Update()
        # The baseline table list contains a manually retained Bảng 3.7b entry;
        # regenerating it would silently drop that valid caption from the list.
        doc.TablesOfFigures(1).Update()
        print('REPAGINATE',flush=True)
        doc.Repaginate()
        pages=doc.ComputeStatistics(2)
        print('SAVE',pages,flush=True)
        doc.SaveAs2(FileName=str(outdoc),FileFormat=16)
        print('PDF_EXPORT',flush=True)
        doc.ExportAsFixedFormat(OutputFileName=str(outpdf),ExportFormat=17,OpenAfterExport=False,OptimizeFor=0,CreateBookmarks=1,DocStructureTags=True,BitmapMissingFonts=True,UseISO19005_1=True)
        doc.Close(SaveChanges=False)
    except:
        doc.Close(SaveChanges=False)
        raise
    print('REOPEN',flush=True)
    reopened=word.Documents.Open(FileName=str(outdoc),ConfirmConversions=False,ReadOnly=True,AddToRecentFiles=False,OpenAndRepair=False)
    try:
        reopened.Repaginate()
        reopened.ExportAsFixedFormat(OutputFileName=str(reopened_pdf),ExportFormat=17,OpenAfterExport=False,OptimizeFor=0,CreateBookmarks=1,DocStructureTags=True,BitmapMissingFonts=True,UseISO19005_1=True)
        record={'status':'PASS','opened_without_repair_api':True,'reopened_without_repair_api':True,'pages_before_save':pages,'pages_immediate_reopen_word_statistic':reopened.ComputeStatistics(2),'fields':reopened.Fields.Count,'math':reopened.OMaths.Count,'docx':str(outdoc),'pdf':str(reopened_pdf),'pdf_bytes':reopened_pdf.stat().st_size}
        print(json.dumps(record,ensure_ascii=False),flush=True)
        (ROOT/'docs/OMML-CLARITY-WORD-COM-QA.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:reopened.Close(SaveChanges=False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
