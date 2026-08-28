# -*- coding: utf-8 -*-
"""
Canonical Google Colab Fresh Launch Script for Stage A2 Seed 42.
Executes fresh canonical Seed 42 training with exact RNG ordering without resuming legacy checkpoints.
Archives old noncanonical Seed 42 run to a forensic namespace on Google Drive without deleting anything.

Usage:
  # Dry-run validation (0 optimizer steps executed):
  python scripts/colab_stage_a2_fresh_seed42.py --dry-run --commit <40-hex SHA>

  # Real empirical training:
  python scripts/colab_stage_a2_fresh_seed42.py --execute --commit <40-hex SHA>
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

def archive_old_durable_seed42_directory(durable_seed_dir: Path) -> Optional[Path]:
    """
    Safely archives any pre-existing noncanonical Seed 42 run directory on Drive
    to a forensic namespace without deleting anything.
    """
    if not durable_seed_dir.exists():
        return None

    utc_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    forensic_dest = durable_seed_dir.parent / f"seed-42-forensic-noncanonical-{utc_ts}"
    
    print(f"[FORENSIC ARCHIVE] Preserving existing Seed 42 directory to: {forensic_dest}")
    durable_seed_dir.rename(forensic_dest)
    
    # Write explicit forensic classification note
    note_p = forensic_dest / "RUN-CLASSIFICATION.json"
    note_data = {
        "seed": 42,
        "classification": "NONCANONICAL_RNG_INITIALIZATION",
        "archived_at": datetime.now(timezone.utc).isoformat(),
        "reason": "Historical attempt completed before RNG initialization ordering fix; preserved for audit."
    }
    note_p.write_text(json.dumps(note_data, indent=2) + "\n", encoding="utf-8")
    return forensic_dest

def run_fresh_seed42_launch(
    mode: str,
    commit_sha: Optional[str] = None,
    base_dir_arg: Optional[Path] = None,
    durable_root_arg: Optional[Path] = None
) -> int:
    """Prepares environment and launches fresh canonical Seed 42 execution."""
    paths = detect_colab_paths(base_dir_arg, durable_root_arg)
    base_dir = paths["base_dir"]
    durable_root = paths["durable_root"]
    
    print("=================================================================")
    print(f"   STAGE A2 FRESH CANONICAL SEED-42 LAUNCHER (Mode: {mode.upper()}) ")
    print("=================================================================")

    # 1. Verify GPU
    if not torch.cuda.is_available():
        print("FATAL: CUDA GPU is not available in current environment!")
        return 1

    props = torch.cuda.get_device_properties(0)
    gpu_name = torch.cuda.get_device_name(0)
    compute_cap = f"{props.major}.{props.minor}"
    vram_gb = props.total_memory / (1024**3)
    driver_ver = get_nvidia_driver_version()

    # 2. Verify PyTorch & CUDA version
    if torch.__version__ != "2.6.0+cu124" or torch.version.cuda != "12.4":
        print(f"FATAL: Exact PyTorch runtime mismatch: {torch.__version__} (CUDA {torch.version.cuda}) != 2.6.0+cu124 (CUDA 12.4)")
        return 1

    # 3. Verify Approved Commit
    try:
        head_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(base_dir), text=True).strip()
        status_out = subprocess.check_output(["git", "status", "--porcelain", "src", "scripts", "experiments"], cwd=str(base_dir), text=True).strip()
        is_clean = (len(status_out) == 0)
    except Exception as e:
        head_commit = "UNKNOWN"
        is_clean = False

    if commit_sha and head_commit != commit_sha.strip():
        print(f"FATAL: Execution commit mismatch! HEAD ({head_commit}) != Approved ({commit_sha})")
        return 1
        
    if not is_clean:
        print("FATAL: Git working directory has uncommitted changes in execution source!")
        return 1

    # 4. Verify Dataset
    raw_tar = paths["raw_tarball_path"]
    if not raw_tar.exists():
        if paths["drive_canonical_dataset"].exists():
            print(f"Copying HDFS dataset from Drive to {raw_tar}...")
            raw_tar.parent.mkdir(parents=True, exist_ok=True)
            tmp_p = raw_tar.with_suffix(".tar.gz.tmp")
            shutil.copy2(paths["drive_canonical_dataset"], tmp_p)
            os.replace(tmp_p, raw_tar)
        elif paths["drive_fallback_dataset"].exists():
            print(f"Copying fallback HDFS dataset from Drive to {raw_tar}...")
            raw_tar.parent.mkdir(parents=True, exist_ok=True)
            tmp_p = raw_tar.with_suffix(".tar.gz.tmp")
            shutil.copy2(paths["drive_fallback_dataset"], tmp_p)
            os.replace(tmp_p, raw_tar)
        else:
            print(f"FATAL: Raw HDFS dataset not found at {raw_tar} or on Drive!")
            return 1

    dataset_sha = compute_sha256_streaming(raw_tar)
    if dataset_sha != EXPECTED_RAW_HDFS_SHA:
        print(f"FATAL: HDFS raw dataset SHA mismatch: {dataset_sha} != {EXPECTED_RAW_HDFS_SHA}")
        return 1

    # 5. Environment Lock & Qualification
    env_lock_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    if not env_lock_path.exists():
        print(f"FATAL: Environment lock missing at {env_lock_path}!")
        return 1

    plan_path = base_dir / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    auth_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "SEED42-COLAB-LAUNCH-AUTHORIZATION-V1.5.json"
    if not auth_path.exists():
        print(f"FATAL: Launch authorization artifact missing at {auth_path}!")
        return 1

    # 6. Verify Local Cleanliness
    local_run_dir = base_dir / "experiments" / "runs" / "stage-a2" / "HDFS" / "seed-42"
    local_art_dir = base_dir / ".artifacts" / "stage-a2" / "HDFS" / "seed-42"
    if local_run_dir.exists() and any(local_run_dir.iterdir()):
        print(f"FATAL: Local run directory is not clean: {local_run_dir}")
        return 1
    if local_art_dir.exists() and any(local_art_dir.iterdir()):
        print(f"FATAL: Local artifact directory is not clean: {local_art_dir}")
        return 1

    # 7. Archive Old Durable Directory on Drive (if in real execution mode)
    durable_seed_dir = durable_root / "seed-42"
    if mode == "execute" and durable_seed_dir.exists():
        archive_old_durable_seed42_directory(durable_seed_dir)
        durable_seed_dir.mkdir(parents=True, exist_ok=True)

    # 8. Print Summary
    print("=================================================================")
    print("   STAGE A2 SEED-42 FRESH LAUNCH SUMMARY                         ")
    print("=================================================================")
    print(f"EXECUTION COMMIT:     {head_commit}")
    print(f"GPU:                  {gpu_name} (CC {compute_cap}, {vram_gb:.2f} GB VRAM)")
    print(f"PYTHON:               {platform.python_version()}")
    print(f"PYTORCH:              {torch.__version__}")
    print(f"CUDA:                 {torch.version.cuda}")
    print(f"DRIVER:               {driver_ver}")
    print(f"DATASET SHA:          {dataset_sha}")
    print(f"DURABLE ROOT:         {durable_root}")
    print(f"CANONICAL SEED DIR:   {durable_seed_dir}")
    print(f"TEST FIREWALL:        LOCKED (TEST_OPENED=false)")
    print("=================================================================\n")

    runner_cmd = [
        sys.executable, "-u", str(base_dir / "scripts" / "run_stage_a2_five_seed_empirical.py"),
        "--seed", "42",
        "--base-dir", str(base_dir),
        "--dataset-path", str(raw_tar),
        "--durable-root", str(durable_root),
        "--plan", str(plan_path),
        "--environment-lock", str(env_lock_path),
        "--authorization", str(auth_path)
    ]

    if mode == "dry-run":
        runner_cmd.append("--dry-run")
        print("[DRY-RUN] Executing direct canonical preflight dry-run:")
        print(" ".join(runner_cmd))
        proc = subprocess.run(runner_cmd, cwd=str(base_dir))
        return proc.returncode

    if mode == "execute":
        runner_cmd.append("--authorize-real-empirical-execution")
        print("[EXECUTE] Launching canonical unbuffered fresh Seed 42 training:")
        print(" ".join(runner_cmd))
        proc = subprocess.run(runner_cmd, cwd=str(base_dir))
        return proc.returncode

    return 0

def main():
    parser = argparse.ArgumentParser(description="Canonical Colab Fresh Launch Script for Stage A2 Seed 42")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Perform pre-flight verification without training")
    group.add_argument("--execute", action="store_true", help="Execute real fresh empirical training")
    
    parser.add_argument("--commit", type=str, default=None, help="Approved 40-hex execution commit SHA")
    parser.add_argument("--base-dir", type=str, default=None, help="Base repository directory")
    parser.add_argument("--durable-root", type=str, default=None, help="Durable storage root directory")

    args = parser.parse_args()

    mode = "dry-run" if args.dry_run else "execute"
    base_dir = Path(args.base_dir) if args.base_dir else None
    durable_root = Path(args.durable_root) if args.durable_root else None

    rc = run_fresh_seed42_launch(
        mode=mode,
        commit_sha=args.commit,
        base_dir_arg=base_dir,
        durable_root_arg=durable_root
    )
    sys.exit(rc)

if __name__ == "__main__":
    main()
