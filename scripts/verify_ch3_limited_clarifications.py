"""Verify the narrow Chapter 3 edit against the user's current Word baseline."""
from __future__ import annotations
import argparse, copy, hashlib, json, re, sys, zipfile
from collections import Counter
from pathlib import Path
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.patch_ch3_limited_clarifications import canonical,pageref_slots,W,M,BASELINE_SHA
from scripts.verify_omml_repair_release import parse_docx,field_types,relationship_errors,font_embedding,surface
from pypdf import PdfReader
import pypdfium2 as pdfium

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def region(body,start,end):return hashlib.sha256(b''.join(canonical(n) for n in body[start:end])).hexdigest()

def fixed_field_results(root):
    stack=[];results=[]
    for node in root.iter():
        if node.tag==W+'fldChar':
            kind=node.get(W+'fldCharType')
            if kind=='begin':stack.append({'code':'','result':False,'texts':[]})
            elif kind=='separate' and stack:stack[-1]['result']=True
            elif kind=='end' and stack:
                field=stack.pop();code=field['code'].strip()
                if code.split(' ',1)[0] in {'CITATION','BIBLIOGRAPHY','REF','SEQ'}:
                    results.append((code,''.join(field['texts'])))
        elif node.tag==W+'instrText' and stack:stack[-1]['code']+=node.text or ''
        elif node.tag in {W+'t',M+'t'} and stack and stack[-1]['result']:
            stack[-1]['texts'].append(node.text or '')
    assert not stack
    return results

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('baseline',type=Path);parser.add_argument('docx',type=Path)
    parser.add_argument('pdf',type=Path);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    assert sha(args.baseline)==BASELINE_SHA
    old,ob,os,oc,of=parse_docx(args.baseline)
    new,nb,ns,nc,nf=parse_docx(args.docx)
    assert os==ns and os[3]==573
    chapter_hashes={}
    for chapter,end in [(1,os[2]),(2,os[3])]:
        before=region(ob,os[chapter],end);after=region(nb,ns[chapter],end)
        assert before==after
        chapter_hashes[str(chapter)]={'baseline_xml_sha256':before,'final_xml_sha256':after}
    with zipfile.ZipFile(args.baseline) as a,zipfile.ZipFile(args.docx) as b:
        assert set(a.namelist())==set(b.namelist())
        altered=[name for name in a.namelist() if a.read(name)!=b.read(name)]
        assert altered==['word/document.xml'],altered
    om=list(old.iter(M+'oMath'));nm=list(new.iter(M+'oMath'))
    assert len(om)==len(nm)==861 and [canonical(x) for x in om]==[canonical(x) for x in nm]
    assert not [x for x in nm if not surface(x).strip()]
    assert field_types(old)==field_types(new)
    assert fixed_field_results(old)==fixed_field_results(new)
    assert [canonical(n) for n in old.iter(W+'instrText')]==[canonical(n) for n in new.iter(W+'instrText')]
    for tag in ['bookmarkStart','bookmarkEnd','fldChar','drawing','tbl','sectPr']:
        assert [canonical(n) for n in old.iter(W+tag)]==[canonical(n) for n in new.iter(W+tag)],tag
    assert len(nb)==len(ob)+1
    rebuilt=copy.deepcopy(new);rb=rebuilt.find(W+'body')
    added=rb[616]
    assert surface(added).startswith('Hai hệ số đầu giữ nguyên')
    rb.remove(added)
    old_slots=pageref_slots(old);rebuilt_slots=pageref_slots(rebuilt)
    assert set(old_slots)==set(rebuilt_slots) and len(old_slots)==82
    pager_changes=[]
    for key,texts in old_slots.items():
        other=rebuilt_slots[key]
        assert len(texts)==len(other)
        if [t.text for t in texts]!=[t.text for t in other]:
            pager_changes.append(key)
        for a,b in zip(texts,other):b.text=a.text
    approved={599,607,632,636,640,641,659,664}
    changed=[i for i in range(len(ob)) if canonical(ob[i])!=canonical(rb[i])]
    assert set(changed)==approved,changed
    numbers=lambda v:Counter(re.findall(r'\d+(?:[.,]\d+)*',v))
    prior_numbers=numbers(''.join(surface(x) for x in ob[573:698]))
    final_numbers=numbers(''.join(surface(x) for x in nb[573:699]))
    assert final_numbers==prior_numbers+Counter({'2':1,'2.3.3':1})
    dangling,missing=relationship_errors(args.docx,new)
    assert not dangling and not missing
    reader=PdfReader(args.pdf);fonts=font_embedding(reader)
    assert all(fonts.values())
    pdf=pdfium.PdfDocument(str(args.pdf));outside=[];empty=[]
    for i in range(len(pdf)):
        page=pdf[i];tp=page.get_textpage();txt=tp.get_text_range()
        if i>=98 and len(txt.strip())<40:empty.append(i+1)
        width,height=page.get_size()
        for j in range(tp.count_chars()):
            left,bottom,right,top=tp.get_charbox(j)
            if min(left,bottom)<-2 or right>width+2 or top>height+2:
                outside.append([i+1,j]);break
        tp.close();page.close()
    assert not outside and not empty
    report={'status':'PASS','baseline_docx_sha256':BASELINE_SHA,
        'final_docx_sha256':sha(args.docx),'final_pdf_sha256':sha(args.pdf),
        'chapter_1_2_complete_xml_unchanged':True,'chapter_xml_hashes':chapter_hashes,
        'all_existing_bullets_styles_indentation_numbering_glyphs_preserved':True,
        'numbering_styles_headers_footers_metadata_fonts_relationship_parts_byte_identical':True,
        'changed_zip_parts':altered,'original_paragraphs_changed':changed,
        'paragraphs_added':1,'original_omml_unchanged':len(om),'omml_added':0,
        'original_formulae_and_numbers_unchanged':True,'added_numeric_text_only':'references to Chapter 2 and section 2.3.3',
        'all_tables_figures_sections_and_field_codes_unchanged':True,
        'citation_bibliography_ref_and_sequence_field_results_unchanged':True,
        'field_type_counts':dict(field_types(new)),'citation_count':field_types(new)['CITATION'],
        'pageref_cache_results_updated':len(pager_changes),
        'dangling_relationships':dangling,'missing_relationship_ids':missing,
        'pdf_pages':len(pdf),'pdf_fonts_embedded':fonts,
        'blank_or_nearly_blank_pages':empty,'outside_page_boxes':outside}
    pdf.close()
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='pdf_fonts_embedded'},ensure_ascii=False))

if __name__=='__main__':main()
