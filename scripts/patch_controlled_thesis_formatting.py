"""Apply the seven authorized local formatting repairs to the current master."""
from __future__ import annotations
import argparse,copy,hashlib,json,re,sys
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.patch_ch3_limited_clarifications import load,replace_member,canonical,W,M,pageref_slots
from scripts.verify_omml_repair_release import surface,field_types
BASELINE=ROOT/'.tmp/controlled-formatting/baseline.docx'
TARGET=ROOT/'Chuyên đề chuyên sâu.docx'
SHA='d29077dbecb3fff58b417734e0b19e49d271c34750b361c89f534b6d6d15c319'
BODY13=[302,366,402,557,584,596,602,605,645,646,647,652]
XMLSPACE='{http://www.w3.org/XML/1998/namespace}space'

def ensure(parent,tag):
    child=parent.find(W+tag)
    if child is None:child=etree.SubElement(parent,W+tag)
    return child

def run(text=None,rpr=None,code=None,kind=None):
    r=etree.Element(W+'r')
    if rpr is not None:r.append(copy.deepcopy(rpr))
    if text is not None:
        t=etree.SubElement(r,W+'t');t.text=text;t.set(XMLSPACE,'preserve')
    if code is not None:
        t=etree.SubElement(r,W+'instrText');t.text=code;t.set(XMLSPACE,'preserve')
    if kind is not None:etree.SubElement(r,W+'fldChar').set(W+'fldCharType',kind)
    return r

def field(code,result,rpr):
    return [run(rpr=rpr,kind='begin'),run(rpr=rpr,code=code),run(rpr=rpr,kind='separate'),run(result,rpr),run(rpr=rpr,kind='end')]

def replace_reference(p,needle,code,result):
    candidates=[t for t in p.iter(W+'t') if needle in (t.text or '')]
    assert len(candidates)==1,(needle,surface(p))
    t=candidates[0];r=t.getparent();parent=r.getparent();rpr=r.find(W+'rPr')
    assert r.tag==W+'r' and len([c for c in r if c.tag!=W+'rPr'])==1
    before,after=t.text.split(needle,1);at=parent.index(r);parent.remove(r)
    additions=([run(before,rpr)] if before else [])+field(code,result,rpr)+([run(after,rpr)] if after else [])
    for offset,n in enumerate(additions):parent.insert(at+offset,n)

def roman(number):
    out=''
    for value,glyph in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        count,number=divmod(number,value);out+=glyph*count
    return out

def refresh(path):
    root=load(TARGET);record=json.loads(path.read_text(encoding='utf-8'))
    old=pageref_slots(load(BASELINE));slots=pageref_slots(root);changes=[]
    assert len(slots)==len(record['pageref_results'])==83
    for key,texts in slots.items():
        before=''.join(t.text or '' for t in texts);after=record['pageref_results'][key]
        prior=''.join(t.text or '' for t in old.get(key,[]))
        if re.fullmatch('[ivxlcdm]+',prior):after=roman(int(after))
        if before==after:continue
        texts[0].text=after
        for t in texts[1:]:t.text=''
        changes.append({'bookmark':key,'before':before,'after':after})
    replace_member(TARGET,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True))
    (ROOT/'docs/CONTROLLED-FORMATTING-PAGINATION.json').write_text(json.dumps({'status':'PASS','count':len(changes),'changes':changes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pageref_cache_updates':len(changes)}))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--refresh',type=Path);args=parser.parse_args()
    if args.refresh:return refresh(args.refresh)
    assert hashlib.sha256(BASELINE.read_bytes()).hexdigest()==SHA
    assert hashlib.sha256(TARGET.read_bytes()).hexdigest()==SHA
    original=load(BASELINE);root=copy.deepcopy(original);body=root.find(W+'body');b=list(body)
    changes=[];ref_changes=[]
    def note(indices,reason):changes.append({'original_body_indices':indices,'reason':reason})
    for i in list(range(96,107))+BODY13:
        p=b[i];ppr=ensure(p,'pPr');spacing=ensure(ppr,'spacing')
        if i<107:assert spacing.get(W+'line')=='240'
        else:assert any(n.get(W+'val')=='26' for n in p.iter(W+'sz'))
        spacing.set(W+'line','360');spacing.set(W+'lineRule','auto')
        for r in p.iter(W+'r'):
            if any(n.tag in {M+'oMath',M+'oMathPara'} for n in r.iterancestors()):continue
            rp=ensure(r,'rPr');ensure(rp,'sz').set(W+'val','28')
            if i<107:
                fonts=ensure(rp,'rFonts');fonts.set(W+'ascii','Times New Roman');fonts.set(W+'hAnsi','Times New Roman')
    note(list(range(96,107)),'11 prose Lời nói đầu: TNR 14 pt, 1.5; giữ nội dung và indent/căn lề')
    note(BODY13,'12 prose Chương 2–3: 13 → 14 pt, 1.3 → 1.5; không sửa heading/table/code/caption/math')

    # Bookmark names encode the new number; opaque Word TOC identifiers stay
    # with their original object. Rename all links and instructions together.
    renames={'BK_TBL_3_008':'BK_TBL_3_009','BK_TBL_3_009':'BK_TBL_3_010','_Toc_B37b':'_TocCF_Table38'}
    for n in root.iter():
        if n.tag==W+'bookmarkStart' and n.get(W+'name') in renames:n.set(W+'name',renames[n.get(W+'name')])
        if n.tag==W+'hyperlink' and n.get(W+'anchor') in renames:n.set(W+'anchor',renames[n.get(W+'anchor')])
        if n.tag==W+'instrText':
            n.text=re.sub(r'BK_TBL_3_008|BK_TBL_3_009|_Toc_B37b',lambda m:renames[m.group()],n.text or '')

    next_id=max(int(n.get(W+'id')) for n in root.iter(W+'bookmarkStart'))+1
    def bookmark(p,name):
        nonlocal next_id
        value=str(next_id);next_id+=1
        start=etree.SubElement(p,W+'bookmarkStart');start.set(W+'id',value);start.set(W+'name',name)
        return value
    def end(p,value):etree.SubElement(p,W+'bookmarkEnd').set(W+'id',value)
    def caption(index,label,number,identifier,reset=False,template=None,toc_name=None,toc_id=None):
        p=b[index];title=surface(p).split(':',1)[1];source=template if template is not None else p
        pr=copy.deepcopy(source.find(W+'pPr'));rp=copy.deepcopy(next(source.iter(W+'r')).find(W+'rPr'))
        attrs=dict(p.attrib);p.clear();p.attrib.update(attrs)
        if pr is not None:p.append(pr)
        if toc_name:
            if toc_id is None:toc_id=bookmark(p,toc_name)
            else:
                t=etree.SubElement(p,W+'bookmarkStart');t.set(W+'id',toc_id);t.set(W+'name',toc_name)
        value=bookmark(p,f'BK_{identifier}_3_{number:03d}')
        p.append(run(f'{label} 3.',rp))
        sequence='Hình' if identifier=='FIG' else 'Bảng' if identifier=='TBL' else 'ĐoạnMã'
        code=f'SEQ {sequence} '+('\\r 1 ' if reset else '')+'\\* ARABIC '
        for node in field(code,str(number),rp):p.append(node)
        end(p,value);p.append(run(':'+title,rp))
        if toc_name:end(p,toc_id)

    for j,i in enumerate([583,595,601,604],1):caption(i,'Đoạn mã',j,'CODE',reset=j==1)
    note([583,595,601,604],'Đoạn mã 3.1 → 3.4 theo thứ tự xuất hiện; native SEQ; giữ nguyên code và phần mô tả caption')
    caption(648,'Bảng',8,'TBL',template=b[662],toc_name='_TocCF_Table38',toc_id='99')
    caption(651,'Hình',1,'FIG',reset=True,template=b[564],toc_name='_TocCF_Fig31')
    ensure(ensure(b[650],'pPr'),'keepNext')
    ensure(ensure(b[651],'pPr'),'keepLines')
    # Keep the renumbered reproduction table's caption and header with its
    # first data row when the nearby body font correction changes pagination.
    for p in b[649].find(W+'tr').iter(W+'p'):ensure(ensure(p,'pPr'),'keepNext')
    note([650,651],'Hình 3.1: sao chép đúng pPr/rPr caption Hình 2.4, native SEQ và bookmark; giữ ảnh đi cùng caption')
    for i,number in [(662,9),(668,10)]:
        seq=[n for n in b[i].iter(W+'fldChar') if n.get(W+'fldCharType')=='separate'][0]
        texts=[n for n in seq.getparent().itersiblings() if n.find(W+'t') is not None]
        assert texts
        texts[0].find(W+'t').text=str(number)
    note([648,662,668],'Bảng 3.7b/3.8/3.9 → 3.8/3.9/3.10; giữ nguyên nội dung bảng')

    table_map={'3.7b':'3.8','3.8':'3.9','3.9':'3.10'}
    for i in [90,91,92]:
        for t in b[i].iter(W+'t'):t.text=re.sub(r'Bảng 3\.(?:7b|8|9)(?!\d)',lambda m:'Bảng '+table_map[m.group().split(' ')[1]],t.text or '')
    for i,p in enumerate(b):
        if i<573 or i in [648,662,668]:continue
        matches=re.findall(r'Bảng (3\.(?:7b|8|9))(?!\d)',surface(p))
        for old_number in matches:
            new_number=table_map[old_number];target=f'BK_TBL_3_{int(new_number.split(".")[1]):03d}'
            replace_reference(p,'Bảng '+old_number,f'REF {target} \\h ','Bảng '+new_number)
            ref_changes.append({'original_body_index':i,'before':'Bảng '+old_number,'after':'Bảng '+new_number,'target':target})
    replace_reference(b[652],'Hình 3.1','REF BK_FIG_3_001 \\h ','Hình 3.1')
    ref_changes.append({'original_body_index':652,'before':'Hình 3.1','after':'Hình 3.1','target':'BK_FIG_3_001'})

    # Insert inside the existing native TOC field for figures, before its end.
    entry=copy.deepcopy(b[72]);entry.attrib.clear();link=entry.find(W+'hyperlink');link.set(W+'anchor','_TocCF_Fig31')
    for n in link.iter(W+'instrText'):n.text=' PAGEREF _TocCF_Fig31 \\h '
    texts=list(link.iter(W+'t'));assert len(texts)==2
    texts[0].text=surface(b[651]);texts[1].text='104'
    body.insert(body.index(b[73]),entry)
    note([72,73],'Thêm Hình 3.1 vào kết quả danh mục hình native, dùng hyperlink/PAGEREF theo hệ hiện có')

    # Fixed grid and original 10.5 pt table text remain unchanged. Reduce only
    # horizontal cell padding from 6 pt to 1.8 pt to prevent digit wrapping.
    for cell in b[621].iter(W+'tc'):
        margins=ensure(ensure(cell,'tcPr'),'tcMar')
        for side in ['left','right']:ensure(margins,side).set(W+'w','36')
    note([621],'Bảng 3.3: giảm padding ngang 120 → 36 twip; giữ nguyên grid, font, số liệu và OMML header')
    for i in range(76,93):
        spacing=ensure(ensure(b[i],'pPr'),'spacing')
        for key,value in [('before','0'),('after','0'),('line','336'),('lineRule','auto')]:spacing.set(W+key,value)
    note(list(range(76,93)),'Chỉ danh mục bảng: spacing 1.5 → 1.4, Before/After 0; giữ font 11 pt hiện hành')
    assert not surface(b[93]).strip() and len(list(b[93].iter(W+'fldChar')))==1
    assert next(b[93].iter(W+'fldChar')).get(W+'fldCharType')=='end'
    assert b[94].find(W+'pPr/'+W+'sectPr') is not None
    for child in list(b[93]):
        if child.tag!=W+'pPr':b[92].append(child)
    body.remove(b[93])
    note([92,93],'Chuyển field end TOC sang entry cuối, bỏ đoạn đóng field trống có spacing thừa; giữ nguyên field code và section break')
    note([649,651],'Chống tách header bảng tái lập khỏi dữ liệu và chống tách các dòng caption Hình 3.1')
    assert [canonical(n) for n in original.iter(M+'oMath')]==[canonical(n) for n in root.iter(M+'oMath')]
    assert len(list(root.iter(M+'oMath')))==861
    replace_member(TARGET,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True))
    report={'baseline_docx_sha256':SHA,'changes':changes,'reference_changes':ref_changes,
            'field_counts_before':dict(field_types(original)),'field_counts_after':dict(field_types(root)),
            'body13_indices':BODY13,'caption_style_source_original_body_index':564,'bookmark_renames':renames,
            'kept_13pt_heading_indices':[i for i,p in enumerate(b) if p.find(W+'pPr/'+W+'pStyle') is not None and p.find(W+'pPr/'+W+'pStyle').get(W+'val')=='Heading4' and any(n.get(W+'val')=='26' for n in p.iter(W+'sz'))],
            'added_list_paragraph_index':73,'removed_empty_field_end_original_body_index':93}
    (ROOT/'docs/CONTROLLED-FORMATTING-CHANGES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'changes':len(changes),'native_prose_references':len(ref_changes),'fields':report['field_counts_after']},ensure_ascii=False))

if __name__=='__main__':main()
