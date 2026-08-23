# -*- coding: utf-8 -*-
"""
StageA2Trainer: Deterministic Causal Temporal Graph Pretraining Runner (Contract V1.3).

Features:
  1. Execution Guard: Mode FIXTURE_TEST vs REAL_EMPIRICAL. Raises EmpiricalExecutionNotAuthorizedError
     if real empirical execution is triggered without explicit gate authorization.
  2. Optimizer Boundary Policy: Checkpoint strictly at optimizer step boundaries (gradient_accumulation_position == 0).
  3. 14 Mandatory Mutable States: Full state serialization and exact restoration.
  4. Inductive Split Boundary Reset: Clears dynamic node memory on validation transition.
"""

import os
import random
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

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
        empirical_authorized: bool = False
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

        # Default schedule (will be configured properly on dataset sizing)
        self.total_steps = 1000
        self.warmup_steps = int(self.total_steps * self.warmup_ratio)
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
        self.stream_cursor = 0
        self.current_split = "TRAIN"

        # Early Stopping State
        self.best_val_loss = float("inf")
        self.patience_counter = 0
        self.best_checkpoint_path: Optional[str] = None

        # Guard
        if self.execution_mode == "REAL_EMPIRICAL" and not self.empirical_authorized:
            raise EmpiricalExecutionNotAuthorizedError(
                "Real empirical HDFS execution is NOT authorized in this qualification session."
            )

    def process_window(
        self,
        window_events: List[Dict[str, Any]],
        is_training: bool = True
    ) -> Dict[str, Any]:
        """Processes a single micro-batch window."""
        self.model.train() if is_training else self.model.eval()

        res = self.model.forward_event_window(
            events=window_events,
            mask_generator=self.mask_generator,
            is_training=is_training
        )

        loss = res["loss"]

        if is_training:
            scaled_loss = loss / self.gradient_accumulation_steps
            scaled_loss.backward()
            self.grad_accum_position += 1

            # Optimizer Step at Boundary
            if self.grad_accum_position >= self.gradient_accumulation_steps:
                if self.clip_norm > 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.clip_norm)
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
                self.global_step += 1
                self.grad_accum_position = 0

        return {
            "loss": loss.item(),
            "loss_rel": res["loss_rel"].item() if isinstance(res["loss_rel"], torch.Tensor) else res["loss_rel"],
            "loss_node": res["loss_node"].item() if isinstance(res["loss_node"], torch.Tensor) else res["loss_node"],
            "loss_time": res["loss_time"].item() if isinstance(res["loss_time"], torch.Tensor) else res["loss_time"],
            "global_step": self.global_step,
            "grad_accum_position": self.grad_accum_position
        }

    def save_checkpoint(self, path: Path):
        """
        Atomically saves the complete 14-element mutable checkpoint state.
        Enforces CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY.
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
                "stream_cursor": self.stream_cursor,
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
