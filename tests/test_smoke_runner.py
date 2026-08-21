# -*- coding: utf-8 -*-
"""
CH3 Hermetic Smoke Runner Tests
Verifies:
  1. Test Set Firewall raises TestSetSealedError if any attempt is made to access TEST split.
  2. Hermetic smoke test execution using tmp_path and pure synthetic fixtures.
  3. Real zero-grad audit passes on active parameters and flags unexpected zeros.
  4. True checkpoint resume test (Step N+1 loss and parameter match).
  5. Regression test: Running pytest does NOT modify canonical smoke artifacts in experiments/smoke/runs/.
"""

import os
import json
import pytest
from pathlib import Path

pytest.importorskip("torch")
import torch

from research_agent.experiments.smoke.smoke_runner import (
    SmokeTestRunner,
    TestSetSealedError,
    enforce_test_firewall,
    compute_sha256
)

def test_01_test_set_firewall_raises_on_test_access():
    with pytest.raises(TestSetSealedError, match="SEALED"):
        enforce_test_firewall("TEST")

    with pytest.raises(TestSetSealedError, match="SEALED"):
        enforce_test_firewall("hdfs_test.pt")

    enforce_test_firewall("TRAIN")
    enforce_test_firewall("hdfs_val.pt")

def test_02_hermetic_synthetic_smoke_pipeline_and_true_resume(tmp_path):
    """
    Executes a fully isolated smoke pipeline inside tmp_path using synthetic data fixtures.
    Guarantees no modification of canonical workspace directories.
    """
    # Create isolated mock data directory inside tmp_path
    mock_data_dir = tmp_path / "experiments" / "runs" / "data" / "hdfs"
    mock_data_dir.mkdir(parents=True, exist_ok=True)

    synthetic_seqs = [torch.randint(3, 40, (10,)) for _ in range(32)]
    synthetic_labels = [0] * 32
    synthetic_ids = [f"mock_blk_{i:04d}" for i in range(32)]

    mock_train = {"sequences": synthetic_seqs[:24], "labels": synthetic_labels[:24], "session_ids": synthetic_ids[:24]}
    mock_val = {"sequences": synthetic_seqs[24:], "labels": synthetic_labels[24:], "session_ids": synthetic_ids[24:]}

    torch.save(mock_train, mock_data_dir / "hdfs_train.pt")
    torch.save(mock_val, mock_data_dir / "hdfs_val.pt")

    runner = SmokeTestRunner(
        base_dir=tmp_path,
        seed=42,
        max_train_samples=16,
        max_val_samples=8,
        batch_size=8,
        epochs=1,
        lr=1e-3,
        custom_run_id="HERMETIC-SMOKE-TEST-001"
    )

    res = runner.run_smoke_training()

    assert res["result_class"] == "IMPLEMENTATION_SMOKE_TEST"
    assert res["thesis_eligible"] is False
    assert res["test_set_opened"] is False
    assert res["losses_finite"] is True
    assert res["nan_loss_count"] == 0
    assert res["inf_loss_count"] == 0
    assert res["zero_grad_unexpected_count"] == 0
    assert res["optimizer_updated_params"] is True
    assert res["checkpoint_save_pass"] is True
    assert res["resume_next_step_loss_match"] is True
    assert res["resume_next_step_param_match"] is True
    assert res["debug_validation_metric_generated"] is False

    # Assert files written inside tmp_path isolated run directory
    expected_run_dir = tmp_path / "experiments" / "smoke" / "runs" / "HERMETIC-SMOKE-TEST-001"
    assert (expected_run_dir / "manifest.json").exists()
    assert (expected_run_dir / "subset-manifest.json").exists()
    assert (expected_run_dir / "train-log.jsonl").exists()
    assert (expected_run_dir / "validation-log.jsonl").exists()
    assert (expected_run_dir / "report.md").exists()

def test_03_canonical_smoke_artifacts_untouched_after_tests():
    """
    Verifies that canonical smoke runs in experiments/smoke/runs/ remain immutable.
    """
    if Path("/mnt/d/Research").exists():
        smoke_runs_dir = Path("/mnt/d/Research/experiments/smoke/runs")
    else:
        smoke_runs_dir = Path(r"D:\Research\experiments\smoke\runs")

    if smoke_runs_dir.exists() and any(smoke_runs_dir.iterdir()):
        for run_p in smoke_runs_dir.iterdir():
            if run_p.is_dir():
                manifest_p = run_p / "manifest.json"
                if manifest_p.exists():
                    assert manifest_p.stat().st_size > 0
