# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Stage A2 Seed 42 Colab Resume Shell.
"""

import sys
import json
import shutil
import hashlib
import tempfile
import subprocess
from pathlib import Path
import pytest
import torch

from scripts.colab_stage_a2_resume_seed42 import (
    APPROVED_EXECUTION_COMMIT,
    TARGET_SEED,
    EXPECTED_RAW_HDFS_SHA,
    compute_sha256_streaming,
    discover_durable_seed42_state,
    inspect_checkpoint_integrity,
    run_preflight_and_resume
)

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_approved_execution_commit_constant():
    assert len(APPROVED_EXECUTION_COMMIT) == 40

def test_expected_raw_hdfs_sha():
    assert EXPECTED_RAW_HDFS_SHA == "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"

def test_status_mode_does_not_mutate_nonexistent_run(tmp_path, capsys):
    state = discover_durable_seed42_state(tmp_path, tmp_path)
    assert state["found"] is False
    assert state["is_resumable"] is False
    rc = run_preflight_and_resume(mode="status", base_dir_arg=REPO_ROOT, durable_root_arg=tmp_path)
    assert rc == 0
    captured = capsys.readouterr().out
    assert "STAGE A2 SEED-42 DURABLE STATUS REPORT" in captured
    assert "RESUMABLE:               NO" in captured

def test_forensic_only_checkpoint_refuses_resume(tmp_path, capsys):
    # Setup mock forensic run directory
    run_dir = tmp_path / "runs" / "HDFS" / "seed-42"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    mock_run_state = {
        "seed": 42,
        "run_id": "RUN-STAGE-A2-HDFS-SEED42",
        "status": "INTERRUPTED",
        "completed_epoch": 1,
        "classification": "NONCANONICAL_RNG_INITIALIZATION",
        "last_checkpoint_sha256": "dummy"
    }
    (run_dir / "RUN-STATE.json").write_text(json.dumps(mock_run_state), encoding="utf-8")
    
    state = discover_durable_seed42_state(tmp_path, tmp_path)
    assert state["is_forensic_only"] is True
    assert state["is_resumable"] is False
    
    rc = run_preflight_and_resume(mode="dry-run", base_dir_arg=REPO_ROOT, durable_root_arg=tmp_path)
    assert rc == 1
    captured = capsys.readouterr().out
    assert "RESUME REFUSED:" in captured
    assert "EXISTING SEED42 CHECKPOINT IS FORENSIC-ONLY" in captured

def test_completed_run_refuses_resume(tmp_path, capsys):
    run_dir = tmp_path / "runs" / "HDFS" / "seed-42"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    mock_run_state = {
        "seed": 42,
        "run_id": "RUN-STAGE-A2-HDFS-SEED42",
        "status": "COMPLETED",
        "completed_epoch": 20,
        "next_epoch_to_run": 21,
        "global_step": 11460,
        "last_checkpoint_sha256": "dummy"
    }
    (run_dir / "RUN-STATE.json").write_text(json.dumps(mock_run_state), encoding="utf-8")
    
    state = discover_durable_seed42_state(tmp_path, tmp_path)
    assert state["status"] == "COMPLETED"
    assert state["is_resumable"] is False
    assert "already COMPLETED" in state["non_resumable_reason"]

def test_corrupted_checkpoint_sha_fails(tmp_path):
    ckpt_path = tmp_path / "corrupt.pt"
    ckpt_path.write_bytes(b"corrupted bytes")
    
    with pytest.raises(ValueError, match="Checkpoint SHA mismatch"):
        inspect_checkpoint_integrity(ckpt_path, expected_sha="0000000000000000000000000000000000000000000000000000000000000000")

def test_valid_checkpoint_metadata_inspection(tmp_path):
    ckpt_path = tmp_path / "valid_ckpt.pt"
    meta = {
        "seed": 42,
        "run_id": "RUN-STAGE-A2-HDFS-SEED42",
        "completed_epoch": 1,
        "next_epoch_to_run": 2,
        "global_step": 573,
        "execution_code_commit_sha": APPROVED_EXECUTION_COMMIT,
        "raw_dataset_sha256": EXPECTED_RAW_HDFS_SHA,
        "train_membership_sha256": "65b76694b0a3cf5c6d684a26899b1e5dca634cfd0985560149feddc12ca8ccfc",
        "val_membership_sha256": "14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a",
        "protocol_lock_sha256": "dummy_proto",
        "environment_lock_sha256": "dummy_env"
    }
    dummy_payload = {
        "model_state": {},
        "optimizer_state": {},
        "scheduler_state": {},
        "epoch": 1,
        "global_step": 573,
        "checkpoint_metadata": meta
    }
    torch.save(dummy_payload, ckpt_path)
    
    actual_sha = compute_sha256_streaming(ckpt_path)
    inspected = inspect_checkpoint_integrity(ckpt_path, expected_sha=actual_sha)
    assert inspected["seed"] == 42
    assert inspected["completed_epoch"] == 1
    assert inspected["next_epoch_to_run"] == 2
    assert inspected["global_step"] == 573
    assert inspected["execution_code_commit_sha"] == APPROVED_EXECUTION_COMMIT

def test_cli_dry_run_subprocess_invocation():
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "colab_stage_a2_resume_seed42.py"),
        "--status",
        "--base-dir", str(REPO_ROOT)
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "STAGE A2 SEED-42 DURABLE STATUS REPORT" in proc.stdout
    assert "TEST_FIREWALL:           LOCKED" in proc.stdout
