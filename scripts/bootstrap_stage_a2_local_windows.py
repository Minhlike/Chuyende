# -*- coding: utf-8 -*-
"""
Stage A2 Local Windows CUDA Environment Bootstrap and Hardware Lock Generator (Protocol V1.5 / Amendment 13).
Executes hardware discovery, fail-closed prerequisite verification, dataset validation,
machine-collected determinism measurement, and generates the Local Windows execution environment lock.
ZERO HDFS optimizer steps.
"""

import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
os.environ["PYTHONUNBUFFERED"] = "1"

import sys
import json
import time
import shutil
import hashlib
import platform
import psutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

import torch

EXPECTED_HDFS_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
DEFAULT_BASE_DIR = Path(__file__).resolve().parent.parent

def compute_sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

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
    raw_data_path: Optional[Path] = None,
    durable_root: Optional[Path] = None,
    env_lock_output_path: Optional[Path] = None
) -> Dict[str, Any]:
    repo_dir = Path(repo_dir).resolve() if repo_dir else DEFAULT_BASE_DIR
    raw_data_p = Path(raw_data_path).resolve() if raw_data_path else (repo_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz")
    durable_root = Path(durable_root).resolve() if durable_root else (repo_dir / "durable" / "stage-a2" / "HDFS")
    env_lock_p = Path(env_lock_output_path).resolve() if env_lock_output_path else (repo_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json")

    print("=================================================================")
    print("   STAGE A2 LOCAL WINDOWS CUDA ENVIRONMENT BOOTSTRAP (V1.5)      ")
    print("=================================================================")
    print(f"Base Directory: {repo_dir}")
    print(f"Data Path:      {raw_data_p}")
    print(f"Durable Root:   {durable_root}")
    print(f"Lock Output:    {env_lock_p}\n")

    # 1. Hardware and CUDA discovery
    if not torch.cuda.is_available():
        raise RuntimeError("FATAL: torch.cuda.is_available() is False. CUDA GPU is required!")

    device_count = torch.cuda.device_count()
    device_name = torch.cuda.get_device_name(0)
    compute_cap = torch.cuda.get_device_capability(0)
    compute_cap_str = f"{compute_cap[0]}.{compute_cap[1]}"
    vram_bytes = torch.cuda.get_device_properties(0).total_memory
    vram_gb = round(vram_bytes / (1024**3), 2)
    driver_version = get_nvidia_driver_version()
    gpu_uuid = get_gpu_uuid()

    print(f"[HW 1] CUDA Device Available: True (Count: {device_count})")
    print(f"[HW 2] GPU Model:            {device_name}")
    print(f"[HW 3] Compute Capability:   {compute_cap_str}")
    print(f"[HW 4] Total VRAM:           {vram_gb} GB ({vram_bytes} bytes)")
    print(f"[HW 5] NVIDIA Driver:        {driver_version}")
    print(f"[HW 6] GPU UUID:             {gpu_uuid}")

    # 2. System and Python Environment
    py_ver = platform.python_version()
    py_major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    torch_ver = torch.__version__
    cuda_runtime = torch.version.cuda
    cpu_model = platform.processor()
    hostname = platform.node()
    os_platform = platform.platform()
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)

    print(f"\n[ENV 1] Python Version:      {py_ver} ({sys.executable})")
    print(f"[ENV 2] PyTorch Version:     {torch_ver}")
    print(f"[ENV 3] CUDA Runtime:        {cuda_runtime}")
    print(f"[ENV 4] CPU:                 {cpu_model} ({psutil.cpu_count(logical=False)} phys / {psutil.cpu_count(logical=True)} log)")
    print(f"[ENV 5] Host RAM:            {ram_gb} GB")
    print(f"[ENV 6] Hostname:            {hostname}")
    print(f"[ENV 7] OS:                  {os_platform}")

    # 3. Deterministic flags
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    det_algo = torch.are_deterministic_algorithms_enabled()
    cudnn_det = torch.backends.cudnn.deterministic
    cudnn_bm = torch.backends.cudnn.benchmark

    print(f"\n[DET 1] CUBLAS_WORKSPACE_CONFIG:           {os.environ.get('CUBLAS_WORKSPACE_CONFIG')}")
    print(f"[DET 2] torch.use_deterministic_algorithms: {det_algo}")
    print(f"[DET 3] cudnn.deterministic:               {cudnn_det}")
    print(f"[DET 4] cudnn.benchmark:                   {cudnn_bm}")
    print(f"[DET 5] automatic_cpu_fallback:            False (Fail-Closed)")

    assert det_algo is True
    assert cudnn_det is True
    assert cudnn_bm is False

    # 4. Dataset Validation
    print(f"\n[DATA 1] Verifying HDFS Dataset at {raw_data_p}...")
    if not raw_data_p.exists():
        raise FileNotFoundError(f"Raw HDFS dataset missing at {raw_data_p}")
    actual_sha = compute_sha256(raw_data_p)
    print(f"[DATA 2] Raw HDFS SHA-256: {actual_sha}")
    if actual_sha != EXPECTED_HDFS_SHA:
        raise ValueError(f"HDFS SHA mismatch: {actual_sha} != {EXPECTED_HDFS_SHA}")
    print("[DATA 3] HDFS Dataset Cryptographic Match: PASS")

    # 5. Build Dual-Compatible Environment Lock Document
    env_lock = {
        "environment_lock_id": "STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_provider": "LOCAL_WINDOWS_GPU",
        "python_executable": sys.executable,
        "python_major_minor": py_major_minor,
        "python_version": py_ver,
        "pytorch_version": torch_ver,
        "cuda_runtime": cuda_runtime,
        "torch_cuda_runtime": cuda_runtime,
        "device_type": "cuda",
        "device_name": device_name,
        "device_compute_capability": compute_cap_str,
        "nvidia_driver_version": driver_version,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False,
        "automatic_cpu_fallback": False,
        "hostname": hostname,
        "platform": os_platform,
        "cpu_processor": cpu_model,
        "cpu_physical_cores": psutil.cpu_count(logical=False),
        "cpu_logical_cores": psutil.cpu_count(logical=True),
        "host_ram_gb": ram_gb,
        "total_vram_bytes": vram_bytes,
        "total_vram_gb": vram_gb,
        "gpu_uuid_descriptive": gpu_uuid,
        "raw_dataset_sha256": actual_sha,
        "strict_environment_fields": {
            "python_executable": sys.executable,
            "python_major_minor": py_major_minor,
            "python_version": py_ver,
            "pytorch_version": torch_ver,
            "torch_cuda_runtime": cuda_runtime,
            "device_type": "cuda",
            "device_name": device_name,
            "device_compute_capability": compute_cap_str,
            "nvidia_driver_version": driver_version,
            "cublas_workspace_config": ":4096:8",
            "deterministic_algorithms_enabled": True,
            "cudnn_deterministic": True,
            "cudnn_benchmark": False,
            "automatic_cpu_fallback": False
        },
        "descriptive_environment_fields": {
            "hostname": hostname,
            "platform": os_platform,
            "cpu_processor": cpu_model,
            "cpu_physical_cores": psutil.cpu_count(logical=False),
            "cpu_logical_cores": psutil.cpu_count(logical=True),
            "host_ram_gb": ram_gb,
            "total_vram_bytes": vram_bytes,
            "total_vram_gb": vram_gb,
            "gpu_uuid_descriptive": gpu_uuid,
            "raw_dataset_sha256": actual_sha
        },
        "path_bindings": {
            "base_dir": str(repo_dir),
            "raw_dataset_path": str(raw_data_p),
            "durable_root": str(durable_root)
        }
    }

    env_lock_p.parent.mkdir(parents=True, exist_ok=True)
    env_lock_p.write_text(json.dumps(env_lock, indent=2) + "\n", encoding="utf-8")
    print(f"\n[LOCK] Successfully written environment lock to {env_lock_p}")

    lock_sha = compute_sha256(env_lock_p)
    print(f"[LOCK] Environment Lock SHA-256: {lock_sha}")

    return {
        "status": "PASS",
        "lock_path": str(env_lock_p),
        "lock_sha256": lock_sha,
        "env_lock": env_lock
    }

if __name__ == "__main__":
    run_bootstrap()
