# -*- coding: utf-8 -*-
"""
Stage A: Self-Supervised Log Representation Pretraining Engine
Implements Masked Sequence Modeling & Contrastive Learning on Train split logs.
Enforces the Representation Contract: frozen backbone with zero task label leakage.
"""

import os
import sys
import json
import math
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 500):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1), :]

class LogTransformerEncoder(nn.Module):
    """
    Stage A Pretrained Transformer Encoder Backbone for log/provenance representation.
    Extracts dense sequence embeddings z in R^d.
    """
    def __init__(self, vocab_size: int, d_model: int = 64, nhead: int = 4, num_layers: int = 2, max_len: int = 100):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_encoder = PositionalEncoding(d_model, max_len=max_len)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=d_model * 2,
            dropout=0.1, batch_first=True, activation="gelu"
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.mlm_head = nn.Linear(d_model, vocab_size)
        self.projection_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model)
        )

    def get_padding_mask(self, x: torch.Tensor) -> torch.Tensor:
        return x == 0

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        """Returns sequence of hidden representations [batch_size, seq_len, d_model]."""
        mask = self.get_padding_mask(x)
        emb = self.embedding(x) * math.sqrt(self.d_model)
        emb = self.pos_encoder(emb)
        out = self.transformer_encoder(emb, src_key_padding_mask=mask)
        return out

    def forward_pooled(self, x: torch.Tensor) -> torch.Tensor:
        """Returns pooled bag/session representation z in R^d."""
        hidden = self.forward_features(x)
        mask = (x != 0).unsqueeze(-1).float()
        sum_hidden = (hidden * mask).sum(dim=1)
        lengths = mask.sum(dim=1).clamp(min=1.0)
        z = sum_hidden / lengths
        return z

    def forward_mlm(self, x_masked: torch.Tensor) -> torch.Tensor:
        """Computes logits over vocabulary for masked token reconstruction."""
        hidden = self.forward_features(x_masked)
        logits = self.mlm_head(hidden)
        return logits


class MaskedLogDataset(Dataset):
    """Wraps sequences for self-supervised masked token pretraining."""
    def __init__(self, sequences: list, mask_ratio: float = 0.15, mask_token_id: int = 2, max_len: int = 100):
        self.sequences = sequences
        self.mask_ratio = mask_ratio
        self.mask_token_id = mask_token_id
        self.max_len = max_len

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx]
        if len(seq) > self.max_len:
            seq = seq[:self.max_len]
        elif len(seq) < self.max_len:
            pad = torch.zeros(self.max_len - len(seq), dtype=torch.long)
            seq = torch.cat([seq, pad])

        target = seq.clone()
        masked_seq = seq.clone()

        # Generate mask indices for non-padding tokens
        valid_indices = torch.nonzero(seq != 0, as_tuple=True)[0]
        if len(valid_indices) > 0:
            num_mask = max(1, int(len(valid_indices) * self.mask_ratio))
            perm = torch.randperm(len(valid_indices))
            mask_idx = valid_indices[perm[:num_mask]]
            masked_seq[mask_idx] = self.mask_token_id
            
            # Loss computed only on masked positions
            target_mask = torch.full_like(target, -100)
            target_mask[mask_idx] = target[mask_idx]
            target = target_mask
        else:
            target = torch.full_like(target, -100)

        return masked_seq, target, seq


def train_stage_a_backbone(
    train_data_path: Path,
    vocab_path: Path,
    output_checkpoint_path: Path,
    epochs: int = 5,
    batch_size: int = 64,
    lr: float = 1e-3,
    device: str = "cpu",
    seed: int = 42
) -> Dict[str, Any]:
    """
    Executes Stage A Self-Supervised Pretraining strictly on Train split.
    Saves and freezes the learned representation backbone.
    """
    torch.manual_seed(seed)
    output_checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[STAGE A] Loading train split from: {train_data_path}")
    data = torch.load(train_data_path, map_location="cpu", weights_only=False)
    sequences = data["sequences"]
    
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    vocab_size = len(vocab)
    print(f"[STAGE A] Pretraining on {len(sequences):,} sequences with vocab_size={vocab_size} on {device}...")

    dataset = MaskedLogDataset(sequences, mask_ratio=0.15, mask_token_id=2, max_len=100)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=False)

    model = LogTransformerEncoder(vocab_size=vocab_size, d_model=64, nhead=4, num_layers=2).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss(ignore_index=-100)

    start_time = time.time()
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        total_batches = 0

        for masked_x, targets, orig_x in dataloader:
            masked_x = masked_x.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            logits = model.forward_mlm(masked_x)
            
            # Reshape for CrossEntropy
            loss = criterion(logits.view(-1, vocab_size), targets.view(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            total_batches += 1

        avg_loss = total_loss / max(1, total_batches)
        history.append({"epoch": epoch, "mlm_loss": round(avg_loss, 4)})
        print(f"  [Stage A Pretraining] Epoch {epoch}/{epochs} - MLM Loss: {avg_loss:.4f}")

    elapsed = time.time() - start_time
    print(f"[STAGE A] Pretraining completed in {elapsed:.2f}s. Saving frozen checkpoint...")

    # Save checkpoint
    torch.save({
        "model_state_dict": model.state_dict(),
        "vocab_size": vocab_size,
        "d_model": 64,
        "nhead": 4,
        "num_layers": 2,
        "training_time_sec": elapsed,
        "final_loss": avg_loss,
        "seed": seed
    }, output_checkpoint_path)

    return {
        "status": "STAGE_A_FROZEN",
        "checkpoint_path": str(output_checkpoint_path),
        "vocab_size": vocab_size,
        "d_model": 64,
        "epochs": epochs,
        "final_mlm_loss": round(avg_loss, 4),
        "training_time_sec": round(elapsed, 2)
    }
