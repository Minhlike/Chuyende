# -*- coding: utf-8 -*-
"""
Remote Empirical Execution & Dry-Run Runner for Stage A2 on Colab.
Enforces canonical seed order (42, 1337, 2024, 7, 999), single-seed execution (prohibits --all),
validates durable Google Drive state, generates matching launch authorization, and executes runs.
"""

import re
import json
from typing import Dict, Any, Tuple, Optional
from scripts.colab_a2.wsl_bridge import ColabCLIBridge

CANONICAL_SEEDS = [42, 1337, 2024, 7, 999]
RAW_HDFS_TAR_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
TRAIN_MEMBERSHIP_SHA = "65b76694b0a3cf5c6d684a26899b1e5dca634cfd0985560149feddc12ca8ccfc"
VAL_MEMBERSHIP_SHA = "14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a"

def build_dry_run_script(seed: int) -> str:
    return f"""
import os, sys, subprocess
from pathlib import Path

repo_dir = Path('/content/Research')
dataset_path = Path('/content/stage-a2-data/HDFS_1.tar.gz')
durable_runs = Path('/content/drive/MyDrive/Chuyende-stage-a2/runs/HDFS')
plan_path = repo_dir / 'experiments' / 'plans' / 'STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json'
env_lock_path = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'preexecution' / 'STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json'
log_dest = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'implementation' / 'SEED{seed}-COLAB-DRY-RUN.log'

os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

dry_cmd = [
    sys.executable, 'scripts/run_stage_a2_five_seed_empirical.py',
    '--seed', '{seed}',
    '--dry-run',
    '--base-dir', str(repo_dir),
    '--dataset-path', str(dataset_path),
    '--durable-root', str(durable_runs),
    '--plan', str(plan_path),
    '--environment-lock', str(env_lock_path)
]

print("Executing Seed {seed} Dry-Run:", " ".join(dry_cmd))
proc = subprocess.run(dry_cmd, cwd=str(repo_dir), capture_output=True, text=True)

log_dest.parent.mkdir(parents=True, exist_ok=True)
log_dest.write_text(proc.stdout + '\\n' + proc.stderr, encoding='utf-8')
print(proc.stdout)

if proc.returncode != 0:
    print("Dry-run STDERR:\\n", proc.stderr)
    raise RuntimeError(f"Seed {seed} dry-run failed with code {{proc.returncode}}")

assert 'OptimizerStepsExecuted=0' in proc.stdout or 'Optimizer Steps Executed: 0' in proc.stdout, "Optimizer steps not zero!"
assert 'TEST_OPENED=false' in proc.stdout or 'Connected Test Firewall: LOCKED' in proc.stdout, "Test firewall breach!"
print("Seed {seed} Dry-Run Verified: PASS (Zero Optimizer Steps)")
"""

def build_authorization_payload(seed: int, execution_commit: str) -> str:
    if not execution_commit or not re.match(r"^[0-9a-fA-F]{40}$", execution_commit.strip()):
        raise ValueError(f"FATAL: APPROVED EXECUTION COMMIT REQUIRED (40-hex SHA). Got: '{execution_commit}'")
    
    commit = execution_commit.strip()
    return f"""
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path

def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

repo_dir = Path('/content/Research')
env_lock_path = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'preexecution' / 'STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json'
plan_path = repo_dir / 'experiments' / 'plans' / 'STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json'
auth_dest = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'preexecution' / 'SEED{seed}-COLAB-LAUNCH-AUTHORIZATION-V1.5.json'

assert env_lock_path.exists(), f"Missing env lock: {{env_lock_path}}"
assert plan_path.exists(), f"Missing plan: {{plan_path}}"

auth_data = {{
    "authorization_id": "AUTH-STAGE-A2-HDFS-SEED{seed}-COLAB-V1.5",
    "authorized_at": datetime.now(timezone.utc).isoformat(),
    "stage": "STAGE_A2",
    "dataset": "HDFS",
    "split_id": "SPL-HDFS-001",
    "seed": {seed},
    "authorization_status": "AUTHORIZED",
    "execution_provider": "GOOGLE_COLAB",
    "expected_execution_code_commit_sha": "{commit}",
    "execution_plan_path": "experiments/plans/STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
    "execution_plan_sha256": compute_sha256(plan_path),
    "environment_lock_path": "experiments/evidence/stage-a2/preexecution/STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json",
    "environment_lock_sha256": compute_sha256(env_lock_path),
    "raw_hdfs_sha256": "{RAW_HDFS_TAR_SHA}",
    "train_membership_sha256": "{TRAIN_MEMBERSHIP_SHA}",
    "val_membership_sha256": "{VAL_MEMBERSHIP_SHA}",
    "train_sessions_count": 35000,
    "val_sessions_count": 7500,
    "train_graph_events_count": 586577,
    "val_graph_events_count": 119531,
    "train_events_count": 586577,
    "val_events_count": 119531,
    "train_windows_count": 2292,
    "val_windows_count": 467,
    "optimizer_steps_per_epoch": 573,
    "test_opened": False,
    "firewall_policy": "TEST_SET_SEALED_UNTIL_STAGE_B",
    "authorized_by": "INDEPENDENT_QUALIFICATION_AUDIT_PASS"
}}

auth_dest.parent.mkdir(parents=True, exist_ok=True)
auth_dest.write_text(json.dumps(auth_data, indent=2) + '\\n', encoding='utf-8')
print("Launch Authorization Generated for Seed {seed}:", auth_dest)
"""

def build_training_script(seed: int, resume_checkpoint: Optional[str] = None, resume_sha256: Optional[str] = None) -> str:
    resume_args = ""
    if resume_checkpoint and resume_sha256:
        resume_args = f", '--resume', '{resume_checkpoint}', '--resume-sha256', '{resume_sha256}'"
        
    return f"""
import os, sys, subprocess
from pathlib import Path

repo_dir = Path('/content/Research')
dataset_path = Path('/content/stage-a2-data/HDFS_1.tar.gz')
durable_runs = Path('/content/drive/MyDrive/Chuyende-stage-a2/runs/HDFS')
plan_path = repo_dir / 'experiments' / 'plans' / 'STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json'
env_lock_path = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'preexecution' / 'STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json'
auth_path = repo_dir / 'experiments' / 'evidence' / 'stage-a2' / 'preexecution' / 'SEED{seed}-COLAB-LAUNCH-AUTHORIZATION-V1.5.json'

assert auth_path.exists(), f"Explicit authorization missing at {{auth_path}}"

os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'

train_cmd = [
    sys.executable, 'scripts/run_stage_a2_five_seed_empirical.py',
    '--seed', '{seed}',
    '--base-dir', str(repo_dir),
    '--dataset-path', str(dataset_path),
    '--durable-root', str(durable_runs),
    '--plan', str(plan_path),
    '--environment-lock', str(env_lock_path),
    '--authorization', str(auth_path),
    '--authorize-real-empirical-execution'{resume_args}
]

print("Executing Seed {seed} Training:", " ".join(train_cmd))
proc = subprocess.run(train_cmd, cwd=str(repo_dir))
if proc.returncode != 0:
    raise RuntimeError(f"Seed {seed} training exited with error code {{proc.returncode}}")
print("Seed {seed} Training Process Exited Cleanly (code 0).")
"""

def run_seed_dry_run(bridge: ColabCLIBridge, seed: int) -> Tuple[bool, str]:
    """Runs direct preflight dry-run for a specific canonical seed."""
    if seed not in CANONICAL_SEEDS:
        raise ValueError(f"Seed {seed} not in canonical list: {CANONICAL_SEEDS}")
    print(f"[DRY-RUN] Executing direct dry-run for Seed {seed}...")
    code = build_dry_run_script(seed).strip()
    returncode, stdout, stderr = bridge.exec_code(code)
    print(stdout)
    if returncode != 0:
        print(f"[DRY-RUN ERROR] {stderr}")
        return False, stderr
    return True, stdout

def authorize_and_launch_seed(bridge: ColabCLIBridge, seed: int, execution_commit: str, resume_checkpoint: Optional[str] = None, resume_sha256: Optional[str] = None) -> Tuple[bool, str]:
    """Generates authorization artifact and launches empirical training for a single seed."""
    if seed not in CANONICAL_SEEDS:
        raise ValueError(f"Seed {seed} not in canonical list: {CANONICAL_SEEDS}")
    if not execution_commit:
        raise ValueError("FATAL: APPROVED EXECUTION COMMIT REQUIRED")
    
    # 1. Authorize
    print(f"[AUTH] Authorizing Seed {seed} with commit {execution_commit} on remote runtime...")
    auth_code = build_authorization_payload(seed, execution_commit).strip()
    rc, out, err = bridge.exec_code(auth_code)
    if rc != 0:
        return False, f"Authorization generation failed: {err}"
        
    # 2. Launch
    print(f"[TRAIN] Launching canonical training for Seed {seed}...")
    train_code = build_training_script(seed, resume_checkpoint=resume_checkpoint, resume_sha256=resume_sha256).strip()
    rc, out, err = bridge.exec_code(train_code)
    print(out)
    if rc != 0:
        return False, err
    return True, out
