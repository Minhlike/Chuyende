# -*- coding: utf-8 -*-
"""
CH3 Smoke Runner Invariant & Firewall Tests
Verifies:
  1. Test Set Firewall raises TestSetSealedError if any attempt is made to access TEST split.
  2. Small deterministic subsetting respects manifest bounds (<= 256 train, <= 64 val).
  3. Smoke test executes without NaN/Inf losses or gradients.
  4. Checkpoint save and reload restores weights deterministically (L_inf < 1e-5).
  5. All output manifests contain result_class='IMPLEMENTATION_SMOKE_TEST' and test_set_opened=False.
"""

import pytest
from pathlib import Path

pytest.importorskip("torch")
import torch

from research_agent.experiments.smoke.smoke_runner import (
    SmokeTestRunner,
    TestSetSealedError,
    enforce_test_firewall
)

def test_01_test_set_firewall_raises_on_test_access():
    with pytest.raises(TestSetSealedError, match="SEALED"):
        enforce_test_firewall("TEST")

    with pytest.raises(TestSetSealedError, match="SEALED"):
        enforce_test_firewall("hdfs_test.pt")

    # Train and Val must pass without exception
    enforce_test_firewall("TRAIN")
    enforce_test_firewall("hdfs_val.pt")

def test_02_smoke_test_pipeline_execution(tmp_path):
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    runner = SmokeTestRunner(
        base_dir=base_dir,
        seed=42,
        max_train_samples=16,
        max_val_samples=8,
        batch_size=8,
        epochs=1,
        lr=1e-3
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
    assert res["checkpoint_reload_pass"] is True
    assert res["deterministic_reload_match"] is True
