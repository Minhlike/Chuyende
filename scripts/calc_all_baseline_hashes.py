import hashlib
import sys
from pathlib import Path

code_path = Path("src/research_agent/composition/build_word_visual_qa.py")
lines = code_path.read_text(encoding="utf-8").splitlines()

s1 = [i for i, l in enumerate(lines) if 'add_h1("TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT' in l][0]
s2 = [i for i, l in enumerate(lines) if 'add_h1("PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG' in l][0]
s3 = [i for i, l in enumerate(lines) if 'add_h1("KẾT LUẬN' in l][0]

ch1_block = "\n".join(lines[s1:s2])
ch2_block = "\n".join(lines[s2:s3])

h1 = hashlib.sha256(ch1_block.encode("utf-8")).hexdigest()
h2 = hashlib.sha256(ch2_block.encode("utf-8")).hexdigest()

print(f"CH1: lines {s1+1}..{s2} ({s2-s1} lines) SHA256: {h1}")
print(f"CH2: lines {s2+1}..{s3} ({s3-s2} lines) SHA256: {h2}")

for p in sorted(Path(".").glob("*.docx")):
    h_docx = hashlib.sha256(p.read_bytes()).hexdigest()
    print(f"DOCX {p.name} ({p.stat().st_size} bytes) SHA256: {h_docx}")
