"""Freeze reviewed object-specific baseline selectors, never nearest letters.

SCOPES below records the exact original formulas defining each explained object.
The authoring path uses the emitted selectors and hashes, not this search helper.
"""
from __future__ import annotations
import copy, hashlib, json, re, sys, zipfile
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.apply_omml_clarity_repair import added_expressions
from scripts.omml_clarity_math import make_example
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
SCRIPTS={M+x for x in ('sSub','sSup','sSubSup')}
BASELINE_SHA='9bb11639807081f6ee3dafa8907f5293913ffec5697b945993b905ad93a67033'

# Each explicit override names the defining object, not a typographic letter.
# Default scopes contain only the formula being explained at that anchor.
SCOPES={
 127:([127],{'X':[126],'Y':[124]}),
 156:([156],{'d':[154]}),
 164:([164],{'W':[163],'e1':[163],'e2':[163]}),
 165:([165],{'e1':[163],'e2':[163]}),
 166:([166],{'e1':[163],'e2':[163]}),
 168:([168],{}),170:([170],{'⊤':[164]}),
 175:([175],{'e1':[163],'e2':[163],'e3':[163],'eM':[163]}),
 182:([181],{'Tv':[182],'Te':[182]}),
 222:([222],{}),224:([224],{'d':[223]}),234:([234],{}),
 237:([237],{'T':[236],'S':[236]}),239:([239],{}),241:([241],{}),
 245:([245],{'Mem':[239]}),248:([248],{}),251:([251],{}),
 270:([270],{'Retain':[269]}),299:([299],{}),
 303:([303],{'z':[223]}),314:([314],{}),
 326:([325],{'dmodel':[326],'cos':[326]}),330:([330],{}),
 332:([330],{}),337:([337],{'δ':[336]}),
 342:([342],{'dmodel':[343],'I':[168],'h1':[342],'h2':[342]}),
 360:([360],{'log':[337]}),378:([377],{'Msg':[374],'Agg':[376],'Update':[378]}),387:([385],{}),
 395:([395],{'Wm':[394]}),401:([401],{}),416:([416],{}),
 426:([426],{'dproj':[417]}),
 428:([428],{'B':[426]}),
 434:([434],{'C':[431],'B':[426]}),
 441:([441],{}),472:([472],{'stopgrad':[469]}),
 478:([478],{'qseq':[476],'qgraph':[476],'Covevent':[476],
             'Covgraph':[476],'Densityedge':[476],'sseq':[477],
             'sgraph':[477],'log':[337]}),
 482:([482],{'galignproj':[483]}),
 493:([493],{'K':[491],'zbag':[491],'log':[493]}),
 509:([509],{'useq':[504],'ugraph':[504],'ucross':[504],'dcross':[504]}),
 518:([518],{'dproj':[518]}),
}
ALIASES={'φ':'ϕ','ε':'ϵ','εmargin':'ϵmargin','εinv':'ϵinv','⟂':'⊥'}
OBJECTS={
127:'phân phối trôi dạt và biến quan sát/nhãn/biểu diễn',
156:'đầu dò tuyến tính',164:'vector đếm và cửa sổ log',
165:'kho cửa sổ tham chiếu TF-IDF',166:'entropy và loại sự kiện',
168:'phép chiếu PCA / ma trận đơn vị / phần dư',170:'quan hệ bất biến tuyến tính',
175:'tập top-g và họ loại sự kiện e_i',182:'kiểu đỉnh/cạnh và ánh xạ đồ thị',
222:'đối tượng đích thiếu trong bộ sáu sự kiện',224:'bộ nhớ dòng và ánh xạ biểu diễn',234:'biên Utility',237:'biến đổi vô hại và shortcut',
239:'giới hạn tài nguyên theo bước',241:'Utility/PrivacyLoss tại cùng điểm vận hành',245:'thực thể hoạt động / TTL / trạng thái',
248:'watermark và dung sai',251:'chi phí từng thành phần',270:'trường dữ liệu và hàm chuẩn hóa',
299:'khóa giả danh hóa',303:'tham số bảo vệ và biểu diễn hạ nguồn',314:'cửa sổ ngắn/trung/historical',
326:'vector nhúng sự kiện và chiều mô hình',330:'che loại sự kiện',332:'cross-entropy tham số',
337:'khoảng thời gian và Huber',342:'tổng hợp chuỗi có trọng số',360:'suy giảm cạnh theo thời gian',
378:'đỉnh nhận thông điệp',387:'mất mát cạnh',395:'tổng hợp đồ thị',401:'độ phức tạp Bảng 2.2',
416:'chiều không gian chiếu',426:'mất mát invariance',428:'ma trận lô và variance',
434:'ma trận covariance và mất mát ngoài đường chéo',441:'Jaccard và gióng hàng có trọng số',
472:'mất mát tổng Stage A',478:'chỉ báo chất lượng và trọng số dung hợp',482:'gradient PCGrad',
493:'túi MIL',509:'vector dung hợp / tích Hadamard',518:'độ phức tạp Bảng 2.4',
}

def surface(node):return ''.join(t.text or '' for t in node.iter(M+'t'))
def compact(value):return ''.join(value.split()).replace('−','-')
def path(node,root):
    result=[]
    while node is not root:
        parent=node.getparent();result.append(parent.index(node));node=parent
    return list(reversed(result))
def canonical(node):return etree.tostring(node,method='c14n',exclusive=True)
def select(body,anchor,symbol,script=False):
    default,overrides=SCOPES[anchor]
    scopes=overrides.get(symbol,default)
    wanted=ALIASES.get(symbol,symbol)
    if anchor in (164,170) and symbol=='⊤':wanted='T'  # original count-vector transpose
    candidates=[]
    for index in scopes:
        for node in body[index].iter():
            if script:
                if node.tag in SCRIPTS and compact(surface(node))==compact(wanted):
                    candidates.append((index,node,None))
            elif node.tag==M+'r':
                value=surface(node)
                for match in re.finditer(re.escape(wanted),value):
                    # A requested word must be complete; single letters in a
                    # merged formula such as Ax or z+b are intentional spans.
                    if len(wanted)>1 and ((match.start() and value[match.start()-1].isalpha()) or
                          (match.end()<len(value) and value[match.end()].isalpha())):continue
                    if len(wanted)==1 and wanted.isascii():
                        word=next((m.group() for m in re.finditer(r'[A-Za-z]+',value)
                                   if m.start()<=match.start()<m.end()),wanted)
                        if word!=wanted and word not in ('Ax','PP'):continue
                    candidates.append((index,node,[match.start(),match.end()]))
    if not candidates and script and symbol in ('h1','h2','e3'):
        family='hi' if symbol.startswith('h') else 'eM'
        result=select(body,anchor,family,True)
        result['substitution']={'slot':'sub','old':'i' if symbol[0]=='h' else 'M','new':symbol[1:]}
        result['kind']='indexed_example'
        return result
    if not candidates:raise ValueError(f'No object source: anchor={anchor}, symbol={symbol}, scopes={scopes}')
    # These baseline paragraphs contain distinct roles or two local spellings.
    # The selector explicitly names the object in the formula being explained.
    if (anchor,symbol)==(237,'T'):
        candidates=[c for c in candidates if path(c[1],body[c[0]])==[8,0]]
    if (anchor,symbol)==(441,'ρoverlap'):
        candidates=[c for c in candidates if path(c[1],body[c[0]])==[4,2]]
    if not candidates:raise ValueError(f'Reviewed object locator missing: {anchor}, {symbol}')
    index,node,span=candidates[0]
    # All candidates in the first defining formula must have identical style;
    # never resolve a differing mathematical alphabet by textual proximity.
    styles=set()
    for _,candidate,cspan in candidates:
        if script:
            clone=copy.deepcopy(candidate)
            for t in clone.iter(M+'t'):t.text=''
            styles.add(canonical(clone))
        else:
            styles.add(tuple(etree.tostring(p) for p in candidate if p.tag in (M+'rPr',W+'rPr')))
    return {'source_body_index':index,'source_path':path(node,body[index]),
            'source_sha256':hashlib.sha256(canonical(node)).hexdigest(),
            'source_surface':surface(node),'span':span,
            'kind':'symbol' if script else 'run_span',
            'candidate_styles':len(styles)}

def main():
    baseline=ROOT/'.tmp/baseline.docx'
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()==BASELINE_SHA
    with zipfile.ZipFile(baseline) as z:body=etree.fromstring(z.read('word/document.xml')).find(W+'body')
    bindings=[];mixed=[];missing=[]
    token_re=re.compile(r'[A-Za-z]+|[Α-ωϕϵ⟂⊥⊤]')
    for anchor,raw in added_expressions():
        math=make_example(raw);operations=[]
        def checked(symbol,script=False):
            try:return select(body,anchor,symbol,script)
            except ValueError as exc:missing.append(str(exc));return None
        def walk(node):
            for child in list(node):
                if child.tag in SCRIPTS and any(c.isalpha() for c in surface(child.find(M+'e'))):
                    symbol=compact(surface(child))
                    record=checked(symbol,True)
                    if record is None:continue
                    record['target_path']=path(child,math);record['target_surface']=surface(child)
                    operations.append(record);continue
                if child.tag==M+'r':
                    value=surface(child);segments=[]
                    pattern=re.compile(r'[A-Za-z]+|[Α-ωϕϵ⟂⊥⊤]|0') if anchor==170 and raw in ('zero_vector','Ax=0') else token_re
                    for match in pattern.finditer(value):
                        symbol=match.group()
                        if symbol=='Ax':
                            parts=[(match.start(),'A'),(match.start()+1,'x')]
                        elif symbol=='Δt':parts=[(match.start(),'Δ'),(match.start()+1,'t')]
                        else:parts=[(match.start(),symbol)]
                        for start,part in parts:
                            record=checked(part)
                            if record is None:continue
                            record['target_span']=[start,start+len(part)];record['target_surface']=part
                            segments.append(record)
                    if segments:operations.append({'kind':'split_run','target_path':path(child,math),'segments':segments})
                else:walk(child)
        walk(math)
        for operation in operations:
            for record in operation.get('segments',[operation]):
                if record.get('candidate_styles',1)>1:mixed.append((anchor,raw,record['target_surface'],record['source_body_index'],record['source_surface']))
        bindings.append({'anchor':anchor,'expression':raw,'object_context':OBJECTS[anchor],
                         'input_omml_sha256':hashlib.sha256(canonical(math)).hexdigest(),'operations':operations})
    if missing:raise ValueError('\n'.join(sorted(set(missing))))
    if mixed:raise ValueError(f'Unreviewed object ambiguity: {mixed}')
    result={'baseline_sha256':BASELINE_SHA,'selection_policy':'explicit object/formula scopes and frozen XML selectors; no nearest-letter selection',
            'bindings':bindings,'mixed_candidates_to_review':mixed}
    (ROOT/'docs/OMML-OBJECT-SYMBOL-BINDINGS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'expressions':len(bindings),'mixed':mixed},ensure_ascii=False))
if __name__=='__main__':main()
