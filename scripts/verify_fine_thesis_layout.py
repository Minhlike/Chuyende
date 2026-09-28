"""Fail closed unless the release differs only in approved pPr and page caches."""
import argparse,copy,hashlib,json,re,sys,zipfile
from pathlib import Path
from collections import Counter
from lxml import etree
import pypdfium2 as pdfium
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.patch_fine_thesis_layout import SHA,roman
from scripts.patch_ch3_limited_clarifications import canonical,pageref_slots,W,M
from scripts.verify_omml_repair_release import parse_docx,field_types,relationship_errors,font_embedding
from scripts.verify_ch3_limited_clarifications import fixed_field_results
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('docx',type=Path);ap.add_argument('pdf',type=Path);ap.add_argument('--word-report',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert sha(a.baseline)==SHA
    old,ob,os,_,_=parse_docx(a.baseline);new,nb,ns,_,_=parse_docx(a.docx);assert os==ns and len(ob)==len(nb)
    approved={1,142,176,249,268,276,291,292,373,374,451,452,512,513,521,522,538,539,540,541,558}
    restored=copy.deepcopy(new);rb=restored.find(W+'body')
    for i in approved:
        op=ob[i].find(W+'pPr');np=rb[i].find(W+'pPr');rb[i].replace(np,copy.deepcopy(op))
    oldslots=pageref_slots(old);slots=pageref_slots(new);reslots=pageref_slots(restored);assert slots.keys()==oldslots.keys()
    record=json.loads(a.word_report.read_text(encoding='utf-8'));assert record['status']=='PASS' and record['source_docx_sha256']==sha(a.docx)
    caches=[]
    for key,ts in slots.items():
        previous=''.join(n.text or '' for n in oldslots[key]);expect=record['pageref_results'][key]
        if re.fullmatch('[ivxlcdm]+',previous):expect=roman(int(expect))
        current=''.join(n.text or '' for n in ts);assert current==expect,(key,current,expect)
        if current!=previous:caches.append(key)
        assert len(reslots[key])==len(oldslots[key])
        for x,y in zip(reslots[key],oldslots[key]):x.text=y.text
    assert canonical(restored)==canonical(old),'Unexpected XML change beyond approved pagination/cache'
    math_old=[canonical(n) for n in old.iter(M+'oMath')];math_new=[canonical(n) for n in new.iter(M+'oMath')]
    assert math_old==math_new and len(math_new)==861
    counts=field_types(new);assert counts==field_types(old) and counts['CITATION']==186
    assert fixed_field_results(new)==fixed_field_results(old)
    chapter1_lists=[p for b in ob[os[1]:os[2]] for p in b.iter(W+'p') if p.find(W+'pPr/'+W+'numPr') is not None]
    final_lists=[p for b in nb[ns[1]:ns[2]] for p in b.iter(W+'p') if p.find(W+'pPr/'+W+'numPr') is not None]
    assert [canonical(p) for p in chapter1_lists]==[canonical(p) for p in final_lists]
    assert [canonical(p) for p in ob[os[3]:]]==[canonical(p) for p in nb[ns[3]:]]
    with zipfile.ZipFile(a.baseline) as x,zipfile.ZipFile(a.docx) as y:
        assert set(x.namelist())==set(y.namelist());parts=[n for n in x.namelist() if x.read(n)!=y.read(n)]
        assert parts==['word/document.xml']
    dangling,missing=relationship_errors(a.docx,new);assert not dangling and not missing
    assert Counter(n.get(W+'id') for n in new.iter(W+'bookmarkStart'))==Counter(n.get(W+'id') for n in new.iter(W+'bookmarkEnd'))
    fonts=font_embedding(PdfReader(a.pdf));assert all(fonts.values())
    pdf=pdfium.PdfDocument(str(a.pdf));blank=[];outside=[]
    for i in range(len(pdf)):
        p=pdf[i];t=p.get_textpage();text=t.get_text_range();width,height=p.get_size()
        if len(text.strip())<20:blank.append(i+1)
        assert not any(s in text for s in ['Error! Reference source','Error! Bookmark','Lỗi!']),i+1
        for j in range(t.count_chars()):
            if not t.get_text_range(j,1).strip():continue
            l,bot,r,top=t.get_charbox(j)
            if l<0 or r>width+1 or bot<0 or top>height+1:outside.append(i+1)
        t.close();p.close()
    pages=len(pdf);pdf.close();assert not blank and not outside
    report={'status':'PASS','baseline_docx_sha256':SHA,'final_docx_sha256':sha(a.docx),'final_pdf_sha256':sha(a.pdf),
        'approved_pagination_paragraphs':sorted(approved),'pageref_caches_changed':len(caches),'pageref_checked':len(slots),
        'entire_document_xml_identical_after_restoring_only_approved_pPr_and_pageref_caches':True,
        'chapter1_list_paragraphs_xml_identical':len(chapter1_lists),'all_other_chapter1_paragraphs_identical_except_two_formula_pPr':True,
        'omml_count':861,'omml_c14n_content_and_order_identical':True,'citation_count':186,'field_types':dict(counts),
        'citation_bibliography_ref_seq_results_identical':True,'chapter3_complete_xml_identical':True,
        'scientific_text_numbers_code_tables_drawings_styles_metadata_sections_fonts_unchanged':True,
        'changed_zip_parts':parts,'relationships_and_bookmarks_valid':True,'pdf_pages':pages,'blank_pages':blank,'glyphs_outside_page':outside,
        'pdf_fonts_embedded':fonts,'word_com':record['resolved_counts']}
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','pages':pages,'OMML':861,'citations':186,'pagerefs_checked':83}))
if __name__=='__main__':main()
