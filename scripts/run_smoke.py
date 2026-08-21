# -*- coding: utf-8 -*-
import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

from pathlib import Path
from research_agent.experiments.smoke.smoke_runner import SmokeTestRunner

def main():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    runner = SmokeTestRunner(
        base_dir=base_dir,
        seed=42,
        max_train_samples=64,
        max_val_samples=16,
        batch_size=16,
        epochs=2,
        lr=1e-3,
        custom_run_id="CANONICAL-SMOKE-RUN-001"
    )
    result = runner.run_smoke_training()
    print("=== CANONICAL SMOKE TEST RUN COMPLETE ===")
    print("Run ID:", result["smoke_run_id"])
    print("Data Used:", result["dataset_used"])
    print("Losses Finite:", result["losses_finite"])
    print("NaN Losses:", result["nan_loss_count"])
    print("Inf Losses:", result["inf_loss_count"])
    print("Unexpected Zero Grads:", result["zero_grad_unexpected_count"])
    print("NaN Grads:", result["nan_grad_count"])
    print("Optimizer Updated Params:", result["optimizer_updated_params"])
    print("Checkpoint Save Pass:", result["checkpoint_save_pass"])
    print("Resume Step Loss Match:", result["resume_next_step_loss_match"])
    print("Resume Step Param Match:", result["resume_next_step_param_match"])
    print("Debug Validation Metric Generated:", result["debug_validation_metric_generated"])
    print("Test Set Opened:", result["test_set_opened"])
    print("Test Records Read:", result["test_records_read"])

if __name__ == "__main__":
    main()
