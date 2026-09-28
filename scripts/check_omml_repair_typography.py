"""Audit actual Word-saved explanation math against the original OMML styles."""
from __future__ import annotations
import argparse, json, re, sys, unicodedata, zipfile
from pathlib import Path
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.apply_omml_clarity_repair import (NOTES, MATH_RE, DISPLAY_EXAMPLES,
    paragraphs, fix_verified_math, added_expressions)
from scripts.omml_source_style import SourceMathStyle, key, surface

W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
sys.stdout.reconfigure(encoding='utf-8')

def load(path):
    with zipfile.ZipFile(path) as archive:
        return etree.fromstring(archive.read('word/document.xml'))

def text(node):
    return ''.join(t.text or '' for t in node.iter() if t.tag in (W+'t',M+'t'))

def style(run):
    prop=run.find(M+'rPr')
    alphabet='roman'; appearance='i'
    if prop is not None:
        scr=prop.find(M+'scr'); sty=prop.find(M+'sty'); nor=prop.find(M+'nor')
        if scr is not None: alphabet=scr.get(M+'val')
        if sty is not None: appearance=sty.get(M+'val')
        if nor is not None: appearance='p'
    return alphabet,appearance

def letters(node):
    # Word may merge adjacent runs; compare the actual mathematical alphabet
    # and italic/bold/upright state of each symbolic letter independently.
    return [(key(char),*style(run)) for run in node.iter(M+'r')
            for char in surface(run) if char.isalpha()]

def scripts(node):
    result=[]
    for child in node.iter():
        if child.tag not in (M+'sSub',M+'sSup',M+'sSubSup'): continue
        slots=[]
        for slot in ('e','sub','sup'):
            item=child.find(M+slot)
            if item is not None: slots.append((slot,key(surface(item)),letters(item)))
        result.append((etree.QName(child).localname,slots))
    return result

def signature(note):
    return next(chunk.strip()[:22] for chunk in re.split(r'⟦.*?⟧',note) if len(chunk.strip())>=16)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('baseline',type=Path);parser.add_argument('docx',type=Path)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    source=load(args.baseline);body=source.find(W+'body')
    fix_verified_math(body[332].find('.//'+M+'oMath'),body[337].find('.//'+M+'oMath'))
    styler=SourceMathStyle(body)
    final=load(args.docx);all_paragraphs=list(final.iter(W+'p'))
    source_font={font.get(W+'ascii') for font in source.iter(W+'rFonts')
                 if any(parent.tag.startswith(M) for parent in font.iterancestors())}
    defects=[];matched=[];checked_math=0;checked_runs=0
    for anchor,note in NOTES.items():
        sig=signature(note)
        found=[i for i,p in enumerate(all_paragraphs) if sig in text(p)[:300]]
        if len(found)!=1:
            defects.append({'anchor':anchor,'reason':'note_not_unique','matches':len(found)});continue
        first=found[0];matched.append(anchor)
        expected=paragraphs(note,body[165].find(W+'pPr'),body[166].find(W+'pPr'),
                            anchor=anchor,source_style=styler)
        actual=all_paragraphs[first:first+len(expected)]
        em=[math for p in expected for math in p.iter(M+'oMath')]
        am=[math for p in actual for math in p.iter(M+'oMath')]
        if len(em)!=len(am):
            defects.append({'anchor':anchor,'reason':'math_count','expected':len(em),'actual':len(am)});continue
        for i,(original,word_saved) in enumerate(zip(em,am)):
            if letters(original)!=letters(word_saved) or scripts(original)!=scripts(word_saved):
                defects.append({'anchor':anchor,'math_index':i,'reason':'symbol_typography_or_script_position',
                                'expected':surface(original),'actual':surface(word_saved)})
            for run in word_saved.iter(M+'r'):
                checked_runs+=1
                for font in run.iter(W+'rFonts'):
                    if font.get(W+'ascii') not in source_font or font.get(W+'hAnsi') not in source_font:
                        defects.append({'anchor':anchor,'reason':'math_font','font':font.get(W+'ascii')})
            checked_math+=1
        for p in actual:
            prose=''.join(t.text or '' for t in p.iter(W+'t'))
            fake=[char for char in prose if any(term in unicodedata.name(char,'') for term in ('SUBSCRIPT','SUPERSCRIPT'))]
            if fake or re.search(r'\b[A-Za-z]+_[A-Za-z0-9]',prose):
                defects.append({'anchor':anchor,'reason':'math_notation_in_plain_text','glyphs':fake})
    final_text=text(final)
    for label in ('Ví dụ minh họa','Ví dụ khái niệm'):
        if label in final_text: defects.append({'reason':'old_example_label','label':label})
    expected_count=sum(1 for _ in added_expressions())
    if checked_math!=expected_count:
        defects.append({'reason':'total_added_math_count','expected':expected_count,'checked':checked_math})
    report={'status':'FAIL' if defects else 'PASS','notes_expected':len(NOTES),'notes_matched':len(matched),
            'added_math_zones_checked':checked_math,'math_runs_checked':checked_runs,
            'original_math_font':sorted(source_font),'old_example_labels_present':False,
            'source_typography_and_subscript_superscript_positions_match':not defects,
            'defects':defects}
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if defects:raise SystemExit(1)

if __name__=='__main__':main()
