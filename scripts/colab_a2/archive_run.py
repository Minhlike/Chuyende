# -*- coding: utf-8 -*-
"""
Permanent Run Archival Module for Stage A2 on Google Drive.
Creates immutable ZIP archive and companion .sha256 file for completed runs without deleting raw evidence.
"""

from typing import Tuple
from scripts.colab_a2.wsl_bridge import ColabCLIBridge

def build_archive_script(seed: int) -> str:
    return f"""
import os, sys, shutil, hashlib, zipfile
from datetime import datetime, timezone
from pathlib import Path

durable_root = Path('/content/drive/MyDrive/Chuyende-stage-a2')
run_dir = durable_root / 'runs' / 'stage-a2' / 'HDFS' / 'seed-{seed}'
if not run_dir.exists():
    run_dir = durable_root / 'runs' / 'HDFS' / 'seed-{seed}'

assert run_dir.exists(), f"Run directory missing: {{run_dir}}"

state_p = run_dir / 'RUN-STATE.json'
assert state_p.exists(), f"RUN-STATE.json missing in {{run_dir}}"

import json
state = json.loads(state_p.read_text(encoding='utf-8'))
assert state.get('status') == 'COMPLETED', f"Cannot archive incomplete run: status={{state.get('status')}}"

archives_dir = durable_root / 'archives'
archives_dir.mkdir(parents=True, exist_ok=True)

utc_str = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
archive_name = f"STAGE-A2-HDFS-SEED{seed}-COMPLETED-{{utc_str}}"
zip_path = archives_dir / f"{{archive_name}}.zip"
sha_path = archives_dir / f"{{archive_name}}.zip.sha256"

print(f"Creating archive {{zip_path}} from {{run_dir}}...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(run_dir):
        for file in files:
            full_p = Path(root) / file
            rel_p = full_p.relative_to(run_dir)
            zipf.write(full_p, arcname=str(rel_p))

hasher = hashlib.sha256()
with open(zip_path, 'rb') as f:
    while chunk := f.read(8 * 1024 * 1024):
        hasher.update(chunk)
zip_sha = hasher.hexdigest()

sha_path.write_text(f"{{zip_sha}}  {{zip_path.name}}\n", encoding='utf-8')
print(f"Archive Created: {{zip_path}} (SHA-256: {{zip_sha}})")
print(f"Companion Hash:  {{sha_path}}")
print("Archival Complete: PASS")
"""

def archive_completed_seed(bridge: ColabCLIBridge, seed: int) -> Tuple[bool, str]:
    """Archives a completed seed on Google Drive."""
    print(f"[ARCHIVE] Archiving completed Seed {seed} on Google Drive...")
    code = build_archive_script(seed).strip()
    returncode, stdout, stderr = bridge.exec_code(code)
    print(stdout)
    if returncode != 0:
        print(f"[ARCHIVE ERROR] {stderr}")
        return False, stderr
    return True, stdout
