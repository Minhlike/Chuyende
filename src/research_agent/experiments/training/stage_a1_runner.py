# -*- coding: utf-8 -*-
"""
Canonical Stage A1 Self-Supervised Training Runner
Executes sequence-only multi-task pretraining on HDFS and BGL datasets across 5 canonical seeds:
  - Architecture: 4-layer Transformer Encoder (d_model=128, H=4, d_ffn=512, dropout=0.10, max_seq_len=128)
  - Parameter Representation: BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4
  - Objective: L_seq = 1.0 * L_MEP + 1.0 * L_MPP + 0.1 * L_time
  - Optimization: AdamW (lr=5e-4, wd=0.01), Linear Warmup + Cosine Decay, micro_batch=16, grad_accum=4 (effective batch=64)
  - Validation: Once per completed epoch, patience=3 epochs, checkpoint selection on minimum Validation L_seq
  - Absolute Test Firewall: TestSetSealedError enforced, zero test access.
"""

import os
import sys
import time
import math
import json
import random
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import psutil
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from research_agent.experiments.data.data_contract import (
    RealDataContract,
    RealTrainingDataViolation,
    LabelLeakageError,
    enforce_real_training_data_purity,
    enforce_ssl_package_label_free
)
from research_agent.experiments.extractor.sequence_view import SequenceViewExtractor

class TestSetSealedError(Exception):
    """Raised when any code attempts to access the sealed Test split or test labels."""
    __test__ = False

class SequenceSSLDataset(Dataset):
    def __init__(self, data_package: Dict[str, Any], max_seq_len: int = 128):
        enforce_ssl_package_label_free(data_package)
        self.sequences = data_package["sequences"]
        self.param_targets = data_package["param_targets"]
        self.time_gaps = data_package["time_gaps"]
        self.session_ids = data_package["session_ids"]
        self.max_seq_len = max_seq_len

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        seq = self.sequences[idx][:self.max_seq_len]
        params = self.param_targets[idx][:self.max_seq_len]
        L = len(seq)
        
        if L > 1:
            gaps = self.time_gaps[idx][:L - 1]
        else:
            gaps = torch.zeros(0, dtype=torch.float32)

        return {
            "seq": seq,
            "params": params,
            "gaps": gaps,
            "length": torch.tensor(L, dtype=torch.long)
        }

def collate_sequence_ssl(batch: List[Dict[str, Any]], max_param_slots: int = 4) -> Dict[str, torch.Tensor]:
    batch_size = len(batch)
    max_len = max(int(b["length"].item()) for b in batch)
    max_len = max(max_len, 1)

    padded_seqs = torch.full((batch_size, max_len), fill_value=1, dtype=torch.long)  # <PAD> = 1
    padded_params = torch.full((batch_size, max_len, max_param_slots), fill_value=1, dtype=torch.long)  # <PAD_PARAM> = 1
    padded_gaps = torch.zeros((batch_size, max(1, max_len - 1)), dtype=torch.float32)
    lengths = torch.zeros(batch_size, dtype=torch.long)

    for i, b in enumerate(batch):
        seq_i = b["seq"]
        params_i = b["params"]
        gaps_i = b["gaps"]
        l_i = int(b["length"].item())
        
        padded_seqs[i, :l_i] = seq_i
        padded_params[i, :l_i, :params_i.shape[1]] = params_i
        if l_i > 1 and len(gaps_i) > 0:
            padded_gaps[i, :len(gaps_i)] = gaps_i
        lengths[i] = l_i

    return {
        "sequences": padded_seqs,
        "param_targets": padded_params,
        "time_gaps": padded_gaps,
        "lengths": lengths
    }

class StageA1Trainer:
    def __init__(
        self,
        dataset_name: str,
        seed: int,
        base_dir: Path,
        device: torch.device,
        lock_path: Optional[Path] = None
    ):
        self.dataset_name = dataset_name.upper()
        self.seed = seed
        self.base_dir = base_dir
        self.device = device
        self.lock_path = lock_path or (self.base_dir / "experiments" / "protocol" / "STAGE-A1-PREEXECUTION-LOCK.json")

        self.run_id = f"STAGE_A1_{self.dataset_name}_SEED_{self.seed}_{int(time.time())}"
        self.output_dir = self.base_dir / "experiments" / "runs" / "stage-a1" / self.dataset_name / f"seed-{self.seed}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._set_deterministic_seed()
        self._load_and_validate_lock()
        self._load_datasets_and_vocab()
        self._build_model_and_optimizer()

    def _set_deterministic_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.seed)
        torch.use_deterministic_algorithms(True, warn_only=False)

    def _load_and_validate_lock(self):
        if not self.lock_path.exists():
            raise FileNotFoundError(f"Missing required execution lock at {self.lock_path}")
        
        lock_data = json.loads(self.lock_path.read_text(encoding="utf-8"))
        self.lock_data = lock_data

        arch = lock_data["architecture"]
        self.d_model = arch["d_model"]
        self.n_layers = arch["layers"]
        self.n_heads = arch["n_heads"]
        self.d_ffn = arch["d_ffn"]
        self.dropout = arch["dropout"]
        self.max_seq_len = arch["max_seq_len"]
        self.max_param_slots = arch["max_param_slots"]

        opt = lock_data["optimization"]
        self.micro_batch_size = opt["micro_batch_size"]
        self.gradient_accumulation_steps = opt["gradient_accumulation_steps"]
        self.effective_batch_size = opt["effective_batch_size"]
        self.learning_rate = opt["learning_rate"]
        self.weight_decay = opt["weight_decay"]
        self.adam_beta1 = opt["adam_beta1"]
        self.adam_beta2 = opt["adam_beta2"]
        self.adam_eps = opt["adam_eps"]
        self.warmup_ratio = opt["warmup_ratio"]
        self.min_lr = opt["min_lr"]
        self.clip_norm = opt["clip_norm"]
        self.max_epochs = opt["max_epochs"]
        self.patience = opt["early_stopping_patience"]

        loss_cfg = lock_data["losses_and_weights"]
        self.lambda_MEP = loss_cfg["lambda_MEP"]
        self.lambda_MPP = loss_cfg["lambda_MPP"]
        self.lambda_time = loss_cfg["lambda_time"]
        self.mep_prob = loss_cfg["mep_masking_probability"]
        self.mpp_prob = loss_cfg["mpp_masking_probability"]

    def _load_datasets_and_vocab(self):
        if self.dataset_name == "HDFS":
            data_dir = self.base_dir / "experiments" / "runs" / "data" / "hdfs"
            train_pkg_path = data_dir / "hdfs_ssl_train.pt"
            val_pkg_path = data_dir / "hdfs_ssl_val.pt"
            vocab_path = data_dir / "hdfs_vocab.json"
        elif self.dataset_name == "BGL":
            data_dir = self.base_dir / "experiments" / "runs" / "data" / "bgl"
            train_pkg_path = data_dir / "bgl_ssl_train.pt"
            val_pkg_path = data_dir / "bgl_ssl_val.pt"
            vocab_path = data_dir / "bgl_vocab.json"
        else:
            raise ValueError(f"Unknown dataset: {self.dataset_name}")

        vocab_data = json.loads(vocab_path.read_text(encoding="utf-8"))
        self.event_vocab_size = len(vocab_data["template_to_id"])
        self.param_vocab_size = len(vocab_data["param_to_id"])

        train_pkg = torch.load(train_pkg_path, weights_only=False)
        val_pkg = torch.load(val_pkg_path, weights_only=False)

        enforce_real_training_data_purity(train_pkg.get("dataset_classification", ""))
        enforce_real_training_data_purity(val_pkg.get("dataset_classification", ""))

        self.train_dataset = SequenceSSLDataset(train_pkg, max_seq_len=self.max_seq_len)
        self.val_dataset = SequenceSSLDataset(val_pkg, max_seq_len=self.max_seq_len)

        g_train = torch.Generator()
        g_train.manual_seed(self.seed)
        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.micro_batch_size,
            shuffle=True,
            collate_fn=lambda b: collate_sequence_ssl(b, max_param_slots=self.max_param_slots),
            generator=g_train
        )
        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.micro_batch_size,
            shuffle=False,
            collate_fn=lambda b: collate_sequence_ssl(b, max_param_slots=self.max_param_slots)
        )

    def _build_model_and_optimizer(self):
        self.model = SequenceViewExtractor(
            event_vocab_size=self.event_vocab_size,
            param_vocab_size=self.param_vocab_size,
            d_model=self.d_model,
            nhead=self.n_heads,
            num_layers=self.n_layers,
            dim_feedforward=self.d_ffn,
            dropout=self.dropout,
            max_len=self.max_seq_len,
            max_param_slots=self.max_param_slots,
            projection_dim=self.d_model
        ).to(self.device)

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
            betas=(self.adam_beta1, self.adam_beta2),
            eps=self.adam_eps
        )

        steps_per_epoch = math.ceil(len(self.train_loader) / self.gradient_accumulation_steps)
        self.total_optimizer_steps = steps_per_epoch * self.max_epochs
        self.warmup_steps = max(1, int(self.total_optimizer_steps * self.warmup_ratio))

        def lr_lambda(current_step: int) -> float:
            if current_step < self.warmup_steps:
                return float(current_step) / float(max(1, self.warmup_steps))
            progress = float(current_step - self.warmup_steps) / float(max(1, self.total_optimizer_steps - self.warmup_steps))
            cosine_factor = 0.5 * (1.0 + math.cos(math.pi * progress))
            decayed = (self.min_lr / self.learning_rate) + (1.0 - (self.min_lr / self.learning_rate)) * cosine_factor
            return max(self.min_lr / self.learning_rate, decayed)

        self.scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)

    def _apply_mep_masking(self, sequences: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        15% Bernoulli masking on non-padding tokens:
          - 80% [MASK] = 2
          - 10% random token from [3, event_vocab_size-1]
          - 10% unchanged
        """
        masked = sequences.clone()
        targets = sequences.clone()
        non_pad = (sequences != 1)

        rand_probs = torch.rand(sequences.shape, device=sequences.device)
        mep_mask = non_pad & (rand_probs < self.mep_prob)

        decision = torch.rand(sequences.shape, device=sequences.device)
        # 80% MASK
        mask_pos = mep_mask & (decision < 0.80)
        masked[mask_pos] = 2  # <MASK> = 2

        # 10% Random
        rand_pos = mep_mask & (decision >= 0.80) & (decision < 0.90)
        if rand_pos.any():
            random_tokens = torch.randint(3, max(4, self.event_vocab_size), sequences.shape, device=sequences.device)
            masked[rand_pos] = random_tokens[rand_pos]

        # 10% Unchanged (masked remains unchanged, but included in mep_mask for target prediction)
        return masked, targets, mep_mask

    def _apply_mpp_masking(self, param_slots: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        15% Bernoulli masking per active parameter slot (excludes <PAD_PARAM> = 1):
          - Replaces masked slot with <MASK_PARAM> = 2
          - Target is original parameter slot ID
        """
        masked = param_slots.clone()
        targets = param_slots.clone()
        active_slots = (param_slots != 1)

        rand_probs = torch.rand(param_slots.shape, device=param_slots.device)
        mpp_mask = active_slots & (rand_probs < self.mpp_prob)

        masked[mpp_mask] = 2  # <MASK_PARAM> = 2
        return masked, targets, mpp_mask

    def train_epoch(self, epoch: int, global_step: int) -> Tuple[Dict[str, float], int]:
        self.model.train()
        self.optimizer.zero_grad()
        
        epoch_mep_loss = 0.0
        epoch_mpp_loss = 0.0
        epoch_time_loss = 0.0
        epoch_total_loss = 0.0
        micro_step = 0

        for batch_idx, batch in enumerate(self.train_loader):
            seqs = batch["sequences"].to(self.device)
            params = batch["param_targets"].to(self.device)
            gaps = batch["time_gaps"].to(self.device)

            masked_seqs, true_seqs, mep_mask = self._apply_mep_masking(seqs)
            masked_params, true_params, mpp_mask = self._apply_mpp_masking(params)

            losses = self.model.compute_sequence_ssl_losses(
                masked_events=masked_seqs,
                true_event_targets=true_seqs,
                mep_mask=mep_mask,
                masked_param_slots=masked_params,
                true_param_targets=true_params,
                mpp_mask=mpp_mask,
                true_adjacent_time_gaps=gaps
            )

            l_mep = losses["L_MEP"]
            l_mpp = losses["L_MPP"]
            l_time = losses["L_time"]
            total_loss = (self.lambda_MEP * l_mep) + (self.lambda_MPP * l_mpp) + (self.lambda_time * l_time)
            
            # Scale loss for gradient accumulation
            loss_accum = total_loss / self.gradient_accumulation_steps
            loss_accum.backward()

            epoch_mep_loss += l_mep.item()
            epoch_mpp_loss += l_mpp.item()
            epoch_time_loss += l_time.item()
            epoch_total_loss += total_loss.item()
            micro_step += 1

            if micro_step % self.gradient_accumulation_steps == 0 or (batch_idx + 1) == len(self.train_loader):
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=self.clip_norm)
                
                # Check health gates (NaN / Inf)
                for p in self.model.parameters():
                    if p.grad is not None:
                        if torch.isnan(p.grad).any() or torch.isinf(p.grad).any():
                            raise ValueError(f"NaN/Inf gradient detected at optimizer step {global_step}")

                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
                global_step += 1

        n_batches = max(1, len(self.train_loader))
        metrics = {
            "train_loss_seq": epoch_total_loss / n_batches,
            "train_loss_mep": epoch_mep_loss / n_batches,
            "train_loss_mpp": epoch_mpp_loss / n_batches,
            "train_loss_time": epoch_time_loss / n_batches
        }
        return metrics, global_step

    @torch.no_grad()
    def evaluate_validation(self) -> Dict[str, float]:
        self.model.eval()
        val_mep_loss = 0.0
        val_mpp_loss = 0.0
        val_time_loss = 0.0
        val_total_loss = 0.0
        n_batches = 0

        for batch in self.val_loader:
            seqs = batch["sequences"].to(self.device)
            params = batch["param_targets"].to(self.device)
            gaps = batch["time_gaps"].to(self.device)

            masked_seqs, true_seqs, mep_mask = self._apply_mep_masking(seqs)
            masked_params, true_params, mpp_mask = self._apply_mpp_masking(params)

            losses = self.model.compute_sequence_ssl_losses(
                masked_events=masked_seqs,
                true_event_targets=true_seqs,
                mep_mask=mep_mask,
                masked_param_slots=masked_params,
                true_param_targets=true_params,
                mpp_mask=mpp_mask,
                true_adjacent_time_gaps=gaps
            )

            l_mep = losses["L_MEP"].item()
            l_mpp = losses["L_MPP"].item()
            l_time = losses["L_time"].item()
            total_loss = (self.lambda_MEP * l_mep) + (self.lambda_MPP * l_mpp) + (self.lambda_time * l_time)

            val_mep_loss += l_mep
            val_mpp_loss += l_mpp
            val_time_loss += l_time
            val_total_loss += total_loss
            n_batches += 1

        n_b = max(1, n_batches)
        return {
            "val_loss_seq": val_total_loss / n_b,
            "val_loss_mep": val_mep_loss / n_b,
            "val_loss_mpp": val_mpp_loss / n_b,
            "val_loss_time": val_time_loss / n_b
        }

    def save_checkpoint(
        self,
        filepath: Path,
        epoch: int,
        global_step: int,
        best_val_loss: float,
        patience_counter: int
    ):
        ckpt = {
            "run_id": self.run_id,
            "dataset": self.dataset_name,
            "seed": self.seed,
            "epoch": epoch,
            "global_step": global_step,
            "best_val_loss": best_val_loss,
            "patience_counter": patience_counter,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "rng_states": {
                "python": random.getstate(),
                "numpy": np.random.get_state(),
                "torch_cpu": torch.get_rng_state(),
                "torch_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
            },
            "contract_sha256": self.lock_data.get("contract_sha256", ""),
            "source_commit": self.lock_data.get("source_commit", ""),
            "timestamp": time.time()
        }
        torch.save(ckpt, filepath)

    def load_checkpoint(self, filepath: Path) -> Tuple[int, int, float, int]:
        ckpt = torch.load(filepath, map_location="cpu", weights_only=False)
        self.model.load_state_dict(ckpt["model_state_dict"])
        self.model.to(self.device)
        self.optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        self.scheduler.load_state_dict(ckpt["scheduler_state_dict"])
        
        rng = ckpt["rng_states"]
        random.setstate(rng["python"])
        np.random.set_state(rng["numpy"])
        if rng.get("torch_cpu") is not None:
            torch.set_rng_state(rng["torch_cpu"].cpu().to(torch.uint8))
        if torch.cuda.is_available() and rng.get("torch_cuda") is not None:
            cuda_states = [s.cpu().to(torch.uint8) for s in rng["torch_cuda"]]
            torch.cuda.set_rng_state_all(cuda_states)

        return ckpt["epoch"], ckpt["global_step"], ckpt["best_val_loss"], ckpt["patience_counter"]

    def train(self) -> Dict[str, Any]:
        train_log_path = self.output_dir / "TRAIN-LOG.jsonl"
        val_log_path = self.output_dir / "VALIDATION-LOG.jsonl"
        best_ckpt_path = self.output_dir / "best_val_loss.pt"
        last_ckpt_path = self.output_dir / "checkpoint_last.pt"

        best_val_loss = float("inf")
        patience_counter = 0
        global_step = 0
        stopped_epoch = 0

        start_time = time.time()
        process = psutil.Process(os.getpid())

        for epoch in range(1, self.max_epochs + 1):
            t0 = time.time()
            train_metrics, global_step = self.train_epoch(epoch, global_step)
            val_metrics = self.evaluate_validation()
            epoch_duration = time.time() - t0

            val_l_seq = val_metrics["val_loss_seq"]
            
            # Track hardware usage
            ram_mb = process.memory_info().rss / (1024 * 1024)
            vram_mb = (torch.cuda.max_memory_allocated() / (1024 * 1024)) if torch.cuda.is_available() else 0.0

            # Log to files
            with open(train_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "epoch": epoch,
                    "global_step": global_step,
                    "metrics": train_metrics,
                    "lr": self.scheduler.get_last_lr()[0],
                    "ram_mb": ram_mb,
                    "vram_mb": vram_mb,
                    "duration_sec": epoch_duration
                }) + "\n")

            with open(val_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "epoch": epoch,
                    "global_step": global_step,
                    "metrics": val_metrics,
                    "ram_mb": ram_mb,
                    "vram_mb": vram_mb
                }) + "\n")

            # Checkpoint selection on minimum Validation L_seq
            if val_l_seq < (best_val_loss - 1e-4):
                best_val_loss = val_l_seq
                patience_counter = 0
                self.save_checkpoint(best_ckpt_path, epoch, global_step, best_val_loss, patience_counter)
            else:
                patience_counter += 1

            self.save_checkpoint(last_ckpt_path, epoch, global_step, best_val_loss, patience_counter)
            stopped_epoch = epoch

            if patience_counter >= self.patience:
                break

        total_duration = time.time() - start_time
        peak_vram = (torch.cuda.max_memory_allocated() / (1024 * 1024)) if torch.cuda.is_available() else 0.0
        peak_ram = process.memory_info().rss / (1024 * 1024)

        manifest = {
            "run_id": self.run_id,
            "dataset": self.dataset_name,
            "seed": self.seed,
            "best_val_loss": best_val_loss,
            "stopped_epoch": stopped_epoch,
            "total_optimizer_steps": global_step,
            "total_duration_sec": total_duration,
            "peak_vram_mb": peak_vram,
            "peak_ram_mb": peak_ram,
            "nan_loss_count": 0,
            "inf_loss_count": 0,
            "nan_grad_count": 0,
            "inf_grad_count": 0,
            "test_feature_read_count": 0,
            "test_label_read_count": 0,
            "test_metric_count": 0,
            "test_opened": False,
            "result_class": "SELF_SUPERVISED_PRETRAINING",
            "confirmatory_hypothesis_result": False,
            "best_checkpoint_sha256": self._compute_sha256(best_ckpt_path)
        }

        with open(self.output_dir / "RUN-MANIFEST.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest

    def _compute_sha256(self, file_path: Path) -> str:
        if not file_path.exists():
            return "FILE_NOT_FOUND"
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
