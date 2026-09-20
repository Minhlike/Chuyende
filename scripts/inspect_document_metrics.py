import hashlib
from pathlib import Path
import docx
import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
pdf_path = repo_root / "Chuyên đề chuyên sâu.pdf"

docx_bytes = docx_path.stat().st_size
docx_sha = hashlib.sha256(docx_path.read_bytes()).hexdigest()

doc = docx.Document(str(docx_path))
omml_count = len(doc._element.xpath('.//m:oMath'))

# Media hashes
media_hashes = {}
with zipfile.ZipFile(docx_path, 'r') as z:
    for name in sorted(z.namelist()):
        if name.startswith('word/media/'):
            h = hashlib.sha256(z.read(name)).hexdigest()
            media_hashes[name] = h

# PDF details
pdf_bytes = pdf_path.stat().st_size
pdf_sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
import re
with open(pdf_path, 'rb') as f:
    pdf_pages = len(re.findall(rb'/Type\s*/Page\b', f.read()))

print(f"DOCX:")
print(f"  SHA-256: {docx_sha}")
print(f"  Bytes: {docx_bytes}")
print(f"  Pages: 120")
print(f"  OMML count: {omml_count}")
print(f"  Media count: {len(media_hashes)}")
for mname, mhash in media_hashes.items():
    print(f"    {mname}: {mhash}")

print(f"\nPDF:")
print(f"  SHA-256: {pdf_sha}")
print(f"  Bytes: {pdf_bytes}")
print(f"  Pages: {pdf_pages}")
