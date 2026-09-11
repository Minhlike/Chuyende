# -*- coding: utf-8 -*-
"""
Chapter Hash Provenance and Diff Ledger Auditor

Audits Chapter 1 and Chapter 2 text transformation against the immutable
historical baseline from authority commit a99d5dc0e1499f8454293a2931a4962ad214d4af.
Guarantees non-circular hash validation:
- baseline is immutable and external from git object store;
- modifications are strictly governed by APPROVED-SCIENTIFIC-EDIT-LEDGER.json;
- verifies 100% of diff hunks match approved ledger entries;
- outputs CHAPTER-DIFF-LEDGER-VERIFICATION.json.
"""

import sys
import io
import docx
import hashlib
import unicodedata
import subprocess
import json
import difflib
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

BASELINE_SOURCE_COMMIT = 'a99d5dc0e1499f8454293a2931a4962ad214d4af'
BASELINE_DOCX_BLOB_SHA = '2e7caa307dc8ffcc1f5e920e133da1bad6e79cac'

def normalize_text(text):
    if not text:
        return ''
    nfc = unicodedata.normalize('NFC', text).strip()
    return ' '.join(nfc.split())

def extract_chapter_paragraphs(doc):
    paragraphs = doc.paragraphs
    c1_matches = []
    c2_matches = []
    c2_end_matches = []

    for idx, p in enumerate(paragraphs):
        txt = p.text.strip()
        style_name = p.style.name if p.style else ''
        
        if idx >= 70 and style_name == 'Heading 1' and 'TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT' in txt and not c1_matches:
            c1_matches.append(idx)
        elif idx > 150 and style_name == 'Heading 1' and 'PHƯƠNG PHÁP BIỂU DIỄN ĐẶC TRƯNG LOG' in txt and not c2_matches:
            c2_matches.append(idx)
        elif c2_matches and idx > c2_matches[0] and (('THỰC NGHIỆM' in txt and style_name == 'Heading 1') or (txt in ['Kết luận', 'KẾT LUẬN', 'Tài liệu tham khảo', 'TÀI LIỆU THAM KHẢO'] or style_name == 'UH1')):
            c2_end_matches.append(idx)

    assert len(c1_matches) == 1, f'Expected 1 C1 start, got {c1_matches}'
    assert len(c2_matches) == 1, f'Expected 1 C2 start, got {c2_matches}'
    assert len(c2_end_matches) >= 1, f'Expected C2 end, got {c2_end_matches}'

    c1_start = c1_matches[0]
    c2_start = c2_matches[0]
    c2_end = c2_end_matches[0]

    ch1_lines = [normalize_text(p.text) for p in paragraphs[c1_start:c2_start] if normalize_text(p.text)]
    ch2_lines = [normalize_text(p.text) for p in paragraphs[c2_start:c2_end] if normalize_text(p.text)]

    ch1_hash = hashlib.sha256('\n'.join(ch1_lines).encode('utf-8')).hexdigest()
    ch2_hash = hashlib.sha256('\n'.join(ch2_lines).encode('utf-8')).hexdigest()

    return ch1_lines, ch2_lines, ch1_hash, ch2_hash, c1_start, c2_start, c2_end

def compute_hunks(base_lines, curr_lines, ch_num):
    matcher = difflib.SequenceMatcher(None, base_lines, curr_lines)
    hunks = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            old_chunk = base_lines[i1:i2]
            new_chunk = curr_lines[j1:j2]
            old_str = '\n'.join(old_chunk)
            new_str = '\n'.join(new_chunk)
            old_sha = hashlib.sha256(old_str.encode('utf-8')).hexdigest() if old_str else None
            new_sha = hashlib.sha256(new_str.encode('utf-8')).hexdigest() if new_str else None
            hunks.append({
                'chapter': ch_num,
                'opcode': tag,
                'base_indices': [i1, i2],
                'curr_indices': [j1, j2],
                'old_lines': old_chunk,
                'new_lines': new_chunk,
                'old_text_sha256': old_sha,
                'new_text_sha256': new_sha
            })
    return hunks

def audit_and_verify():
    repo_root = Path(r'D:\Research')
    docx_path = repo_root / 'Chuyên đề chuyên sâu.docx'
    if not docx_path.exists():
        raise FileNotFoundError(f'Master DOCX not found at {docx_path}')

    current_doc_bytes = docx_path.read_bytes()
    current_docx_sha256 = hashlib.sha256(current_doc_bytes).hexdigest()

    # Extract historical baseline DOCX directly from git object store
    cmd = ['git', 'show', f'{BASELINE_SOURCE_COMMIT}:Chuyên đề chuyên sâu.docx']
    res = subprocess.run(cmd, capture_output=True, cwd=str(repo_root))
    if res.returncode != 0:
        raise RuntimeError(f'Failed to extract historical baseline from git commit {BASELINE_SOURCE_COMMIT}')

    hist_doc = docx.Document(io.BytesIO(res.stdout))
    curr_doc = docx.Document(str(docx_path))

    b_ch1, b_ch2, b_h1, b_h2, b_s1, b_s2, b_e2 = extract_chapter_paragraphs(hist_doc)
    c_ch1, c_ch2, c_h1, c_h2, c_s1, c_s2, c_e2 = extract_chapter_paragraphs(curr_doc)

    ch1_hunks = compute_hunks(b_ch1, c_ch1, 1)
    ch2_hunks = compute_hunks(b_ch2, c_ch2, 2)
    total_computed_hunks = ch1_hunks + ch2_hunks

    # Load approved edit ledger
    ledger_path = repo_root / 'experiments/evidence/citation-audit/APPROVED-SCIENTIFIC-EDIT-LEDGER.json'
    assert ledger_path.exists(), f'Ledger missing at {ledger_path}'
    with open(ledger_path, 'r', encoding='utf-8') as lf:
        ledger_items = json.load(lf)

    # Verification checks
    matched_hunks = 0
    unmatched_hunks = 0
    self_attested_fields_used = 0

    ledger_matched_indices = set()

    for idx, hunk in enumerate(total_computed_hunks):
        found = False
        for l_idx, item in enumerate(ledger_items):
            if (item.get('chapter') == hunk['chapter'] and 
                item.get('old_text_sha256') == hunk['old_text_sha256'] and
                item.get('new_text_sha256') == hunk['new_text_sha256']):
                found = True
                ledger_matched_indices.add(l_idx)
                break
        if found:
            matched_hunks += 1
        else:
            unmatched_hunks += 1
            print(f'[UNMATCHED HUNK] Ch{hunk["chapter"]} {hunk["opcode"]}: {hunk["new_lines"][:1]}')

    unused_ledger = len(ledger_items) - len(ledger_matched_indices)

    # Check for self-attested provenance fields
    prov_path = repo_root / 'experiments/evidence/citation-audit/CHAPTER_HASH_PROVENANCE.json'
    with open(prov_path, 'r', encoding='utf-8') as pf:
        prov = json.load(pf)

    if prov.get('expected_hash_commit') != BASELINE_SOURCE_COMMIT:
        self_attested_fields_used += 1
    if prov.get('circular_allowlisting_detected') is True:
        self_attested_fields_used += 1

    verification_status = 'PASS' if (unmatched_hunks == 0 and unused_ledger == 0 and self_attested_fields_used == 0) else 'FAIL'

    verification_result = {
        'status': verification_status,
        'verification_gate': 'CHAPTER_DIFF_LEDGER_VERIFICATION',
        'baseline_source_commit': BASELINE_SOURCE_COMMIT,
        'baseline_docx_blob_sha': BASELINE_DOCX_BLOB_SHA,
        'expected_baseline_hashes': {
            'chapter_1_sha256': b_h1,
            'chapter_2_sha256': b_h2
        },
        'observed_current_hashes': {
            'chapter_1_sha256': c_h1,
            'chapter_2_sha256': c_h2
        },
        'diff_statistics': {
            'ch1_diff_hunks': len(ch1_hunks),
            'ch2_diff_hunks': len(ch2_hunks),
            'total_diff_hunks': len(total_computed_hunks),
            'ledger_entries_count': len(ledger_items),
            'matched_diff_hunks': matched_hunks,
            'unmatched_diff_hunks': unmatched_hunks,
            'unused_ledger_entries': unused_ledger,
            'self_attested_fields_used': self_attested_fields_used
        },
        'current_docx_sha256': current_docx_sha256,
        'current_docx_size': len(current_doc_bytes)
    }

    out_verification_path = repo_root / 'experiments/evidence/citation-audit/CHAPTER-DIFF-LEDGER-VERIFICATION.json'
    with open(out_verification_path, 'w', encoding='utf-8') as vf:
        json.dump(verification_result, vf, indent=2, ensure_ascii=False)

    # Also update CHAPTER_HASH_PROVENANCE.json with latest observed hashes and count
    prov['observed_hash']['chapter_1_sha256'] = c_h1
    prov['observed_hash']['chapter_2_sha256'] = c_h2
    prov['approved_edits_count'] = len(ledger_items)
    prov['total_diff_hunks'] = len(total_computed_hunks)
    with open(prov_path, 'w', encoding='utf-8') as pf:
        json.dump(prov, pf, indent=2, ensure_ascii=False)

    # Also sync root CHAPTER_HASH_PROVENANCE.json if it exists
    root_prov = repo_root / 'CHAPTER_HASH_PROVENANCE.json'
    if root_prov.exists():
        with open(root_prov, 'w', encoding='utf-8') as rpf:
            json.dump(prov, rpf, indent=2, ensure_ascii=False)

    print('\n==================================================')
    print('CHAPTER DIFF LEDGER VERIFICATION SUMMARY')
    print('==================================================')
    print(f'Status:                     {verification_status}')
    print(f'Total Diff Hunks:           {len(total_computed_hunks)} (CH1: {len(ch1_hunks)}, CH2: {len(ch2_hunks)})')
    print(f'Ledger Entries:             {len(ledger_items)}')
    print(f'Matched Diff Hunks:         {matched_hunks}')
    print(f'Unmatched Diff Hunks:       {unmatched_hunks}')
    print(f'Unused Ledger Entries:      {unused_ledger}')
    print(f'Self-Attested Fields Used:  {self_attested_fields_used}')
    print('==================================================')

    assert verification_status == 'PASS', f'Verification failed: unmatched={unmatched_hunks}, unused={unused_ledger}'
    return verification_result

if __name__ == '__main__':
    try:
        audit_and_verify()
        sys.exit(0)
    except AssertionError as e:
        print(f'\n[FAIL-CLOSED ASSERTION ERROR] {e}', file=sys.stderr)
        sys.exit(1)

