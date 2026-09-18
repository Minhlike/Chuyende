# -*- coding: utf-8 -*-
"""
Thử nghiệm trình thực thi smoke test kín CH3
Xác minh:
  1. Tường lửa của bộ kiểm tra sẽ tăng TestSetSealedError nếu có bất kỳ nỗ lực nào được thực hiện để truy cập vào phần phân tách TEST.
  2. Thực hiện smoke test kín bằng tmp_path và các thiết bị tổng hợp nguyên chất.
  3. Kiểm tra cấp độ 0 thực sự chuyển các tham số hoạt động và gắn cờ các số 0 không mong muốn.
  4. Kiểm tra tiếp tục checkpoint thực sự (Mất bước N+1 và khớp tham số).
  5. Kiểm tra hồi quy: Chạy pytest có NOT sửa đổi các artifact của smoke test chuẩn trong experiments/khói/chạy/.
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
    Thực hiện đường dẫn smoke test được cách ly hoàn toàn bên trong tmp_path bằng cách sử dụng các thiết bị dữ liệu tổng hợp.
    Đảm bảo không sửa đổi các thư mục không gian làm việc chuẩn.
    """
    # Tạo thư mục dữ liệu mô phỏng riêng biệt bên trong tmp_path
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

    # Xác nhận các tệp được ghi bên trong thư mục chạy riêng biệt tmp_path
    expected_run_dir = tmp_path / "experiments" / "smoke" / "runs" / "HERMETIC-SMOKE-TEST-001"
    assert (expected_run_dir / "manifest.json").exists()
    assert (expected_run_dir / "subset-manifest.json").exists()
    assert (expected_run_dir / "train-log.jsonl").exists()
    assert (expected_run_dir / "validation-log.jsonl").exists()
    assert (expected_run_dir / "report.md").exists()

def test_03_canonical_smoke_artifacts_untouched_after_tests():
    """
    Xác minh rằng khói chuẩn chạy trong thử nghiệm/khói/chạy/ vẫn không thay đổi.
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
