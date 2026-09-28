"""Add only approved reading aids to Chapter 3 of the user's current master."""
from __future__ import annotations
import argparse, copy, hashlib, json, re, sys, tempfile, zipfile
from pathlib import Path
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
BASELINE_SHA = 'cb6a9f9691d21c98af6c0381049412ed90ad7da268e13cae5ce25dc9c76ca57b'

def load(path):
    with zipfile.ZipFile(path) as z:
        return etree.fromstring(z.read('word/document.xml'))

def canonical(node):
    return etree.tostring(node, method='c14n', exclusive=True)

def replace_member(docx, payload):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx', dir=docx.parent) as temp:
        temporary = Path(temp.name)
    try:
        with zipfile.ZipFile(docx) as src, zipfile.ZipFile(temporary, 'w') as dst:
            for info in src.infolist():
                dst.writestr(info, payload if info.filename == 'word/document.xml' else src.read(info.filename))
        temporary.replace(docx)
    finally:
        if temporary.exists():
            temporary.unlink()

def insert_words(paragraph, needle, addition, *, before=False):
    nodes = list(paragraph.iter(W+'t'))
    joined = ''.join(n.text or '' for n in nodes)
    assert joined.count(needle) == 1, (needle, joined)
    offset = joined.index(needle) + (0 if before else len(needle))
    cursor = 0
    for node in nodes:
        value = node.text or ''
        if cursor <= offset <= cursor + len(value):
            at = offset - cursor
            node.text = value[:at] + addition + value[at:]
            node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            return
        cursor += len(value)
    raise AssertionError('Insertion point not in a text run')

def make_run(text, paragraph):
    run = etree.Element(W+'r')
    template = next((r for r in paragraph.iter(W+'r')
                     if r.find(W+'t') is not None), None)
    if template is not None and template.find(W+'rPr') is not None:
        run.append(copy.deepcopy(template.find(W+'rPr')))
    t = etree.SubElement(run, W+'t')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return run

def pageref_slots(root):
    stack=[];slots={}
    for node in root.iter():
        if node.tag==W+'fldChar':
            kind=node.get(W+'fldCharType')
            if kind=='begin':stack.append({'code':'','result':False,'texts':[]})
            elif kind=='separate' and stack:stack[-1]['result']=True
            elif kind=='end' and stack:
                field=stack.pop()
                match=re.match(r'\s*PAGEREF\s+(\S+)',field['code'])
                if match:
                    assert match.group(1) not in slots
                    slots[match.group(1)]=field['texts']
        elif node.tag==W+'instrText' and stack:
            stack[-1]['code']+=node.text or ''
        elif node.tag==W+'t' and stack and stack[-1]['result']:
            stack[-1]['texts'].append(node)
    assert not stack
    return slots

def refresh_pagination(map_path):
    target=ROOT/'Chuyên đề chuyên sâu.docx'
    root=load(target);body=root.find(W+'body')
    values=json.loads(map_path.read_text(encoding='utf-8'))['pageref_results']
    slots=pageref_slots(root)
    baseline_slots=pageref_slots(load(ROOT/'.tmp/baseline-ch3.docx'))
    assert len(slots)==len(values)==82
    changes=[]
    for bookmark,texts in slots.items():
        old=''.join(t.text or '' for t in texts);new=values[bookmark]
        assert re.fullmatch(r'\d+',new) and texts
        original_format=''.join(t.text or '' for t in baseline_slots[bookmark])
        if re.fullmatch(r'[ivxlcdm]+',original_format):
            remaining=int(new);roman=''
            for value,glyph in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
                count,remaining=divmod(remaining,value);roman+=glyph*count
            new=roman
        if old==new:continue
        paragraph=next(p for p in texts[0].iterancestors(W+'p') if p.getparent() is body)
        assert body.index(paragraph)<111,'Pagination update reached Chapter 1/2'
        texts[0].text=new
        for t in texts[1:]:t.text=''
        changes.append({'bookmark':bookmark,'old':old,'new':new})
    replace_member(target,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True))
    (ROOT/'docs/CH3-LIMITED-PAGINATION-UPDATES.json').write_text(json.dumps({
        'status':'PASS','source':'Microsoft Word bookmark adjusted page numbers',
        'original_field_codes_and_styles_preserved':True,'changes':changes,
    },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pageref_cache_values_updated':len(changes)}))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--refresh-pagination',type=Path)
    args=parser.parse_args()
    if args.refresh_pagination:
        refresh_pagination(args.refresh_pagination)
        return
    target = ROOT/'Chuyên đề chuyên sâu.docx'
    assert hashlib.sha256(target.read_bytes()).hexdigest() == BASELINE_SHA
    original = load(target)
    root = copy.deepcopy(original)
    body = root.find(W+'body')
    baseline = original.find(W+'body')
    assert 'THỰC NGHIỆM' in ''.join(body[573].itertext())
    assert 'Kết luận' == ''.join(body[698].itertext())
    changes = []

    def words(index, location, needle, addition, before=False):
        insert_words(body[index], needle, addition, before=before)
        changes.append({'original_body_index':index, 'location':location,
                        'addition':addition.strip()})

    p = body[599]
    math = next(p.iter(M+'oMath'))
    assert ''.join(math.itertext()) == 'W∈R128×1'
    assert math.getparent() is p
    extra = ' (ở đây là trọng số của bộ phân loại tuyến tính, khác ký hiệu cửa sổ ngữ cảnh ở Chương 2)'
    p.insert(p.index(math)+1, make_run(extra, p))
    changes.append({'original_body_index':599, 'location':'3.1.3 — W của đầu dò tuyến tính', 'addition':extra.strip()})
    words(599, '3.1.3 — lần đầu nêu AP/ROC-AUC', '(ROC-AUC).',
          ' AP đo chất lượng xếp hạng lớp dương và hữu ích khi dữ liệu mất cân bằng; ROC-AUC đo khả năng phân biệt hai lớp trên toàn dải ngưỡng.')
    words(607, '3.1.3 — dẫn chiếu ký hiệu các mất mát Stage A2',
          'ba thành phần tổn thất cục bộ', ' (ký hiệu và định nghĩa chi tiết theo Mục 2.3.3)')

    weight_text = ('Hai hệ số đầu giữ nguyên giá trị hai mất mát tương ứng; hệ số cuối giảm thành phần thời gian '
                   'còn một phần mười trước khi cộng. Các hệ số này không phải tỷ lệ đóng góp thực tế vì các mất mát '
                   'có thể khác thang giá trị.')
    new = etree.Element(W+'p')
    ppr = body[614].find(W+'pPr')
    if ppr is not None:
        new.append(copy.deepcopy(ppr))
        assert new.find(W+'pPr/'+W+'numPr') is None
        if new.find(W+'pPr/'+W+'keepLines') is None:
            etree.SubElement(new.find(W+'pPr'), W+'keepLines')
    new.append(make_run(weight_text, body[614]))

    # Append after the existing native Var(z), leaving the original OMML intact.
    body[632].append(make_run(' Phương sai này đo mức phân tán của biểu diễn ẩn, không tự nó chứng minh mô hình đã tránh sụp đổ biểu diễn.', body[632]))
    changes.append({'original_body_index':632, 'location':'3.2.3 — cách đọc Var(z)',
                    'addition':'Phương sai này đo mức phân tán của biểu diễn ẩn, không tự nó chứng minh mô hình đã tránh sụp đổ biểu diễn.'})
    body[636].append(make_run(' Chênh lệch âm nghĩa là Multi-View kém Sequence trên thước đo tương ứng; biên không thua kém là mức giảm cho phép đã đặt trước.', body[636]))
    changes.append({'original_body_index':636, 'location':'3.2.3 — cách đọc chênh lệch và biên không thua kém',
                    'addition':'Chênh lệch âm nghĩa là Multi-View kém Sequence trên thước đo tương ứng; biên không thua kém là mức giảm cho phép đã đặt trước.'})
    for index in (640, 641):
        words(index, '3.2.3 — trung bình và độ lệch chuẩn mẫu', 'độ lệch chuẩn mẫu',
              ' qua các seed, không phải khoảng tin cậy')
    words(659, '3.3.2 — hai chiều của mục tiêu tham số', 'Trong khi đó,',
          'Chiều đầu đếm sự kiện trong phiên; chiều sau là tối đa bốn khe tham số mỗi sự kiện. ', before=True)
    words(664, '3.3.2 — ngay sau Bảng 3.8', 'Kết quả Bảng 3.8',
          'Cosine càng gần một thì hướng hai vector càng giống nhau; khoảng cách Euclid càng lớn thì hai vector càng cách xa nhau. ', before=True)

    changed = {599, 607, 632, 636, 640, 641, 659, 664}
    assert all(canonical(baseline[i]) == canonical(body[i]) for i in range(len(body)) if i not in changed)
    assert all(canonical(a) == canonical(b) for a,b in zip(original.iter(M+'oMath'),root.iter(M+'oMath')))
    assert len(list(original.iter(M+'oMath'))) == len(list(root.iter(M+'oMath'))) == 861
    body.insert(616, new)
    changes.append({'original_body_index':615, 'location':'3.1.3 — ngay sau công thức mất mát tổng hợp', 'addition':weight_text})
    payload = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    replace_member(target, payload)
    (ROOT/'docs/CH3-LIMITED-CLARIFICATIONS-CHANGES.json').write_text(json.dumps({
        'baseline_docx_sha256':BASELINE_SHA, 'changes':changes,
        'new_paragraphs':1, 'modified_original_paragraphs':8,
        'new_math_zones':0, 'original_math_zones_changed':0,
        'evidence_for_parameter_shape':json.loads((ROOT/'.tmp/ch3-param-shape-evidence.json').read_text(encoding='utf-8')),
    }, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'paragraphs_modified':8, 'paragraphs_added':1, 'original_math_unchanged':861}))

if __name__ == '__main__':
    main()
