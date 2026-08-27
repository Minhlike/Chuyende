# -*- coding: utf-8 -*-
"""
Remote Deterministic Qualification Runner for Stage A2 on Colab.
Executes bootstrap and qualification scripts on the remote GPU instance,
verifies exact numerical identity (divergence < 1e-6, fresh-process resume PASS),
and mirrors durable qualification evidence to Google Drive.
"""

from typing import Tuple
from scripts.colab_a2.wsl_bridge import ColabCLIBridge

REMOTE_QUALIFY_SCRIPT = """
import os, sys, subprocess, json, hashlib, shutil
from datetime import datetime, timezone
from pathlib import Path

def compute_sha256_streaming(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8 * 1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()

repo_dir = Path('/content/Research')
local_data = Path('/content/stage-a2-data/HDFS_1.tar.gz')
durable_root = Path('/content/drive/MyDrive/Chuyende-stage-a2')
env_lock_output = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'preexecution' / 'STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json'
output_dir = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'implementation'

os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

print("=================================================================")
print("   STAGE A2 REMOTE DETERMINISTIC QUALIFICATION                   ")
print("=================================================================")

# 1. Run bootstrap to create dynamic environment lock candidate
bootstrap_cmd = [
    sys.executable, 'scripts/bootstrap_stage_a2_colab.py',
    '--repo-dir', str(repo_dir),
    '--local-data-dest', str(local_data),
    '--durable-root', str(durable_root),
    '--env-lock-output', str(env_lock_output)
]
print("Running Bootstrap:", " ".join(bootstrap_cmd))
subprocess.run(bootstrap_cmd, cwd=str(repo_dir), check=True)
assert env_lock_output.exists(), f"Environment lock missing: {env_lock_output}"

# 2. Run deterministic qualification
qual_cmd = [
    sys.executable, 'scripts/run_stage_a2_deterministic_qualification.py',
    '--device', 'cuda',
    '--base-dir', str(repo_dir),
    '--environment-lock', str(env_lock_output),
    '--output-dir', str(output_dir)
]
print("Running Qualification:", " ".join(qual_cmd))
subprocess.run(qual_cmd, cwd=str(repo_dir), check=True)

# 3. Verify qualification evidence in place
resume_p = output_dir / 'DETERMINISTIC-RESUME-EVIDENCE.json'
resume_data = json.loads(resume_p.read_text(encoding='utf-8'))
assert resume_data['qualification_status'] == 'PASS', f"Qualification status: {resume_data['qualification_status']}"
assert resume_data['evidence_class'] == 'NON_EMPIRICAL_TEST_FIXTURE'
assert resume_data['fresh_process_isolated'] is True

# 4. Mirror qualification artifacts to Google Drive
qual_run_id = f"QUAL-COLAB-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
dest_dir = durable_root / 'qualification' / qual_run_id
dest_dir.mkdir(parents=True, exist_ok=True)

# Fail-closed nvidia-smi capture
nvidiasmi_dest = output_dir / 'NVIDIA-SMI.txt'
smi_out = subprocess.check_output(['nvidia-smi'], text=True)
nvidiasmi_dest.write_text(smi_out, encoding='utf-8')

files_to_mirror = [
    ('experiments/evidence/stage-a2/preexecution/STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json', 'STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json'),
    ('experiments/evidence/stage-a2/implementation/IMPLEMENTATION-QUALIFICATION.json', 'IMPLEMENTATION-QUALIFICATION.json'),
    ('experiments/evidence/stage-a2/implementation/DETERMINISTIC-RESUME-EVIDENCE.json', 'DETERMINISTIC-RESUME-EVIDENCE.json'),
    ('experiments/evidence/stage-a2/implementation/ENVIRONMENT.json', 'ENVIRONMENT.json'),
    ('experiments/evidence/stage-a2/implementation/EXPERIMENTAL-SOURCE.json', 'EXPERIMENTAL-SOURCE.json'),
    ('experiments/evidence/stage-a2/implementation/EVIDENCE-MANIFEST.json', 'EVIDENCE-MANIFEST.json'),
    ('experiments/evidence/stage-a2/implementation/deterministic_resume.log', 'deterministic_resume.log'),
    ('experiments/evidence/stage-a2/implementation/qualification_checkpoint.pt', 'qualification_checkpoint.pt'),
    ('experiments/evidence/stage-a2/implementation/NVIDIA-SMI.txt', 'NVIDIA-SMI.txt')
]

manifest_entries = []
for rel_src, rel_dst in files_to_mirror:
    src_p = repo_dir / rel_src
    assert src_p.exists(), f"Missing artifact: {src_p}"
    dst_p = dest_dir / rel_dst
    shutil.copy2(src_p, dst_p)
    src_sha = compute_sha256_streaming(src_p)
    dst_sha = compute_sha256_streaming(dst_p)
    assert src_sha == dst_sha, f"Mirror hash mismatch for {rel_dst}"
    manifest_entries.append({
        "name": rel_dst,
        "sha256": src_sha,
        "size_bytes": src_p.stat().st_size
    })

final_manifest = {
    "qualification_run_id": qual_run_id,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "storage": "GOOGLE_DRIVE_DURABLE",
    "qualification_directory": str(dest_dir),
    "artifact_count": len(manifest_entries),
    "artifacts": manifest_entries
}
(dest_dir / 'FINAL-QUALIFICATION-MANIFEST.json').write_text(json.dumps(final_manifest, indent=2) + '\n', encoding='utf-8')
print("Qualification Durably Mirrored to:", dest_dir)
print("=================================================================")
print("   QUALIFICATION COMPLETE: PASS                                  ")
print("=================================================================")
"""

def run_remote_qualify(bridge: ColabCLIBridge) -> Tuple[bool, str]:
    """Executes remote qualification script via Colab CLI bridge."""
    print("[QUALIFY] Sending qualification payload to Colab session...")
    code = REMOTE_QUALIFY_SCRIPT.strip()
    returncode, stdout, stderr = bridge.exec_code(code)
    print(stdout)
    if returncode != 0:
        print(f"[QUALIFY ERROR] {stderr}")
        return False, stderr
    return True, stdout
