# -*- coding: utf-8 -*-
"""
Canonical DOCX Chapter Content Extractor & Hasher
Version: 1.0.0 (DOCX_CANONICAL_CONTENT_HASH_V1)
Extracts Chapter 1 and Chapter 2 text from D:\\Research\\Chuyên đề chuyên sâu.docx
Normalizes unicode, whitespace, and structural boundaries, and computes immutable SHA-256 hashes.
"""

import sys
import docx
import hashlib
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

def compute_chapter_hashes():
    docx_path = Path(r"D:\Research\Chuyên đề chuyên sâu.docx")
    if not docx_path.exists():
        raise FileNotFoundError(f"Master DOCX not found at {docx_path}")

    doc_bytes = docx_path.read_bytes()
    master_docx_sha256 = hashlib.sha256(doc_bytes).hexdigest()
    print(f"Master DOCX Path: {docx_path}")
    print(f"Master DOCX File Size: {len(doc_bytes)} bytes")
    print(f"Master DOCX SHA-256: {master_docx_sha256}")

    doc = docx.Document(str(docx_path))
    paragraphs = doc.paragraphs

    # Locate Chapter 1 boundary
    # Chapter 1 starts at heading: "TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG..."
    # Chapter 2 starts at heading: "PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG ĐA GÓC NHÌN..."
    # Chapter 2 ends at heading: "Kết luận" or "Tài liệu tham khảo"
    ch1_start = None
    ch2_start = None
    ch2_end = None

    for idx, p in enumerate(paragraphs):
        txt = p.text.strip()
        style_name = p.style.name if p.style else ""
        
        # Chapter 1 starts at Heading 1 after front matter (idx >= 70)
        if idx >= 70 and style_name == "Heading 1" and "TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT" in txt and ch1_start is None:
            ch1_start = idx
        # Chapter 2 starts at Heading 1 after Chapter 1
        elif idx > 150 and style_name == "Heading 1" and "PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG" in txt and ch2_start is None:
            ch2_start = idx
        # Chapter 2 ends at Conclusion or Bibliography heading
        elif ch2_start is not None and idx > ch2_start and (txt in ["Kết luận", "KẾT LUẬN", "Tài liệu tham khảo", "TÀI LIỆU THAM KHẢO"] or style_name == "UH1"):
            ch2_end = idx
            break

    if ch2_end is None:
        ch2_end = len(paragraphs)

    print(f"\n[Boundaries] Chapter 1: Paragraphs {ch1_start}..{ch2_start-1} ({ch2_start - ch1_start} paragraphs)")
    print(f"[Boundaries] Chapter 2: Paragraphs {ch2_start}..{ch2_end-1} ({ch2_end - ch2_start} paragraphs)")

    ch1_paras = paragraphs[ch1_start:ch2_start]
    ch2_paras = paragraphs[ch2_start:ch2_end]

    # Normalization Algorithm: DOCX_CANONICAL_CONTENT_HASH_V1
    # 1. Unicode NFC normalization on each paragraph string
    # 2. Collapse internal whitespace (tabs, consecutive spaces) to single space ' '
    # 3. Strip leading/trailing whitespaces
    # 4. Filter out empty/whitespace-only paragraphs
    # 5. Join non-empty normalized lines with newline '\n'
    # 6. Encode to UTF-8 and compute SHA-256

    def normalize_chapter_paragraphs(paras):
        norm_lines = []
        for p in paras:
            raw_text = p.text
            if not raw_text:
                continue
            nfc_text = unicodedata.normalize('NFC', raw_text).strip()
            if not nfc_text:
                continue
            collapsed_line = ' '.join(nfc_text.split())
            norm_lines.append(collapsed_line)
        return '\n'.join(norm_lines)

    ch1_normalized_text = normalize_chapter_paragraphs(ch1_paras)
    ch2_normalized_text = normalize_chapter_paragraphs(ch2_paras)

    ch1_hash = hashlib.sha256(ch1_normalized_text.encode('utf-8')).hexdigest()
    ch2_hash = hashlib.sha256(ch2_normalized_text.encode('utf-8')).hexdigest()

    print(f"\n[Algorithm: DOCX_CANONICAL_CONTENT_HASH_V1]")
    print(f"CH1_NORMALIZED_LINES: {len(ch1_normalized_text.splitlines())}")
    print(f"CH1_HASH: {ch1_hash}")
    print(f"CH2_NORMALIZED_LINES: {len(ch2_normalized_text.splitlines())}")
    print(f"CH2_HASH: {ch2_hash}")

    # Also compute exact raw paragraph join hash for comparison
    ch1_raw_join = '\n'.join([p.text for p in ch1_paras])
    ch2_raw_join = '\n'.join([p.text for p in ch2_paras])
    ch1_raw_hash = hashlib.sha256(ch1_raw_join.encode('utf-8')).hexdigest()
    ch2_raw_hash = hashlib.sha256(ch2_raw_join.encode('utf-8')).hexdigest()

    print(f"\n[Raw Paragraph String Join Hashes]")
    print(f"CH1_RAW_JOIN_HASH: {ch1_raw_hash}")
    print(f"CH2_RAW_JOIN_HASH: {ch2_raw_hash}")

    return {
        "master_docx_sha256": master_docx_sha256,
        "algorithm_version": "DOCX_CANONICAL_CONTENT_HASH_V1",
        "ch1_start_para": ch1_start,
        "ch1_end_para": ch2_start,
        "ch2_start_para": ch2_start,
        "ch2_end_para": ch2_end,
        "ch1_normalized_hash": ch1_hash,
        "ch2_normalized_hash": ch2_hash,
        "ch1_raw_join_hash": ch1_raw_hash,
        "ch2_raw_join_hash": ch2_raw_hash
    }

if __name__ == "__main__":
    compute_chapter_hashes()
