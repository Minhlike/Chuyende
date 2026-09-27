"""Promote the Word-verified artifact while preserving thesis attribution."""
from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

from lxml import etree

sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / '.tmp/baseline.docx'
WORD = ROOT / '.tmp/wordqa.docx'
PDF = ROOT / '.tmp/wordqa-reopened.pdf'
FINAL_DOCX = ROOT / 'Chuyên đề chuyên sâu.docx'
FINAL_PDF = ROOT / 'Chuyên đề chuyên sâu.pdf'
CORE = 'docProps/core.xml'
CP = 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'
DC = 'http://purl.org/dc/elements/1.1/'
DCT = 'http://purl.org/dc/terms/'

with ZipFile(BASELINE) as z:
    original = etree.fromstring(z.read(CORE))
with ZipFile(WORD) as z:
    current = etree.fromstring(z.read(CORE))
for namespace, name in (
    (DC, 'title'), (DC, 'subject'), (DC, 'creator'),
    (CP, 'lastModifiedBy'), (DCT, 'created'), (CP, 'lastPrinted'),
):
    source = original.find(f'{{{namespace}}}{name}')
    target = current.find(f'{{{namespace}}}{name}')
    if source is not None and target is not None:
        target.text = source.text
revision = current.find(f'{{{CP}}}revision')
original_revision = original.find(f'{{{CP}}}revision')
if revision is not None and original_revision is not None:
    revision.text = str(int(original_revision.text or '0') + 1)
modified = current.find(f'{{{DCT}}}modified')
if modified is not None:
    modified.text = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
new_core = etree.tostring(current, xml_declaration=True, encoding='UTF-8', standalone=True)

with tempfile.NamedTemporaryFile(delete=False, suffix='.docx', dir=ROOT) as temp:
    temporary = Path(temp.name)
try:
    with ZipFile(WORD) as source, ZipFile(temporary, 'w') as dest:
        for info in source.infolist():
            dest.writestr(info, new_core if info.filename == CORE else source.read(info.filename))
    with ZipFile(temporary) as z:
        assert z.testzip() is None
    temporary.replace(FINAL_DOCX)
finally:
    if temporary.exists():
        temporary.unlink()
shutil.copy2(PDF, FINAL_PDF)
print(f'Finalized {FINAL_DOCX.name} and {FINAL_PDF.name}')
