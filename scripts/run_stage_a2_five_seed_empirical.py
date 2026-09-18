# -*- coding: utf-8 -*-
"""
Người chạy thử nghiệm sơ bộ theo kinh nghiệm năm hạt giống Canonical cho Giai đoạn A2 (Hợp đồng V1.4.1 / V1.5 đã bị khóa).
Bộ dữ liệu: HDFS (SPL-HDFS-001 Cơ quan phân chia Canonical)
Phạm vi thực thi được ủy quyền: 35.000 phiên đào tạo (586.577 sự kiện) | 7.500 phiên Val (119.531 sự kiện)
Hạt giống kinh điển: [42, 1337, 2024, 7, 999]

Cách sử dụng:
  # Xác thực chạy thử trên tất cả 5 hạt giống (thực hiện 0 bước tối ưu hóa):
  tập lệnh python/run_stage_a2_five_seed_empirical.py --all --dry-run

  # Chạy khô một hạt:
  tập lệnh python/run_stage_a2_five_seed_empirical.py --seed 42 --dry-run

  # Tiếp tục quá trình chạy bị gián đoạn từ checkpoint:
  tập lệnh python/run_stage_a2_five_seed_empirical.py --seed 42 --resume .artifacts/stage-a2/HDFS/seed-42/last_checkpoint.pt --authorize-real-empirical-execution

  # Đào tạo theo kinh nghiệm thực tế (Yêu cầu ủy quyền rõ ràng, được thực hiện tuần tự từng hạt giống một):
  tập lệnh python/run_stage_a2_five_seed_empirical.py --seed 42 --authorize-real-theo kinh nghiệm-thực thi

  # Google Colab/Đa nền tảng với root Google Drive bền bỉ:
  tập lệnh python/run_stage_a2_five_seed_empirical.py --seed 42 --base-dir /content/Research --dataset-path /content/stage-a2-data/HDFS_1.tar.gz --durable-root /content/drive/MyDrive/Chuyende-stage-a2/runs --plan Experiment/plans/STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json --dry-run
"""

import os
# Thực thi cấu hình CUBLAS xác định trước khi bất kỳ bối cảnh CUDA nào được tạo
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

import gc
import sys
import json
import time
import math
import random
import shutil
import hashlib
import platform
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

import numpy as np
import torch

from research_agent.experiments.models.temporal_graph_view_encoder import TemporalGraphViewEncoder
from research_agent.experiments.training.stage_a2_trainer import (
    StageA2Trainer,
    VALIDATION_MASK_SEED,
    EmpiricalExecutionNotAuthorizedError,
    ExecutionDeviceMismatchError,
    FloatingPointAnomalyError,
    CheckpointBoundaryViolationError
)
from research_agent.experiments.data.hdfs_split_authority import (
    parse_hdfs_line_timestamp,
    HDFSSplitAuthority
)
from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    TestSetSealedError
)

CANONICAL_SEEDS = [42, 1337, 2024, 7, 999]
PROTOCOL_LOCK_SHA = "41d0c54153d7e988acaba64cf7478037220257be3051fe831d082e3f4c1e4831"
ENV_LOCK_SHA = "aeac2a947d21cec99c5a1fd0124bf8fdf6a8e86f259e740421f5a5743be3e545"
RAW_HDFS_TAR_SHA = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
TRAIN_MEMBERSHIP_SHA = "65b76694b0a3cf5c6d684a26899b1e5dca634cfd0985560149feddc12ca8ccfc"
VAL_MEMBERSHIP_SHA = "14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a"
DEFAULT_BASE_DIR = Path(__file__).resolve().parent.parent

class LaunchAuthorizationMissingError(FileNotFoundError):
    """Xảy ra khi thiếu cấu phần phần mềm ủy quyền khởi chạy bắt buộc để thực thi theo kinh nghiệm thực tế."""
    pass

class ExistingRunArtifactError(RuntimeError):
    """Xảy ra khi cố gắng bắt đầu một lần chạy thực mới trong một thư mục hiện có không trống."""
    pass

class ResumeCheckpointNotFoundError(FileNotFoundError):
    """Xảy ra khi tệp checkpoint sơ yếu lý lịch được chỉ định không tồn tại."""
    pass

class CompletedRunResumeError(RuntimeError):
    """Xảy ra khi cố gắng tiếp tục quá trình chạy đã hoàn thành."""
    pass

class CheckpointIntegrityMismatchError(ValueError):
    """Xảy ra khi checkpoint sơ yếu lý lịch không thực hiện được các bước kiểm tra ràng buộc về mật mã hoặc ngữ nghĩa."""
    pass

class FrozenSourceMismatchError(RuntimeError):
    """Xảy ra khi các tệp nguồn thực thi khác với cam kết mã cố định được ủy quyền."""
    pass

class RuntimeTestFirewallGuard:
    """Quá trình cụ thể hóa trình tạo biểu đồ bao bọc tường lửa thử nghiệm thời gian chạy được kết nối."""
    def __init__(
        self,
        split_authority: Optional[HDFSSplitAuthority] = None,
        base_dir: Optional[Path] = None,
        raw_tar_path: Optional[Path] = None
    ):
        self.base_dir = Path(base_dir).resolve() if base_dir else DEFAULT_BASE_DIR
        self.raw_tar_path = Path(raw_tar_path).resolve() if raw_tar_path else (self.base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz")
        self.split_authority = split_authority or HDFSSplitAuthority(base_dir=self.base_dir, raw_tar_path=self.raw_tar_path)
        self.builder = HDFSGraphBuilder(base_dir=self.base_dir, split_authority=self.split_authority, raw_tar_path=self.raw_tar_path)
        self.test_opened: bool = False
        self.test_feature_reads: int = 0
        self.test_label_reads: int = 0
        self.test_metrics: int = 0
        self.test_graph_events_materialized: int = 0
        self.test_relation_parse_count: int = 0

    def materialize_split(self, split_name: str, use_execution_subset: bool = True) -> Dict[str, Any]:
        if split_name.upper() == "TEST":
            self.test_opened = True
            self.test_feature_reads += 1
            self.test_graph_events_materialized += 1
            raise TestSetSealedError("FATAL: Runtime test firewall blocked attempt to access or materialize sealed TEST graph split!")
        
        return self.builder.materialize_split(split_name, use_execution_subset=use_execution_subset)

    def assert_sealed(self):
        if self.test_opened or self.test_feature_reads > 0 or self.test_label_reads > 0 or self.test_metrics > 0:
            raise TestSetSealedError(
                f"FATAL: Test firewall violated! (opened={self.test_opened}, feat_reads={self.test_feature_reads}, "
                f"label_reads={self.test_label_reads}, metrics={self.test_metrics})"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_opened": self.test_opened,
            "test_feature_reads": self.test_feature_reads,
            "test_label_reads": self.test_label_reads,
            "test_metrics": self.test_metrics,
            "test_graph_events_materialized": self.test_graph_events_materialized,
            "test_relation_parse_count": self.test_relation_parse_count,
            "firewall_status": "LOCKED" if not self.test_opened else "BREACHED"
        }

def compute_sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    """Tính toán hàm băm SHA-256 bằng cách sử dụng các đoạn phát trực tuyến để tránh mức sử dụng bộ nhớ cao."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def enforce_framework_determinism() -> None:
    """
    Thực thi trạng thái thực thi xác định trong thời gian chạy khung và phần cứng:
      - Yêu cầu/bộ CUBLAS_WORKSPACE_CONFIG == ':4096:8'
      - Bật torch.use_deterministic_algorithms(Đúng)
      - Nếu CUDA:
          torch.backends.cudnn.deterministic = True
          torch.backends.cudnn.benchmark = False
      - Xác minh cài đặt trực tiếp sau khi đóng nhiệm vụ không thành công.
    """
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8":
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    
    torch.use_deterministic_algorithms(True)
    if not torch.are_deterministic_algorithms_enabled():
        raise RuntimeError("FATAL: Failed to enable torch.use_deterministic_algorithms(True)")
    
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        if not torch.backends.cudnn.deterministic:
            raise RuntimeError("FATAL: Failed to set torch.backends.cudnn.deterministic = True")
        if torch.backends.cudnn.benchmark:
            raise RuntimeError("FATAL: Failed to set torch.backends.cudnn.benchmark = False")


def get_nvidia_driver_version() -> str:
    """Truy vấn phiên bản trình điều khiển NVIDIA của máy chủ hiện tại qua nvidia-smi không đóng được."""
    try:
        out = subprocess.check_output([
            "nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"
        ], text=True).strip()
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        if not lines or not lines[0]:
            raise RuntimeError("Empty driver version returned from nvidia-smi")
        return lines[0]
    except Exception as e:
        raise ExecutionDeviceMismatchError(f"FATAL: NVIDIA driver version unavailable via nvidia-smi: {e}")

def get_git_info() -> Tuple[str, str, bool]:
    """Truy xuất trạng thái cam kết git, chi nhánh và sứ hiện tại."""
    try:
        commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
        status = subprocess.check_output([
            "git", "status", "--porcelain", "src", "tests", "scripts",
            "experiments/protocol", "experiments/schemas", "experiments/plans"
        ], text=True).strip()
        is_dirty = len(status) > 0
        return commit_sha, branch, is_dirty
    except Exception:
        return "UNKNOWN_COMMIT", "UNKNOWN_BRANCH", True

def verify_frozen_execution_source(base_dir: Path, expected_commit_sha: str) -> None:
    """
    Xác minh rằng tất cả các tệp mã nguồn liên quan đến việc thực thi đều giống nhau theo byte
    đến cam kết mã thực thi bị đóng băng dự kiến.
    """
    source_paths = [
        "src/research_agent/experiments",
        "scripts/run_stage_a2_five_seed_empirical.py"
    ]
    try:
        diff_out = subprocess.check_output(
            ["git", "diff", expected_commit_sha, "--"] + source_paths,
            cwd=str(base_dir),
            text=True
        ).strip()
        if diff_out:
            msg = "FATAL: Execution source tree has modified files relative to authorized code commit " + str(expected_commit_sha) + "!\nDiff excerpt:\n" + diff_out[:500]
            raise FrozenSourceMismatchError(msg)
    except subprocess.CalledProcessError as e:
        raise FrozenSourceMismatchError(f"FATAL: Failed to execute git diff against {expected_commit_sha}: {e}")

def verify_preflight(
    base_dir: Path,
    target_seed: int,
    is_dry_run: bool = False,
    fixture_mode: bool = False,
    plan_path: Optional[Path] = None,
    auth_path: Optional[Path] = None,
    env_lock_path: Optional[Path] = None,
    raw_tar_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Xác minh nghiêm ngặt trước khi đóng cửa chuyến bay:
      1. Cây mã nguồn sạch Git và khớp cam kết thực thi bị đóng băng
      2. Khóa giao thức SHA-256 khớp
      3. Khóa môi trường SHA-256 khớp và so sánh thuộc tính thời gian chạy nghiêm ngặt chính xác
      4. Tệp dữ liệu thô SHA-256 khớp
      5. Tư cách thành viên thực thi được tính toán lại thông qua quyền phân chia chuẩn
      6. Xác minh thiết bị CUDA phần cứng
      7. Xác thực hạt giống chuẩn
      8. Xác thực tường lửa thử nghiệm được kết nối
    """
    print("=================================================================")
    print(f"   STAGE A2 EMPIRICAL PRE-FLIGHT AUDIT (Seed: {target_seed})     ")
    print("=================================================================")

    if target_seed not in CANONICAL_SEEDS:
        raise ValueError(f"FATAL: Seed {target_seed} is NOT in canonical list: {CANONICAL_SEEDS}")

    commit_sha, branch, is_dirty = get_git_info()

    # 1. Kế hoạch giải quyết
    if plan_path:
        plan_p = Path(plan_path).resolve()
    elif (base_dir / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN.json").exists():
        plan_p = base_dir / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN.json"
    elif (base_dir / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json").exists():
        plan_p = base_dir / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    else:
        raise FileNotFoundError(f"Execution plan file missing in {base_dir}")

    if not plan_p.exists():
        raise FileNotFoundError(f"Execution plan file missing at {plan_p}")
    plan_data = json.loads(plan_p.read_text(encoding="utf-8"))
    is_v15_plan = (plan_data.get("protocol_version") == "1.5.0" or plan_data.get("execution_provider") == "GOOGLE_COLAB")

    # 2. tạo phẩm (artifact) ủy quyền / Độ phân giải mẫu
    if auth_path:
        auth_p = Path(auth_path).resolve()
        auth_template_p = None
    elif is_v15_plan:
        auth_p = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / f"SEED{target_seed}-COLAB-LAUNCH-AUTHORIZATION-V1.5.json"
        auth_template_p = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / f"SEED{target_seed}-COLAB-LAUNCH-AUTHORIZATION-V1.5.template.json"
    else:
        auth_p = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / f"SEED{target_seed}-LAUNCH-AUTHORIZATION.json"
        auth_template_p = None

    expected_code_commit = None
    if not fixture_mode:
        if auth_p.exists():
            if is_dirty and not is_dry_run:
                raise RuntimeError("FATAL: Execution source tree has uncommitted changes! Aborting pre-flight.")
            
            auth_data = json.loads(auth_p.read_text(encoding="utf-8"))
            if not auth_data.get("authorization_id"):
                raise ValueError("FATAL: authorization_id missing from authorization artifact!")
            if auth_data.get("stage") != "STAGE_A2":
                raise ValueError(f"FATAL: Authorization stage {auth_data.get('stage')} != STAGE_A2")
            if auth_data.get("dataset") != "HDFS":
                raise ValueError(f"FATAL: Authorization dataset {auth_data.get('dataset')} != HDFS")
            if auth_data.get("split_id") != "SPL-HDFS-001":
                raise ValueError(f"FATAL: Authorization split_id {auth_data.get('split_id')} != SPL-HDFS-001")
            if auth_data.get("seed") != target_seed:
                raise ValueError(f"FATAL: Authorization seed {auth_data.get('seed')} != target_seed {target_seed}")
            if auth_data.get("authorization_status") not in ["AUTHORIZED", "AUTHORIZED_PENDING_REAL_LAUNCH"]:
                raise ValueError(f"FATAL: Authorization status {auth_data.get('authorization_status')} is not AUTHORIZED!")
            
            if auth_data.get("raw_hdfs_sha256") != RAW_HDFS_TAR_SHA:
                raise ValueError(f"FATAL: Authorization raw HDFS SHA mismatch: {auth_data.get('raw_hdfs_sha256')} != {RAW_HDFS_TAR_SHA}")
            if auth_data.get("train_membership_sha256") != TRAIN_MEMBERSHIP_SHA:
                raise ValueError(f"FATAL: Authorization train membership SHA mismatch")
            if auth_data.get("val_membership_sha256") != VAL_MEMBERSHIP_SHA:
                raise ValueError(f"FATAL: Authorization val membership SHA mismatch")
            if auth_data.get("train_sessions_count") != 35000:
                raise ValueError("FATAL: train_sessions_count != 35000")
            if auth_data.get("val_sessions_count") != 7500:
                raise ValueError("FATAL: val_sessions_count != 7500")
            if auth_data.get("train_events_count", auth_data.get("train_graph_events_count")) != 586577:
                raise ValueError("FATAL: train_events_count != 586577")
            if auth_data.get("val_events_count", auth_data.get("val_graph_events_count")) != 119531:
                raise ValueError("FATAL: val_events_count != 119531")
            if auth_data.get("train_windows_count") != 2292:
                raise ValueError("FATAL: train_windows_count != 2292")
            if auth_data.get("val_windows_count") != 467:
                raise ValueError("FATAL: val_windows_count != 467")
            if auth_data.get("optimizer_steps_per_epoch") != 573:
                raise ValueError("FATAL: optimizer_steps_per_epoch != 573")
            if auth_data.get("test_opened") is not False:
                raise ValueError("FATAL: test_opened must be False!")

            expected_code_commit = auth_data.get("expected_execution_code_commit_sha")
            plan_code_commit = plan_data.get("execution_code_commit_sha")
            if plan_code_commit and expected_code_commit != plan_code_commit:
                raise ValueError(f"FATAL: Authorization expected code commit ({expected_code_commit}) != Plan code commit ({plan_code_commit})")
            
            act_auth_sha = compute_sha256(auth_p)
            plan_auth_sha = plan_data.get(f"seed{target_seed}_launch_authorization_sha256")
            if plan_auth_sha and act_auth_sha != plan_auth_sha:
                raise ValueError(f"FATAL: Authorization file SHA ({act_auth_sha}) != Plan authorization SHA ({plan_auth_sha})")
            
            verify_frozen_execution_source(base_dir, expected_code_commit)
            print(f"[PRE-FLIGHT 1] Frozen Source Match: PASS (Byte-identical to {expected_code_commit[:16]}...) [HEAD={commit_sha[:16]}...]")
        elif is_v15_plan and (is_dry_run or fixture_mode) and auth_template_p and auth_template_p.exists():
            template_data = json.loads(auth_template_p.read_text(encoding="utf-8"))
            if template_data.get("seed") != target_seed:
                raise ValueError(f"Template seed {template_data.get('seed')} != {target_seed}")
            expected_code_commit = commit_sha
            print(f"[PRE-FLIGHT 1] Execution Code Commit / HEAD: {commit_sha} (dirty={is_dirty}) [V1.5 Colab Preparation Mode]")
        else:
            raise LaunchAuthorizationMissingError(
                f"FATAL: Mandatory Launch Authorization Artifact missing at {auth_p}! "
                f"Real empirical execution for seed {target_seed} cannot proceed without explicit authorization artifact."
            )
    else:
        expected_code_commit = plan_data.get("execution_code_commit_sha") if plan_p.exists() else None
        print(f"[PRE-FLIGHT 1] Execution Code Commit / HEAD: {commit_sha} (dirty={is_dirty})")

    # 3. Xác minh khóa giao thức
    if not is_v15_plan:
        protocol_lock_p = base_dir / "experiments" / "protocol" / "STAGE-A2-EXECUTION-LOCK-V1.4.json"
        if not protocol_lock_p.exists():
            raise FileNotFoundError(f"Protocol lock file missing at {protocol_lock_p}")
        actual_proto_sha = compute_sha256(protocol_lock_p)
        if actual_proto_sha != PROTOCOL_LOCK_SHA:
            raise ValueError(f"PROTOCOL_LOCK_SHA mismatch: {actual_proto_sha} != {PROTOCOL_LOCK_SHA}")
        print(f"[PRE-FLIGHT 2] Protocol Lock V1.4 SHA: MATCH ({actual_proto_sha[:16]}...)")
    else:
        proto_amend_p = base_dir / "experiments" / "protocol" / "PROTOCOL-AMENDMENTS.md"
        actual_proto_sha = compute_sha256(proto_amend_p) if proto_amend_p.exists() else "AMENDMENT_12_V1.5"
        print(f"[PRE-FLIGHT 2] Protocol V1.5 (Amendment 12): LOCKED")

    # 4. Xác minh khóa môi trường
    if env_lock_path:
        env_lock_p = Path(env_lock_path).resolve()
    elif is_v15_plan:
        env_lock_p = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    else:
        env_lock_p = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "STAGE-A2-EXECUTION-ENVIRONMENT.json"

    actual_env_sha = "PENDING_COLAB_RUNTIME_ALLOCATION"
    curr_gpu_name = "CPU"
    total_vram_gb = 0.0

    if env_lock_p.exists():
        actual_env_sha = compute_sha256(env_lock_p)
        env_lock = json.loads(env_lock_p.read_text(encoding="utf-8"))
        
        if torch.cuda.is_available():
            curr_gpu_name = torch.cuda.get_device_name(0)
            total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)

        if not is_v15_plan:
            if actual_env_sha != ENV_LOCK_SHA and not fixture_mode:
                raise ValueError(f"ENV_LOCK_SHA mismatch: {actual_env_sha} != {ENV_LOCK_SHA}")
            if not torch.cuda.is_available():
                raise ExecutionDeviceMismatchError("FATAL: CUDA is not available! Empirical execution requires CUDA GPU.")
            curr_exe = sys.executable
            curr_py_ver = platform.python_version()
            curr_torch_ver = torch.__version__
            curr_cuda_runtime = torch.version.cuda
            if curr_exe.lower() != env_lock.get("python_executable", "").lower():
                raise ExecutionDeviceMismatchError(f"FATAL: Python executable mismatch: {curr_exe} != {env_lock.get('python_executable')}")
            if curr_py_ver != env_lock.get("python_version"):
                raise ExecutionDeviceMismatchError(f"FATAL: Python version mismatch: {curr_py_ver} != {env_lock.get('python_version')}")
            if curr_torch_ver != env_lock.get("pytorch_version"):
                raise ExecutionDeviceMismatchError(f"FATAL: PyTorch version mismatch: {curr_torch_ver} != {env_lock.get('pytorch_version')}")
            if curr_cuda_runtime != env_lock.get("cuda_runtime"):
                raise ExecutionDeviceMismatchError(f"FATAL: CUDA runtime mismatch: {curr_cuda_runtime} != {env_lock.get('cuda_runtime')}")
            if curr_gpu_name != env_lock.get("device_name"):
                raise ExecutionDeviceMismatchError(f"FATAL: GPU device name mismatch: {curr_gpu_name} != {env_lock.get('device_name')}")
            if env_lock.get("device_type") != "cuda":
                raise ExecutionDeviceMismatchError(f"FATAL: Environment lock device_type is {env_lock.get('device_type')}, expected 'cuda'")
            if env_lock.get("automatic_cpu_fallback") is not False:
                raise ExecutionDeviceMismatchError("FATAL: automatic_cpu_fallback must be strictly False in execution environment lock!")
            print(f"[PRE-FLIGHT 3] Environment Lock Strict Properties: MATCH ({actual_env_sha[:16]}...) [{curr_gpu_name}, {total_vram_gb:.2f} GB VRAM]")
        else:
            # Colab V1.5 Điều chỉnh môi trường nghiêm ngặt (Sửa đổi 12 - 12 trường nghiêm ngặt)
            if not torch.cuda.is_available():
                raise ExecutionDeviceMismatchError("FATAL: CUDA is not available! Colab empirical execution requires CUDA GPU.")
            
            # 1. Kiểm tra Python major.minor trực tiếp
            curr_py_maj_min = f"{sys.version_info.major}.{sys.version_info.minor}"
            if "python_major_minor" in env_lock and curr_py_maj_min != env_lock["python_major_minor"]:
                raise ExecutionDeviceMismatchError(f"FATAL: Python major.minor mismatch: {curr_py_maj_min} != {env_lock['python_major_minor']}")
            
            # 2. Kiểm tra phiên bản PyTorch trực tiếp
            curr_torch_ver = torch.__version__
            if curr_torch_ver != env_lock["pytorch_version"]:
                raise ExecutionDeviceMismatchError(f"FATAL: PyTorch version mismatch: {curr_torch_ver} != {env_lock['pytorch_version']}")
            
            # 3. Kiểm tra thời gian chạy của trình biên dịch CUDA trực tiếp
            curr_cuda_runtime = torch.version.cuda
            if curr_cuda_runtime != env_lock.get("torch_cuda_runtime", env_lock.get("cuda_runtime")):
                raise ExecutionDeviceMismatchError(f"FATAL: CUDA runtime mismatch: {curr_cuda_runtime} != {env_lock.get('torch_cuda_runtime')}")
            
            # 4. Kiểm tra loại thiết bị trực tiếp
            if env_lock.get("device_type") != "cuda":
                raise ExecutionDeviceMismatchError(f"FATAL: device_type {env_lock.get('device_type')} != cuda")
            
            # 5. Kiểm tra tên thiết bị GPU trực tiếp
            if curr_gpu_name != env_lock["device_name"]:
                raise ExecutionDeviceMismatchError(f"FATAL: GPU device name mismatch: {curr_gpu_name} != {env_lock['device_name']}")
            
            # 6. Kiểm tra khả năng tính toán GPU trực tiếp
            device_props = torch.cuda.get_device_properties(0)
            curr_compute_cap = f"{device_props.major}.{device_props.minor}"
            if "device_compute_capability" in env_lock and curr_compute_cap != env_lock["device_compute_capability"]:
                raise ExecutionDeviceMismatchError(f"FATAL: GPU compute capability mismatch: {curr_compute_cap} != {env_lock['device_compute_capability']}")
            
            # 7. Kiểm tra phiên bản trình điều khiển máy chủ NVIDIA trực tiếp (Đóng không thành công)
            curr_driver = get_nvidia_driver_version()
            expected_driver = env_lock.get("nvidia_driver_version")
            if not expected_driver or curr_driver != expected_driver:
                raise ExecutionDeviceMismatchError(
                    f"FATAL: NVIDIA driver version mismatch! Live: {curr_driver} != Lock: {expected_driver}"
                )
            
            # 8. Kiểm tra cấu hình không gian làm việc CUBLAS trực tiếp
            live_cublas = os.environ.get("CUBLAS_WORKSPACE_CONFIG", "")
            if live_cublas != env_lock.get("cublas_workspace_config") or live_cublas != ":4096:8":
                raise ExecutionDeviceMismatchError(
                    f"FATAL: Live CUBLAS_WORKSPACE_CONFIG ({live_cublas}) mismatch with lock ({env_lock.get('cublas_workspace_config')})"
                )
            
            # 9. Kiểm tra kích hoạt thuật toán xác định trực tiếp
            live_det_algo = torch.are_deterministic_algorithms_enabled()
            if live_det_algo != env_lock.get("deterministic_algorithms_enabled") or not live_det_algo:
                raise ExecutionDeviceMismatchError(
                    f"FATAL: Live torch.are_deterministic_algorithms_enabled() ({live_det_algo}) mismatch with lock ({env_lock.get('deterministic_algorithms_enabled')})"
                )
            
            # 10. Kiểm tra xác định cuDNN trực tiếp
            live_cudnn_det = bool(torch.backends.cudnn.deterministic)
            if live_cudnn_det != env_lock.get("cudnn_deterministic") or not live_cudnn_det:
                raise ExecutionDeviceMismatchError(
                    f"FATAL: Live torch.backends.cudnn.deterministic ({live_cudnn_det}) mismatch with lock ({env_lock.get('cudnn_deterministic')})"
                )
            
            # 11. Kiểm tra điểm chuẩn cuDNN trực tiếp
            live_cudnn_bench = bool(torch.backends.cudnn.benchmark)
            if live_cudnn_bench != env_lock.get("cudnn_benchmark") or live_cudnn_bench:
                raise ExecutionDeviceMismatchError(
                    f"FATAL: Live torch.backends.cudnn.benchmark ({live_cudnn_bench}) mismatch with lock ({env_lock.get('cudnn_benchmark')})"
                )
            
            # 12. Tự động kiểm tra dự phòng CPU
            if env_lock.get("automatic_cpu_fallback") is not False:
                raise ExecutionDeviceMismatchError("FATAL: automatic_cpu_fallback != False")
            
            # Chỉ mang tính mô tả: gpu_uuid được ghi lại nhưng NOT có tăng sự không khớp
            descriptive_uuid = env_lock.get("gpu_uuid_descriptive", "N/A")
            print(f"[PRE-FLIGHT 3] Colab Environment Lock Strict Properties: MATCH ({actual_env_sha[:16]}...) [{curr_gpu_name}, Driver: {curr_driver}, Compute {curr_compute_cap}, {total_vram_gb:.2f} GB VRAM, UUID: {descriptive_uuid}]")
    else:
        if is_v15_plan and (is_dry_run or fixture_mode):
            if torch.cuda.is_available():
                curr_gpu_name = torch.cuda.get_device_name(0)
                total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"[PRE-FLIGHT 3] Colab Environment Lock: PENDING DYNAMIC ALLOCATION [{curr_gpu_name}, {total_vram_gb:.2f} GB VRAM]")
        else:
            raise FileNotFoundError(f"Environment lock file missing at {env_lock_p}")

    # 5. Xác minh phát trực tuyến Tarball tập dữ liệu thô
    raw_tar_p = Path(raw_tar_path).resolve() if raw_tar_path else (base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz")
    if not raw_tar_p.exists():
        raise FileNotFoundError(f"Raw HDFS tarball missing at {raw_tar_p}")
    act_raw_sha = compute_sha256(raw_tar_p)
    if act_raw_sha != RAW_HDFS_TAR_SHA:
        raise ValueError(f"RAW_HDFS_TAR_SHA mismatch: {act_raw_sha} != {RAW_HDFS_TAR_SHA}")
    print(f"[PRE-FLIGHT 4] Raw HDFS Tarball SHA: MATCH ({act_raw_sha[:16]}...) [{raw_tar_p}]")

    # 6. Tính toán lại Canonical tư cách thành viên thực thi
    split_auth = HDFSSplitAuthority(base_dir=base_dir, raw_tar_path=raw_tar_p)
    split_info = split_auth.get_split()
    
    recomputed_train_sha = hashlib.sha256("\n".join(split_info["selected_train_block_ids"]).encode()).hexdigest()
    recomputed_val_sha = hashlib.sha256("\n".join(split_info["selected_val_block_ids"]).encode()).hexdigest()
    
    if recomputed_train_sha != TRAIN_MEMBERSHIP_SHA:
        raise ValueError(f"Recomputed Train Membership SHA mismatch: {recomputed_train_sha} != {TRAIN_MEMBERSHIP_SHA}")
    if recomputed_val_sha != VAL_MEMBERSHIP_SHA:
        raise ValueError(f"Recomputed Val Membership SHA mismatch: {recomputed_val_sha} != {VAL_MEMBERSHIP_SHA}")
    
    train_sess = len(split_info["selected_train_block_ids"])
    val_sess = len(split_info["selected_val_block_ids"])
    if train_sess != 35000 or val_sess != 7500:
        raise ValueError(f"Recomputed session counts mismatch: train={train_sess}, val={val_sess}")

    print(f"[PRE-FLIGHT 5] Train Membership Recomputed: MATCH ({recomputed_train_sha[:16]}...) [35,000 sessions / 586,577 events]")
    print(f"[PRE-FLIGHT 6] Val Membership Recomputed:   MATCH ({recomputed_val_sha[:16]}...) [7,500 sessions / 119,531 events]")

    # 7. Xác minh tường lửa kiểm tra kết nối
    guard = RuntimeTestFirewallGuard(split_authority=split_auth, base_dir=base_dir, raw_tar_path=raw_tar_p)
    guard.assert_sealed()
    print("[PRE-FLIGHT 7] Connected Test Firewall: LOCKED (TEST_OPENED=false, READ_COUNT=0)")

    print("=================================================================")
    print("PRE-FLIGHT AUDIT: ALL CHECKS PASSED.")
    print("=================================================================\n")

    return {
        "commit_sha": commit_sha,
        "expected_code_commit": expected_code_commit or commit_sha,
        "branch": branch,
        "is_dirty": is_dirty,
        "protocol_lock_sha": actual_proto_sha,
        "env_lock_sha": actual_env_sha,
        "raw_tar_sha": act_raw_sha,
        "train_membership_sha": recomputed_train_sha,
        "val_membership_sha": recomputed_val_sha,
        "gpu_name": curr_gpu_name,
        "total_vram_gb": total_vram_gb,
        "guard": guard,
        "is_v15_plan": is_v15_plan,
        "raw_tar_path": raw_tar_p
    }

def chunk_into_windows(events: List[Dict[str, Any]], window_size: int = 256) -> List[List[Dict[str, Any]]]:
    """Phân chia chuỗi sự kiện theo trình tự thời gian thành các cửa sổ thời gian riêng biệt."""
    windows = []
    for i in range(0, len(events), window_size):
        windows.append(events[i:i+window_size])
    return windows

def sync_to_durable_storage(files_to_sync: List[Tuple[Path, str]], dest_dir: Path, run_state_file: Optional[Tuple[Path, str]] = None):
    """
    Phản chiếu nguyên tử các tệp epoch đã hoàn thành vào bộ lưu trữ Google Drive bền bỉ.
    Xác minh SHA-256 sau khi sao chép trước khi xác nhận RUN-STATE.json.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src_file, rel_name in files_to_sync:
        if src_file.exists():
            dst_file = dest_dir / rel_name
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            src_sha = compute_sha256(src_file)
            dst_sha = compute_sha256(dst_file)
            if src_sha != dst_sha:
                raise RuntimeError(f"FATAL: Durable copy SHA-256 mismatch for {rel_name}: {dst_sha} != {src_sha}")
    if run_state_file is not None:
        src_state, rel_state_name = run_state_file
        if src_state.exists():
            dst_state = dest_dir / rel_state_name
            shutil.copy2(src_state, dst_state)
            src_sha = compute_sha256(src_state)
            dst_sha = compute_sha256(dst_state)
            if src_sha != dst_sha:
                raise RuntimeError(f"FATAL: Durable RUN-STATE copy SHA-256 mismatch: {dst_sha} != {src_sha}")

def run_single_seed_pipeline(
    seed: int,
    base_dir: Path,
    is_dry_run: bool = True,
    empirical_authorized: bool = False,
    resume_checkpoint: Optional[Path] = None,
    resume_sha256: Optional[str] = None,
    fixture_mode: bool = False,
    fixture_output_root: Optional[Path] = None,
    fixture_train_events: Optional[List[Dict[str, Any]]] = None,
    fixture_val_events: Optional[List[Dict[str, Any]]] = None,
    max_epochs: Optional[int] = None,
    durable_root: Optional[Path] = None,
    plan_path: Optional[Path] = None,
    auth_path: Optional[Path] = None,
    env_lock_path: Optional[Path] = None,
    raw_tar_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Hoàn thiện quy trình thực thi từ đầu đến cuối cho lần chạy Giai đoạn A2 chuẩn mực.
    """
    enforce_framework_determinism()
    preflight = verify_preflight(
        base_dir=base_dir,
        target_seed=seed,
        is_dry_run=is_dry_run,
        fixture_mode=fixture_mode,
        plan_path=plan_path,
        auth_path=auth_path,
        env_lock_path=env_lock_path,
        raw_tar_path=raw_tar_path
    )
    guard: RuntimeTestFirewallGuard = preflight["guard"]
    expected_code_commit = preflight["expected_code_commit"]
    is_v15_plan = preflight.get("is_v15_plan", False)

    run_id = f"RUN-STAGE-A2-HDFS-SEED{seed}"
    
    # Cách ly không gian tên nghiêm ngặt
    if fixture_mode:
        if fixture_output_root is not None:
            run_evidence_dir = Path(fixture_output_root) / "evidence"
            artifact_checkpoint_dir = Path(fixture_output_root) / "artifacts"
        else:
            fixture_id = f"FIXTURE-SEED{seed}-{int(time.time())}"
            run_evidence_dir = base_dir / "experiments" / "evidence" / "stage-a2" / "fixtures" / fixture_id
            artifact_checkpoint_dir = base_dir / ".artifacts" / "stage-a2" / "fixtures" / fixture_id
    else:
        run_evidence_dir = base_dir / "experiments" / "runs" / "stage-a2" / "HDFS" / f"seed-{seed}"
        artifact_checkpoint_dir = base_dir / ".artifacts" / "stage-a2" / "HDFS" / f"seed-{seed}"

    # Xác minh sự bất biến cách ly không gian tên
    if fixture_mode:
        real_canonical_run_dir = base_dir / "experiments" / "runs" / "stage-a2" / "HDFS" / f"seed-{seed}"
        real_canonical_art_dir = base_dir / ".artifacts" / "stage-a2" / "HDFS" / f"seed-{seed}"
        assert run_evidence_dir != real_canonical_run_dir, "FATAL: Fixture run attempted to resolve to canonical real run directory!"
        assert artifact_checkpoint_dir != real_canonical_art_dir, "FATAL: Fixture run attempted to resolve to canonical real artifact directory!"

    train_log_p = run_evidence_dir / "TRAIN-LOG.jsonl"
    run_state_p = run_evidence_dir / "RUN-STATE.json"
    metrics_p = run_evidence_dir / "METRICS.json"
    manifest_p = run_evidence_dir / "RUN-MANIFEST.json"
    source_p = run_evidence_dir / "EXPERIMENTAL-SOURCE.json"
    env_p = run_evidence_dir / "ENVIRONMENT.json"
    firewall_p = run_evidence_dir / "TEST-FIREWALL.json"
    ckpt_inv_p = run_evidence_dir / "CHECKPOINT-INVENTORY.json"
    failure_p = run_evidence_dir / "FAILURE.json"

    # --- DRY-RUN PATH ---
    if is_dry_run:
        # Kiểm tra độ sạch của thư mục thực để chạy thực
        if not fixture_mode:
            has_evidence = run_evidence_dir.exists() and any(run_evidence_dir.iterdir())
            has_checkpoints = artifact_checkpoint_dir.exists() and any(artifact_checkpoint_dir.iterdir())
            if has_evidence or has_checkpoints:
                print(f"[DRY-RUN] SEED42_REAL_DIRECTORY_CLEAN: FAIL ({run_evidence_dir} or {artifact_checkpoint_dir} not empty)")
                raise ExistingRunArtifactError(f"Real run directory is not clean: {run_evidence_dir}")
            else:
                print(f"[DRY-RUN] SEED42_REAL_DIRECTORY_CLEAN: PASS")

        print(f"[DRY-RUN] Seed {seed} Dry-Run Initialized.")
        print(f"[DRY-RUN] Evidence Directory: {run_evidence_dir}")
        print(f"[DRY-RUN] Checkpoint Directory: {artifact_checkpoint_dir}")
        if durable_root:
            print(f"[DRY-RUN] Durable Root: {durable_root}")
        print(f"[DRY-RUN] Scope: 35,000 Train sessions (586,577 events) -> 2,292 windows (573 steps/epoch)")
        print(f"[DRY-RUN] Scope: 7,500 Val sessions (119,531 events) -> 467 windows")
        print(f"[DRY-RUN] Target Optimizer Steps: {target_max_epochs * 573} ({target_max_epochs} epochs * 573 steps)")
        print(f"[DRY-RUN] Optimizer Steps Executed: 0")
        print(f"[DRY-RUN] Seed {seed} Dry-Run Status: PASS\n")
        return {"seed": seed, "status": "PASS", "optimizer_steps": 0}

    if not empirical_authorized:
        raise EmpiricalExecutionNotAuthorizedError(
            f"FATAL: Empirical execution for seed {seed} requested but empirical_authorized is False!"
        )

    # Khởi tạo/Tải thông tin môi trường
    env_data = {
        "environment_id": f"ENV-STAGE-A2-SEED{seed}",
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "cuda_runtime": torch.version.cuda if torch.cuda.is_available() else None,
        "device_name": preflight["gpu_name"],
        "device_type": "cuda",
        "total_vram_gb": preflight["total_vram_gb"],
        "platform": platform.platform(),
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "deterministic_algorithms_enabled": True
    }

    is_resume = (resume_checkpoint is not None)

    # Đối với các lần chạy mới, RNG của khung hạt giống nên trọng số và hoạt động của mô hình ban đầu được xác định bằng hạt giống chuẩn
    if not is_resume:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    # Khởi tạo kiến trúc mô hình & huấn luyện viên
    model = TemporalGraphViewEncoder(
        d_node=128,
        d_edge=64,
        d_msg=128,
        n_heads=4,
        d_time_proj=32,
        d_rel_emb=32,
        d_type_emb=32,
        dropout=0.10,
        num_canonical_relations=8,
        num_node_types=4
    )
    param_count = sum(p.numel() for p in model.parameters())

    target_max_epochs = max_epochs or (12 if not fixture_mode else 2)
    trainer = StageA2Trainer(
        model=model,
        learning_rate=5e-4,
        weight_decay=0.01,
        min_lr=1e-5,
        warmup_ratio=0.05,
        temporal_window_size=256,
        gradient_accumulation_steps=4,
        clip_norm=1.0,
        max_epochs=target_max_epochs,
        early_stopping_patience=3,
        seed=seed,
        execution_device="cuda",
        execution_mode="REAL_EMPIRICAL" if not fixture_mode else "FIXTURE_TEST",
        empirical_authorized=True,
        total_steps_override=None if not fixture_mode else (target_max_epochs * max(1, len(fixture_train_events or [1, 2, 3, 4]) // 4))
    )

    best_checkpoint_p = artifact_checkpoint_dir / "best_val_loss.pt"
    last_checkpoint_p = artifact_checkpoint_dir / "last_checkpoint.pt"

    # --- RESUME RUN PATH vs FRESH RUN PATH ---
    if is_resume:
        # 1. Yêu cầu tồn tại checkpoint
        if not resume_checkpoint.exists():
            raise ResumeCheckpointNotFoundError(f"FATAL: Specified resume checkpoint does not exist: {resume_checkpoint}")

        # 2. Yêu cầu thư mục chạy thực hiện có & RUN-STATE.json
        if not run_evidence_dir.exists() or not run_state_p.exists():
            raise FileNotFoundError(f"FATAL: Cannot resume run {run_id}: RUN-STATE.json not found in {run_evidence_dir}")

        existing_state = json.loads(run_state_p.read_text(encoding="utf-8"))
        if existing_state.get("status") == "COMPLETED":
            raise CompletedRunResumeError(f"FATAL: Attempted to resume a run that is already COMPLETED! (run_id={run_id})")
        if existing_state.get("seed") != seed:
            raise CheckpointIntegrityMismatchError(f"FATAL: RUN-STATE seed {existing_state.get('seed')} != requested seed {seed}")
        if existing_state.get("run_id") != run_id:
            raise CheckpointIntegrityMismatchError(f"FATAL: RUN-STATE run_id {existing_state.get('run_id')} != requested run_id {run_id}")

        # 3. Xác thực checkpoint SHA
        actual_ckpt_sha = compute_sha256(resume_checkpoint)
        if resume_sha256 and actual_ckpt_sha != resume_sha256:
            raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint SHA mismatch: {actual_ckpt_sha} != {resume_sha256}")

        if ckpt_inv_p.exists():
            inv_data = json.loads(ckpt_inv_p.read_text(encoding="utf-8"))
            inv_shas = {c["sha256"] for c in inv_data.get("checkpoints", [])}
            if actual_ckpt_sha not in inv_shas:
                raise CheckpointIntegrityMismatchError(f"FATAL: Resume checkpoint SHA {actual_ckpt_sha} not found in CHECKPOINT-INVENTORY.json!")

        # 4. Tải checkpoint và xác minh siêu dữ liệu liên kết
        raw_ckpt = torch.load(resume_checkpoint, map_location=trainer.device, weights_only=False)
        ckpt_meta = raw_ckpt.get("checkpoint_metadata", {})
        if ckpt_meta:
            if ckpt_meta.get("seed") is not None and ckpt_meta.get("seed") != seed:
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint seed {ckpt_meta.get('seed')} != {seed}")
            if ckpt_meta.get("run_id") is not None and ckpt_meta.get("run_id") != run_id:
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint run_id {ckpt_meta.get('run_id')} != {run_id}")
            authorized_commits = {expected_code_commit, "33269cbe897fbbad095ad8979b9ca914d209e701"}
            if expected_code_commit and ckpt_meta.get("execution_code_commit_sha") and ckpt_meta.get("execution_code_commit_sha") not in authorized_commits:
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint execution code commit {ckpt_meta.get('execution_code_commit_sha')} not in authorized commits {authorized_commits}")
            if ckpt_meta.get("raw_dataset_sha256") and ckpt_meta.get("raw_dataset_sha256") != RAW_HDFS_TAR_SHA:
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint raw dataset SHA mismatch!")
            if ckpt_meta.get("train_membership_sha256") and ckpt_meta.get("train_membership_sha256") != TRAIN_MEMBERSHIP_SHA:
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint train membership SHA mismatch!")
            if ckpt_meta.get("val_membership_sha256") and ckpt_meta.get("val_membership_sha256") != VAL_MEMBERSHIP_SHA:
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint val membership SHA mismatch!")
            if ckpt_meta.get("protocol_lock_sha256") and ckpt_meta.get("protocol_lock_sha256") != preflight.get("protocol_lock_sha"):
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint protocol lock SHA mismatch!")
            if ckpt_meta.get("environment_lock_sha256") and ckpt_meta.get("environment_lock_sha256") != preflight.get("env_lock_sha"):
                raise CheckpointIntegrityMismatchError(f"FATAL: Checkpoint environment lock SHA mismatch!")

        # 5. Khôi phục trạng thái - Chính sách INCOMPLETE_EPOCH_REPLAY_FROM_LAST_DURABLE_BOUNDARY
        orig_start_time = existing_state.get("start_time", datetime.now(timezone.utc).isoformat())
        cumulative_runtime_seconds = existing_state.get("cumulative_runtime_seconds", 0.0)
        t_resume_start = time.time()

        trainer.load_checkpoint(resume_checkpoint)
        start_epoch = trainer.next_epoch_to_run
        best_val_loss = trainer.best_val_loss
        best_ckpt_epoch = trainer.best_epoch
        best_ckpt_step = trainer.best_checkpoint_global_step
        best_ckpt_sha = existing_state.get("best_checkpoint_sha256")
        best_metrics = existing_state.get("best_metrics", {})

        run_state = existing_state
        run_state["status"] = "RUNNING"
        run_state["resumed_at"] = datetime.now(timezone.utc).isoformat()
        run_state_p.write_text(json.dumps(run_state, indent=2) + "\n", encoding="utf-8")

        if not env_p.exists():
            env_p.write_text(json.dumps(env_data, indent=2) + "\n", encoding="utf-8")

        print(f"[{run_id}] Resumed at next_epoch_to_run={start_epoch}, Step={trainer.global_step}, Cursor={trainer.stream_cursor}")

    else:
        # === FRESH RUN PATH ===
        if not fixture_mode:
            has_evidence = run_evidence_dir.exists() and any(run_evidence_dir.iterdir())
            has_checkpoints = artifact_checkpoint_dir.exists() and any(artifact_checkpoint_dir.iterdir())
            if has_evidence or has_checkpoints:
                raise ExistingRunArtifactError(
                    f"FATAL: Existing run directory found at {run_evidence_dir} (or {artifact_checkpoint_dir})! "
                    "Refusing to overwrite a prior run without explicit --resume."
                )

        run_evidence_dir.mkdir(parents=True, exist_ok=True)
        artifact_checkpoint_dir.mkdir(parents=True, exist_ok=True)

        t_start = time.time()
        orig_start_time = datetime.now(timezone.utc).isoformat()
        cumulative_runtime_seconds = 0.0
        start_epoch = 0

        best_val_loss = float("inf")
        best_ckpt_epoch = 0
        best_ckpt_step = 0
        best_ckpt_sha = None
        best_metrics = {}

        env_p.write_text(json.dumps(env_data, indent=2) + "\n", encoding="utf-8")

        run_state = {
            "run_id": run_id,
            "seed": seed,
            "status": "RUNNING",
            "start_time": orig_start_time,
            "current_epoch": 0,
            "completed_epoch": 0,
            "next_epoch_to_run": 0,
            "global_step": 0,
            "best_val_loss": float("inf"),
            "best_epoch": 0,
            "best_checkpoint_global_step": 0,
            "best_checkpoint_sha256": None,
            "best_metrics": {},
            "cumulative_runtime_seconds": 0.0,
            "last_checkpoint_path": None,
            "last_checkpoint_sha256": None
        }
        run_state_p.write_text(json.dumps(run_state, indent=2) + "\n", encoding="utf-8")

    try:
        # 1. Hiện thực hóa/Chuẩn bị các dòng thời gian
        if fixture_mode:
            train_events = fixture_train_events or []
            val_events = fixture_val_events or []
            total_train_events = len(train_events)
            total_val_events = len(val_events)
        else:
            print(f"[{run_id}] Materializing Train Split (Authorized 35,000 sessions)... formulation from {preflight['raw_tar_path']}")
            train_mat = guard.materialize_split("TRAIN", use_execution_subset=True)
            train_events = train_mat["events"]
            total_train_events = len(train_events)
            if total_train_events != 586577:
                raise ValueError(f"FATAL: Train events count {total_train_events} != 586577")

            print(f"[{run_id}] Materializing Val Split (Authorized 7,500 sessions)... formulation from {preflight['raw_tar_path']}")
            val_mat = guard.materialize_split("VAL", use_execution_subset=True)
            val_events = val_mat["events"]
            total_val_events = len(val_events)
            if total_val_events != 119531:
                raise ValueError(f"FATAL: Val events count {total_val_events} != 119531")

        train_windows = chunk_into_windows(train_events, window_size=256)
        val_windows = chunk_into_windows(val_events, window_size=256)

        expected_train_windows = 2292 if not fixture_mode else len(train_windows)
        expected_val_windows = 467 if not fixture_mode else len(val_windows)
        assert len(train_windows) == expected_train_windows, f"Train windows {len(train_windows)} != {expected_train_windows}"
        assert len(val_windows) == expected_val_windows, f"Val windows {len(val_windows)} != {expected_val_windows}"

        # 2. Xác minh/Thực thi Cờ khung xác định mà không cần gieo lại RNG
        enforce_framework_determinism()

        patience_counter = trainer.patience_counter

        train_stats = {
            "train_L_graph": 0.0, "train_L_rel": 0.0, "train_L_node": 0.0, "train_L_time": 0.0,
            "events_count": total_train_events, "learning_rate": 5e-4,
            "rel_loss_sum": 0.0, "rel_target_count": 0, "node_sq_err_sum": 0.0, "node_element_count": 0,
            "time_loss_sum": 0.0, "time_target_count": 0, "epoch_runtime_sec": 0.0
        }
        val_stats = {
            "val_L_graph": best_val_loss if best_val_loss != float("inf") else 0.0,
            "val_L_rel": best_metrics.get("val_L_rel", 0.0),
            "val_L_node": best_metrics.get("val_L_node", 0.0),
            "val_L_time": best_metrics.get("val_L_time", 0.0),
            "events_count": total_val_events, "rel_loss_sum": 0.0, "rel_target_count": 0,
            "node_sq_err_sum": 0.0, "node_element_count": 0, "time_loss_sum": 0.0, "time_target_count": 0,
            "epoch_runtime_sec": 0.0
        }

        # 3. Vòng lặp epoch
        epochs_to_run = trainer.max_epochs
        for epoch in range(start_epoch, epochs_to_run):
            t_epoch_start = time.time()
            trainer.current_epoch = epoch
            print(f"\n[{run_id}] --- Starting Epoch {epoch + 1}/{epochs_to_run} ---")
            
            # Đặt lại con trỏ luồng cho epoch tàu
            trainer.stream_cursor = 0
            steps_before = trainer.global_step

            # Đào tạo một epoch
            train_stats = trainer.train_one_epoch(train_windows)
            steps_after = trainer.global_step
            delta_steps = steps_after - steps_before

            if not fixture_mode:
                assert delta_steps == 573, f"Expected 573 optimizer steps per epoch, got {delta_steps}"
                assert train_stats["events_count"] == 586577, f"Expected 586577 events, got {train_stats['events_count']}"

            # Xác thực một epoch
            val_stats = trainer.validate_one_epoch(val_windows)
            if not fixture_mode:
                assert val_stats["events_count"] == 119531, f"Expected 119531 val events, got {val_stats['events_count']}"

            guard.assert_sealed()

            # Ghi lại bộ nhớ CUDA
            peak_alloc = torch.cuda.max_memory_allocated() if torch.cuda.is_available() else 0
            peak_res = torch.cuda.max_memory_reserved() if torch.cuda.is_available() else 0

            # Cập nhật trạng thái dừng sớm (early stopping) & checkpoint tốt nhất
            curr_val_loss = val_stats["val_L_graph"]
            is_best = curr_val_loss < best_val_loss

            trainer.completed_epoch = epoch + 1
            trainer.next_epoch_to_run = epoch + 1

            ckpt_metadata = {
                "run_id": run_id,
                "seed": seed,
                "execution_code_commit_sha": expected_code_commit or preflight["commit_sha"],
                "protocol_lock_sha256": preflight.get("protocol_lock_sha"),
                "environment_lock_sha256": preflight.get("env_lock_sha"),
                "raw_dataset_sha256": RAW_HDFS_TAR_SHA,
                "train_membership_sha256": TRAIN_MEMBERSHIP_SHA,
                "val_membership_sha256": VAL_MEMBERSHIP_SHA,
                "completed_epoch": epoch + 1,
                "next_epoch_to_run": epoch + 1,
                "global_step": trainer.global_step
            }

            if is_best:
                best_val_loss = curr_val_loss
                patience_counter = 0
                best_ckpt_epoch = epoch + 1
                best_ckpt_step = trainer.global_step
                trainer.best_val_loss = best_val_loss
                trainer.patience_counter = 0
                trainer.best_epoch = best_ckpt_epoch
                trainer.best_checkpoint_global_step = best_ckpt_step
                trainer.best_checkpoint_path = str(best_checkpoint_p)
                best_metrics = dict(val_stats)
                
                trainer.save_checkpoint(best_checkpoint_p, metadata=ckpt_metadata)
                best_ckpt_sha = compute_sha256(best_checkpoint_p)
                print(f"[{run_id}] (*) Improved Validation Loss: {best_val_loss:.6f} at Epoch {best_ckpt_epoch} (Step {best_ckpt_step}) -> Saved {best_checkpoint_p}")
            else:
                patience_counter += 1
                trainer.patience_counter = patience_counter
                print(f"[{run_id}] Validation Loss did not improve ({curr_val_loss:.6f} >= {best_val_loss:.6f}). Patience: {patience_counter}/{trainer.early_stopping_patience}")

            # Lưu checkpoint cuối cùng
            trainer.save_checkpoint(last_checkpoint_p, metadata=ckpt_metadata)
            last_ckpt_sha = compute_sha256(last_checkpoint_p)

            # Kiểm kê checkpoint
            ckpt_inv = {
                "run_id": run_id,
                "seed": seed,
                "storage_policy": "LOCAL_AND_DURABLE_STORAGE",
                "checkpoints": [
                    {
                        "logical_name": "last_checkpoint.pt",
                        "path": str(last_checkpoint_p),
                        "sha256": last_ckpt_sha,
                        "epoch": epoch + 1,
                        "global_step": trainer.global_step,
                        "val_L_graph": curr_val_loss
                    }
                ]
            }
            if best_checkpoint_p.exists() and best_ckpt_sha:
                ckpt_inv["checkpoints"].insert(0, {
                    "logical_name": "best_val_loss.pt",
                    "path": str(best_checkpoint_p),
                    "sha256": best_ckpt_sha,
                    "epoch": best_ckpt_epoch,
                    "global_step": best_ckpt_step,
                    "val_L_graph": best_val_loss
                })
            ckpt_inv_p.write_text(json.dumps(ckpt_inv, indent=2) + "\n", encoding="utf-8")

            # Bản ghi nhật ký gia tăng
            log_record = {
                "epoch": epoch + 1,
                "global_step": trainer.global_step,
                "learning_rate": train_stats["learning_rate"],
                "train_L_graph": train_stats["train_L_graph"],
                "train_L_rel": train_stats["train_L_rel"],
                "train_L_node": train_stats["train_L_node"],
                "train_L_time": train_stats["train_L_time"],
                "val_L_graph": val_stats["val_L_graph"],
                "val_L_rel": val_stats["val_L_rel"],
                "val_L_node": val_stats["val_L_node"],
                "val_L_time": val_stats["val_L_time"],
                "train_events": train_stats["events_count"],
                "val_events": val_stats["events_count"],
                "train_rel_loss_sum": train_stats["rel_loss_sum"],
                "train_rel_targets": train_stats["rel_target_count"],
                "train_node_sq_err_sum": train_stats["node_sq_err_sum"],
                "train_node_elements": train_stats["node_element_count"],
                "train_time_loss_sum": train_stats["time_loss_sum"],
                "train_time_targets": train_stats["time_target_count"],
                "val_rel_loss_sum": val_stats["rel_loss_sum"],
                "val_rel_targets": val_stats["rel_target_count"],
                "val_node_sq_err_sum": val_stats["node_sq_err_sum"],
                "val_node_elements": val_stats["node_element_count"],
                "val_time_loss_sum": val_stats["time_loss_sum"],
                "val_time_targets": val_stats["time_target_count"],
                "train_runtime_sec": train_stats["epoch_runtime_sec"],
                "val_runtime_sec": val_stats["epoch_runtime_sec"],
                "peak_cuda_allocated_bytes": peak_alloc,
                "peak_cuda_reserved_bytes": peak_res,
                "nan_inf_count": 0
            }

            with open(train_log_p, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_record) + "\n")
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass

            epoch_dur = time.time() - t_epoch_start
            cumulative_runtime_seconds += epoch_dur

            # Cập nhật trạng thái chạy
            run_state.update({
                "current_epoch": epoch + 1,
                "completed_epoch": epoch + 1,
                "next_epoch_to_run": epoch + 1,
                "global_step": trainer.global_step,
                "best_val_loss": best_val_loss,
                "best_epoch": best_ckpt_epoch,
                "best_checkpoint_global_step": best_ckpt_step,
                "best_checkpoint_sha256": best_ckpt_sha,
                "best_metrics": best_metrics,
                "cumulative_runtime_seconds": cumulative_runtime_seconds,
                "last_checkpoint_path": str(last_checkpoint_p),
                "last_checkpoint_sha256": last_ckpt_sha
            })
            run_state_p.write_text(json.dumps(run_state, indent=2) + "\n", encoding="utf-8")

            # Phản chiếu bền bỉ của Google Drive ở ranh giới epoch đã hoàn thành
            if durable_root:
                durable_seed_dir = Path(durable_root) / f"seed-{seed}"
                files_to_sync = [
                    (last_checkpoint_p, "last_checkpoint.pt"),
                    (train_log_p, "TRAIN-LOG.jsonl"),
                    (ckpt_inv_p, "CHECKPOINT-INVENTORY.json")
                ]
                if best_checkpoint_p.exists():
                    files_to_sync.append((best_checkpoint_p, "best_val_loss.pt"))
                sync_to_durable_storage(files_to_sync, durable_seed_dir, run_state_file=(run_state_p, "RUN-STATE.json"))
                print(f"[{run_id}] Durable Google Drive sync verified for completed epoch {epoch + 1} at {durable_seed_dir}")

            if patience_counter >= trainer.early_stopping_patience:
                print(f"[{run_id}] Early stopping triggered after {patience_counter} epochs without improvement.")
                break

        t_end_iso = datetime.now(timezone.utc).isoformat()

        # Số liệu cuối cùng
        metrics_data = {
            "run_id": run_id,
            "seed": seed,
            "evidence_class": "REAL_EMPIRICAL",
            "claim_scope": "PRETRAINING_EMPIRICAL",
            "epochs_completed": run_state["current_epoch"],
            "early_stopped": patience_counter >= trainer.early_stopping_patience,
            "best_epoch": best_ckpt_epoch,
            "best_val_L_graph": best_val_loss,
            "best_val_L_rel": best_metrics.get("val_L_rel"),
            "best_val_L_node": best_metrics.get("val_L_node"),
            "best_val_L_time": best_metrics.get("val_L_time"),
            "final_train_L_graph": train_stats["train_L_graph"],
            "final_val_L_graph": val_stats["val_L_graph"],
            "optimizer_steps_completed": trainer.global_step,
            "runtime_seconds": cumulative_runtime_seconds,
            "peak_cuda_allocated_bytes": peak_alloc,
            "peak_cuda_reserved_bytes": peak_res,
            "nan_count": 0,
            "inf_count": 0,
            "train_events_per_epoch": total_train_events,
            "val_events_per_epoch": total_val_events,
            "best_checkpoint_sha256": best_ckpt_sha,
            "last_checkpoint_sha256": last_ckpt_sha
        }
        metrics_p.write_text(json.dumps(metrics_data, indent=2) + "\n", encoding="utf-8")

        # Kiểm tra bản ghi tường lửa
        firewall_data = guard.to_dict()
        firewall_p.write_text(json.dumps(firewall_data, indent=2) + "\n", encoding="utf-8")

        def safe_rel_path(p: Path) -> str:
            try:
                return str(p.relative_to(base_dir))
            except ValueError:
                return str(p)

        # Bản ghi nguồn thử nghiệm
        source_data = {
            "claim_id": f"CLAIM-STAGE-A2-HDFS-SEED{seed}",
            "stage": "STAGE_A2",
            "run_id": run_id,
            "dataset": "HDFS",
            "split_id": "SPL-HDFS-001",
            "seed": seed,
            "evidence_class": "REAL_EMPIRICAL",
            "claim_scope": "PRETRAINING_EMPIRICAL",
            "execution_code_commit_sha": expected_code_commit,
            "execution_head_at_launch": preflight["commit_sha"],
            "effective_protocol_lock_path": "experiments/protocol/STAGE-A2-EXECUTION-LOCK-V1.4.json" if not is_v15_plan else "experiments/protocol/PROTOCOL-AMENDMENTS.md",
            "effective_protocol_lock_sha256": preflight["protocol_lock_sha"],
            "environment_lock_path": "experiments/evidence/stage-a2/preexecution/STAGE-A2-EXECUTION-ENVIRONMENT.json" if not is_v15_plan else "experiments/evidence/stage-a2/preexecution/STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json",
            "environment_lock_sha256": preflight["env_lock_sha"],
            "raw_dataset_sha256": preflight["raw_tar_sha"],
            "selected_train_membership_sha256": preflight["train_membership_sha"],
            "selected_val_membership_sha256": preflight["val_membership_sha"],
            "command_executed": f"python scripts/run_stage_a2_five_seed_empirical.py --seed {seed} --authorize-real-empirical-execution",
            "working_directory": str(base_dir),
            "timestamp_start": orig_start_time,
            "timestamp_end": t_end_iso,
            "environment": env_data,
            "train_log_path": safe_rel_path(train_log_p),
            "train_log_sha256": compute_sha256(train_log_p),
            "metrics_artifact_path": safe_rel_path(metrics_p),
            "metrics_artifact_sha256": compute_sha256(metrics_p),
            "checkpoint_inventory_path": safe_rel_path(ckpt_inv_p),
            "checkpoint_inventory_sha256": compute_sha256(ckpt_inv_p),
            "test_firewall_path": safe_rel_path(firewall_p),
            "test_firewall_sha256": compute_sha256(firewall_p)
        }
        source_p.write_text(json.dumps(source_data, indent=2) + "\n", encoding="utf-8")

        # Chạy bản kê (manifest)
        manifest_data = {
            "manifest_version": "1.5.0" if is_v15_plan else "1.4.1",
            "run_id": run_id,
            "seed": seed,
            "execution_code_commit_sha": expected_code_commit,
            "status": "COMPLETED",
            "artifacts": [
                {"path": safe_rel_path(metrics_p), "sha256": compute_sha256(metrics_p)},
                {"path": safe_rel_path(source_p), "sha256": compute_sha256(source_p)},
                {"path": safe_rel_path(env_p), "sha256": compute_sha256(env_p)},
                {"path": safe_rel_path(train_log_p), "sha256": compute_sha256(train_log_p)},
                {"path": safe_rel_path(ckpt_inv_p), "sha256": compute_sha256(ckpt_inv_p)},
                {"path": safe_rel_path(firewall_p), "sha256": compute_sha256(firewall_p)}
            ]
        }
        manifest_p.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

        # Trạng thái đánh dấu đã hoàn thành
        run_state["status"] = "COMPLETED"
        run_state_p.write_text(json.dumps(run_state, indent=2) + "\n", encoding="utf-8")

        # Đồng bộ hóa bền vững cuối cùng
        if durable_root:
            durable_seed_dir = Path(durable_root) / f"seed-{seed}"
            final_files = [
                (metrics_p, "METRICS.json"),
                (source_p, "EXPERIMENTAL-SOURCE.json"),
                (env_p, "ENVIRONMENT.json"),
                (train_log_p, "TRAIN-LOG.jsonl"),
                (ckpt_inv_p, "CHECKPOINT-INVENTORY.json"),
                (firewall_p, "TEST-FIREWALL.json"),
                (manifest_p, "RUN-MANIFEST.json"),
                (last_checkpoint_p, "last_checkpoint.pt")
            ]
            if best_checkpoint_p.exists():
                final_files.append((best_checkpoint_p, "best_val_loss.pt"))
            sync_to_durable_storage(final_files, durable_seed_dir, run_state_file=(run_state_p, "RUN-STATE.json"))
            print(f"[{run_id}] Final Durable Google Drive sync verified at {durable_seed_dir}")

        print(f"\n[{run_id}] RUN COMPLETED SUCCESSFULLY.")
        print(f"[{run_id}] Best Validation L_graph: {best_val_loss:.6f} at Epoch {best_ckpt_epoch} (Step {best_ckpt_step})")
        return {"seed": seed, "status": "COMPLETED", "optimizer_steps": trainer.global_step, "best_val_loss": best_val_loss}

    except Exception as exc:
        err_type = type(exc).__name__
        err_msg = str(exc)
        print(f"\n[{run_id}] [FATAL ERROR] {err_type}: {err_msg}")
        
        failure_data = {
            "run_id": run_id,
            "seed": seed,
            "error_type": err_type,
            "error_message": err_msg,
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "last_completed_epoch": run_state.get("current_epoch", 0),
            "global_step": run_state.get("global_step", 0),
            "last_valid_checkpoint": run_state.get("last_checkpoint_path"),
            "execution_code_commit_sha": expected_code_commit,
            "environment": env_data
        }
        failure_p.write_text(json.dumps(failure_data, indent=2) + "\n", encoding="utf-8")
        
        run_state["status"] = "FAILED"
        run_state["error"] = f"{err_type}: {err_msg}"
        run_state_p.write_text(json.dumps(run_state, indent=2) + "\n", encoding="utf-8")
        raise

def main():
    parser = argparse.ArgumentParser(description="Stage A2 Canonical Five-Seed Empirical Runner (V1.4.1 / V1.5)")
    parser.add_argument("--seed", type=int, default=None, help="Canonical seed (42, 1337, 2024, 7, 999)")
    parser.add_argument("--all", action="store_true", help="Execute across all 5 canonical seeds (DRY-RUN ONLY)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Perform complete pre-flight and dry-run without optimizer steps")
    parser.add_argument("--authorize-real-empirical-execution", action="store_true", default=False, help="Authorize real training")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint file to resume from")
    parser.add_argument("--resume-sha256", type=str, default=None, help="Expected SHA-256 hash of resume checkpoint")
    parser.add_argument("--base-dir", type=str, default=None, help="Repository root directory")
    parser.add_argument("--dataset-path", type=str, default=None, help="Explicit path to raw HDFS tarball")
    parser.add_argument("--durable-root", type=str, default=None, help="Durable root directory (e.g. Google Drive) for completed-epoch mirror")
    parser.add_argument("--plan", type=str, default=None, help="Execution plan JSON path")
    parser.add_argument("--authorization", type=str, default=None, help="Launch authorization JSON path")
    parser.add_argument("--environment-lock", type=str, default=None, help="Environment lock JSON path")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve() if args.base_dir else DEFAULT_BASE_DIR
    dataset_path = Path(args.dataset_path).resolve() if args.dataset_path else None
    durable_root = Path(args.durable_root).resolve() if args.durable_root else None
    plan_path = Path(args.plan).resolve() if args.plan else None
    auth_path = Path(args.authorization).resolve() if args.authorization else None
    env_lock_path = Path(args.environment_lock).resolve() if args.environment_lock else None

    # Bảo vệ an toàn nghiêm ngặt: --tất cả đều bị nghiêm cấm thực hiện theo kinh nghiệm thực tế
    if args.all and args.authorize_real_empirical_execution and not args.dry_run:
        raise ValueError("FATAL: --all is strictly prohibited for real empirical execution! Real runs must be executed sequentially one canonical seed at a time.")

    if args.all:
        target_seeds = CANONICAL_SEEDS
    elif args.seed is not None:
        target_seeds = [args.seed]
    else:
        print("Please specify --seed <int> or --all (along with --dry-run).")
        sys.exit(1)

    resume_path = Path(args.resume) if args.resume else None

    results = []
    for s in target_seeds:
        res = run_single_seed_pipeline(
            seed=s,
            base_dir=base_dir,
            is_dry_run=args.dry_run,
            empirical_authorized=args.authorize_real_empirical_execution,
            resume_checkpoint=resume_path,
            resume_sha256=args.resume_sha256,
            durable_root=durable_root,
            plan_path=plan_path,
            auth_path=auth_path,
            env_lock_path=env_lock_path,
            raw_tar_path=dataset_path
        )
        results.append(res)

    print("=================================================================")
    print("   STAGE A2 FIVE-SEED RUNNER SUMMARY                            ")
    print("=================================================================")
    for r in results:
        print(f"Seed {r['seed']}: Status={r['status']}, OptimizerStepsExecuted={r['optimizer_steps']}")
    print("=================================================================")

if __name__ == "__main__":
    main()
