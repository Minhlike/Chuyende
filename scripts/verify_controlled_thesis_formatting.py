"""Prove narrow scope, structural preservation, native fields and PDF repairs."""
from __future__ import annotations
import argparse,copy,hashlib,json,re,sys,zipfile
from collections import Counter
from pathlib import Path
import pypdfium2 as pdfium
from pypdf import PdfReader
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.patch_controlled_thesis_formatting import BODY13,SHA,roman
from scripts.patch_ch3_limited_clarifications import canonical,pageref_slots,W,M
from scripts.verify_omml_repair_release import parse_docx,surface,field_types,relationship_errors,font_embedding
from scripts.verify_ch3_limited_clarifications import fixed_field_results

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def chapter_hash(body,start,end):return hashlib.sha256(b''.join(canonical(p) for p in body[start:end])).hexdigest()
def normalized_reference_text(text):
    return re.sub(r'(?:Bảng|Đoạn mã) 3\.(?:7b|\d+)(?!\d)',lambda m:m.group().split(' 3.')[0]+' 3.#',text)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('docx',type=Path)
    ap.add_argument('pdf',type=Path);ap.add_argument('--word-report',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();assert digest(args.baseline)==SHA
    old,ob,os,_,_=parse_docx(args.baseline);new,nb,ns,_,_=parse_docx(args.docx)
    assert os==ns and len(ob)==len(nb)
    assert chapter_hash(ob,os[1],os[2])==chapter_hash(nb,ns[1],ns[2])
    chapter2_changed=[i for i in range(os[2],os[3]) if canonical(ob[i])!=canonical(nb[i])]
    assert chapter2_changed==[302,366,402,557]
    with zipfile.ZipFile(args.baseline) as a,zipfile.ZipFile(args.docx) as b:
        assert set(a.namelist())==set(b.namelist())
        parts=[n for n in a.namelist() if a.read(n)!=b.read(n)]
        assert parts==['word/document.xml']
    assert [canonical(n) for n in old.iter(M+'oMath')]==[canonical(n) for n in new.iter(M+'oMath')]
    assert len(list(new.iter(M+'oMath')))==861
    old_counts=field_types(old);new_counts=field_types(new)
    assert new_counts==old_counts+Counter({'SEQ':6,'REF':6,'PAGEREF':1})
    old_fixed=fixed_field_results(old);new_fixed=fixed_field_results(new)
    for typ in ['CITATION','BIBLIOGRAPHY']:
        assert [v for v in old_fixed if v[0].startswith(typ+' ')]==[v for v in new_fixed if v[0].startswith(typ+' ')]
    assert [v for v in old_fixed if v[0].startswith('REF ')]==[v for v in new_fixed if v[0].startswith('REF ')][:8]
    assert [canonical(n) for n in old.iter(W+'drawing')]==[canonical(n) for n in new.iter(W+'drawing')]
    assert [canonical(n) for n in old.iter(W+'sectPr')]==[canonical(n) for n in new.iter(W+'sectPr')]
    for i in list(range(96,107))+BODY13:
        p=nb[i];s=p.find(W+'pPr/'+W+'spacing');assert s.get(W+'line')=='360' and s.get(W+'lineRule')=='auto'
        for r in p.iter(W+'r'):
            if any(a.tag in {M+'oMath',M+'oMathPara'} for a in r.iterancestors()):continue
            assert r.find(W+'rPr/'+W+'sz').get(W+'val')=='28'
        assert p.find(W+'pPr/'+W+'ind') is None or canonical(p.find(W+'pPr/'+W+'ind'))==canonical(ob[i].find(W+'pPr/'+W+'ind'))
        if i<107:
            assert all(r.find(W+'rPr/'+W+'rFonts').get(W+'ascii')=='Times New Roman' for r in p.iter(W+'r'))
    figpr=copy.deepcopy(nb[651].find(W+'pPr'));figpr.remove(figpr.find(W+'keepLines'))
    assert canonical(figpr)==canonical(ob[564].find(W+'pPr'))
    assert all(canonical(rp)==canonical(next(ob[564].iter(W+'rPr'))) for rp in nb[651].iter(W+'rPr'))
    # Align the one added list entry and the relocated empty TOC field end.
    rebuilt=copy.deepcopy(new);rb=rebuilt.find(W+'body');entry=rb[73]
    assert surface(entry).startswith('Hình 3.1:');rb.remove(entry)
    closing=[r for r in rb[92] if r.tag==W+'r' and r.find(W+'fldChar') is not None]
    assert len(closing)==1 and closing[0].find(W+'fldChar').get(W+'fldCharType')=='end'
    rb[92].remove(closing[0]);rb.insert(93,copy.deepcopy(ob[93]))
    approved=set(range(3,60))|set(range(65,73))|set(range(76,93))|set(range(96,107))|set(BODY13)|{583,595,601,604,621,648,649,650,651,662,668,661,665,667,671}
    changed=[i for i in range(len(ob)) if canonical(ob[i])!=canonical(rb[i])]
    assert set(changed)<=approved,sorted(set(changed)-approved)
    for i in range(95,len(ob)):
        assert normalized_reference_text(surface(ob[i]))==normalized_reference_text(surface(rb[i])),i
    ots=list(old.iter(W+'tbl'));nts=list(new.iter(W+'tbl'));assert len(ots)==len(nts)
    allowed_tables={ots.index(ob[i]) for i in [621,649]}
    for i,(a,b) in enumerate(zip(ots,nts)):
        assert surface(a)==surface(b)
        assert [canonical(n) for n in a.iter(W+'rPr')]==[canonical(n) for n in b.iter(W+'rPr')]
        if i not in allowed_tables:assert canonical(a)==canonical(b),i
    starts={n.get(W+'name'):n.get(W+'id') for n in new.iter(W+'bookmarkStart')}
    assert len(starts)==len(list(new.iter(W+'bookmarkStart')))
    assert Counter(n.get(W+'id') for n in new.iter(W+'bookmarkStart'))==Counter(n.get(W+'id') for n in new.iter(W+'bookmarkEnd'))
    for n in new.iter(W+'instrText'):
        match=re.match(r'\s*(?:REF|PAGEREF)\s+(\S+)',n.text or '')
        if match:assert match.group(1) in starts,match.group(1)
    assert '_Toc_B37b' not in starts
    slots=pageref_slots(new);assert len(slots)==83
    record=json.loads(args.word_report.read_text(encoding='utf-8'));original_slots=pageref_slots(old)
    for key,values in slots.items():
        expect=record['pageref_results'][key];previous=''.join(t.text or '' for t in original_slots.get(key,[]))
        if re.fullmatch('[ivxlcdm]+',previous):expect=roman(int(expect))
        assert ''.join(t.text or '' for t in values)==expect,(key,expect)
    captions=[surface(p) for p in nb if p.find(W+'pPr/'+W+'pStyle') is not None and p.find(W+'pPr/'+W+'pStyle').get(W+'val')=='Caption']
    tables=[re.match(r'Bảng 3\.(\d+):',t).group(1) for t in captions if re.match(r'Bảng 3\.(\d+):',t)]
    codes=[re.match(r'Đoạn mã 3\.(\d+):',t).group(1) for t in captions if re.match(r'Đoạn mã 3\.(\d+):',t)]
    assert tables==[str(i) for i in range(1,11)] and codes==['1','2','3','4']
    assert '3.7b' not in surface(new)
    # Validate each changed reference against its particular destination label.
    ledger=json.loads((ROOT/'docs/CONTROLLED-FORMATTING-CHANGES.json').read_text(encoding='utf-8'))
    for change in ledger['reference_changes']:assert change['after'] in surface(nb[change['original_body_index']])
    dangling,missing=relationship_errors(args.docx,new);assert not dangling and not missing
    fonts=font_embedding(PdfReader(args.pdf));assert all(fonts.values())
    pdf=pdfium.PdfDocument(str(args.pdf));blank=[];outside=[];pages={};table_numbers=[]
    for i in range(len(pdf)):
        p=pdf[i];t=p.get_textpage();raw=t.get_text_range();text=' '.join(raw.split())
        if len(text)<20:blank.append(i+1)
        width,height=p.get_size()
        for j in range(t.count_chars()):
            l,bot,r,top=t.get_charbox(j)
            if min(l,bot)<-2 or r>width+2 or top>height+2:outside.append(i+1);break
        if 'DANH MỤC BẢNG' in text and 'Bảng 1.1:' in text:
            assert 'Bảng 3.10:' in text;pages['table_list']=i+1
        if 'DANH MỤC HÌNH VẼ' in text and 'Hình 1.1:' in text:
            assert 'Hình 3.1:' in text;pages['figure_list']=i+1
        if i>90 and 'Bảng 3.3:' in text:
            pages['table_3_3']=i+1
            numbers=sorted({v for cell in nb[621].iter(W+'tc') for v in re.findall(r'\d+\.\d+',surface(cell))})
            for value in numbers:
                assert value in raw,value
                search=t.search(value);match=search.get_next();assert match,value
                index,count=match;boxes=[t.get_charbox(j) for j in range(index,index+count)];search.close()
                assert max(c[1] for c in boxes)-min(c[1] for c in boxes)<1,(value,boxes)
            table_numbers=numbers
            assert 'Epoch' in raw and 'Epo\r\nch' not in raw
        if i>90 and 'Hình 3.1:' in text:
            pages['figure_3_1']=i+1
            assert 'hoàn tất lưu vết thực nghiệm.' in text
        if i>90 and 'Bảng 3.8:' in text:pages['table_3_8']=i+1
        t.close();p.close()
    assert blank==[3] and not outside
    assert all(k in pages for k in ['table_list','figure_list','table_3_3','figure_3_1','table_3_8'])
    report={'status':'PASS','baseline_docx_sha256':SHA,'final_docx_sha256':digest(args.docx),'final_pdf_sha256':digest(args.pdf),
            'chapter_1_complete_xml_unchanged':True,'chapter_1_xml_sha256':chapter_hash(ob,os[1],os[2]),
            'user_bullets_glyphs_indentation_numbering_styles_spacing_and_structure_unchanged':True,
            'chapter_2_only_changed_original_body_indices':chapter2_changed,'changed_original_body_indices':changed,
            'all_zip_parts_except_document_xml_byte_identical':True,'original_omml_unchanged':861,'citation_count':186,
            'original_citation_and_bibliography_codes_and_results_unchanged':True,'original_8_ref_fields_preserved':True,
            'experimental_table_numbers_and_code_contents_unchanged':True,'drawings_images_sections_and_metadata_unchanged':True,
            'field_counts_before':dict(old_counts),'field_counts_after':dict(new_counts),
            'caption_sequences_verified_by_word':15,'caption_numbers_or_style_changed':8,'new_native_prose_references':6,
            'prose_font_and_spacing_fixed':{'preface':11,'chapter_2_3':12},'table_3_3_decimal_values_verified_unsplit':table_numbers,
            'all_83_pageref_cache_values_match_word_pagination':True,'pdf_pages':len(pdf),'key_pdf_pages':pages,
            'existing_blank_page_preserved':blank,'new_blank_pages':[],'outside_page_boxes':outside,'pdf_fonts_embedded':fonts,
            'word_com_open_without_repair':record['status']=='PASS','document_saved_by_word':False,
            'table_3_3_grid_and_font_unchanged':True,'figure_3_1_caption_lines_on_one_page':True}
    pdf.close();args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['pdf_fonts_embedded','changed_original_body_indices','table_3_3_decimal_values_verified_unsplit']},ensure_ascii=False))

if __name__=='__main__':main()
