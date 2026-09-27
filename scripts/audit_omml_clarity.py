from __future__ import annotations
import argparse, hashlib, json, re, unicodedata
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS = {'w': W, 'm': M}

def surface(node):
    return ''.join(x.text or '' for x in node.iter() if x.tag in (f'{{{W}}}t', f'{{{M}}}t'))

def top_child(node, body):
    while node.getparent() is not body:
        node = node.getparent()
    return node

def nearest_paragraph(node):
    while node is not None and node.tag != f'{{{W}}}p':
        node = node.getparent()
    return node

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('docx', type=Path)
    ap.add_argument('--json', type=Path, required=True)
    ap.add_argument('--review', type=Path, required=True)
    args = ap.parse_args()
    with ZipFile(args.docx) as z:
        xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    body = root.find(f'{{{W}}}body')
    heading = {}
    chapter = 0
    boundaries = {}
    for i, node in enumerate(body):
        if node.tag == f'{{{W}}}p':
            sty = node.find(f'{{{W}}}pPr/{{{W}}}pStyle')
            style = sty.get(f'{{{W}}}val') if sty is not None else ''
            txt = surface(node).strip()
        else:
            style = ''
            txt = ''
        if style == 'Heading1':
            if 'TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT' in txt:
                chapter = 1; boundaries['ch1'] = i
            elif 'PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG' in txt:
                chapter = 2; boundaries['ch2'] = i
            elif 'THỰC NGHIỆM' in txt:
                chapter = 3; boundaries['ch3'] = i
            heading = {'Heading1': txt}
        elif style in ('Heading2','Heading3','Heading4'):
            level = int(style[-1]); heading = {k:v for k,v in heading.items() if int(k[-1]) < level}; heading[style] = txt
        if chapter not in (1,2):
            continue
        # Each m:oMath is inventoried separately, including inline math and math in table cells.
        for math in node.iter(f'{{{M}}}oMath'):
            p = nearest_paragraph(math)
            plain = surface(math)
            context = surface(p) if p is not None else surface(node)
            para_style = p.find(f'{{{W}}}pPr/{{{W}}}pStyle') if p is not None else None
            kind = 'display' if math.getparent().tag == f'{{{M}}}oMathPara' else 'inline'
            raw = etree.tostring(math, method='c14n')
            yield {
                'id': f'OMML-{chapter}-{main.counts[chapter]+1:03d}',
                'chapter': chapter,
                'heading_path': dict(heading),
                'body_index': i,
                'paragraph_style': para_style.get(f'{{{W}}}val') if para_style is not None else '',
                'kind': kind,
                'in_table': top_child(math,body).tag == f'{{{W}}}tbl',
                'formula_surface': plain,
                'omml_c14n_sha256': hashlib.sha256(raw).hexdigest(),
                'paragraph_context': context,
                'symbol_tokens_surface': [t for t in re.findall(r'[A-Za-zΑ-ω𝒜-𝓏θλσμδϕψϵ]+(?:[0-9]+)?', plain) if t],
                'purpose': 'REVIEW_REQUIRED',
                'symbol_explanations_current': 'REVIEW_REQUIRED',
                'missing_domain_unit_or_intuition': 'REVIEW_REQUIRED',
                'numeric_example_feasible': 'REVIEW_REQUIRED',
                'conceptual_example_if_not_numeric': 'REVIEW_REQUIRED',
                'difficulty': 'REVIEW_REQUIRED',
                'simplification_risk': 'REVIEW_REQUIRED'
            }
            main.counts[chapter] += 1

if __name__ == '__main__':
    # Generator above needs counts initialized before iteration.
    main.counts = Counter()
    parser = argparse.ArgumentParser()
    parser.add_argument('docx', type=Path)
    parser.add_argument('--json', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    a = parser.parse_args()
    records = list(main())
    # Re-read for transparent provenance and global counts.
    with ZipFile(a.docx) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    data = {
        'baseline_docx_sha256': hashlib.sha256(a.docx.read_bytes()).hexdigest(),
        'total_document_omath': len(root.findall(f'.//{{{M}}}oMath')),
        'chapter_1_omath': main.counts[1],
        'chapter_2_omath': main.counts[2],
        'records': records,
    }
    a.json.parent.mkdir(parents=True, exist_ok=True)
    a.json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    lines=[]
    for rec in records:
        sec=' > '.join(rec['heading_path'].values())
        lines.append(f"{rec['id']} | body={rec['body_index']} | {rec['kind']} | table={rec['in_table']} | {sec}")
        lines.append(f"  MATH: {rec['formula_surface']}")
        lines.append(f"  CONTEXT: {rec['paragraph_context'][:850]}")
    a.review.parent.mkdir(parents=True, exist_ok=True)
    a.review.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k!='records'},ensure_ascii=False))
