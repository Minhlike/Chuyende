from __future__ import annotations
import argparse, collections, hashlib, json, posixpath, sys, zipfile
from pathlib import Path
from lxml import etree
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_omml_clarity_repair import NOTES, MATH_RE, added_expressions, fix_verified_math
from scripts.omml_clarity_math import make_example
from scripts.omml_source_style import SourceMathStyle
sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'

def sha(x):return hashlib.sha256(x).hexdigest()
def c14n(x):return etree.tostring(x,method='c14n')
def text(x):return ''.join(n.text or '' for n in x.iter() if n.tag in (f'{{{W}}}t',f'{{{M}}}t'))
def body_chapters(body):
    out={}
    for i,node in enumerate(body):
        if node.tag!=f'{{{W}}}p':continue
        style=node.find(f'{{{W}}}pPr/{{{W}}}pStyle')
        if style is None or style.get(f'{{{W}}}val')!='Heading1':continue
        t=text(node)
        if 'TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT' in t:out[1]=i
        elif 'PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG' in t:out[2]=i
        elif 'THỰC NGHIỆM' in t:out[3]=i
    assert set(out)=={1,2,3},out
    assert out[1]<out[2]<out[3]
    return out

def check_rels(z):
    names=set(z.namelist()); dangling=[]
    for name in names:
        if not name.endswith('.rels'):continue
        root=etree.fromstring(z.read(name))
        if name=='_rels/.rels':base=''
        else:
            d,part=posixpath.split(name)
            source=posixpath.join(posixpath.dirname(d),part[:-5])
            base=posixpath.dirname(source)
        for rel in root.findall(f'{{{P}}}Relationship'):
            if rel.get('TargetMode')=='External':continue
            target=rel.get('Target','')
            resolved=posixpath.normpath(posixpath.join(base,target)).lstrip('/')
            if resolved not in names:dangling.append([name,rel.get('Id'),resolved])
    return dangling

def load(path):
    z=zipfile.ZipFile(path)
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith(('.xml','.rels')):etree.fromstring(z.read(name))
    root=etree.fromstring(z.read('word/document.xml'))
    return z,root,root.find(f'{{{W}}}body')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('final',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    bz,br,bb=load(a.baseline);fz,fr,fb=load(a.final)
    bh=body_chapters(bb);fh=body_chapters(fb)
    bmath=list(br.iter(f'{{{M}}}oMath'));fmath=list(fr.iter(f'{{{M}}}oMath'))
    bmath_hash=[sha(c14n(x)) for x in bmath];fmath_hash=[sha(c14n(x)) for x in fmath]
    math_to_body={}
    for i,x in enumerate(bb):
        for m in x.iter(f'{{{M}}}oMath'):math_to_body[id(m)]=i
    corrected_math=[j for j,m in enumerate(bmath) if math_to_body[id(m)] in (332,337)]
    corrected_old=[text(bmath[j]) for j in corrected_math]
    # Original math zones except approved corrections must remain, in original order.
    wanted=[h for j,h in enumerate(bmath_hash) if j not in corrected_math]
    it=iter(fmath_hash)
    math_subsequence=all(any(x==h for x in it) for h in wanted)
    # Original top-level body nodes except two corrections and one layout-only
    # caption adjustment must remain in original order.
    wanted_body=[sha(c14n(x)) for i,x in enumerate(bb) if i not in (332,337,462)]
    it=iter(sha(c14n(x)) for x in fb)
    body_subsequence=all(any(x==h for x in it) for h in wanted_body)
    ch3_base=sha(b''.join(c14n(x) for x in bb[bh[3]:]))
    ch3_final=sha(b''.join(c14n(x) for x in fb[fh[3]:]))
    part_equal=all(bz.read(n)==fz.read(n) for n in bz.namelist() if n!='word/document.xml') and set(bz.namelist())==set(fz.namelist())
    def stat(root):
        return {k:len(root.findall(f'.//{{{W}}}{k}')) for k in ('fldChar','fldSimple','instrText','bookmarkStart','bookmarkEnd','drawing','sectPr')}
    bs,fs=stat(br),stat(fr)
    def bookmarks(root,tag):return collections.Counter(x.get(f'{{{W}}}id') for x in root.findall(f'.//{{{W}}}{tag}'))
    book_ok=bookmarks(br,'bookmarkStart')==bookmarks(fr,'bookmarkStart')==bookmarks(fr,'bookmarkEnd')
    field_ok=collections.Counter(x.text for x in br.findall(f'.//{{{W}}}instrText'))==collections.Counter(x.text for x in fr.findall(f'.//{{{W}}}instrText'))
    final_rels=etree.fromstring(fz.read('word/_rels/document.xml.rels'))
    relids={x.get('Id') for x in final_rels.findall(f'{{{P}}}Relationship')}
    used={v for el in fr.iter() for k,v in el.attrib.items() if k in (f'{{{R}}}id',f'{{{R}}}embed',f'{{{R}}}link')}
    missing_ids=sorted(used-relids)
    math_empty=[j for j,m in enumerate(fmath) if not text(m).strip()]
    math_bad=[j for j,m in enumerate(fmath) if any(c in text(m) for c in ('□','\u200b','\ufffd'))]
    structural_tags={f'{{{M}}}{tag}' for tag in ('f','sSub','sSup','sSubSup','nary','rad','d','m','eqArr','func')}
    def flat_math(math):return not any(node.tag in structural_tags for node in math.iter())
    flat_before=collections.Counter(text(m) for m in bmath if flat_math(m))
    flat_after=collections.Counter(text(m) for m in fmath if flat_math(m))
    added_flat=list((flat_after-flat_before).elements())
    style_root=etree.fromstring(etree.tostring(br))
    style_body=style_root.find(f'{{{W}}}body')
    source_style=SourceMathStyle(style_body)
    added_raw=list(added_expressions())
    expected_new=[source_style.apply(make_example(raw),anchor,raw) for anchor,raw in added_raw]
    permitted_flat=collections.Counter(text(m) for m in expected_new if flat_math(m))
    expected_structured=sum(not flat_math(m) for m in expected_new)
    counts={}
    for ch,a0,e0 in ((1,fh[1],fh[2]),(2,fh[2],fh[3]),(3,fh[3],len(fb))):
        counts[str(ch)]=sum(len(x.findall(f'.//{{{M}}}oMath')) for x in fb[a0:e0])
    report={
      'status':'PASS', 'baseline_sha256':sha(a.baseline.read_bytes()),'final_sha256':sha(a.final.read_bytes()),
      'baseline_math_count':len(bmath),'final_math_count':len(fmath),'added_math_count':len(fmath)-len(bmath),
      'corrected_math_count':len(corrected_math),'corrected_old_surfaces':corrected_old,
      'chapter_math_counts_final':counts,'unchanged_math_in_order':math_subsequence,'unchanged_body_in_order':body_subsequence,
      'chapter_3_xml_sha256_baseline':ch3_base,'chapter_3_xml_sha256_final':ch3_final,'chapter_3_unchanged':ch3_base==ch3_final,
      'all_other_zip_parts_byte_identical':part_equal,'baseline_structure':bs,'final_structure':fs,
      'structure_counts_preserved':bs==fs,'bookmarks_preserved':book_ok,'field_codes_preserved':field_ok,
      'dangling_relationship_targets':check_rels(fz),'missing_document_relationship_ids':missing_ids,
      'empty_math_indexes':math_empty,'bad_math_indexes':math_bad
    }
    report.update({'baseline_structured_math':len(bmath)-sum(map(flat_math,bmath)),
                   'final_structured_math':len(fmath)-sum(map(flat_math,fmath)),
                   'added_flat_simple_math':added_flat,
                   'baseline_display_math_count':len(list(br.iter(f'{{{M}}}oMathPara'))),
                   'final_display_math_count':len(list(fr.iter(f'{{{M}}}oMathPara')))})
    checks=[math_subsequence,body_subsequence,ch3_base==ch3_final,part_equal,bs==fs,book_ok,field_ok,
        len(corrected_math)==2,len(fmath)-len(bmath)==len(expected_new),
        counts=={'1':30+sum(1 for i,_ in added_raw if i<bh[2]),
                 '2':525+sum(1 for i,_ in added_raw if bh[2]<=i<bh[3]),
                 '3':67},
        flat_after-flat_before==permitted_flat,
        report['baseline_structured_math']==516,
        report['final_structured_math']==516+expected_structured,
        report['baseline_display_math_count']==98,report['final_display_math_count']==102,
        not report['dangling_relationship_targets'],not missing_ids,not math_empty,not math_bad]
    if not all(checks):report['status']='FAIL'
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('baseline_structure','final_structure')},ensure_ascii=False))
    if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
