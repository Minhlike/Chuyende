# -*- coding: utf-8 -*-
"""
Execution Script: Real Stage A1 Multi-Task Self-Supervised Pretraining
Executes canonical Stage A1 on HDFS and BGL datasets across 5 canonical seeds:
  - Seeds: [42, 1337, 2024, 7, 999]
  - Architecture: 4-layer Transformer Encoder, d_model=128, H=4, d_ffn=512, max_len=128
  - Batching: micro_batch=16, grad_accum=4 (effective batch=64)
  - Optimizer: AdamW (lr=5e-4, wd=0.01), Linear Warmup + Cosine Decay
  - Validation: Once per completed epoch, early stopping patience=3 epochs
  - Checkpoint Resume Verification: Included
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
import numpy as np
import torch

from research_agent.experiments.training.stage_a1_runner import StageA1Trainer

def verify_checkpoint_resumption(base_dir: Path, device: torch.device):
    print("\n--- [VERIFICATION] CHECKPOINT RESUME & CONTINUATION INTEGRITY ---")
    dataset = "HDFS"
    seed = 42
    
    # 1. Initialize trainer and run 1 epoch
    trainer_init = StageA1Trainer(dataset_name=dataset, seed=seed, base_dir=base_dir, device=device)
    metrics_e1, step_e1 = trainer_init.train_epoch(1, 0)
    val_e1 = trainer_init.evaluate_validation()
    
    test_ckpt_path = trainer_init.output_dir / "resume_test_checkpoint.pt"
    trainer_init.save_checkpoint(test_ckpt_path, 1, step_e1, val_e1["val_loss_seq"], 0)
    
    # 2. Get next step prediction on a probe batch
    probe_batch = next(iter(trainer_init.train_loader))
    seqs = probe_batch["sequences"].to(device)
    params = probe_batch["param_targets"].to(device)
    gaps = probe_batch["time_gaps"].to(device)
    
    trainer_init.model.eval()
    with torch.no_grad():
        out_init = trainer_init.model.forward_features(seqs, param_slots=params)
    
    # 3. Create brand new trainer instance and load checkpoint
    trainer_resumed = StageA1Trainer(dataset_name=dataset, seed=seed, base_dir=base_dir, device=device)
    e_res, step_res, best_loss_res, pat_res = trainer_resumed.load_checkpoint(test_ckpt_path)
    
    trainer_resumed.model.eval()
    with torch.no_grad():
        out_resumed = trainer_resumed.model.forward_features(seqs, param_slots=params)
    
    max_diff = torch.max(torch.abs(out_init - out_resumed)).item()
    print(f"[RESUME VERIFICATION] Epoch: {e_res}, Global Step: {step_res}, Max Weight Diff: {max_diff:.8e}")
    assert max_diff < 1e-6, f"Checkpoint continuation divergence: {max_diff}"
    print("[RESUME VERIFICATION] PASS: Exact deterministic model state restored.")

def run_dataset_pretraining(dataset: str, seeds: list, base_dir: Path, device: torch.device):
    print(f"\n=======================================================")
    print(f"  EXECUTING REAL STAGE A1 PRETRAINING: DATASET {dataset}")
    print(f"=======================================================")
    results = []

    for seed in seeds:
        print(f"\n>>> Running {dataset} Pretraining [Seed {seed}] on {device}...")
        trainer = StageA1Trainer(
            dataset_name=dataset,
            seed=seed,
            base_dir=base_dir,
            device=device
        )
        manifest = trainer.train()
        results.append(manifest)
        print(f">>> Completed {dataset} [Seed {seed}]: "
              f"Best Val Loss = {manifest['best_val_loss']:.4f} | "
              f"Stopped Epoch = {manifest['stopped_epoch']} | "
              f"Total Steps = {manifest['total_optimizer_steps']} | "
              f"Duration = {manifest['total_duration_sec']:.1f}s | "
              f"Peak VRAM = {manifest['peak_vram_mb']:.1f}MB")

    # Aggregate Mean +- SD
    val_losses = [r["best_val_loss"] for r in results]
    epochs = [r["stopped_epoch"] for r in results]
    steps = [r["total_optimizer_steps"] for r in results]
    durations = [r["total_duration_sec"] for r in results]
    vrams = [r["peak_vram_mb"] for r in results]
    rams = [r["peak_ram_mb"] for r in results]

    summary = {
        "dataset": dataset,
        "seeds": seeds,
        "val_loss_mean": float(np.mean(val_losses)),
        "val_loss_sd": float(np.std(val_losses, ddof=1)),
        "stopped_epoch_mean": float(np.mean(epochs)),
        "stopped_epoch_sd": float(np.std(epochs, ddof=1)),
        "optimizer_steps_mean": float(np.mean(steps)),
        "optimizer_steps_sd": float(np.std(steps, ddof=1)),
        "duration_sec_mean": float(np.mean(durations)),
        "duration_sec_sd": float(np.std(durations, ddof=1)),
        "peak_vram_mb_mean": float(np.mean(vrams)),
        "peak_vram_mb_sd": float(np.std(vrams, ddof=1)),
        "peak_ram_mb_mean": float(np.mean(rams)),
        "peak_ram_mb_sd": float(np.std(rams, ddof=1)),
        "runs": results
    }

    summary_file = base_dir / "experiments" / "runs" / "stage-a1" / dataset / "DATASET-SUMMARY.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n--- {dataset} 5-SEED STABILITY SUMMARY ---")
    print(f"Best Val Loss (L_seq): {summary['val_loss_mean']:.4f} +- {summary['val_loss_sd']:.4f}")
    print(f"Stopped Epoch:         {summary['stopped_epoch_mean']:.1f} +- {summary['stopped_epoch_sd']:.1f}")
    print(f"Optimizer Steps:       {summary['optimizer_steps_mean']:.1f} +- {summary['optimizer_steps_sd']:.1f}")
    print(f"Duration (sec):        {summary['duration_sec_mean']:.1f} +- {summary['duration_sec_sd']:.1f}")
    print(f"Peak VRAM (MB):        {summary['peak_vram_mb_mean']:.1f} +- {summary['peak_vram_mb_sd']:.1f}")
    print(f"Peak RAM (MB):         {summary['peak_ram_mb_mean']:.1f} +- {summary['peak_ram_mb_sd']:.1f}")

    return summary

def main():
    parser = argparse.ArgumentParser(description="Stage A1 Self-Supervised Pretraining Runner")
    parser.add_argument("--dataset", choices=["HDFS", "BGL", "ALL"], default="ALL", help="Dataset to train")
    parser.add_argument("--seed", type=int, default=None, help="Specific seed or None for all 5 canonical seeds")
    parser.add_argument("--verify-resume", action="store_true", help="Run crash/resume verification")
    args = parser.parse_args()

    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    if args.verify_resume:
        verify_checkpoint_resumption(base_dir, device)
        return

    # Verify checkpoint resume first
    verify_checkpoint_resumption(base_dir, device)

    canonical_seeds = [42, 1337, 2024, 7, 999]
    target_seeds = [args.seed] if args.seed is not None else canonical_seeds

    if args.dataset in ["HDFS", "ALL"]:
        run_dataset_pretraining("HDFS", target_seeds, base_dir, device)

    if args.dataset in ["BGL", "ALL"]:
        run_dataset_pretraining("BGL", target_seeds, base_dir, device)

    print("\n[ALL STAGE A1 RUNS COMPLETED SUCCESSFULLY]")

if __name__ == "__main__":
    main()
