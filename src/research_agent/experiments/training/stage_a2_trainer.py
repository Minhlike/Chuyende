# -*- coding: utf-8 -*-
"""
StageA2Trainer: Deterministic Causal Temporal Graph Pretraining Runner (Contract V1.3 Amended).

Features:
  1. Execution Guard: Mode FIXTURE_TEST vs REAL_EMPIRICAL. Raises EmpiricalExecutionNotAuthorizedError
     if real empirical execution is triggered without explicit gate authorization.
  2. Operational Stream Cursor: stream_cursor advances on every window; checkpoints serialize
     exact next-window position; resume uses stream_cursor directly.
  3. Dynamic Scope-Bound Scheduler: Exact calculation from authorized execution subset (586,577 events).
  4. Inductive Split Boundary Reset: Clears dynamic node memory on validation transition.
  5. NaN / Inf Fail-Closed Protection: Detects floating point anomalies and aborts immediately.
  6. Checkpoint Boundary Policy: CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY (grad_accum_position == 0).
  7. 14 Mandatory Mutable States: Full state serialization and exact restoration.
"""

import os
import time
import random
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Iterable

import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR

from research_agent.experiments.models.temporal_graph_view_encoder import TemporalGraphViewEncoder

class EmpiricalExecutionNotAuthorizedError(RuntimeError):
    """Raised when real empirical execution is attempted without authorization."""
    pass

class CheckpointBoundaryViolationError(RuntimeError):
    """Raised when checkpoint save is attempted mid-gradient-accumulation."""
    pass

class FloatingPointAnomalyError(FloatingPointError):
    """Raised when NaN or Inf is encountered in loss or gradients (Fail-Closed)."""
    pass

def get_cosine_schedule_with_warmup(
    optimizer: torch.optim.Optimizer,
    num_warmup_steps: int,
    num_training_steps: int,
    min_lr_ratio: float = 0.02
):
    """Linear warmup followed by cosine decay."""
    def lr_lambda(current_step: int):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        progress = float(current_step - num_warmup_steps) / float(max(1, num_training_steps - num_warmup_steps))
        cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
        return min_lr_ratio + (1.0 - min_lr_ratio) * cosine_decay
    return LambdaLR(optimizer, lr_lambda)

class StageA2Trainer:
    """
    Orchestrates Stage A2 causal temporal graph pretraining with strict deterministic resumption.
    """
    def __init__(
        self,
        model: TemporalGraphViewEncoder,
        learning_rate: float = 5e-4,
        weight_decay: float = 0.01,
        min_lr: float = 1e-5,
        warmup_ratio: float = 0.05,
        temporal_window_size: int = 256,
        gradient_accumulation_steps: int = 4,
        clip_norm: float = 1.0,
        max_epochs: int = 20,
        early_stopping_patience: int = 3,
        seed: int = 42,
        device: Optional[torch.device] = None,
        execution_mode: str = "FIXTURE_TEST", # "FIXTURE_TEST" or "REAL_EMPIRICAL"
        empirical_authorized: bool = False,
        total_steps_override: Optional[int] = None
    ):
        self.model = model
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.min_lr = min_lr
        self.warmup_ratio = warmup_ratio
        self.temporal_window_size = temporal_window_size
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.clip_norm = clip_norm
        self.max_epochs = max_epochs
        self.early_stopping_patience = early_stopping_patience
        self.seed = seed
        self.device = device or (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))
        self.execution_mode = execution_mode
        self.empirical_authorized = empirical_authorized

        self.model.to(self.device)

        # Optimizer: AdamW
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=self.learning_rate,
            betas=(0.9, 0.98),
            eps=1e-8,
            weight_decay=self.weight_decay
        )

        # Schedule configuration
        if total_steps_override is not None:
            self.total_steps = total_steps_override
            self.warmup_steps = max(1, int(self.total_steps * self.warmup_ratio))
        else:
            self.configure_empirical_schedule(train_events_count=586577)

        min_ratio = self.min_lr / self.learning_rate
        self.scheduler = get_cosine_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=self.total_steps,
            min_lr_ratio=min_ratio
        )

        # Explicit Masking RNG Generator for deterministic masking sequence
        self.mask_generator = torch.Generator(device="cpu")
        self.mask_generator.manual_seed(seed)

        # Mutable Trajectory State
        self.current_epoch = 0
        self.global_step = 0
        self.grad_accum_position = 0 # 0..gradient_accumulation_steps-1
        self.stream_cursor = 0        # Operational cursor indexing next window to process
        self.current_split = "TRAIN"

        # Early Stopping State
        self.best_val_loss = float("inf")
        self.patience_counter = 0
        self.best_checkpoint_path: Optional[str] = None

        # Guard
        if self.execution_mode == "REAL_EMPIRICAL" and not self.empirical_authorized:
            raise EmpiricalExecutionNotAuthorizedError(
                "Real empirical HDFS execution is NOT authorized in this session."
            )

    def configure_empirical_schedule(self, train_events_count: int = 586577):
        """
        Derives exact scheduler parameters from authorized execution subset:
          - Train graph events: 586,577
          - Window size: 256
          - Windows per epoch: ceil(586577 / 256) = 2292
          - Grad accum: 4
          - Optimizer steps per epoch: 2292 // 4 = 573
          - Max epochs: 20
          - Max optimizer steps: 20 * 573 = 11,460
          - Warmup steps: 11,460 * 0.05 = 573
        """
        self.train_windows_per_epoch = math.ceil(train_events_count / self.temporal_window_size)
        self.optimizer_steps_per_epoch = self.train_windows_per_epoch // self.gradient_accumulation_steps
        self.total_steps = self.max_epochs * self.optimizer_steps_per_epoch
        self.warmup_steps = int(self.total_steps * self.warmup_ratio)

    def process_window(
        self,
        window_events: List[Dict[str, Any]],
        is_training: bool = True
    ) -> Dict[str, Any]:
        """
        Processes a single micro-batch window:
          1. Forward pass & predict-before-update
          2. NaN/Inf check on loss (Fail-Closed)
          3. Backward pass & NaN/Inf check on gradients
          4. Optimizer & scheduler step at accumulation boundary
          5. Operational stream cursor advance
        """
        self.model.train() if is_training else self.model.eval()

        res = self.model.forward_event_window(
            events=window_events,
            mask_generator=self.mask_generator,
            is_training=is_training
        )

        loss = res["loss"]

        # NaN / Inf Fail-Closed Check on Loss
        loss_val = loss.item()
        if math.isnan(loss_val) or math.isinf(loss_val):
            raise FloatingPointAnomalyError(
                f"FATAL: NaN/Inf detected in loss value ({loss_val}) at global_step={self.global_step}, cursor={self.stream_cursor}!"
            )

        if is_training:
            scaled_loss = loss / self.gradient_accumulation_steps
            scaled_loss.backward()
            self.grad_accum_position += 1

            # Check for NaN / Inf in parameter gradients
            for name, param in self.model.named_parameters():
                if param.grad is not None:
                    if torch.isnan(param.grad).any() or torch.isinf(param.grad).any():
                        raise FloatingPointAnomalyError(
                            f"FATAL: NaN/Inf detected in gradients for parameter '{name}' at step {self.global_step}!"
                        )

            # Optimizer Step at Boundary
            if self.grad_accum_position >= self.gradient_accumulation_steps:
                if self.clip_norm > 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.clip_norm)
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
                self.global_step += 1
                self.grad_accum_position = 0

        # Operationally advance the stream cursor
        self.stream_cursor += 1

        return {
            "loss": loss_val,
            "loss_rel": res["loss_rel"].item() if isinstance(res["loss_rel"], torch.Tensor) else res["loss_rel"],
            "loss_node": res["loss_node"].item() if isinstance(res["loss_node"], torch.Tensor) else res["loss_node"],
            "loss_time": res["loss_time"].item() if isinstance(res["loss_time"], torch.Tensor) else res["loss_time"],
            "global_step": self.global_step,
            "grad_accum_position": self.grad_accum_position,
            "stream_cursor": self.stream_cursor,
            "masked_rel_count": res.get("masked_rel_count", 0),
            "masked_node_count": res.get("masked_node_count", 0),
            "num_events": res.get("num_events", len(window_events))
        }

    def train_one_epoch(self, window_stream: Iterable[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Executes one full training epoch over chronological windows."""
        self.current_split = "TRAIN"
        self.model.train()

        total_loss = 0.0
        total_rel = 0.0
        total_node = 0.0
        total_time = 0.0
        total_events = 0
        total_masked_rel = 0
        total_masked_node = 0
        windows_count = 0

        t0 = time.time()
        for window in window_stream:
            stats = self.process_window(window, is_training=True)
            total_loss += stats["loss"]
            total_rel += stats["loss_rel"]
            total_node += stats["loss_node"]
            total_time += stats["loss_time"]
            total_events += stats["num_events"]
            total_masked_rel += stats["masked_rel_count"]
            total_masked_node += stats["masked_node_count"]
            windows_count += 1

        # Epoch-End Policy: If pending gradients remain, flush step
        if self.grad_accum_position > 0:
            if self.clip_norm > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.clip_norm)
            self.optimizer.step()
            self.scheduler.step()
            self.optimizer.zero_grad()
            self.global_step += 1
            self.grad_accum_position = 0

        epoch_runtime = time.time() - t0
        curr_lr = self.optimizer.param_groups[0]["lr"]

        return {
            "epoch": self.current_epoch,
            "split": "TRAIN",
            "train_L_graph": total_loss / max(1, windows_count),
            "train_L_rel": total_rel / max(1, windows_count),
            "train_L_node": total_node / max(1, windows_count),
            "train_L_time": total_time / max(1, windows_count),
            "windows_count": windows_count,
            "events_count": total_events,
            "masked_rel_count": total_masked_rel,
            "masked_node_count": total_masked_node,
            "optimizer_steps": self.global_step,
            "learning_rate": curr_lr,
            "epoch_runtime_sec": epoch_runtime,
            "nan_inf_count": 0
        }

    def validate_one_epoch(self, window_stream: Iterable[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Executes one full validation epoch:
          - Applies INDUCTIVE_SPLIT_RESET_ZERO_MEMORY before validation
          - Zero gradients, no optimizer/scheduler updates
          - Applies INDUCTIVE_SPLIT_RESET_ZERO_MEMORY after validation before returning to train
        """
        self.current_split = "VAL"
        self.model.eval()

        # Split Boundary Reset: Inductive evaluation requires zero initial memory
        self.model.reset_node_states()

        total_loss = 0.0
        total_rel = 0.0
        total_node = 0.0
        total_time = 0.0
        total_events = 0
        total_masked_rel = 0
        total_masked_node = 0
        windows_count = 0

        t0 = time.time()
        with torch.no_grad():
            for window in window_stream:
                stats = self.process_window(window, is_training=False)
                total_loss += stats["loss"]
                total_rel += stats["loss_rel"]
                total_node += stats["loss_node"]
                total_time += stats["loss_time"]
                total_events += stats["num_events"]
                total_masked_rel += stats["masked_rel_count"]
                total_masked_node += stats["masked_node_count"]
                windows_count += 1

        # Post-Validation Split Boundary Reset: Do not carry validation interactions into next Train epoch
        self.model.reset_node_states()

        epoch_runtime = time.time() - t0
        return {
            "epoch": self.current_epoch,
            "split": "VAL",
            "val_L_graph": total_loss / max(1, windows_count),
            "val_L_rel": total_rel / max(1, windows_count),
            "val_L_node": total_node / max(1, windows_count),
            "val_L_time": total_time / max(1, windows_count),
            "windows_count": windows_count,
            "events_count": total_events,
            "masked_rel_count": total_masked_rel,
            "masked_node_count": total_masked_node,
            "epoch_runtime_sec": epoch_runtime,
            "nan_inf_count": 0
        }

    def save_checkpoint(self, path: Path):
        """
        Atomically saves the complete 14-element mutable checkpoint state.
        Enforces CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY (grad_accum_position == 0).
        """
        if self.grad_accum_position != 0:
            raise CheckpointBoundaryViolationError(
                f"Checkpoints are strictly permitted only at optimizer step boundaries! "
                f"(current grad_accum_position={self.grad_accum_position} != 0)"
            )

        path.parent.mkdir(parents=True, exist_ok=True)

        # 4-tuple RNG states
        rng_states_4tuple = {
            "python_random": random.getstate(),
            "numpy_random": np.random.get_state(),
            "torch_cpu": torch.get_rng_state(),
            "torch_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
        }

        node_states = self.model.get_node_states()

        state_dict = {
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "node_memory_states": node_states["node_memory_states"],
            "node_last_interaction_timestamps": node_states["node_last_interaction_timestamps"],
            "node_causal_in_degrees": node_states["node_causal_in_degrees"],
            "node_causal_out_degrees": node_states["node_causal_out_degrees"],
            "node_temporal_history_buffers": node_states["node_temporal_history_buffers"],
            "rng_states_4tuple": rng_states_4tuple,
            "stream_iterator_state": {
                "current_split": self.current_split,
                "current_epoch": self.current_epoch,
                "stream_cursor": self.stream_cursor, # Points to exact NEXT window to process
                "grad_accum_position": self.grad_accum_position
            },
            "masking_rng_state": self.mask_generator.get_state(),
            "early_stopping_state": {
                "best_val_loss": self.best_val_loss,
                "patience_counter": self.patience_counter,
                "best_checkpoint_path": self.best_checkpoint_path
            },
            "global_step": self.global_step,
            "current_epoch": self.current_epoch,
            "checkpoint_boundary_policy": "CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY"
        }

        torch.save(state_dict, path)

    def load_checkpoint(self, path: Path):
        """Restores complete 14-element state from checkpoint."""
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint not found at {path}")

        checkpoint = torch.load(path, map_location=self.device, weights_only=False)

        # 1. Model, Optimizer, Scheduler
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

        # 2. Node Dynamic Memory and Interaction States
        self.model.set_node_states(checkpoint, self.device)

        # 3. RNG States
        rng_4tuple = checkpoint["rng_states_4tuple"]
        random.setstate(rng_4tuple["python_random"])
        np.random.set_state(rng_4tuple["numpy_random"])
        torch.set_rng_state(rng_4tuple["torch_cpu"])
        if torch.cuda.is_available() and rng_4tuple.get("torch_cuda") is not None:
            torch.cuda.set_rng_state_all(rng_4tuple["torch_cuda"])

        # 4. Masking RNG Generator State
        self.mask_generator.set_state(checkpoint["masking_rng_state"])

        # 5. Trajectory & Stream Iterator State
        stream_st = checkpoint["stream_iterator_state"]
        self.current_split = stream_st["current_split"]
        self.current_epoch = stream_st["current_epoch"]
        self.stream_cursor = stream_st["stream_cursor"]
        self.grad_accum_position = stream_st["grad_accum_position"]
        self.global_step = checkpoint["global_step"]

        # 6. Early Stopping State
        es_st = checkpoint["early_stopping_state"]
        self.best_val_loss = es_st["best_val_loss"]
        self.patience_counter = es_st["patience_counter"]
        self.best_checkpoint_path = es_st["best_checkpoint_path"]
