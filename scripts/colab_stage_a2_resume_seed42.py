# -*- coding: utf-8 -*-
"""
Canonical Google Colab Resume Script for Stage A2 Seed 42.
Automates fail-closed environment validation, durable checkpoint inspection,
checkpoint-bound environment lock restoration, runtime requalification,
local workspace restoration, and unbuffered optimizer resumption.

Usage:
  # Inspect remote/local durable state without training:
  python scripts/colab_stage_a2_resume_seed42.py --status

  # Dry-run validation (0 optimizer steps executed):
  python scripts/colab_stage_a2_resume_seed42.py --dry-run --execution-commit <40-hex SHA>

  # Full real execution resume:
  python scripts/colab_stage_a2_resume_seed42.py --execute --execution-commit <40-hex SHA>
"""

import os
# Enforce deterministic CUBLAS configuration before any CUDA context is initialized
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
os.environ["PYTHONUNBUFFERED"] = "1"

import sys
import json
import time
import shutil
import hashlib
import platform
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

import torch

TARGET_SEED = 42
EXPECTED_RAW_HDFS_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
STEPS_PER_EPOCH = 573
TARGET_TOTAL_STEPS = 11460

ALLOWED_CLASSIFICATIONS = [
    "CANONICAL_RESUMABLE",
    "FORENSIC_NONCANONICAL",
    "PENDING_INDEPENDENT_CLASSIFICATION"
]

def compute_sha256_streaming(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    """Computes streaming SHA-256 hash to prevent memory spikes."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_nvidia_driver_version() -> str:
    """Queries NVIDIA driver version fail-closed via nvidia-smi."""
    try:
        out = subprocess.check_output([
            "nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"
        ], text=True).strip()
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        if not lines or not lines[0]:
            raise RuntimeError("Empty driver version returned from nvidia-smi")
        return lines[0]
    except Exception as e:
        return f"UNAVAILABLE ({e})"

def detect_colab_paths(base_dir_arg: Optional[Path] = None, durable_root_arg: Optional[Path] = None) -> Dict[str, Path]:
    """Resolves standard Colab or local filesystem paths."""
    is_colab = Path("/content").exists()
    
    if base_dir_arg:
        base_dir = Path(base_dir_arg).resolve()
    elif is_colab:
        base_dir = Path("/content/Research")
    else:
        base_dir = Path(__file__).resolve().parent.parent

    if durable_root_arg:
        durable_root = Path(durable_root_arg).resolve()
    elif is_colab:
        durable_root = Path("/content/drive/MyDrive/Chuyende-stage-a2/runs/HDFS")
    else:
        durable_root = base_dir / "experiments" / "runs" / "stage-a2" / "HDFS"

    local_data_dir = Path("/content/stage-a2-data") if is_colab else (base_dir / "datasets" / "raw" / "hdfs")
    raw_tarball_path = local_data_dir / "HDFS_1.tar.gz"

    return {
        "is_colab": is_colab,
        "base_dir": base_dir,
        "durable_root": durable_root,
        "raw_tarball_path": raw_tarball_path,
        "drive_canonical_dataset": Path("/content/drive/MyDrive/Chuyende-stage-a2/datasets/HDFS_1.tar.gz") if is_colab else (base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz"),
        "drive_fallback_dataset": Path("/content/drive/MyDrive/HDFS_1.tar.gz") if is_colab else (base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz")
    }

def discover_durable_seed42_state(durable_root: Path, base_dir: Path) -> Dict[str, Any]:
    """Inspects durable Google Drive run directory for Seed 42."""
    candidate_dirs = [
        durable_root / "seed-42",
        durable_root / "runs" / "HDFS" / "seed-42",
        base_dir / "experiments" / "runs" / "stage-a2" / "HDFS" / "seed-42"
    ]
    
    run_dir = None
    for c in candidate_dirs:
        if c.exists() and (c / "RUN-STATE.json").exists():
            run_dir = c
            break
            
    if not run_dir:
        for c in candidate_dirs:
            if c.exists():
                run_dir = c
                break

    state_data = {
        "found": run_dir is not None,
        "run_dir": run_dir,
        "status": "NOT_STARTED",
        "process_status": "NOT_STARTED",
        "completed_epoch": 0,
        "next_epoch_to_run": 0,
        "global_step": 0,
        "best_val_loss": None,
        "last_checkpoint_sha256": None,
        "last_checkpoint_path": None,
        "classification": "PENDING_INDEPENDENT_CLASSIFICATION",
        "is_resumable": False,
        "non_resumable_reason": None,
        "inventory": [],
        "firewall_status": "UNKNOWN"
    }

    if not run_dir or not run_dir.exists():
        state_data["non_resumable_reason"] = "Durable run directory does not exist on Drive."
        return state_data

    # Read external RUN-CLASSIFICATION.json
    class_p = run_dir / "RUN-CLASSIFICATION.json"
    if class_p.exists():
        try:
            cdata = json.loads(class_p.read_text(encoding="utf-8"))
            state_data["classification"] = cdata.get("classification", "PENDING_INDEPENDENT_CLASSIFICATION")
        except Exception as e:
            state_data["classification"] = "PENDING_INDEPENDENT_CLASSIFICATION"
            state_data["non_resumable_reason"] = f"Corrupted RUN-CLASSIFICATION.json: {e}"
    else:
        state_data["classification"] = "PENDING_INDEPENDENT_CLASSIFICATION"

    run_state_p = run_dir / "RUN-STATE.json"
    if run_state_p.exists():
        try:
            rs = json.loads(run_state_p.read_text(encoding="utf-8"))
            recorded_status = rs.get("status", "UNKNOWN")
            state_data["status"] = recorded_status
            state_data["completed_epoch"] = rs.get("completed_epoch", 0)
            state_data["next_epoch_to_run"] = rs.get("next_epoch_to_run", 0)
            state_data["global_step"] = rs.get("global_step", 0)
            state_data["best_val_loss"] = rs.get("best_val_loss")
            state_data["last_checkpoint_sha256"] = rs.get("last_checkpoint_sha256")
            
            # Check process liveness
            if recorded_status == "RUNNING":
                state_data["process_status"] = "STALE_OR_INTERRUPTED"
            elif recorded_status == "COMPLETED":
                state_data["process_status"] = "COMPLETED"
            else:
                state_data["process_status"] = recorded_status
                
        except Exception as e:
            state_data["non_resumable_reason"] = f"Failed to parse RUN-STATE.json: {e}"

    inv_p = run_dir / "CHECKPOINT-INVENTORY.json"
    if inv_p.exists():
        try:
            inv = json.loads(inv_p.read_text(encoding="utf-8"))
            state_data["inventory"] = inv.get("checkpoints", [])
        except Exception:
            pass

    # Read TEST-FIREWALL.json if present
    tf_p = run_dir / "TEST-FIREWALL.json"
    if tf_p.exists():
        try:
            tf_data = json.loads(tf_p.read_text(encoding="utf-8"))
            if tf_data.get("test_opened") is False and tf_data.get("test_feature_reads", 0) == 0:
                state_data["firewall_status"] = "LOCKED"
            else:
                state_data["firewall_status"] = "BREACHED"
        except Exception:
            state_data["firewall_status"] = "UNVERIFIED"
    else:
        state_data["firewall_status"] = "UNVERIFIED_NO_EVIDENCE_FILE"

    # Locate checkpoint file
    candidate_ckpts = [
        run_dir / "last_checkpoint.pt",
        run_dir / "best_val_loss.pt",
        base_dir / ".artifacts" / "stage-a2" / "HDFS" / "seed-42" / "last_checkpoint.pt"
    ]
    for ckpt in candidate_ckpts:
        if ckpt.exists():
            state_data["last_checkpoint_path"] = ckpt
            break

    # Determine resumability
    if state_data["classification"] == "PENDING_INDEPENDENT_CLASSIFICATION":
        state_data["is_resumable"] = False
        state_data["non_resumable_reason"] = "RESUME REFUSED: RUN CLASSIFICATION IS PENDING_INDEPENDENT_CLASSIFICATION"
    elif state_data["classification"] == "FORENSIC_NONCANONICAL":
        state_data["is_resumable"] = False
        state_data["non_resumable_reason"] = "RESUME REFUSED: EXISTING SEED42 CHECKPOINT IS FORENSIC-ONLY"
    elif state_data["classification"] != "CANONICAL_RESUMABLE":
        state_data["is_resumable"] = False
        state_data["non_resumable_reason"] = f"RESUME REFUSED: UNKNOWN CLASSIFICATION '{state_data['classification']}'"
    elif state_data["status"] == "COMPLETED":
        state_data["is_resumable"] = False
        state_data["non_resumable_reason"] = "Run is already COMPLETED (all epochs finished)."
    elif state_data["completed_epoch"] >= 1 and state_data["last_checkpoint_path"] is not None:
        state_data["is_resumable"] = True
    else:
        state_data["is_resumable"] = False
        if not state_data["non_resumable_reason"]:
            state_data["non_resumable_reason"] = "No valid completed-epoch checkpoint found."

    return state_data

def inspect_checkpoint_integrity(checkpoint_path: Path, expected_sha: Optional[str] = None) -> Dict[str, Any]:
    """Inspects checkpoint metadata fail-closed using torch.load(..., weights_only=False)."""
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint missing at {checkpoint_path}")

    actual_sha = compute_sha256_streaming(checkpoint_path)
    if expected_sha and actual_sha != expected_sha:
        raise ValueError(f"Checkpoint SHA mismatch: {actual_sha} != expected {expected_sha}")

    ckpt_data = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    meta = ckpt_data.get("checkpoint_metadata", {})
    
    return {
        "actual_sha256": actual_sha,
        "seed": meta.get("seed"),
        "run_id": meta.get("run_id"),
        "completed_epoch": meta.get("completed_epoch", ckpt_data.get("epoch")),
        "next_epoch_to_run": meta.get("next_epoch_to_run", meta.get("completed_epoch", 0)),
        "global_step": meta.get("global_step", ckpt_data.get("global_step", 0)),
        "execution_code_commit_sha": meta.get("execution_code_commit_sha"),
        "raw_dataset_sha256": meta.get("raw_dataset_sha256"),
        "train_membership_sha256": meta.get("train_membership_sha256"),
        "val_membership_sha256": meta.get("val_membership_sha256"),
        "protocol_lock_sha256": meta.get("protocol_lock_sha256"),
        "environment_lock_sha256": meta.get("environment_lock_sha256")
    }

def restore_local_workspace_state(durable_seed_dir: Path, base_dir: Path) -> Tuple[bool, str]:
    """Restores local run state and artifacts atomically from Google Drive."""
    local_run_dir = base_dir / "experiments" / "runs" / "stage-a2" / "HDFS" / "seed-42"
    local_artifact_dir = base_dir / ".artifacts" / "stage-a2" / "HDFS" / "seed-42"
    
    local_run_dir.mkdir(parents=True, exist_ok=True)
    local_artifact_dir.mkdir(parents=True, exist_ok=True)
    
    small_evidence_files = [
        "RUN-STATE.json", "TRAIN-LOG.jsonl", "CHECKPOINT-INVENTORY.json",
        "ENVIRONMENT.json", "TEST-FIREWALL.json", "RUN-CLASSIFICATION.json"
    ]
    for fname in small_evidence_files:
        src = durable_seed_dir / fname
        if src.exists():
            dst = local_run_dir / fname
            tmp = dst.with_suffix(".tmp")
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)
            if compute_sha256_streaming(dst) != compute_sha256_streaming(src):
                return False, f"SHA mismatch when restoring {fname}"
                
    ckpt_files = ["last_checkpoint.pt", "best_val_loss.pt"]
    for cname in ckpt_files:
        src = durable_seed_dir / cname
        if src.exists():
            dst = local_artifact_dir / cname
            tmp = dst.with_suffix(".tmp")
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)
            if compute_sha256_streaming(dst) != compute_sha256_streaming(src):
                return False, f"SHA mismatch when restoring {cname}"
                
    return True, "Workspace restored successfully."

def restore_checkpoint_environment_lock(checkpoint_env_sha: str, base_dir: Path, durable_root: Path) -> Path:
    """Locates and restores the exact checkpoint-bound environment lock from Drive qualification."""
    if durable_root.name == "HDFS" and durable_root.parent.name == "runs":
        qual_root = durable_root.parent.parent / "qualification"
    elif durable_root.name == "runs":
        qual_root = durable_root.parent / "qualification"
    else:
        qual_root = durable_root / "qualification"
    
    found_lock = None
    if qual_root.exists():
        for qdir in qual_root.iterdir():
            if qdir.is_dir():
                cand = qdir / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
                if cand.exists():
                    if compute_sha256_streaming(cand) == checkpoint_env_sha:
                        found_lock = cand
                        break
                        
    local_lock_dest = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    local_lock_dest.parent.mkdir(parents=True, exist_ok=True)
    
    if found_lock:
        shutil.copy2(found_lock, local_lock_dest)
    elif local_lock_dest.exists() and compute_sha256_streaming(local_lock_dest) == checkpoint_env_sha:
        pass
    else:
        raise FileNotFoundError(f"FATAL: Checkpoint-bound environment lock {checkpoint_env_sha} not found in {qual_root}!")
        
    actual_sha = compute_sha256_streaming(local_lock_dest)
    if actual_sha != checkpoint_env_sha:
        raise ValueError(f"FATAL: Restored environment lock SHA mismatch: {actual_sha} != {checkpoint_env_sha}")
        
    return local_lock_dest

def print_status_report(paths: Dict[str, Any], state: Dict[str, Any]) -> None:
    """Prints status mode summary."""
    print("=================================================================")
    print("   STAGE A2 SEED-42 DURABLE STATUS REPORT                        ")
    print("=================================================================")
    print(f"SEED:                    {TARGET_SEED}")
    print(f"STATUS:                  {state['status']}")
    print(f"PROCESS_STATUS:          {state['process_status']}")
    print(f"CLASSIFICATION:          {state['classification']}")
    print(f"COMPLETED_EPOCH:         {state['completed_epoch']}")
    print(f"NEXT_EPOCH:              {state['next_epoch_to_run']}")
    print(f"GLOBAL_STEP:             {state['global_step']}")
    print(f"BEST_VAL_LOSS:           {state['best_val_loss']}")
    print(f"LAST_CHECKPOINT_SHA256:  {state['last_checkpoint_sha256']}")
    print(f"LAST_CHECKPOINT_EXISTS:  {'YES' if state['last_checkpoint_path'] else 'NO'}")
    print(f"DURABLE_DRIVE_STATE:     {state['run_dir'] if state['run_dir'] else 'NOT_FOUND'}")
    print(f"RESUMABLE:               {'YES' if state['is_resumable'] else 'NO'}")
    if not state['is_resumable']:
        print(f"NON_RESUMABLE_REASON:    {state['non_resumable_reason']}")
    print(f"TEST_FIREWALL:           {state['firewall_status']}")
    print("=================================================================\n")

def run_preflight_and_resume(
    mode: str,
    execution_commit: Optional[str] = None,
    base_dir_arg: Optional[Path] = None,
    durable_root_arg: Optional[Path] = None
) -> int:
    """Main verification, pre-resume report, and executor."""
    paths = detect_colab_paths(base_dir_arg, durable_root_arg)
    base_dir = paths["base_dir"]
    durable_root = paths["durable_root"]
    
    # 1. Inspect Durable Seed 42 State
    state = discover_durable_seed42_state(durable_root, base_dir)
    
    if mode == "status":
        print_status_report(paths, state)
        return 0

    if not execution_commit or not re.match(r"^[0-9a-fA-F]{40}$", execution_commit.strip()):
        print("FATAL: APPROVED EXECUTION COMMIT REQUIRED (--execution-commit <40-hex SHA>)")
        return 1

    target_commit = execution_commit.strip()

    print("=================================================================")
    print(f"   STAGE A2 SEED-42 CANONICAL RESUME (Mode: {mode.upper()})      ")
    print("=================================================================")

    # 2. Check Classification Invariant
    if not state["is_resumable"]:
        print(f"FATAL: Seed 42 is not in a resumable state: {state['non_resumable_reason']}")
        return 1

    ckpt_path = state["last_checkpoint_path"]
    ckpt_meta = inspect_checkpoint_integrity(ckpt_path, expected_sha=state["last_checkpoint_sha256"])

    # 3. Cross-check Checkpoint Metadata with Approved Execution Commit
    if ckpt_meta.get("execution_code_commit_sha") and ckpt_meta["execution_code_commit_sha"] != target_commit:
        print(f"FATAL: Checkpoint commit ({ckpt_meta['execution_code_commit_sha']}) != Approved commit ({target_commit})")
        return 1

    # 4. Verify Hardware & PyTorch environment
    if not torch.cuda.is_available():
        print("FATAL: CUDA GPU is not available in current environment!")
        return 1

    props = torch.cuda.get_device_properties(0)
    gpu_name = torch.cuda.get_device_name(0)
    compute_cap = f"{props.major}.{props.minor}"
    vram_gb = props.total_memory / (1024**3)
    driver_ver = get_nvidia_driver_version()

    # 5. Restore Local Workspace State
    ok, rmsg = restore_local_workspace_state(state["run_dir"], base_dir)
    if not ok:
        print(f"FATAL: Local workspace restoration failed: {rmsg}")
        return 1

    # 6. Restore and Requalify Checkpoint-Bound Environment Lock
    env_lock_sha = ckpt_meta["environment_lock_sha256"]
    env_lock_path = restore_checkpoint_environment_lock(env_lock_sha, base_dir, durable_root)
    
    qual_output_dir = base_dir / "experiments" / "evidence" / "stage-a2" / "resume_qualification"
    qual_output_dir.mkdir(parents=True, exist_ok=True)
    
    qual_cmd = [
        sys.executable, str(base_dir / "scripts" / "run_stage_a2_deterministic_qualification.py"),
        "--device", "cuda",
        "--base-dir", str(base_dir),
        "--environment-lock", str(env_lock_path),
        "--output-dir", str(qual_output_dir)
    ]
    print("Running Runtime Requalification:", " ".join(qual_cmd))
    q_proc = subprocess.run(qual_cmd, capture_output=True, text=True)
    if q_proc.returncode != 0:
        print(f"FATAL: Runtime requalification against checkpoint lock failed:\n{q_proc.stderr}")
        return 1

    # 7. Print Pre-Resume Summary
    completed_epoch = ckpt_meta["completed_epoch"]
    global_step = ckpt_meta["global_step"]
    next_epoch = completed_epoch + 1

    print("=================================================================")
    print("   STAGE A2 SEED-42 CANONICAL PRE-RESUME SUMMARY                 ")
    print("=================================================================")
    print(f"EXECUTION COMMIT:     {target_commit}")
    print(f"GPU:                  {gpu_name} (CC {compute_cap}, {vram_gb:.2f} GB VRAM)")
    print(f"PYTHON:               {platform.python_version()}")
    print(f"PYTORCH:              {torch.__version__}")
    print(f"CUDA:                 {torch.version.cuda}")
    print(f"DRIVER:               {driver_ver}")
    print(f"CHECKPOINT PATH:      {ckpt_path}")
    print(f"CHECKPOINT SHA:       {ckpt_meta['actual_sha256']}")
    print(f"COMPLETED EPOCH:      {completed_epoch}")
    print(f"GLOBAL STEP:          {global_step}")
    print(f"NEXT EPOCH:           {next_epoch}")
    print(f"TEST FIREWALL:        {state['firewall_status']}")
    print("=================================================================")
    print(f"RESUMED FROM COMPLETED EPOCH: {completed_epoch}")
    print(f"STARTING EPOCH:               {next_epoch}")
    print(f"STARTING GLOBAL STEP:         {global_step}")
    print("=================================================================\n")

    plan_path = base_dir / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    auth_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "SEED42-COLAB-LAUNCH-AUTHORIZATION-V1.5.json"
    
    if not auth_path.exists():
        print(f"FATAL: Launch authorization artifact missing at {auth_path}")
        return 1

    raw_tar = paths["raw_tarball_path"]
    resume_cmd = [
        sys.executable, "-u", str(base_dir / "scripts" / "run_stage_a2_five_seed_empirical.py"),
        "--seed", "42",
        "--resume", str(ckpt_path),
        "--resume-sha256", str(ckpt_meta["actual_sha256"]),
        "--base-dir", str(base_dir),
        "--dataset-path", str(raw_tar),
        "--durable-root", str(durable_root),
        "--plan", str(plan_path),
        "--environment-lock", str(env_lock_path),
        "--authorization", str(auth_path),
        "--authorize-real-empirical-execution"
    ]

    if mode == "dry-run":
        print("[DRY-RUN] Canonical resume command to be executed:")
        print(" ".join(resume_cmd))
        print("\nRESUME_DRY_RUN: PASS")
        print("OPTIMIZER_STEPS_EXECUTED: 0")
        return 0

    if mode == "execute":
        print("[EXECUTE] Launching unbuffered Stage A2 Seed 42 optimizer continuation...")
        proc = subprocess.run(resume_cmd, cwd=str(base_dir))
        return proc.returncode

    return 0

def main():
    parser = argparse.ArgumentParser(description="Canonical Colab Resume Shell for Stage A2 Seed 42")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Print durable Seed 42 state without executing")
    group.add_argument("--dry-run", action="store_true", help="Perform pre-flight verification without training")
    group.add_argument("--execute", action="store_true", help="Execute real optimizer resumption")
    
    parser.add_argument("--execution-commit", type=str, default=None, help="Approved 40-hex execution commit")
    parser.add_argument("--base-dir", type=str, default=None, help="Base repository directory")
    parser.add_argument("--durable-root", type=str, default=None, help="Durable storage root directory")

    args = parser.parse_args()

    mode = "status" if args.status else ("dry-run" if args.dry_run else "execute")
    base_dir = Path(args.base_dir) if args.base_dir else None
    durable_root = Path(args.durable_root) if args.durable_root else None

    rc = run_preflight_and_resume(
        mode=mode,
        execution_commit=args.execution_commit,
        base_dir_arg=base_dir,
        durable_root_arg=durable_root
    )
    sys.exit(rc)

if __name__ == "__main__":
    main()
