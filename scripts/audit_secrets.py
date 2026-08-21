# -*- coding: utf-8 -*-
"""
Automated Secret and Privacy Auditor
Scans the repository for credentials, private keys, authentication tokens, and oversized binaries.
"""

import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

def scan_repository():
    root = Path(r"D:\Research")
    
    secret_patterns = [
        re.compile(r'(?i)(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})'),
        re.compile(r'(?i)-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----'),
        re.compile(r'(?i)(sk-[a-zA-Z0-9]{48}|AIzaSy[a-zA-Z0-9_-]{33})'),
        re.compile(r'(?i)(aws_access_key_id|aws_secret_access_key)\s*=\s*[A-Za-z0-9/+=]{20,}'),
    ]

    findings = []
    large_files = []
    
    ignored_dirs = {".git", ".pytest_cache", ".venv", "venv", "__pycache__", "runtime", "pdf_closure_pages", "pdf_closure_pages2", "pdf_hotfix_pages", "pdf_pages", "current_audit_pages", "final_rendered_pages"}

    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in ignored_dirs for part in path.parts):
            continue

        # File size check (warn on files > 10MB)
        try:
            sz = path.stat().st_size
            if sz > 10 * 1024 * 1024:
                large_files.append((str(path.relative_to(root)), sz))
        except Exception:
            pass

        # Text secret scanning
        if path.suffix in [".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt", ".sh", ".ps1", ".env", ".example"]:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                for pat in secret_patterns:
                    matches = pat.findall(content)
                    if matches:
                        findings.append((str(path.relative_to(root)), str(matches[:2])))
            except Exception:
                pass

    print(f"=== SECRET SCAN AUDIT ===")
    print(f"Total Secret Findings: {len(findings)}")
    for f in findings:
        print(f"[VIOLATION] Found secret pattern in: {f[0]} -> {f[1]}")

    print(f"\n=== LARGE FILE AUDIT (>10MB) ===")
    print(f"Total Large Files: {len(large_files)}")
    for lf in large_files:
        print(f"[WARN] Large file: {lf[0]} ({lf[1]} bytes)")

    if len(findings) == 0:
        print("\n[PASS] 0 secrets detected. Safe for public repository commit.")
        return True
    else:
        print("\n[FAIL] Secrets detected! Commit blocked.")
        return False

if __name__ == "__main__":
    scan_repository()
