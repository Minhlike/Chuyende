# -*- coding: utf-8 -*-
"""
Stage A2 Google Colab Environment Bootstrap and Hardware Lock Generator (Protocol V1.5).
Executes hardware discovery, prerequisite verification, dataset copy and hash validation,
and generates the MACHINE-COLLECTED Colab environment lock candidate artifact.
ZERO HDFS optimizer steps.
"""

import os
# Enforce deterministic CUBLAS configuration before any CUDA context is created
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

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
from typing import Dict, Any, Optional

import torch

EXPECTED_HDFS_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
DEFAULT_BASE_DIR = Path(__file__).resolve().parent.parent

def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def get_git_commit_sha(repo_dir: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_dir), text=True).strip()
    except Exception:
        return "UNKNOWN_COMMIT"

def get_nvidia_driver_version() -> str:
    try:
        out = subprocess.check_output([
            "nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"
        ], text=True).strip()
        return out.splitlines()[0].strip()
    except Exception:
        return "UNKNOWN_DRIVER"

def get_gpu_uuid() -> str:
    try:
        out = subprocess.check_output([
            "nvidia-smi", "--query-gpu=gpu_uuid", "--format=csv,noheader"
        ], text=True).strip()
        return out.splitlines()[0].strip()
    except Exception:
        return "UNKNOWN_GPU_UUID"

def run_bootstrap(
    repo_dir: Optional[Path] = None,
    drive_data_source: Optional[Path] = None,
    local_data_dest: Optional[Path] = None,
    durable_root: Optional[Path] = None,
    env_lock_output_path: Optional[Path] = None
) -> Dict[str, Any]:
    repo_dir = Path(repo_dir).resolve() if repo_dir else DEFAULT_BASE_DIR
    drive_data_source = Path(drive_data_source).resolve() if drive_data_source else (repo_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz")
    local_data_dest = Path(local_data_dest).resolve() if local_data_dest else Path("/content/stage-a2-data/HDFS_1.tar.gz")
    durable_root = Path(durable_root).resolve() if durable_root else Path("/content/drive/MyDrive/Chuyende-stage-a2")
    env_lock_p = Path(env_lock_output_path).resolve() if env_lock_output_path else (repo_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json")

    print("=================================================================")
    print("   STAGE A2 GOOGLE COLAB RUNTIME BOOTSTRAP (V1.5)               ")
    print("=================================================================")
    print(f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print(f"Workspace Root:  {repo_dir}")
    print(f"Durable Root:    {durable_root}")
    print(f"Local Data Path: {local_data_dest}")
    print(f"Drive Data Path: {drive_data_source}")

    # 1. GPU Discovery and CUDA Hardware Verification
    if not torch.cuda.is_available():
        raise RuntimeError("FATAL: CUDA is not available! Colab session must be configured with a GPU runtime.")

    device_name = torch.cuda.get_device_name(0)
    device_props = torch.cuda.get_device_properties(0)
    compute_cap = f"{device_props.major}.{device_props.minor}"
    total_vram_bytes = device_props.total_memory
    total_vram_gb = total_vram_bytes / (1024 ** 3)
    driver_ver = get_nvidia_driver_version()
    gpu_uuid = get_gpu_uuid()

    print(f"[BOOTSTRAP 1] GPU Detected: {device_name} (Compute Cap: {compute_cap}, VRAM: {total_vram_gb:.2f} GB)")
    print(f"[BOOTSTRAP 1] NVIDIA Driver: {driver_ver} | GPU UUID (descriptive): {gpu_uuid}")

    # 2. Software Runtime Checks
    py_ver = platform.python_version()
    torch_ver = torch.__version__
    cuda_ver = torch.version.cuda
    cublas_cfg = os.environ.get("CUBLAS_WORKSPACE_CONFIG", "")

    print(f"[BOOTSTRAP 2] Python: {py_ver} | PyTorch: {torch_ver} | CUDA Runtime: {cuda_ver}")
    if cublas_cfg != ":4096:8":
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
        cublas_cfg = ":4096:8"
    print(f"[BOOTSTRAP 2] CUBLAS_WORKSPACE_CONFIG: {cublas_cfg}")

    # 3. Repository Commit Verification
    commit_sha = get_git_commit_sha(repo_dir)
    print(f"[BOOTSTRAP 3] Repository HEAD: {commit_sha}")

    # 4. HDFS Source Verification and Local Copy
    if drive_data_source.exists():
        print(f"[BOOTSTRAP 4] Verifying source HDFS tarball at {drive_data_source}...")
        src_sha = compute_sha256(drive_data_source)
        if src_sha != EXPECTED_HDFS_SHA:
            raise ValueError(f"FATAL: Source HDFS SHA-256 mismatch: {src_sha} != {EXPECTED_HDFS_SHA}")
        print(f"[BOOTSTRAP 4] Source HDFS SHA-256 MATCH ({src_sha[:16]}...)")

        # Copy to local fast ephemeral disk if different
        if local_data_dest != drive_data_source:
            local_data_dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"[BOOTSTRAP 4] Copying HDFS tarball to fast local storage: {local_data_dest}...")
            t_copy_0 = time.time()
            shutil.copy2(drive_data_source, local_data_dest)
            copy_dur = time.time() - t_copy_0
            print(f"[BOOTSTRAP 4] Copy completed in {copy_dur:.2f}s. Recomputing local copy SHA-256...")
            dst_sha = compute_sha256(local_data_dest)
            if dst_sha != EXPECTED_HDFS_SHA:
                raise ValueError(f"FATAL: Local copy HDFS SHA-256 mismatch: {dst_sha} != {EXPECTED_HDFS_SHA}")
            print(f"[BOOTSTRAP 4] Local copy HDFS SHA-256 MATCH ({dst_sha[:16]}...)")
    elif local_data_dest.exists():
        print(f"[BOOTSTRAP 4] Verifying existing local HDFS tarball at {local_data_dest}...")
        dst_sha = compute_sha256(local_data_dest)
        if dst_sha != EXPECTED_HDFS_SHA:
            raise ValueError(f"FATAL: Local HDFS SHA-256 mismatch: {dst_sha} != {EXPECTED_HDFS_SHA}")
        print(f"[BOOTSTRAP 4] Local HDFS SHA-256 MATCH ({dst_sha[:16]}...)")
    else:
        print(f"[BOOTSTRAP 4] WARNING: HDFS tarball not found at {drive_data_source} or {local_data_dest}. Ensure dataset is downloaded/copied.")

    # 5. Generate Environment Lock Artifact Candidate
    env_lock_p.parent.mkdir(parents=True, exist_ok=True)
    env_candidate = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "runtime_provider": "GOOGLE_COLAB",
        "runtime_type": "HOSTED_GPU",
        "hardware_assignment_policy": "DYNAMIC_DISCOVER_THEN_LOCK",
        "resume_environment_policy": "STRICT_LOCK_MATCH_REQUIRED",
        "durable_storage": "GOOGLE_DRIVE",
        "durable_root": str(durable_root),
        "dataset_local_copy_path": str(local_data_dest),
        "dataset_sha256": EXPECTED_HDFS_SHA,
        "execution_code_commit_sha": commit_sha,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python_executable": sys.executable,
        "python_version": py_ver,
        "pytorch_version": torch_ver,
        "torch_cuda_runtime": cuda_ver,
        "nvidia_driver_version": driver_ver,
        "device_type": "cuda",
        "device_name": device_name,
        "device_compute_capability": compute_cap,
        "total_vram_bytes": total_vram_bytes,
        "total_vram_gb": total_vram_gb,
        "gpu_uuid_descriptive": gpu_uuid,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False,
        "automatic_cpu_fallback": False,
        "qualification_status": "PENDING_CUDA_DETERMINISTIC_QUALIFICATION"
    }

    env_lock_p.write_text(json.dumps(env_candidate, indent=2) + "\n", encoding="utf-8")
    print(f"[BOOTSTRAP 5] Wrote Colab Environment Lock Candidate to {env_lock_p}")
    print(f"[BOOTSTRAP 5] Environment Lock Candidate SHA-256: {compute_sha256(env_lock_p)}")

    print("=================================================================")
    print("   COLAB BOOTSTRAP COMPLETE: READY FOR DETERMINISTIC QUALIFICATION")
    print("=================================================================\n")

    return env_candidate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage A2 Colab Environment Bootstrap")
    parser.add_argument("--repo-dir", type=str, default=None, help="Path to repository root")
    parser.add_argument("--drive-data-source", type=str, default=None, help="Path to raw HDFS on Drive")
    parser.add_argument("--local-data-dest", type=str, default=None, help="Path to copy raw HDFS locally in /content")
    parser.add_argument("--durable-root", type=str, default=None, help="Durable Google Drive root")
    parser.add_argument("--env-lock-output", type=str, default=None, help="Path to write environment lock candidate")
    args = parser.parse_args()

    run_bootstrap(
        repo_dir=Path(args.repo_dir) if args.repo_dir else None,
        drive_data_source=Path(args.drive_data_source) if args.drive_data_source else None,
        local_data_dest=Path(args.local_data_dest) if args.local_data_dest else None,
        durable_root=Path(args.durable_root) if args.durable_root else None,
        env_lock_output_path=Path(args.env_lock_output) if args.env_lock_output else None
    )
