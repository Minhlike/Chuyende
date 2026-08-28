# -*- coding: utf-8 -*-
"""
Remote Environment Preparation for Stage A2 on Colab.
Performs fail-closed discovery, clean clone of approved execution commit,
exact PyTorch 2.6.0+cu124 verification, and streaming SHA-256 HDFS raw dataset copy.
"""

import re
from typing import Dict, Any, Tuple, Optional
from scripts.colab_a2.wsl_bridge import ColabCLIBridge

EXPECTED_HDFS_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
REPO_URL = "https://github.com/Minhlike/Chuyende.git"

def build_prepare_script(execution_commit: str) -> str:
    if not execution_commit or not re.match(r"^[0-9a-fA-F]{40}$", execution_commit.strip()):
        raise ValueError(f"FATAL: APPROVED EXECUTION COMMIT REQUIRED (40-hex SHA). Got: '{execution_commit}'")
    
    commit = execution_commit.strip()
    return f"""
import os, sys, subprocess, shutil, hashlib, re
from pathlib import Path

def compute_sha256_streaming(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

print("=================================================================")
print("   STAGE A2 REMOTE ENVIRONMENT PREPARATION                      ")
print("=================================================================")

# 1. Host discovery & nvidia-smi fail-closed
smi = subprocess.check_output(['nvidia-smi'], text=True)
print("Host GPU Detected:\\n", smi.strip())

# 2. Clean fresh clone & checkout of approved commit
repo_dir = Path('/content/Research')
if repo_dir.exists():
    print(f"Removing existing {{repo_dir}} for fresh clone...")
    shutil.rmtree(repo_dir)

print(f"Cloning clean repository from {REPO_URL}...")
subprocess.run(['git', 'clone', '{REPO_URL}', str(repo_dir)], check=True)

print(f"Detached checkout of approved commit: {commit}")
subprocess.run(['git', 'checkout', '{commit}'], cwd=str(repo_dir), check=True)

head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=str(repo_dir), text=True).strip()
assert head == '{commit}', f"Commit mismatch: {{head}} != {commit}"

status = subprocess.check_output(['git', 'status', '--porcelain', 'src', 'scripts', 'experiments', 'tests'], cwd=str(repo_dir), text=True).strip()
assert len(status) == 0, f"Source tree dirty: {{status}}"
print("Approved Clean Source Verified at HEAD:", head)

# 3. Editable install & PyTorch 2.6.0+cu124 verification
subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], cwd=str(repo_dir), check=True)

def verify_torch():
    cmd = [
        sys.executable, '-c',
        "import torch; "
        "assert torch.__version__ == '2.6.0+cu124', f'Torch version mismatch: {{torch.__version__}}'; "
        "assert torch.version.cuda == '12.4', f'CUDA mismatch: {{torch.version.cuda}}'; "
        "assert torch.cuda.is_available() is True, 'CUDA unavailable!'"
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

res = verify_torch()
if res.returncode != 0:
    print("Reinstalling official PyTorch 2.6.0+cu124 wheel...")
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '--force-reinstall',
        'torch==2.6.0', '--index-url', 'https://download.pytorch.org/whl/cu124'
    ], check=True)
    res_re = verify_torch()
    if res_re.returncode != 0:
        raise RuntimeError(f"FATAL: Torch verification failed: {{res_re.stderr}}")

print("PyTorch 2.6.0+cu124 Verified.")

# 4. Fail-closed dataset streaming copy & SHA-256 verification
drive_canonical = Path('/content/drive/MyDrive/Chuyende-stage-a2/datasets/HDFS_1.tar.gz')
drive_fallback = Path('/content/drive/MyDrive/HDFS_1.tar.gz')

if drive_canonical.exists():
    drive_src = drive_canonical
elif drive_fallback.exists():
    drive_src = drive_fallback
else:
    raise FileNotFoundError(f"FATAL: HDFS dataset missing on Drive! ({{drive_canonical}} / {{drive_fallback}})")

print(f"Drive Dataset Source: {{drive_src}}")
src_sha = compute_sha256_streaming(drive_src)
assert src_sha == '{EXPECTED_HDFS_SHA}', f"Drive SHA mismatch: {{src_sha}} != {EXPECTED_HDFS_SHA}"

local_dest = Path('/content/stage-a2-data/HDFS_1.tar.gz')
local_dest.parent.mkdir(parents=True, exist_ok=True)
tmp_dest = Path('/content/stage-a2-data/HDFS_1.tar.gz.tmp')

shutil.copy2(drive_src, tmp_dest)
tmp_sha = compute_sha256_streaming(tmp_dest)
assert tmp_sha == '{EXPECTED_HDFS_SHA}', f"Temp copy SHA mismatch: {{tmp_sha}} != {EXPECTED_HDFS_SHA}"

os.replace(tmp_dest, local_dest)
final_local_sha = compute_sha256_streaming(local_dest)
assert final_local_sha == '{EXPECTED_HDFS_SHA}', f"Final local SHA mismatch: {{final_local_sha}}"
assert local_dest.stat().st_size == drive_src.stat().st_size, "File size mismatch!"

print("=================================================================")
print("   REMOTE PREPARATION COMPLETE: PASS                            ")
print("=================================================================")
"""

def run_remote_prepare(bridge: ColabCLIBridge, execution_commit: str) -> Tuple[bool, str]:
    """Executes remote preparation script via Colab CLI bridge."""
    if not execution_commit:
        raise ValueError("FATAL: APPROVED EXECUTION COMMIT REQUIRED")
    print(f"[PREPARE] Sending preparation payload (Commit: {execution_commit}) to Colab session...")
    code = build_prepare_script(execution_commit).strip()
    returncode, stdout, stderr = bridge.exec_code(code)
    print(stdout)
    if returncode != 0:
        print(f"[PREPARE ERROR] {stderr}")
        return False, stderr
    return True, stdout
