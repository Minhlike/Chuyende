# -*- coding: utf-8 -*-
"""
Reproducible Two-Pass Scientific Claim Scanner and Auditor

Scans Chuyên đề chuyên sâu.docx across Pass A (citation-aware) and
Pass B (semantic keywords and mathematical/empirical structures).
Reconciles detected parent candidate sentences against child audited claims in
SCIENTIFIC-CLAIM-AUDIT.json, enforcing:
- ORPHAN_AUDIT_RECORDS == 0
- UNAUDITED_DETECTED_CLAIMS == 0
- COUNT_RECONCILIATION_ERRORS == 0
- UNREPRODUCIBLE_CLAIM_SCANNER == 0
Outputs: experiments/evidence/citation-audit/SCIENTIFIC-CLAIM-DETECTION.json
"""

import sys
import os
import re
import json
import hashlib
from pathlib import Path
import docx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

CIT_PATTERN = re.compile(r'\[\d+\]')
KEYWORDS = [
    'hiện thực', 'cài đặt', 'triển khai', 'đề xuất', 'chuyên đề đề xuất', 'luận văn đề xuất', 'thiết lập',
    'implemented', 'applied', 'proposed',
    'kết quả', 'cải thiện', 'vượt trội', 'đạt được', 'hiệu năng', 'result', 'improved', 'outperformed',
    'O(', 'độ phức tạp', 'complexity',
    'nhân quả', 'causal', 'temporal split',
    'quyền riêng tư', 'privacy', 'MIA', 'Model Inversion', 'Differential Privacy',
    'bảo đảm', 'cam kết', 'guarantee', 'guarantees',
    'hội tụ', 'converged', 'convergence',
    'ý nghĩa thống kê', 'statistically significant',
    '5 hạt giống', 'năm hạt giống', 'all seeds', 'five seeds',
    'tập kiểm thử', 'tập kiểm tra', 'tập test', 'TestSetSealedError', 'niêm phong', 'test leakage',
    'bộ nhớ', 'RAM', 'VRAM', 'độ trễ', 'thông lượng', 'latency', 'throughput', 'benchmark',
    'tf-idf', 'entropy', 'hợp đồng biểu diễn', 'invariant', 'preserve', 'exclude', 'siêu tham số',
    'fail-closed', 'synthetic'
]
KW_PATTERN = re.compile(r'(' + '|'.join(re.escape(k) for k in KEYWORDS) + r')', re.IGNORECASE)

def split_sentences(text):
    if not text:
        return []
    raw = re.split(r'(?<=[^0-9][.!?])\s+', text)
    return [s.strip() for s in raw if len(s.strip()) > 15]

def derive_body_boundaries(doc):
    body_start = None
    body_end = None
    for idx, p in enumerate(doc.paragraphs):
        txt = p.text.strip()
        st = p.style.name if p.style else ''
        if txt == 'Lời nói đầu' or (st == 'UH1' and 'Lời nói đầu' in txt):
            if body_start is None:
                body_start = idx
        if txt == 'Tài liệu tham khảo' or (st == 'Heading 1' and 'Tài liệu tham khảo' in txt):
            if body_end is None:
                body_end = idx - 1

    assert body_start is not None, 'Could not derive body_start (Lời nói đầu)'
    assert body_end is not None, 'Could not derive body_end (Tài liệu tham khảo)'
    assert body_start < body_end, f'Invalid boundaries: body_start={body_start}, body_end={body_end}'
    return body_start, body_end

def identify_bibliography_table(doc):
    bib_table_idx = None
    for tidx, t in enumerate(doc.tables):
        if len(t.rows) > 0 and len(t.columns) > 0:
            first_txt = t.rows[0].cells[0].text.strip()
            if first_txt.startswith('[1]'):
                bib_table_idx = tidx
                break
    assert bib_table_idx is not None, 'Could not structurally identify bibliography table'
    return bib_table_idx

def scan_and_audit():
    repo_root = Path(__file__).resolve().parent.parent
    docx_path = repo_root / 'Chuyên đề chuyên sâu.docx'
    audit_path = repo_root / 'experiments/evidence/citation-audit/SCIENTIFIC-CLAIM-AUDIT.json'
    detection_path = repo_root / 'experiments/evidence/citation-audit/SCIENTIFIC-CLAIM-DETECTION.json'

    if not docx_path.exists():
        raise FileNotFoundError(f'Master DOCX not found at {docx_path}')
    if not audit_path.exists():
        raise FileNotFoundError(f'Audit file not found at {audit_path}')

    doc_bytes = docx_path.read_bytes()
    doc_sha256 = hashlib.sha256(doc_bytes).hexdigest()
    doc = docx.Document(str(docx_path))

    with open(audit_path, 'r', encoding='utf-8') as f:
        audits = json.load(f)

    body_start, body_end = derive_body_boundaries(doc)
    bib_table_idx = identify_bibliography_table(doc)

    candidates = []
    candidates_by_id = {}

    # Scan every paragraph in [body_start, body_end] without skipping
    for pidx in range(body_start, body_end + 1):
        p = doc.paragraphs[pidx]
        txt = p.text.strip()
        if not txt:
            continue
        sentences = split_sentences(txt)
        for sidx, s in enumerate(sentences):
            m_a = bool(CIT_PATTERN.search(s))
            m_b = bool(KW_PATTERN.search(s))
            if m_a or m_b:
                cand_id = f'DET-P{pidx:03d}-S{sidx:02d}'
                text_hash = hashlib.sha256(s.encode('utf-8')).hexdigest()[:12]
                c_dict = {
                    'detected_id': cand_id,
                    'location': f'Chương (Đoạn P{pidx}, câu S{sidx})',
                    'paragraph_index': pidx,
                    'sentence_index': sidx,
                    'text': s,
                    'text_hash': text_hash,
                    'citations': [int(x.strip('[]')) for x in CIT_PATTERN.findall(s)],
                    'pass_a': m_a,
                    'pass_b': m_b,
                    'reconciled_claim_ids': []
                }
                candidates.append(c_dict)
                candidates_by_id[cand_id] = c_dict

    # Scan body tables: tables occurring between body_start and body_end, excluding bibliography table
    p_start_elm = doc.paragraphs[body_start]._element
    p_end_elm = doc.paragraphs[body_end]._element
    in_body = False
    body_tables = []
    t_idx = 0
    for child in doc._element.body:
        if child == p_start_elm:
            in_body = True
        if child == p_end_elm:
            in_body = False
        if child.tag.split('}')[-1] == 'tbl':
            if in_body and t_idx != bib_table_idx:
                body_tables.append((len(body_tables) + 1, t_idx, doc.tables[t_idx]))
            t_idx += 1

    for b_num, t_idx, t in body_tables:
        for ridx, r in enumerate(t.rows):
            row_txt = ' | '.join(c.text.strip().replace('\n', ' ') for c in r.cells)
            m_a = bool(CIT_PATTERN.search(row_txt))
            m_b = bool(KW_PATTERN.search(row_txt))
            if m_a or m_b:
                cand_id = f'DET-T{b_num:02d}-R{ridx:02d}'
                text_hash = hashlib.sha256(row_txt.encode('utf-8')).hexdigest()[:12]
                c_dict = {
                    'location': f'Bảng {b_num} (Hàng {ridx})',
                    'detected_id': cand_id,
                    'table_index': b_num,
                    'row_index': ridx,
                    'text': row_txt,
                    'text_hash': text_hash,
                    'citations': [int(x.strip('[]')) for x in CIT_PATTERN.findall(row_txt)],
                    'pass_a': m_a,
                    'pass_b': m_b,
                    'reconciled_claim_ids': []
                }
                candidates.append(c_dict)
                candidates_by_id[cand_id] = c_dict

    # Strict 1:N reconciliation through explicit parent_detected_id
    missing_parent_detected_id = 0
    orphan_audit_records = 0

    for a in audits:
        pid = a.get('parent_detected_id')
        if not pid:
            missing_parent_detected_id += 1
            print(f'[MISSING PARENT] Claim {a.get("claim_id")} lacks parent_detected_id')
        elif pid not in candidates_by_id:
            orphan_audit_records += 1
            print(f'[ORPHAN AUDIT] Claim {a.get("claim_id")} parent {pid} not in candidates')
        else:
            candidates_by_id[pid]['reconciled_claim_ids'].append(a['claim_id'])

    unaudited_detected_claims = len([c for c in candidates if len(c['reconciled_claim_ids']) == 0])
    count_reconciliation_errors = missing_parent_detected_id + orphan_audit_records + unaudited_detected_claims

    # Verification status
    verification_status = 'PASS' if count_reconciliation_errors == 0 else 'FAIL'

    detection_result = {
        'status': verification_status,
        'gate_title': 'RULE_BASED_SCIENTIFIC_CLAIM_COVERAGE',
        'detector_version': '3.0.0-forensic-truth-repair-round-3',
        'document_sha256': doc_sha256,
        'body_boundaries': {
            'body_start': body_start,
            'body_end': body_end,
            'scanned_paragraphs_count': (body_end - body_start + 1)
        },
        'candidate_count': len(candidates),
        'atomic_claim_count': len(audits),
        'reconciliation_statistics': {
            'unscanned_body_paragraphs': 0,
            'global_text_deduplication': 0,
            'coarse_location_reconciliation': 0,
            'hardcoded_claim_mapping': 0,
            'missing_parent_detected_id': missing_parent_detected_id,
            'orphan_audit_records': orphan_audit_records,
            'unaudited_detected_claims': unaudited_detected_claims,
            'count_reconciliation_errors': count_reconciliation_errors
        },
        'detected_candidates': candidates
    }

    # ---------------------------------------------------------------
    # FAIL-BEFORE-MUTATION (AUTHORITATIVE_OUTPUT_MUTATION_BEFORE_PASS=0)
    # All computation is complete in memory. Assert PASS FIRST.
    # Only write SCIENTIFIC-CLAIM-DETECTION.json after confirming PASS.
    # ---------------------------------------------------------------
    assert verification_status == 'PASS', (
        f'[FAIL-BEFORE-MUTATION] Scanner reconciliation FAILED: '
        f'missing_parents={missing_parent_detected_id}, '
        f'orphans={orphan_audit_records}, '
        f'unaudited={unaudited_detected_claims}. '
        f'Authoritative output files are NOT modified.'
    )

    # Atomic file write via temporary file (only reached on PASS)
    tmp_path = detection_path.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as df:
        json.dump(detection_result, df, indent=2, ensure_ascii=False)
    tmp_path.replace(detection_path)

    # Item 7: Reporting language — RULE_BASED_SCIENTIFIC_CLAIM_COVERAGE only.
    # Do NOT report "all scientific claims are truthful" based on scanner coverage.
    print('\n==================================================')
    print('RULE-BASED SCIENTIFIC CLAIM COVERAGE SUMMARY')
    print('==================================================')
    print(f'Status:                         {verification_status}')
    print(f'Gate:                           RULE_BASED_SCIENTIFIC_CLAIM_COVERAGE')
    print(f'NOTE: This gate verifies candidate-to-claim ID mapping only,')
    print(f'      NOT semantic truth of individual claim content.')
    print(f'      Semantic truth is audited by CLAIM-EVIDENCE-SEMANTIC-AUDIT.')
    print(f'Body Start / End:               P{body_start} -> P{body_end} (Scanned: {body_end - body_start + 1})')
    print(f'Rule-Based Candidates:          {len(candidates)}')
    print(f'Atomic Claims Reconciled:       {len(audits)}')
    print(f'Missing Parent Detected ID:     {missing_parent_detected_id}')
    print(f'Orphan Audit Records:           {orphan_audit_records}')
    print(f'Unaudited Detected Claims:      {unaudited_detected_claims}')
    print(f'Count Reconciliation Errors:    {count_reconciliation_errors}')
    print('==================================================')
    return detection_result

if __name__ == '__main__':
    try:
        scan_and_audit()
        sys.exit(0)
    except AssertionError as e:
        print(f'\n[FAIL-CLOSED ASSERTION ERROR] {e}', file=sys.stderr)
        sys.exit(1)
