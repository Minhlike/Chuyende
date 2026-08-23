# -*- coding: utf-8 -*-
"""
Regression Test for Deterministic Checkpoint Continuation in Stage A1 Trainer.
Verifies that resuming training from a saved checkpoint produces an EXACT identical
training trajectory (data batch order, loss values, gradients, optimizer state, scheduler state,
and model weights) as an uninterrupted continuous training run.
"""

import os
import tempfile
import json
import pytest
from pathlib import Path

torch = pytest.importorskip("torch")
np = pytest.importorskip("numpy")

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import torch.nn as nn

from research_agent.experiments.extractor.sequence_view import SequenceViewExtractor
from research_agent.experiments.training.stage_a1_runner import (
    StageA1Trainer,
    SequenceSSLDataset,
    collate_sequence_ssl
)


def create_synthetic_data_package(num_sessions: int = 64, seq_len: int = 32, num_slots: int = 4):
    """Creates a deterministic synthetic SSL package for regression testing."""
    torch.manual_seed(42)
    seqs = [torch.randint(3, 50, (seq_len,), dtype=torch.long) for _ in range(num_sessions)]
    params = [torch.randint(2, 30, (seq_len, num_slots), dtype=torch.long) for _ in range(num_sessions)]
    gaps = [torch.rand((seq_len - 1,), dtype=torch.float32) for _ in range(num_sessions)]
    session_ids = [f"synth_{i}" for i in range(num_sessions)]

    return {
        "dataset_classification": "REAL_DATA_CANONICAL",
        "sequences": seqs,
        "param_targets": params,
        "time_gaps": gaps,
        "session_ids": session_ids
    }


def create_dummy_lock_file(lock_path: Path):
    """Creates a minimal mock lock file for the test trainer."""
    lock_content = {
        "lock_identifier": "TEST-LOCK-STAGE-A1",
        "contract_sha256": "mock_contract_hash",
        "source_commit": "mock_commit",
        "architecture": {
            "d_model": 64,
            "layers": 2,
            "n_heads": 2,
            "d_ffn": 128,
            "dropout": 0.0,
            "max_seq_len": 32,
            "max_param_slots": 4,
            "parameter_representation_mode": "BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4"
        },
        "optimization": {
            "micro_batch_size": 4,
            "gradient_accumulation_steps": 2,
            "effective_batch_size": 8,
            "learning_rate": 0.001,
            "weight_decay": 0.01,
            "adam_beta1": 0.9,
            "adam_beta2": 0.98,
            "adam_eps": 1e-8,
            "scheduler": "LinearWarmupCosineDecay",
            "warmup_ratio": 0.10,
            "min_lr": 0.0001,
            "clip_norm": 1.0,
            "max_epochs": 4,
            "early_stopping_patience": 3
        },
        "losses_and_weights": {
            "lambda_MEP": 1.0,
            "lambda_MPP": 1.0,
            "lambda_time": 0.1,
            "mep_masking_probability": 0.15,
            "mpp_masking_probability": 0.15
        }
    }
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(lock_content, indent=2), encoding="utf-8")


class MockStageA1Trainer(StageA1Trainer):
    """Mock trainer overriding dataset loading with deterministic synthetic data."""
    def __init__(self, seed: int, base_dir: Path, device: torch.device, lock_path: Path):
        self.mock_lock_path = lock_path
        super().__init__(
            dataset_name="HDFS",
            seed=seed,
            base_dir=base_dir,
            device=device,
            lock_path=lock_path
        )

    def _load_datasets_and_vocab(self):
        self.event_vocab_size = 60
        self.param_vocab_size = 40

        train_pkg = create_synthetic_data_package(num_sessions=64, seq_len=self.max_seq_len, num_slots=self.max_param_slots)
        val_pkg = create_synthetic_data_package(num_sessions=16, seq_len=self.max_seq_len, num_slots=self.max_param_slots)

        self.train_dataset = SequenceSSLDataset(train_pkg, max_seq_len=self.max_seq_len)
        self.val_dataset = SequenceSSLDataset(val_pkg, max_seq_len=self.max_seq_len)

        self.train_generator = torch.Generator()
        self.train_generator.manual_seed(self.seed)
        self.train_loader = torch.utils.data.DataLoader(
            self.train_dataset,
            batch_size=self.micro_batch_size,
            shuffle=True,
            collate_fn=lambda b: collate_sequence_ssl(b, max_param_slots=self.max_param_slots),
            generator=self.train_generator
        )
        self.val_loader = torch.utils.data.DataLoader(
            self.val_dataset,
            batch_size=self.micro_batch_size,
            shuffle=False,
            collate_fn=lambda b: collate_sequence_ssl(b, max_param_slots=self.max_param_slots)
        )


def test_stage_a1_exact_deterministic_resume():
    """
    Verifies that:
    1. Continuous Run A (Epoch 1 -> Epoch 2)
    2. Resumed Run B (Epoch 1 -> Save Checkpoint -> Fresh Process/Trainer -> Load Checkpoint -> Epoch 2)
    Yield identical next-batch trajectories, identical loss values, identical optimizer states,
    identical learning rates, and identical model parameter weights (max parameter divergence < 1e-6).
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = 42

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        lock_path = base_dir / "protocol" / "STAGE-A1-PREEXECUTION-LOCK.json"
        create_dummy_lock_file(lock_path)
        ckpt_path = base_dir / "ckpt_epoch1.pt"

        # ==========================================
        # 1. CONTINUOUS RUN A: Epoch 1 -> Epoch 2
        # ==========================================
        trainer_a = MockStageA1Trainer(seed=seed, base_dir=base_dir, device=device, lock_path=lock_path)
        
        # Train Epoch 1
        metrics_a_ep1, step_a_ep1 = trainer_a.train_epoch(epoch=1, global_step=0)
        
        # Save Checkpoint at end of Epoch 1
        trainer_a.save_checkpoint(
            filepath=ckpt_path,
            epoch=1,
            global_step=step_a_ep1,
            best_val_loss=metrics_a_ep1["train_loss_seq"],
            patience_counter=0
        )
        
        # Continue uninterrupted to Epoch 2
        metrics_a_ep2, step_a_ep2 = trainer_a.train_epoch(epoch=2, global_step=step_a_ep1)
        lr_a_ep2 = trainer_a.scheduler.get_last_lr()[0]
        state_dict_a = {k: v.clone() for k, v in trainer_a.model.state_dict().items()}
        opt_state_a = trainer_a.optimizer.state_dict()

        # ==========================================
        # 2. RESUMED RUN B: Fresh Trainer -> Load Checkpoint -> Epoch 2
        # ==========================================
        # Delete trainer_a to guarantee clean slate
        del trainer_a

        trainer_b = MockStageA1Trainer(seed=seed, base_dir=base_dir, device=device, lock_path=lock_path)
        
        # Load Checkpoint from Epoch 1
        ep_res, step_res, best_loss_res, pat_res = trainer_b.load_checkpoint(ckpt_path)
        assert ep_res == 1, f"Expected epoch 1, got {ep_res}"
        assert step_res == step_a_ep1, f"Expected step {step_a_ep1}, got {step_res}"

        # Train Epoch 2 from resumed state
        metrics_b_ep2, step_b_ep2 = trainer_b.train_epoch(epoch=2, global_step=step_res)
        lr_b_ep2 = trainer_b.scheduler.get_last_lr()[0]
        state_dict_b = {k: v.clone() for k, v in trainer_b.model.state_dict().items()}
        opt_state_b = trainer_b.optimizer.state_dict()

        # ==========================================
        # 3. VERIFY EXACT DETERMINISTIC TRAJECTORY
        # ==========================================
        # A. Global step & Learning rate
        assert step_a_ep2 == step_b_ep2, f"Global step divergence: {step_a_ep2} vs {step_b_ep2}"
        assert abs(lr_a_ep2 - lr_b_ep2) < 1e-12, f"Learning rate divergence: {lr_a_ep2} vs {lr_b_ep2}"

        # B. Loss metrics
        for key in ["train_loss_seq", "train_loss_mep", "train_loss_mpp", "train_loss_time"]:
            diff_loss = abs(metrics_a_ep2[key] - metrics_b_ep2[key])
            assert diff_loss < 1e-6, f"Loss divergence on {key}: {metrics_a_ep2[key]} vs {metrics_b_ep2[key]} (diff={diff_loss})"

        # C. Model Parameter Divergence
        max_param_diff = 0.0
        for name in state_dict_a:
            p_a = state_dict_a[name].float()
            p_b = state_dict_b[name].float()
            diff = torch.max(torch.abs(p_a - p_b)).item()
            if diff > max_param_diff:
                max_param_diff = diff

        print(f"\n[DETERMINISTIC RESUME REGRESSION] Max Parameter Divergence: {max_param_diff:.8e}")
        assert max_param_diff < 1e-6, f"Parameter divergence exceeded threshold: {max_param_diff}"
        
        # D. Optimizer State Divergence
        # Check step counts in optimizer state
        for p_idx in opt_state_a["state"]:
            state_a = opt_state_a["state"][p_idx]
            state_b = opt_state_b["state"][p_idx]
            assert state_a["step"] == state_b["step"], "Optimizer step divergence"
            if "exp_avg" in state_a:
                exp_avg_diff = torch.max(torch.abs(state_a["exp_avg"].float() - state_b["exp_avg"].float())).item()
                assert exp_avg_diff < 1e-6, f"Optimizer exp_avg divergence: {exp_avg_diff}"
            if "exp_avg_sq" in state_a:
                exp_avg_sq_diff = torch.max(torch.abs(state_a["exp_avg_sq"].float() - state_b["exp_avg_sq"].float())).item()
                assert exp_avg_sq_diff < 1e-6, f"Optimizer exp_avg_sq_diff: {exp_avg_sq_diff}"


def test_resume_fails_on_tampered_rng_or_dataloader():
    """Verifies that the deterministic test would correctly detect any corrupted or non-restored RNG state."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = 42

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        lock_path = base_dir / "protocol" / "STAGE-A1-PREEXECUTION-LOCK.json"
        create_dummy_lock_file(lock_path)
        ckpt_path = base_dir / "ckpt_epoch1.pt"

        trainer_a = MockStageA1Trainer(seed=seed, base_dir=base_dir, device=device, lock_path=lock_path)
        metrics_a_ep1, step_a_ep1 = trainer_a.train_epoch(epoch=1, global_step=0)
        trainer_a.save_checkpoint(
            filepath=ckpt_path,
            epoch=1,
            global_step=step_a_ep1,
            best_val_loss=metrics_a_ep1["train_loss_seq"],
            patience_counter=0
        )
        del trainer_a

        # Load checkpoint but tamper with train_generator
        trainer_b = MockStageA1Trainer(seed=seed, base_dir=base_dir, device=device, lock_path=lock_path)
        trainer_b.load_checkpoint(ckpt_path)
        # Manually alter generator seed
        trainer_b.train_generator.manual_seed(99999)

        # Train Epoch 2
        metrics_b_ep2, _ = trainer_b.train_epoch(epoch=2, global_step=step_a_ep1)

        # Baseline continuous
        trainer_c = MockStageA1Trainer(seed=seed, base_dir=base_dir, device=device, lock_path=lock_path)
        trainer_c.train_epoch(epoch=1, global_step=0)
        metrics_c_ep2, _ = trainer_c.train_epoch(epoch=2, global_step=step_a_ep1)

        # Because generator was tampered, batch order and losses must differ
        diff = abs(metrics_b_ep2["train_loss_seq"] - metrics_c_ep2["train_loss_seq"])
        assert diff > 1e-4, f"Expected tampered generator to cause divergence, but diff was {diff}"
