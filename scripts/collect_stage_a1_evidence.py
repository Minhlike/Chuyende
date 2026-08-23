# -*- coding: utf-8 -*-
"""
Audits and collects reproducible empirical evidence for Stage A1 acceptance.
Generates machine-readable logs and SHA-256 inventory under experiments/evidence/stage-a1/.
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from pathlib import Path

def run_cmd(cmd, cwd=None):
    t0 = time.time()
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    duration = time.time() - t0
    return {
        "command": cmd,
        "returncode": res.returncode,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "duration_sec": duration
    }

def collect_evidence():
    base_dir = Path("D:/Research")
    evidence_dir = base_dir / "experiments" / "evidence" / "stage-a1"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    print("[EVIDENCE] 1. Collecting Windows PyTest Suite Evidence...")
    win_res = run_cmd(f"{sys.executable} -m pytest tests/ --ignore=tests/test_stage_a1_deterministic_resume.py", cwd=base_dir)
    (evidence_dir / "pytest_windows.log").write_text(win_res["stdout"] + "\n" + win_res["stderr"], encoding="utf-8")
    
    # Parse passed/skipped
    out_lines = win_res["stdout"].splitlines()
    summary_line = [l for l in out_lines if "passed" in l or "failed" in l or "error" in l]
    last_summary = summary_line[-1] if summary_line else "UNKNOWN"
    
    win_summary = {
        "platform": "win32",
        "python": sys.version.split()[0],
        "exit_code": win_res["returncode"],
        "summary_text": last_summary,
        "duration_sec": win_res["duration_sec"],
        "passed": (win_res["returncode"] == 0)
    }
    (evidence_dir / "pytest_windows.json").write_text(json.dumps(win_summary, indent=2), encoding="utf-8")

    print("[EVIDENCE] 2. Collecting WSL PyTest Suite & Deterministic Resume Evidence...")
    wsl_cmd = 'wsl.exe -d Research-Ubuntu-24.04 -- bash -c "cd ~/chuyende && source .venv/bin/activate && export PYTHONPATH=/mnt/d/Research/src:$PYTHONPATH && pytest /mnt/d/Research/tests/test_real_data_adapters.py /mnt/d/Research/tests/test_stage_a1_deterministic_resume.py -v"'
    wsl_res = run_cmd(wsl_cmd, cwd=base_dir)
    (evidence_dir / "pytest_wsl.log").write_text(wsl_res["stdout"] + "\n" + wsl_res["stderr"], encoding="utf-8")
    
    wsl_lines = wsl_res["stdout"].splitlines()
    wsl_summary_line = [l for l in wsl_lines if "passed" in l or "failed" in l or "error" in l]
    wsl_last_summary = wsl_summary_line[-1] if wsl_summary_line else "UNKNOWN"

    wsl_summary = {
        "platform": "linux-wsl2",
        "exit_code": wsl_res["returncode"],
        "summary_text": wsl_last_summary,
        "duration_sec": wsl_res["duration_sec"],
        "passed": (wsl_res["returncode"] == 0)
    }
    (evidence_dir / "pytest_wsl.json").write_text(json.dumps(wsl_summary, indent=2), encoding="utf-8")

    print("[EVIDENCE] 3. Collecting Secret Scan Evidence...")
    sec_res = run_cmd(f"{sys.executable} scripts/audit_secrets.py", cwd=base_dir)
    (evidence_dir / "secret_scan.log").write_text(sec_res["stdout"] + "\n" + sec_res["stderr"], encoding="utf-8")
    sec_summary = {
        "exit_code": sec_res["returncode"],
        "zero_secrets": ("0 secrets detected" in sec_res["stdout"]),
        "stdout": sec_res["stdout"].strip()
    }
    (evidence_dir / "secret_scan.json").write_text(json.dumps(sec_summary, indent=2), encoding="utf-8")

    print("[EVIDENCE] 4. Collecting Invariant & Test Firewall Audit Evidence...")
    inv_res = run_cmd(f"{sys.executable} scripts/verify_invariants.py", cwd=base_dir)
    (evidence_dir / "data_firewall.log").write_text(inv_res["stdout"] + "\n" + inv_res["stderr"], encoding="utf-8")

    # Check 10 manifests for test firewall
    manifest_reports = []
    datasets = ["HDFS", "BGL"]
    seeds = [42, 1337, 2024, 7, 999]
    all_firewalled = True
    all_nan_zero = True

    for ds in datasets:
        for seed in seeds:
            mf_path = base_dir / "experiments" / "runs" / "stage-a1" / ds / f"seed-{seed}" / "RUN-MANIFEST.json"
            if mf_path.exists():
                mf = json.loads(mf_path.read_text(encoding="utf-8"))
                firewall_ok = (
                    mf.get("test_opened") is False and
                    mf.get("test_feature_read_count") == 0 and
                    mf.get("test_label_read_count") == 0 and
                    mf.get("test_metric_count") == 0
                )
                nan_ok = (
                    mf.get("nan_loss_count") == 0 and
                    mf.get("inf_loss_count") == 0 and
                    mf.get("nan_grad_count") == 0 and
                    mf.get("inf_grad_count") == 0
                )
                if not firewall_ok:
                    all_firewalled = False
                if not nan_ok:
                    all_nan_zero = False
                manifest_reports.append({
                    "dataset": ds,
                    "seed": seed,
                    "firewall_sealed": firewall_ok,
                    "nan_zero": nan_ok,
                    "best_val_loss": mf.get("best_val_loss"),
                    "checkpoint_sha256": mf.get("best_checkpoint_sha256")
                })

    firewall_summary = {
        "database_invariants_pass": (inv_res["returncode"] == 0),
        "all_10_manifests_firewalled": all_firewalled,
        "all_10_manifests_nan_zero": all_nan_zero,
        "total_manifests_audited": len(manifest_reports),
        "manifests": manifest_reports
    }
    (evidence_dir / "data_firewall.json").write_text(json.dumps(firewall_summary, indent=2), encoding="utf-8")

    print("[EVIDENCE] 5. Generating SHA-256 Inventory of Evidence Files...")
    evidence_files = sorted([f for f in evidence_dir.iterdir() if f.is_file() and f.name not in ["SHA256SUMS.txt", "EVIDENCE-MANIFEST.json"]])
    sha_lines = []
    inventory = {}

    for ef in evidence_files:
        h = hashlib.sha256(ef.read_bytes()).hexdigest()
        sha_lines.append(f"{h}  {ef.name}")
        inventory[ef.name] = {
            "sha256": h,
            "size_bytes": ef.stat().st_size
        }

    (evidence_dir / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    
    manifest_doc = {
        "evidence_id": "EVIDENCE-STAGE-A1-001",
        "created_timestamp": time.time(),
        "total_evidence_files": len(inventory),
        "inventory": inventory
    }
    (evidence_dir / "EVIDENCE-MANIFEST.json").write_text(json.dumps(manifest_doc, indent=2), encoding="utf-8")
    print(f"[EVIDENCE] Evidence generation complete. {len(inventory)} evidence files indexed.")

if __name__ == "__main__":
    collect_evidence()
