"""Read Word's physical pagination without saving or updating the source."""
import argparse,json,hashlib
from pathlib import Path
import pythoncom,win32com.client as win32
def page(r,end=False):
    q=r.Duplicate;q.SetRange(r.End-1 if end and r.End>r.Start else r.Start,r.End-1 if end and r.End>r.Start else r.Start)
    return int(q.Information(3))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('docx',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
    before=hashlib.sha256(a.docx.read_bytes()).hexdigest();pythoncom.CoInitialize();word=win32.DispatchEx('Word.Application');word.Visible=False;word.DisplayAlerts=0
    try:
        d=word.Documents.Open(FileName=str(a.docx.resolve()),ReadOnly=True,AddToRecentFiles=False,OpenAndRepair=False)
        try:
            d.Repaginate();sections=[];paragraphs=[];tables=[]
            for s in d.Sections:
                ps=s.PageSetup
                sections.append({'section':s.Index,'start_page':page(s.Range),'end_page':page(s.Range,True),'range':[s.Range.Start,s.Range.End],
                    'start_type':ps.SectionStart,'odd_even_headers':ps.OddAndEvenPagesHeaderFooter,'different_first':ps.DifferentFirstPageHeaderFooter,
                    'text_start':s.Range.Text[:120],'text_end':s.Range.Text[-120:]})
            for i,p in enumerate(d.Content.Paragraphs):
                r=p.Range;txt=r.Text.strip('\r\x07');pf=p.Format
                paragraphs.append({'index':i,'start':r.Start,'end':r.End,'start_page':page(r),'end_page':page(r,True),
                    'style':str(r.Style),'text':txt,'lines':r.ComputeStatistics(1),'keep_next':pf.KeepWithNext,'keep_lines':pf.KeepTogether,
                    'widow':pf.WidowControl,'page_break_before':pf.PageBreakBefore,'before':pf.SpaceBefore,'after':pf.SpaceAfter,
                    'in_table':bool(r.Information(12))})
                if i%150==0:print(f'paragraph {i}',flush=True)
            for i,t in enumerate(d.Tables):
                item={'index':i,'start_page':page(t.Range),'end_page':page(t.Range,True),'rows':[]}
                try:
                    for j,row in enumerate(t.Rows):
                        item['rows'].append({'row':j,'start_page':page(row.Range),'end_page':page(row.Range,True),'header':row.HeadingFormat,'split':row.AllowBreakAcrossPages,'text':row.Range.Text[:100]})
                except Exception as e:item['row_error']=str(e)
                tables.append(item)
            report={'status':'PASS','read_only':True,'open_and_repair':False,'sections':sections,'paragraphs':paragraphs,'tables':tables}
            a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({'paragraphs':len(paragraphs),'sections':sections,'tables':len(tables)},ensure_ascii=False),flush=True)
        finally:d.Close(SaveChanges=False)
    finally:word.Quit();pythoncom.CoUninitialize()
    assert hashlib.sha256(a.docx.read_bytes()).hexdigest()==before
if __name__=='__main__':main()
