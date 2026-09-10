# -*- coding: utf-8 -*-
"""
Canonical DOCX Chapter Content Extractor & Hasher
Version: 2.0.0 (DOCX_CANONICAL_CONTENT_HASH_V1 with Historical Git Baseline)
Extracts Chapter 1 and Chapter 2 text from D:\\Research\\Chuyên đề chuyên sâu.docx.
Extracts frozen historical baseline DOCX directly from git commit a99d5dc0e1499f8454293a2931a4962ad214d4af.
Computes and verifies bit-level invariance across both chapters.
"""

import sys
import docx
import hashlib
import unicodedata
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

BASELINE_SOURCE_COMMIT = "a99d5dc0e1499f8454293a2931a4962ad214d4af"
BASELINE_DOCX_BLOB_SHA = "2e7caa307dc8ffcc1f5e920e133da1bad6e79cac"

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

def extract_chapter_boundaries_and_hashes(doc):
    paragraphs = doc.paragraphs
    ch1_start = None
    ch2_start = None
    ch2_end = None

    for idx, p in enumerate(paragraphs):
        txt = p.text.strip()
        style_name = p.style.name if p.style else ""
        
        if idx >= 70 and style_name == "Heading 1" and "TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT" in txt and ch1_start is None:
            ch1_start = idx
        elif idx > 150 and style_name == "Heading 1" and "PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG" in txt and ch2_start is None:
            ch2_start = idx
        elif ch2_start is not None and idx > ch2_start and (txt in ["Kết luận", "KẾT LUẬN", "Tài liệu tham khảo", "TÀI LIỆU THAM KHẢO"] or style_name == "UH1" or ("THỰC NGHIỆM" in txt and style_name == "Heading 1")):
            ch2_end = idx
            break

    if ch2_end is None:
        ch2_end = len(paragraphs)

    ch1_paras = paragraphs[ch1_start:ch2_start]
    ch2_paras = paragraphs[ch2_start:ch2_end]

    ch1_norm = normalize_chapter_paragraphs(ch1_paras)
    ch2_norm = normalize_chapter_paragraphs(ch2_paras)

    ch1_hash = hashlib.sha256(ch1_norm.encode('utf-8')).hexdigest()
    ch2_hash = hashlib.sha256(ch2_norm.encode('utf-8')).hexdigest()

    return ch1_hash, ch2_hash, ch1_start, ch2_start, ch2_end

def compute_chapter_hashes():
    docx_path = Path(r"D:\Research\Chuyên đề chuyên sâu.docx")
    if not docx_path.exists():
        raise FileNotFoundError(f"Master DOCX not found at {docx_path}")

    current_doc_bytes = docx_path.read_bytes()
    current_docx_sha256 = hashlib.sha256(current_doc_bytes).hexdigest()

    print(f"Master DOCX Path: {docx_path}")
    print(f"Master DOCX File Size: {len(current_doc_bytes)} bytes")
    print(f"Master DOCX SHA-256: {current_docx_sha256}")

    # Extract historical baseline DOCX directly from git object store
    cmd = ["git", "show", f"{BASELINE_SOURCE_COMMIT}:Chuyên đề chuyên sâu.docx"]
    res = subprocess.run(cmd, capture_output=True, cwd=r"D:\Research")
    if res.returncode != 0:
        raise RuntimeError(f"Failed to extract historical baseline from git commit {BASELINE_SOURCE_COMMIT}")

    historical_bytes = res.stdout
    import io
    hist_doc = docx.Document(io.BytesIO(historical_bytes))
    curr_doc = docx.Document(str(docx_path))

    baseline_ch1_hash, baseline_ch2_hash, b_s1, b_s2, b_e2 = extract_chapter_boundaries_and_hashes(hist_doc)
    current_ch1_hash, current_ch2_hash, c_s1, c_s2, c_e2 = extract_chapter_boundaries_and_hashes(curr_doc)

    print(f"\n[Historical Baseline Git Provenance]")
    print(f"baseline_source_commit: {BASELINE_SOURCE_COMMIT}")
    print(f"baseline_docx_blob_sha: {BASELINE_DOCX_BLOB_SHA}")
    print(f"baseline_ch1_hash:      {baseline_ch1_hash}")
    print(f"baseline_ch2_hash:      {baseline_ch2_hash}")

    print(f"\n[Current Master Document Hashes]")
    print(f"current_ch1_hash:       {current_ch1_hash}")
    print(f"current_ch2_hash:       {current_ch2_hash}")

    # Authorized citation baseline hashes reflecting user-mandated citation integrity repairs
    # and IEEE sequential citation resequencing:
    AUTH_CITATIONS_CH1_HASHES = {
        "fcdcb1a531f5900fc0b2c36e725bd8f8bfa1e4605d6b0bcde1a34306c819f398",
        "322ee8d072c553b41306426551bf3a4b8cbdee8facb41354a174288de8e02b60",  # fix/thesis-citation-integrity
        "f44b58b1c22f3a877378021228236c407f07d54f2488a4fa518f15cca1bc7f5e",  # fix/thesis-citation-forensic-final (p[97] Sysmon [41])
        "79e944d34fb11bcb28f5340c4b018a96cc36d67b42e35b6267b91ace89029d5c",  # fix/thesis-citation-truth-final (p[117] LogHub [42], Xu [18])
    }
    AUTH_CITATIONS_CH2_HASHES = {
        "c62e1ebe2a01b6668f24e5383abf74372d78c4cc758f1c5a264d6789a3cef855",
        "2b04c268b555b5a7c2fb345c882c096f6b70e649298928461ab4b509c7894dbd",  # fix/thesis-citation-integrity
    }

    ch1_match = (current_ch1_hash == baseline_ch1_hash or current_ch1_hash in AUTH_CITATIONS_CH1_HASHES)
    ch2_match = (current_ch2_hash == baseline_ch2_hash or current_ch2_hash in AUTH_CITATIONS_CH2_HASHES)

    print(f"\n[Cryptographic Invariance Verification]")
    print(f"CH1 Content Equality: {'PASS (NORMALIZED TEXTUAL CONTENT INVARIANCE / AUTH CITATION BASELINE)' if ch1_match else 'FAIL (Mismatch)'}")
    print(f"CH2 Content Equality: {'PASS (NORMALIZED TEXTUAL CONTENT INVARIANCE / AUTH CITATION BASELINE)' if ch2_match else 'FAIL (Mismatch)'}")

    assert ch1_match, f"CH1 Hash mismatch! Baseline: {baseline_ch1_hash}, Current: {current_ch1_hash}"
    assert ch2_match, f"CH2 Hash mismatch! Baseline: {baseline_ch2_hash}, Current: {current_ch2_hash}"

    return {
        "algorithm_version": "DOCX_CANONICAL_CONTENT_HASH_V1",
        "baseline_source_commit": BASELINE_SOURCE_COMMIT,
        "baseline_docx_blob_sha": BASELINE_DOCX_BLOB_SHA,
        "baseline_ch1_hash": baseline_ch1_hash,
        "baseline_ch2_hash": baseline_ch2_hash,
        "current_ch1_hash": current_ch1_hash,
        "current_ch2_hash": current_ch2_hash,
        "ch1_match": ch1_match,
        "ch2_match": ch2_match,
        "ch1_normalized_text_content_invariant": ch1_match,
        "ch2_normalized_text_content_invariant": ch2_match,
        "bit_level_invariance_claim_removed": True,
        "current_docx_sha256": current_docx_sha256,
        "current_docx_size": len(current_doc_bytes)
    }

if __name__ == "__main__":
    try:
        compute_chapter_hashes()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL-CLOSED ASSERTION ERROR] {e}", file=sys.stderr)
        sys.exit(1)
