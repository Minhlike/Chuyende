"""Audit every added note against original Word transpose OMML sources."""
from __future__ import annotations
import argparse, hashlib, json, sys, zipfile
from pathlib import Path
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.apply_omml_clarity_repair import NOTES, paragraphs
from scripts.check_omml_repair_typography import signature, text
from scripts.omml_source_style import SourceMathStyle, surface, canonical, M, W

BASELINE_SHA = '9bb11639807081f6ee3dafa8907f5293913ffec5697b945993b905ad93a67033'
# Exact defining formulas, reviewed by object; never search other formulas
# for a visually similar operator. Ax=0 has no transpose itself: its numeric
# count-vector examples use the original definition of that vector at 164.
SOURCES = {
    156: (156, 'W', 'linear-probe weight transpose'),
    164: (164, 'ce1, ce2, …, ceM', 'original count-vector definition'),
    168: (168, 'P', 'PCA transpose convention in the explained formula'),
    170: (164, 'ce1, ce2, …, ceM', 'same count vector defined before Ax=0'),
}

def load(path):
    with zipfile.ZipFile(path) as archive:
        return etree.fromstring(archive.read('word/document.xml'))

def transposes(node):
    for item in node.iter():
        if item.tag in (M+'sSup', M+'sSubSup'):
            sup = item.find(M+'sup')
            if sup is not None and surface(sup) in ('T', '⊤', 'ᵀ'):
                yield item

def xpath(node):
    return node.getroottree().getpath(node)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseline', type=Path)
    parser.add_argument('docx', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert hashlib.sha256(args.baseline.read_bytes()).hexdigest() == BASELINE_SHA
    original = load(args.baseline)
    body = original.find(W+'body')
    final = load(args.docx)
    all_paragraphs = list(final.iter(W+'p'))
    styler = SourceMathStyle(body)
    audit, defects = [], []
    for anchor, note in NOTES.items():
        matches = [i for i,p in enumerate(all_paragraphs)
                   if signature(note) in text(p)[:300]]
        assert len(matches) == 1, (anchor, matches)
        expected = paragraphs(note, body[165].find(W+'pPr'), body[166].find(W+'pPr'),
                              anchor=anchor, source_style=styler)
        actual = all_paragraphs[matches[0]:matches[0]+len(expected)]
        maths = [math for p in actual for math in p.iter(M+'oMath')]
        record = {'anchor': anchor, 'note': text(actual[0]),
                  'native_math_zones': len(maths), 'transposes': []}
        for p in actual:
            if any(char in ''.join(p.itertext()) for char in ('ᵀ', 'ᵗ')):
                defects.append({'anchor': anchor, 'reason': 'fake_transpose_glyph'})
            prose = ''.join(t.text or '' for t in p.iter(W+'t'))
            if '⊤' in prose:
                defects.append({'anchor': anchor, 'reason': 'transpose_outside_native_math'})
        for math in maths:
            for transpose in transposes(math):
                assert anchor in SOURCES, ('Unreviewed transpose source', anchor)
                source_anchor, source_base, reason = SOURCES[anchor]
                candidates = [s for s in transposes(body[source_anchor])
                              if surface(s.find(M+'e')) == source_base]
                assert len(candidates) == 1, (anchor, candidates)
                source_sup = candidates[0].find(M+'sup')
                actual_sup = transpose.find(M+'sup')
                entry = {'base': surface(transpose.find(M+'e')),
                         'actual_glyph': surface(actual_sup),
                         'original_glyph': surface(source_sup),
                         'source_body_index': source_anchor,
                         'source_xpath': xpath(source_sup),
                         'source_reason': reason,
                         'source_sup_sha256': hashlib.sha256(canonical(source_sup)).hexdigest(),
                         'native_sup_xpath': xpath(actual_sup),
                         'exact_sup_xml_matches': canonical(actual_sup) == canonical(source_sup)}
                record['transposes'].append(entry)
                if not entry['exact_sup_xml_matches']:
                    defects.append({'anchor': anchor, **entry})
        audit.append(record)
    count = sum(len(r['transposes']) for r in audit)
    assert len(audit) == 45 and sum(r['native_math_zones'] for r in audit) == 239
    assert count == 8, ('Unreviewed transpose count', count)
    report = {'status': 'FAIL' if defects else 'PASS',
              'baseline_docx_sha256': BASELINE_SHA,
              'docx_sha256': hashlib.sha256(args.docx.read_bytes()).hexdigest(),
              'notes_reviewed': len(audit), 'new_native_omml_zones_reviewed': 239,
              'transpose_operators_reviewed': count, 'mismatch_count': len(defects),
              'source_policy': 'Exact original OMML superscript from the defining formula for the same mathematical object',
              'formula_without_explicit_transpose': {'anchor':170, 'formula':'Ax=0',
                  'reason':'Numeric x is the count vector already defined at original paragraph 164; no unrelated formula or glyph similarity is used.'},
              'positions_changed': [], 'notes': audit, 'defects': defects}
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('notes', 'formula_without_explicit_transpose')}, ensure_ascii=False))
    if defects: raise SystemExit(1)

if __name__ == '__main__':
    main()
