"""Check the actual Word-saved DOCX and PDF before either repository is published."""
from __future__ import annotations

import argparse
import sys
import hashlib
import json
import posixpath
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import pypdfium2 as pdfium
from lxml import etree
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
CP = '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}'
DC = '{http://purl.org/dc/elements/1.1/}'
DCT = '{http://purl.org/dc/terms/}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
P = '{http://schemas.openxmlformats.org/package/2006/relationships}'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def surface(element):
    return ''.join(node.text or '' for node in element.iter() if node.tag in (W + 't', M + 't'))


def parse_docx(path):
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            if name.endswith(('.xml', '.rels')):
                etree.fromstring(archive.read(name))
        root = etree.fromstring(archive.read('word/document.xml'))
        core = etree.fromstring(archive.read('docProps/core.xml'))
        font_parts = [name for name in archive.namelist() if name.startswith('word/fonts/')]
    body = list(root.find(W + 'body'))
    starts = {}
    for index, child in enumerate(body):
        style = child.find(W + 'pPr/' + W + 'pStyle')
        if style is None or style.get(W + 'val') != 'Heading1':
            continue
        heading = surface(child)
        for chapter, title in ((1, 'TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT'),
                               (2, 'PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG'),
                               (3, 'THỰC NGHIỆM')):
            if title in heading:
                starts[chapter] = index
    assert set(starts) == {1, 2, 3}
    return root, body, starts, core, font_parts


def field_types(root):
    return Counter((node.text or '').strip().split(' ')[0] for node in root.iter(W + 'instrText'))


def font_embedding(reader):
    fonts = {}
    for page in reader.pages:
        resources = page['/Resources']
        for reference in resources.get('/Font', {}).values():
            font = reference.get_object()
            descriptor = font.get('/FontDescriptor')
            if descriptor is None and font.get('/DescendantFonts'):
                descriptor = font['/DescendantFonts'][0].get_object().get('/FontDescriptor')
            descriptor = descriptor.get_object() if descriptor else {}
            embedded = any(key in descriptor for key in ('/FontFile', '/FontFile2', '/FontFile3'))
            fonts[str(font.get('/BaseFont'))] = embedded
    return fonts


def relationship_errors(path, document_root):
    dangling = []
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        for name in names:
            if not name.endswith('.rels'):
                continue
            relationships = etree.fromstring(archive.read(name))
            if name == '_rels/.rels':
                base = ''
            else:
                folder, rels_name = posixpath.split(name)
                source_part = posixpath.join(posixpath.dirname(folder), rels_name[:-5])
                base = posixpath.dirname(source_part)
            for rel in relationships.findall(P + 'Relationship'):
                if rel.get('TargetMode') == 'External':
                    continue
                target = posixpath.normpath(posixpath.join(base, rel.get('Target', ''))).lstrip('/')
                if target not in names:
                    dangling.append((name, rel.get('Id'), target))
        document_rels = etree.fromstring(archive.read('word/_rels/document.xml.rels'))
    declared = {rel.get('Id') for rel in document_rels.findall(P + 'Relationship')}
    used = {value for element in document_root.iter() for key, value in element.attrib.items()
            if key in (R+'id', R+'embed', R+'link')}
    return dangling, sorted(used - declared)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseline', type=Path)
    parser.add_argument('docx', type=Path)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected-preword', type=Path,
        default=Path(__file__).resolve().parents[1]/'docs/OMML-TYPOGRAPHY-REPAIR-QA-PREWORD.json')
    args = parser.parse_args()
    expected=json.loads(args.expected_preword.read_text(encoding='utf-8'))
    assert expected['status']=='PASS' and expected['baseline_sha256']==digest(args.baseline)
    br, bb, bs, bc, bf = parse_docx(args.baseline)
    fr, fb, fs, fc, ff = parse_docx(args.docx)
    bm = [surface(x) for x in br.iter(M + 'oMath')]
    fm = [surface(x) for x in fr.iter(M + 'oMath')]
    # Index-based exclusion handles duplicate formula surfaces correctly.
    approved = [x for i, x in enumerate(bm) if i not in (209, 219)]
    iterator = iter(fm)
    original_math_preserved = all(any(candidate == x for candidate in iterator) for x in approved)
    ch3_original = ''.join(surface(x) for x in bb[bs[3]:])
    ch3_final = ''.join(surface(x) for x in fb[fs[3]:])
    ch3_math_original = [surface(x) for b in bb[bs[3]:] for x in b.iter(M + 'oMath')]
    ch3_math_final = [surface(x) for b in fb[fs[3]:] for x in b.iter(M + 'oMath')]
    fields_old, fields_new = field_types(br), field_types(fr)
    attribs = (DC+'title', DC+'subject', DC+'creator', CP+'lastModifiedBy', DCT+'created')
    metadata = {key.rsplit('}', 1)[-1]: (bc.find(key).text, fc.find(key).text) for key in attribs}
    pdf = PdfReader(args.pdf)
    pdf_fonts = font_embedding(pdf)
    catalog = pdf.trailer['/Root']
    xmp = catalog['/Metadata'].get_object().get_data().decode('utf-8', 'ignore') if catalog.get('/Metadata') else ''
    pd = pdfium.PdfDocument(str(args.pdf))
    chapter_pages = {}
    for index in range(len(pd)):
        page_text = pd[index].get_textpage().get_text_range()
        for chapter in (1, 2, 3):
            if f'CHƯƠNG {chapter}' in page_text and chapter not in chapter_pages and index > 10:
                chapter_pages[chapter] = index + 1
    start = chapter_pages[1] - 1
    end = chapter_pages[3] - 1
    short_pages = []
    outside_page = []
    for index in range(start, end):
        page = pd[index]
        textpage = page.get_textpage()
        if len(textpage.get_text_range().strip()) < 150:
            short_pages.append(index + 1)
        width, height = page.get_size()
        for char_index in range(textpage.count_chars()):
            left, bottom, right, top = textpage.get_charbox(char_index, loose=True)
            if left < 0 or bottom < 0 or right > width or top > height:
                outside_page.append((index + 1, char_index))
                break
    page10 = pd[9].get_textpage().get_text_range()
    dangling, missing_ids = relationship_errors(args.docx, fr)
    empty_math = [index for index, math in enumerate(fr.iter(M+'oMath')) if not surface(math).strip()]
    chapter_math = {
        chapter: sum(len(list(node.iter(M+'oMath'))) for node in fb[fs[chapter]:fs.get(chapter+1, len(fb))])
        for chapter in (1, 2, 3)
    }
    structural_tags = {M+tag for tag in ('f','sSub','sSup','sSubSup','nary','rad','d','m','eqArr','func')}
    def flat_math(node):
        return not any(child.tag in structural_tags for child in node.iter())
    old_math_nodes=list(br.iter(M+'oMath'))
    new_math_nodes=list(fr.iter(M+'oMath'))
    old_flat=Counter(surface(node) for node in old_math_nodes if flat_math(node))
    new_flat=Counter(surface(node) for node in new_math_nodes if flat_math(node))
    added_flat=list((new_flat-old_flat).elements())
    normalized_flat=lambda value: value.replace('−','-')
    simple_flat=Counter(normalized_flat(value) for value in expected['added_flat_simple_math'])
    observed_flat=Counter(normalized_flat(value) for value in added_flat)
    report = {
        'status': 'PASS', 'docx_sha256': digest(args.docx), 'pdf_sha256': digest(args.pdf),
        'docx_zip_xml_valid': True, 'original_math_zones': len(bm), 'final_math_zones': len(fm),
        'chapter_math_zones_final': chapter_math, 'empty_math_indexes': empty_math,
        'dangling_relationship_targets': dangling, 'missing_document_relationship_ids': missing_ids,
        'unchanged_original_math_surfaces_in_order': original_math_preserved,
        'chapter_3_text_sha256_baseline': hashlib.sha256(ch3_original.encode()).hexdigest(),
        'chapter_3_text_sha256_final': hashlib.sha256(ch3_final.encode()).hexdigest(),
        'chapter_3_text_unchanged': ch3_original == ch3_final,
        'chapter_3_math_unchanged': ch3_math_original == ch3_math_final,
        'field_code_type_counts_baseline': dict(fields_old), 'field_code_type_counts_final': dict(fields_new),
        'bookmark_start_counts': [len(list(br.iter(W+'bookmarkStart'))), len(list(fr.iter(W+'bookmarkStart')))],
        'drawing_counts': [len(list(br.iter(W+'drawing'))), len(list(fr.iter(W+'drawing')))],
        'embedded_docx_font_parts': [len(bf), len(ff)], 'metadata_baseline_and_final': metadata,
        'pdf_pages': len(pdf.pages), 'chapter_start_pdf_pages': chapter_pages,
        'blank_or_nearly_blank_chapter_pages': short_pages, 'text_outside_page_boxes': outside_page,
        'pdfa_1a_xmp': 'pdfaid:part>1' in xmp and 'pdfaid:conformance>A' in xmp,
        'pdf_output_intent_present': bool(catalog.get('/OutputIntents')),
        'pdf_font_embedding': pdf_fonts, 'table_3_7b_in_list': 'Bảng 3.7b' in page10,
        'baseline_structured_math':len(old_math_nodes)-sum(map(flat_math,old_math_nodes)),
        'final_structured_math':len(new_math_nodes)-sum(map(flat_math,new_math_nodes)),
        'added_flat_simple_math':added_flat,
        'baseline_display_math':len(list(br.iter(M+'oMathPara'))),
        'final_display_math':len(list(fr.iter(M+'oMathPara'))),
    }
    conditions = [
        len(bm) == 622, len(fm) == expected['final_math_count'],
        chapter_math == {int(k):v for k,v in expected['chapter_math_counts_final'].items()},
        report['baseline_structured_math']==516,
        report['final_structured_math']==expected['final_structured_math'],
        observed_flat==simple_flat,
        report['baseline_display_math']==98,report['final_display_math']==102,
        not empty_math, not dangling, not missing_ids, original_math_preserved,
        ch3_original == ch3_final, ch3_math_original == ch3_math_final,
        fields_old == fields_new, report['bookmark_start_counts'] == [114, 114],
        report['drawing_counts'][0] == report['drawing_counts'][1],
        report['embedded_docx_font_parts'][0] == report['embedded_docx_font_parts'][1],
        all(a == b for a, b in metadata.values()),
        len(pdf.pages) == len(pd), set(chapter_pages) == {1, 2, 3},
        not short_pages, not outside_page, report['pdfa_1a_xmp'],
        report['pdf_output_intent_present'], all(pdf_fonts.values()),
        report['table_3_7b_in_list'],
    ]
    if not all(conditions): report['status'] = 'FAIL'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key not in ('pdf_font_embedding', 'metadata_baseline_and_final')}, ensure_ascii=False))
    if report['status'] != 'PASS': raise SystemExit(1)


if __name__ == '__main__': main()
