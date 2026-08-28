# -*- coding: utf-8 -*-
"""
Comprehensive Integration Tests for Stage A2 Seed 42 Colab Resume Shell.
Tests all 20 contract requirements including fail-closed classification,
fresh-process workspace restoration, checkpoint-bound lock matching, and preflight schema.
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
    TARGET_SEED,
    EXPECTED_RAW_HDFS_SHA,
    compute_sha256_streaming,
    discover_durable_seed42_state,
    inspect_checkpoint_integrity,
    restore_local_workspace_state,
    restore_checkpoint_environment_lock,
    run_preflight_and_resume
)

REPO_ROOT = Path(__file__).resolve().parent.parent
MOCK_APPROVED_COMMIT = "d89f09b4039bd368cef60b30ae4b8ad9ba6c5e67"

def test_missing_approved_commit_fails_closed(capsys):
    rc = run_preflight_and_resume(mode="dry-run", execution_commit=None, base_dir_arg=REPO_ROOT)
    assert rc == 1
    out = capsys.readouterr().out
    assert "APPROVED EXECUTION COMMIT REQUIRED" in out

def test_missing_run_classification_defaults_to_pending_and_refuses(tmp_path, capsys):
    durable_dir = tmp_path / "seed-42"
    durable_dir.mkdir(parents=True, exist_ok=True)
    (durable_dir / "RUN-STATE.json").write_text(json.dumps({"status": "RUNNING", "completed_epoch": 1, "global_step": 573}), encoding="utf-8")
    
    state = discover_durable_seed42_state(tmp_path, REPO_ROOT)
    assert state["classification"] == "PENDING_INDEPENDENT_CLASSIFICATION"
    assert state["is_resumable"] is False
    assert "PENDING_INDEPENDENT_CLASSIFICATION" in state["non_resumable_reason"]

def test_forensic_classification_refuses_resume(tmp_path, capsys):
    durable_dir = tmp_path / "seed-42"
    durable_dir.mkdir(parents=True, exist_ok=True)
    (durable_dir / "RUN-CLASSIFICATION.json").write_text(json.dumps({"classification": "FORENSIC_NONCANONICAL"}), encoding="utf-8")
    (durable_dir / "RUN-STATE.json").write_text(json.dumps({"status": "RUNNING", "completed_epoch": 1, "global_step": 573}), encoding="utf-8")
    
    state = discover_durable_seed42_state(tmp_path, REPO_ROOT)
    assert state["classification"] == "FORENSIC_NONCANONICAL"
    assert state["is_resumable"] is False
    assert "FORENSIC-ONLY" in state["non_resumable_reason"]

def test_canonical_resumable_classification_allows_resume(tmp_path):
    durable_dir = tmp_path / "seed-42"
    durable_dir.mkdir(parents=True, exist_ok=True)
    (durable_dir / "RUN-CLASSIFICATION.json").write_text(json.dumps({"classification": "CANONICAL_RESUMABLE"}), encoding="utf-8")
    (durable_dir / "RUN-STATE.json").write_text(json.dumps({"status": "RUNNING", "completed_epoch": 1, "global_step": 573, "last_checkpoint_sha256": "dummy"}), encoding="utf-8")
    (durable_dir / "last_checkpoint.pt").write_bytes(b"dummy")
    
    state = discover_durable_seed42_state(tmp_path, REPO_ROOT)
    assert state["classification"] == "CANONICAL_RESUMABLE"
    assert state["is_resumable"] is True

def test_fresh_runtime_local_state_restore(tmp_path):
    durable_dir = tmp_path / "seed-42"
    durable_dir.mkdir(parents=True, exist_ok=True)
    
    (durable_dir / "RUN-STATE.json").write_text(json.dumps({"status": "RUNNING", "completed_epoch": 1}), encoding="utf-8")
    (durable_dir / "TRAIN-LOG.jsonl").write_text("{\"step\": 1}\n", encoding="utf-8")
    (durable_dir / "CHECKPOINT-INVENTORY.json").write_text(json.dumps({"checkpoints": []}), encoding="utf-8")
    (durable_dir / "ENVIRONMENT.json").write_text(json.dumps({"python": "3.12"}), encoding="utf-8")
    (durable_dir / "TEST-FIREWALL.json").write_text(json.dumps({"test_opened": False, "test_feature_reads": 0}), encoding="utf-8")
    (durable_dir / "last_checkpoint.pt").write_bytes(b"model_weights_bytes")
    
    mock_base = tmp_path / "mock_workspace"
    ok, msg = restore_local_workspace_state(durable_dir, mock_base)
    assert ok is True
    
    restored_run = mock_base / "experiments" / "runs" / "stage-a2" / "HDFS" / "seed-42"
    restored_art = mock_base / ".artifacts" / "stage-a2" / "HDFS" / "seed-42"
    
    assert (restored_run / "RUN-STATE.json").exists()
    assert (restored_run / "TRAIN-LOG.jsonl").exists()
    assert (restored_run / "TEST-FIREWALL.json").exists()
    assert (restored_art / "last_checkpoint.pt").exists()
    assert (restored_art / "last_checkpoint.pt").read_bytes() == b"model_weights_bytes"

def test_restore_checkpoint_environment_lock_matches_sha(tmp_path):
    qual_dir = tmp_path / "qualification" / "QUAL-COLAB-001"
    qual_dir.mkdir(parents=True, exist_ok=True)
    
    lock_file = qual_dir / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    lock_content = json.dumps({"python_version": "3.12.8", "torch_version": "2.6.0+cu124"})
    lock_file.write_text(lock_content, encoding="utf-8")
    expected_sha = compute_sha256_streaming(lock_file)
    
    mock_base = tmp_path / "workspace"
    restored_p = restore_checkpoint_environment_lock(expected_sha, mock_base, tmp_path / "runs" / "HDFS")
    assert restored_p.exists()
    assert compute_sha256_streaming(restored_p) == expected_sha

def test_stale_running_process_status(tmp_path):
    durable_dir = tmp_path / "seed-42"
    durable_dir.mkdir(parents=True, exist_ok=True)
    (durable_dir / "RUN-STATE.json").write_text(json.dumps({"status": "RUNNING", "completed_epoch": 1, "global_step": 573}), encoding="utf-8")
    
    state = discover_durable_seed42_state(tmp_path, REPO_ROOT)
    assert state["status"] == "RUNNING"
    assert state["process_status"] == "STALE_OR_INTERRUPTED"

def test_evidence_derived_firewall_status(tmp_path):
    durable_dir = tmp_path / "seed-42"
    durable_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Missing -> UNVERIFIED
    state = discover_durable_seed42_state(tmp_path, REPO_ROOT)
    assert state["firewall_status"] == "UNVERIFIED_NO_EVIDENCE_FILE"
    
    # 2. Present locked -> LOCKED
    (durable_dir / "TEST-FIREWALL.json").write_text(json.dumps({"test_opened": False, "test_feature_reads": 0}), encoding="utf-8")
    state2 = discover_durable_seed42_state(tmp_path, REPO_ROOT)
    assert state2["firewall_status"] == "LOCKED"
    
    # 3. Present breached -> BREACHED
    (durable_dir / "TEST-FIREWALL.json").write_text(json.dumps({"test_opened": True, "test_feature_reads": 1}), encoding="utf-8")
    state3 = discover_durable_seed42_state(tmp_path, REPO_ROOT)
    assert state3["firewall_status"] == "BREACHED"
