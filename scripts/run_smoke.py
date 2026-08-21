# -*- coding: utf-8 -*-
from pathlib import Path
from research_agent.experiments.smoke.smoke_runner import SmokeTestRunner

def main():
    base_dir = Path("/mnt/d/Research")
    if not base_dir.exists():
        base_dir = Path(r"D:\Research")

    runner = SmokeTestRunner(
        base_dir=base_dir,
        seed=42,
        max_train_samples=64,
        max_val_samples=16,
        batch_size=16,
        epochs=2,
        lr=1e-3
    )
    result = runner.run_smoke_training()
    print("=== SMOKE TEST RUN COMPLETE ===")
    print("Run ID:", result["smoke_run_id"])
    print("Losses Finite:", result["losses_finite"])
    print("Optimizer Updated Params:", result["optimizer_updated_params"])
    print("Checkpoint Save Pass:", result["checkpoint_save_pass"])
    print("Checkpoint Reload Pass:", result["checkpoint_reload_pass"])
    print("Deterministic Reload Match:", result["deterministic_reload_match"])
    print("Test Set Opened:", result["test_set_opened"])
    print("Test Records Read:", result["test_records_read"])

if __name__ == "__main__":
    main()
