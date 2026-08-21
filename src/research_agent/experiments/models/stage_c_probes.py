# -*- coding: utf-8 -*-
"""
Stage C: Capacity-Controlled Probes and Baseline Anomaly Detectors
Implements linear/MLP probing heads under label scarcity and comparator baselines (DeepLog, Autoencoder, Isolation Forest).
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, average_precision_score

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

from research_agent.experiments.models.stage_a_pretrain import LogTransformerEncoder
from research_agent.experiments.data.dataset_loader import SessionBagDataset

class LinearProbe(nn.Module):
    """Parameter-budget-controlled linear classifier probe on frozen z in R^d."""
    def __init__(self, in_features: int = 64):
        super().__init__()
        self.fc = nn.Linear(in_features, 1)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.fc(z).squeeze(-1)


class ShallowMLPProbe(nn.Module):
    """Capacity-controlled 2-layer MLP probe."""
    def __init__(self, in_features: int = 64, hidden_dim: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z).squeeze(-1)


class EndToEndSupervisedTransformer(nn.Module):
    """Baseline: End-to-end trained supervised transformer (DeepLog / LogAnomaly style)."""
    def __init__(self, vocab_size: int, d_model: int = 64, nhead: int = 4, num_layers: int = 2):
        super().__init__()
        self.backbone = LogTransformerEncoder(vocab_size=vocab_size, d_model=d_model, nhead=nhead, num_layers=num_layers)
        self.head = nn.Linear(d_model, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.backbone.forward_pooled(x)
        return self.head(z).squeeze(-1)


class SequenceAutoencoder(nn.Module):
    """Baseline: Unsupervised reconstruction autoencoder."""
    def __init__(self, vocab_size: int, d_model: int = 64, latent_dim: int = 16):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.encoder = nn.GRU(d_model, latent_dim, batch_first=True)
        self.decoder = nn.GRU(latent_dim, d_model, batch_first=True)
        self.output_head = nn.Linear(d_model, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(x)
        _, h_n = self.encoder(emb)
        # Repeat latent vector across sequence
        seq_len = x.size(1)
        rep_latent = h_n.permute(1, 0, 2).repeat(1, seq_len, 1)
        dec_out, _ = self.decoder(rep_latent)
        logits = self.output_head(dec_out)
        return logits

    def compute_anomaly_scores(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            logits = self.forward(x)
            loss_fn = nn.CrossEntropyLoss(reduction="none", ignore_index=0)
            token_loss = loss_fn(logits.view(-1, logits.size(-1)), x.view(-1)).view(x.size(0), x.size(1))
            mask = (x != 0).float()
            scores = (token_loss * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
            return scores


def extract_frozen_embeddings(backbone: LogTransformerEncoder, dataset: SessionBagDataset, batch_size: int = 128, device: str = "cpu") -> Tuple[torch.Tensor, torch.Tensor]:
    """Extracts fixed representations z in R^d for all items in dataset."""
    backbone.eval()
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    all_z = []
    all_y = []
    with torch.no_grad():
        for x, y, _ in loader:
            x = x.to(device)
            z = backbone.forward_pooled(x)
            all_z.append(z.cpu())
            all_y.append(y)
    return torch.cat(all_z, dim=0), torch.cat(all_y, dim=0)


def train_probe_on_subset(
    train_z: torch.Tensor,
    train_y: torch.Tensor,
    label_fraction: float = 1.0,
    epochs: int = 15,
    lr: float = 5e-3,
    device: str = "cpu",
    seed: int = 42
) -> LinearProbe:
    """Trains linear probe on a subset of labeled representations (e.g. 1%, 5%, 10%, 100%)."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    n_samples = len(train_z)
    n_sub = max(10, int(n_samples * label_fraction))
    perm = torch.randperm(n_samples)[:n_sub]
    
    sub_z = train_z[perm].to(device)
    sub_y = train_y[perm].to(device)

    probe = LinearProbe(in_features=train_z.size(-1)).to(device)
    optimizer = torch.optim.AdamW(probe.parameters(), lr=lr, weight_decay=1e-3)
    
    pos_c = int(sub_y.sum().item())
    neg_c = len(sub_y) - pos_c
    pos_w = torch.tensor([neg_c / max(1, pos_c)], dtype=torch.float32).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_w)

    for _ in range(epochs):
        probe.train()
        optimizer.zero_grad()
        logits = probe(sub_z)
        loss = criterion(logits, sub_y)
        loss.backward()
        optimizer.step()

    return probe
