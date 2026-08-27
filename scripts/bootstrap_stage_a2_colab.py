# -*- coding: utf-8 -*-
"""
Stage A2 Google Colab Environment Bootstrap and Hardware Lock Generator (Protocol V1.5).
Executes hardware discovery, fail-closed prerequisite verification, streaming dataset validation,
machine-collected determinism measurement, and generates the candidate Colab environment lock.
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
from typing import Dict, Any, Optional, List, Tuple

import torch

EXPECTED_HDFS_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
DEFAULT_BASE_DIR = Path(__file__).resolve().parent.parent

V15_STRICT_ENVIRONMENT_FIELDS = [
    "python_major_minor",
    "pytorch_version",
    "torch_cuda_runtime",
    "device_type",
    "device_name",
    "device_compute_capability",
    "nvidia_driver_version",
    "cublas_workspace_config",
    "deterministic_algorithms_enabled",
    "cudnn_deterministic",
    "cudnn_benchmark",
    "automatic_cpu_fallback"
]

V15_DESCRIPTIVE_ENVIRONMENT_FIELDS = [
    "gpu_uuid_descriptive",
    "hostname",
    "session_id",
    "pci_bus_id",
    "platform",
    "kernel",
    "total_vram_bytes"
]

def compute_sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    """Computes SHA-256 hash using streaming chunks to prevent high memory usage."""
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

    # 1. GPU Discovery and CUDA Hardware Fail-Closed Verification
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

    # 2. Software Runtime Checks (Strict Target Framework: PyTorch 2.6.0 + CUDA 12.4)
    py_ver = platform.python_version()
    py_maj_min = f"{sys.version_info.major}.{sys.version_info.minor}"
    torch_ver = torch.__version__
    cuda_ver = torch.version.cuda

    print(f"[BOOTSTRAP 2] Python: {py_ver} (major.minor: {py_maj_min}) | PyTorch: {torch_ver} | CUDA Runtime: {cuda_ver}")

    # Fail-closed checks on framework
    if not torch_ver.startswith("2.6.0"):
        raise RuntimeError(f"FATAL: PyTorch version mismatch! Expected PyTorch 2.6.0 series, got {torch_ver}")
    if cuda_ver != "12.4":
        raise RuntimeError(f"FATAL: CUDA runtime mismatch! Expected CUDA 12.4, got {cuda_ver}")

    # 3. Machine-Collect Determinism State
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    det_algo_enabled = torch.are_deterministic_algorithms_enabled()
    cudnn_det = bool(torch.backends.cudnn.deterministic)
    cudnn_bench = bool(torch.backends.cudnn.benchmark)
    cublas_cfg = os.environ.get("CUBLAS_WORKSPACE_CONFIG", "")

    print(f"[BOOTSTRAP 3] Deterministic Algorithms: {det_algo_enabled} | cuDNN Deterministic: {cudnn_det} | cuDNN Benchmark: {cudnn_bench} | CUBLAS: {cublas_cfg}")

    if not det_algo_enabled or not cudnn_det or cudnn_bench or cublas_cfg != ":4096:8":
        raise RuntimeError(
            f"FATAL: Determinism state failed verification! (det_algo={det_algo_enabled}, "
            f"cudnn_det={cudnn_det}, cudnn_bench={cudnn_bench}, cublas_cfg={cublas_cfg})"
        )

    # 4. Repository Commit Verification
    commit_sha = get_git_commit_sha(repo_dir)
    print(f"[BOOTSTRAP 4] Repository HEAD: {commit_sha}")

    # 5. HDFS Source Streaming Verification and Local Copy
    if drive_data_source.exists():
        print(f"[BOOTSTRAP 5] Streaming SHA-256 verification of Drive source: {drive_data_source}...")
        t_hash_0 = time.time()
        src_sha = compute_sha256(drive_data_source)
        hash_dur = time.time() - t_hash_0
        print(f"[BOOTSTRAP 5] Source SHA-256: {src_sha} (computed in {hash_dur:.2f}s)")
        if src_sha != EXPECTED_HDFS_SHA:
            raise ValueError(f"FATAL: Source HDFS SHA-256 mismatch: {src_sha} != {EXPECTED_HDFS_SHA}")

        # Copy to local fast ephemeral disk if different
        if local_data_dest != drive_data_source:
            local_data_dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"[BOOTSTRAP 5] Copying HDFS tarball to fast local storage: {local_data_dest}...")
            t_copy_0 = time.time()
            shutil.copy2(drive_data_source, local_data_dest)
            copy_dur = time.time() - t_copy_0
            print(f"[BOOTSTRAP 5] Copy completed in {copy_dur:.2f}s. Streaming SHA-256 verification of local copy...")
            dst_sha = compute_sha256(local_data_dest)
            if dst_sha != EXPECTED_HDFS_SHA:
                raise ValueError(f"FATAL: Local copy HDFS SHA-256 mismatch: {dst_sha} != {EXPECTED_HDFS_SHA}")
            print(f"[BOOTSTRAP 5] Local copy HDFS SHA-256 MATCH ({dst_sha[:16]}...)")
    elif local_data_dest.exists():
        print(f"[BOOTSTRAP 5] Verifying existing local HDFS tarball at {local_data_dest}...")
        dst_sha = compute_sha256(local_data_dest)
        if dst_sha != EXPECTED_HDFS_SHA:
            raise ValueError(f"FATAL: Local HDFS SHA-256 mismatch: {dst_sha} != {EXPECTED_HDFS_SHA}")
        print(f"[BOOTSTRAP 5] Local HDFS SHA-256 MATCH ({dst_sha[:16]}...)")
    else:
        print(f"[BOOTSTRAP 5] WARNING: HDFS tarball not found at {drive_data_source} or {local_data_dest}. Ensure dataset is downloaded/copied.")

    # 6. Generate Machine-Collected Environment Lock Candidate
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
        "python_executable": sys.executable,
        "python_version": py_ver,
        "python_major_minor": py_maj_min,
        "pytorch_version": torch_ver,
        "torch_cuda_runtime": cuda_ver,
        "nvidia_driver_version": driver_ver,
        "device_type": "cuda",
        "device_name": device_name,
        "device_compute_capability": compute_cap,
        "total_vram_bytes": total_vram_bytes,
        "total_vram_gb": total_vram_gb,
        "gpu_uuid_descriptive": gpu_uuid,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "cublas_workspace_config": cublas_cfg,
        "deterministic_algorithms_enabled": det_algo_enabled,
        "cudnn_deterministic": cudnn_det,
        "cudnn_benchmark": cudnn_bench,
        "automatic_cpu_fallback": False,
        "qualification_status": "PENDING_CUDA_DETERMINISTIC_QUALIFICATION"
    }

    env_lock_p.write_text(json.dumps(env_candidate, indent=2) + "\n", encoding="utf-8")
    print(f"[BOOTSTRAP 6] Wrote Colab Environment Lock Candidate to {env_lock_p}")
    print(f"[BOOTSTRAP 6] Environment Lock Candidate SHA-256: {compute_sha256(env_lock_p)}")

    print("=================================================================")
    print("   COLAB BOOTSTRAP COMPLETE: READY FOR DETERMINISTIC QUALIFICATION")
    print("=================================================================\n")

    return env_candidate

def mirror_qualification_artifacts(
    base_dir: Path,
    durable_root: Path,
    qual_run_id: Optional[str] = None
) -> Path:
    """
    Mirrors all qualification evidence artifacts to durable Google Drive storage
    and verifies source vs destination SHA-256 for each copied file.
    """
    base_dir = Path(base_dir).resolve()
    durable_root = Path(durable_root).resolve()
    
    if qual_run_id is None:
        qual_run_id = f"QUAL-COLAB-{int(time.time())}"
    
    dest_dir = durable_root / "qualification" / qual_run_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_mirror = [
        ("experiments/evidence/stage-a2/preexecution/STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json", "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"),
        ("experiments/evidence/stage-a2/implementation/IMPLEMENTATION-QUALIFICATION.json", "IMPLEMENTATION-QUALIFICATION.json"),
        ("experiments/evidence/stage-a2/implementation/DETERMINISTIC-RESUME-EVIDENCE.json", "DETERMINISTIC-RESUME-EVIDENCE.json"),
        ("experiments/evidence/stage-a2/implementation/ENVIRONMENT.json", "QUALIFICATION-ENVIRONMENT.json"),
        ("experiments/evidence/stage-a2/implementation/EXPERIMENTAL-SOURCE.json", "EXPERIMENTAL-SOURCE.json"),
        ("experiments/evidence/stage-a2/implementation/deterministic_resume.log", "deterministic_resume.log"),
        ("experiments/evidence/stage-a2/implementation/qualification_checkpoint.pt", "qualification_checkpoint.pt"),
        ("experiments/evidence/stage-a2/implementation/EVIDENCE-MANIFEST.json", "EVIDENCE-MANIFEST.json")
    ]
    
    manifest_entries = []
    print("=================================================================")
    print(f"   DURABLE QUALIFICATION MIRROR TO GOOGLE DRIVE: {dest_dir}      ")
    print("=================================================================")
    
    for rel_src, rel_dst in files_to_mirror:
        src_path = base_dir / rel_src
        if src_path.exists():
            dst_path = dest_dir / rel_dst
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            
            src_sha = compute_sha256(src_path)
            dst_sha = compute_sha256(dst_path)
            assert src_sha == dst_sha, f"Mirror SHA mismatch for {rel_dst}: {dst_sha} != {src_sha}"
            
            manifest_entries.append({
                "logical_name": rel_dst,
                "source_path": str(rel_src),
                "durable_path": str(dst_path),
                "sha256": src_sha,
                "size_bytes": src_path.stat().st_size
            })
            print(f"[MIRROR] {rel_dst}: MATCH ({src_sha[:16]}...) -> {dst_path}")
        else:
            print(f"[MIRROR] Optional/Pending file not found: {rel_src}")
            
    mirror_manifest = {
        "qualification_run_id": qual_run_id,
        "mirrored_at": datetime.now(timezone.utc).isoformat(),
        "destination_directory": str(dest_dir),
        "artifacts_count": len(manifest_entries),
        "artifacts": manifest_entries
    }
    
    manifest_path = dest_dir / "QUALIFICATION-MIRROR-MANIFEST.json"
    manifest_path.write_text(json.dumps(mirror_manifest, indent=2) + "\n", encoding="utf-8")
    manifest_sha = compute_sha256(manifest_path)
    print(f"[MIRROR] Qualification Manifest written: {manifest_path} (SHA: {manifest_sha[:16]}...)")
    print("=================================================================\n")
    return dest_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage A2 Colab Environment Bootstrap")
    parser.add_argument("--repo-dir", type=str, default=None, help="Path to repository root")
    parser.add_argument("--drive-data-source", type=str, default=None, help="Path to raw HDFS on Drive")
    parser.add_argument("--local-data-dest", type=str, default=None, help="Path to copy raw HDFS locally in /content")
    parser.add_argument("--durable-root", type=str, default=None, help="Durable Google Drive root")
    parser.add_argument("--env-lock-output", type=str, default=None, help="Path to write environment lock candidate")
    parser.add_argument("--mirror-qualification", action="store_true", default=False, help="Mirror qualification artifacts to Drive")
    parser.add_argument("--qual-run-id", type=str, default=None, help="Qualification run identifier")
    args = parser.parse_args()

    repo_p = Path(args.repo_dir) if args.repo_dir else DEFAULT_BASE_DIR
    durable_p = Path(args.durable_root) if args.durable_root else Path("/content/drive/MyDrive/Chuyende-stage-a2")

    if args.mirror_qualification:
        mirror_qualification_artifacts(base_dir=repo_p, durable_root=durable_p, qual_run_id=args.qual_run_id)
    else:
        run_bootstrap(
            repo_dir=repo_p,
            drive_data_source=Path(args.drive_data_source) if args.drive_data_source else None,
            local_data_dest=Path(args.local_data_dest) if args.local_data_dest else None,
            durable_root=durable_p,
            env_lock_output_path=Path(args.env_lock_output) if args.env_lock_output else None
        )
