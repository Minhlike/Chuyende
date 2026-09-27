"""Verify that every added explanation stays together on a Word page."""

from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path

import pythoncom
import win32com.client as win32

sys.stdout.reconfigure(encoding='utf-8')
root = Path(__file__).resolve().parents[1]
source = root / '.tmp/wordqa.docx'
notes = runpy.run_path(str(root / 'scripts/apply_omml_clarity_repair.py'), run_name='audit')['NOTES']


def signature(note: str) -> str:
    pieces = re.split(r'⟦.*?⟧', note)
    return next((piece.strip()[:22] for piece in pieces if len(piece.strip()) >= 16), '')


signatures = {index: signature(note) for index, note in notes.items()}
records = []
matched = set()
pythoncom.CoInitialize()
word = win32.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(FileName=str(source), ReadOnly=True, OpenAndRepair=False, AddToRecentFiles=False)
    try:
        doc.Repaginate()
        for paragraph in doc.Paragraphs:
            content = paragraph.Range.Text.strip()
            ids = [index for index, match in signatures.items() if match and match in content[:200]]
            if not ids:
                continue
            matched.update(ids)
            first = doc.Range(paragraph.Range.Start, paragraph.Range.Start + 1).Information(3)
            last = doc.Range(paragraph.Range.End - 2, paragraph.Range.End - 1).Information(3)
            records.append({'note_ids': ids, 'start_page': first, 'end_page': last})
    finally:
        doc.Close(SaveChanges=False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()

split = [record for record in records if record['start_page'] != record['end_page']]
missing = sorted(set(signatures) - matched)
result = {'status': 'PASS' if not split and not missing and len(matched) == 45 else 'FAIL',
          'note_count': len(notes), 'matched_note_count': len(matched),
          'missing_note_ids': missing, 'split_across_pages': split}
out = root / 'docs/OMML-CLARITY-REPAIR-PAGINATION-QA.json'
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
if result['status'] != 'PASS':
    raise SystemExit(1)
