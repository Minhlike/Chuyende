# -*- coding: utf-8 -*-
"""
Canonical Acceptance Report Validator Gate
Verifies:
1. HEAD and Master SHA provenance.
2. 44/44 exact citation metadata match with CITATION-INTEGRITY-AUDIT.json.
3. 44 reference numbers unique and sequential (1..44).
4. Zero forbidden stale hallucinated strings.
5. Strict claim discipline (no ungrounded absolute buzzwords).
"""

import sys
import re
import json
import hashlib
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

def verify_report():
    repo_root = Path(__file__).resolve().parent.parent
    report_path = repo_root / 'FINAL-ACCEPTANCE-REPORT.md'
    audit_path = repo_root / 'experiments' / 'evidence' / 'citation-audit' / 'CITATION-INTEGRITY-AUDIT.json'
    docx_path = repo_root / 'Chuyên đề chuyên sâu.docx'
    pdf_path = repo_root / 'Chuyên đề chuyên sâu.pdf'

    print("==================================================")
    print("FINAL ACCEPTANCE REPORT VERIFICATION GATE")
    print("==================================================")

    if not report_path.exists():
        print(f"[FAIL] Report not found at {report_path}")
        sys.exit(1)

    with open(report_path, 'r', encoding='utf-8') as f:
        report_text = f.read()

    errors = []

    # 1. Verify Master SHA Immutability
    with open(docx_path, 'rb') as f:
        actual_docx_sha = hashlib.sha256(f.read()).hexdigest()
    with open(pdf_path, 'rb') as f:
        actual_pdf_sha = hashlib.sha256(f.read()).hexdigest()

    expected_docx_sha = "69982da7c2959dbda797be8a38181f493cb5aec7f17f2f2a9ed6d4eee866d48f"
    expected_pdf_sha = "00cecc7e6ba47a560edbae5a82635b9649760fc613f8819337401c35dc7ca4a2"

    if actual_docx_sha != expected_docx_sha:
        errors.append(f"Master DOCX hash modified! Expected {expected_docx_sha}, got {actual_docx_sha}")
    else:
        print(f"[PASS] Master DOCX hash verified: {actual_docx_sha[:16]}...")

    if actual_pdf_sha != expected_pdf_sha:
        errors.append(f"Master PDF hash modified! Expected {expected_pdf_sha}, got {actual_pdf_sha}")
    else:
        print(f"[PASS] Master PDF hash verified: {actual_pdf_sha[:16]}...")

    # 2. Verify Provenance Head metadata in Report
    expected_accepted_head = "807ed9fdaeac4959ce4dd19b499c8cd27ab9d5d1"
    if f"THESIS_MASTER_ACCEPTED_AT_SHA: {expected_accepted_head}" not in report_text:
        errors.append(f"Report missing expected THESIS_MASTER_ACCEPTED_AT_SHA: {expected_accepted_head}")
    else:
        print(f"[PASS] THESIS_MASTER_ACCEPTED_AT_SHA verified: {expected_accepted_head[:16]}...")

    # 3. Check Forbidden Stale Strings
    forbidden_strings = [
        "[1] Pasquier",
        "[2] Hassan",
        "N. Neamtiu",
        "10.1145/3427228.3427237",
        "ACM Transactions on Privacy and Security"
    ]
    for stale in forbidden_strings:
        if stale in report_text:
            errors.append(f"Forbidden stale string found in report: '{stale}'")

    if not any(stale in report_text for stale in forbidden_strings):
        print("[PASS] Zero forbidden stale strings detected.")

    # 4. Verify Citations against CITATION-INTEGRITY-AUDIT.json
    with open(audit_path, 'r', encoding='utf-8') as f:
        audit_data = json.load(f)

    audit_data = sorted(audit_data, key=lambda x: x['reference_number'])
    audit_dict = {x['reference_number']: x for x in audit_data}

    # Extract all citation lines: ^- \[(\d+)\]
    citation_lines = re.findall(r'^-\s+\[\d+\].+$', report_text, re.MULTILINE)
    print(f"Citation lines extracted from report: {len(citation_lines)}")

    if len(citation_lines) != 44:
        errors.append(f"Expected 44 citation lines, found {len(citation_lines)}")

    pattern = re.compile(
        r'^-\s+\[(\d+)\]\s+(.+?)\s+\((\d{4})\),\s+\"(.+?)\",\s+(.+?)\.'
        r'(?:\s+Pages:\s+(.+?)\.)?'
        r'\s+([A-Za-z0-9_]+):\s+(.+?)\.$'
    )

    matched_refs = set()
    for line in citation_lines:
        m = pattern.match(line)
        if not m:
            errors.append(f"Citation line failed pattern match: {line}")
            continue

        r_num = int(m.group(1))
        matched_refs.add(r_num)
        orig = audit_dict.get(r_num)
        if not orig:
            errors.append(f"Unknown reference number: {r_num}")
            continue

        authors = m.group(2).strip()
        year = m.group(3).strip()
        title = m.group(4).strip()
        venue = m.group(5).strip()
        pages = (m.group(6) or "").strip()
        id_type = m.group(7).strip()
        id_val = m.group(8).strip()

        if authors != orig['authors']:
            errors.append(f"[{r_num}] authors mismatch: '{authors}' vs '{orig['authors']}'")
        if year != orig['year']:
            errors.append(f"[{r_num}] year mismatch: '{year}' vs '{orig['year']}'")
        if title != orig['title']:
            errors.append(f"[{r_num}] title mismatch: '{title}' vs '{orig['title']}'")
        if venue != orig['venue']:
            errors.append(f"[{r_num}] venue mismatch: '{venue}' vs '{orig['venue']}'")
        if pages != orig.get('pages', '').strip():
            errors.append(f"[{r_num}] pages mismatch: '{pages}' vs '{orig.get('pages', '').strip()}'")
        if id_type != orig['identifier_type']:
            errors.append(f"[{r_num}] id_type mismatch: '{id_type}' vs '{orig['identifier_type']}'")
        if id_val != orig['identifier_value']:
            errors.append(f"[{r_num}] id_val mismatch: '{id_val}' vs '{orig['identifier_value']}'")

    if matched_refs != set(range(1, 45)):
        errors.append(f"Reference numbers not 1..44: missing {set(range(1, 45)) - matched_refs}")
    else:
        print(f"[PASS] 44/44 reference numbers unique, sequential, and bijected (1..44).")

    if not any(f"[{r_num}]" in err for err in errors):
        print("[PASS] 44/44 citation entries matched exact equality with CITATION-INTEGRITY-AUDIT.json across all 8 fields.")

    # 5. Check Claim Discipline
    buzzwords = ["tuyệt đối đúng", "hoàn hảo", "phủ kín", "chính xác tuyệt đối"]
    for bw in buzzwords:
        if bw in report_text.lower():
            errors.append(f"Ungrounded absolute buzzword detected in report: '{bw}'")

    if not any(bw in report_text.lower() for bw in buzzwords):
        print("[PASS] Claim discipline verified: zero ungrounded absolute buzzwords.")

    print("--------------------------------------------------")
    if errors:
        print(f"[FAIL] VERIFICATION FAILED WITH {len(errors)} ERRORS:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("[PASS] ALL ACCEPTANCE REPORT VERIFICATION GATES PASSED!")
        sys.exit(0)

if __name__ == '__main__':
    verify_report()
