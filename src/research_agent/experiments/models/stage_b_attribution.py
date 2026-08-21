# -*- coding: utf-8 -*-
"""
Stage B: Weak Attribution Engine (MIL Gated Attention Mechanism)
Learns bag-level anomaly detection and event-level attribution weights without instance-level supervision.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

from research_agent.experiments.models.stage_a_pretrain import LogTransformerEncoder
from research_agent.experiments.data.dataset_loader import SessionBagDataset

class GatedAttentionMIL(nn.Module):
    """
    Gated Attention Multiple Instance Learning (Ilse et al., ICML 2018).
    Takes instance hidden representations h_k and computes instance attention weights a_k.
    """
    def __init__(self, in_features: int = 64, hidden_dim: int = 32):
        super().__init__()
        self.in_features = in_features
        self.hidden_dim = hidden_dim

        self.attention_v = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.Tanh()
        )
        self.attention_u = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.Sigmoid()
        )
        self.attention_w = nn.Linear(hidden_dim, 1)

        self.classifier = nn.Sequential(
            nn.Linear(in_features, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 1)
        )

    def forward(self, h: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        h: [batch_size, seq_len, in_features]
        mask: [batch_size, seq_len] bool (True for padding/ignore)
        Returns:
            logits: [batch_size, 1]
            attention_weights: [batch_size, seq_len]
        """
        v = self.attention_v(h)  # [batch_size, seq_len, hidden_dim]
        u = self.attention_u(h)  # [batch_size, seq_len, hidden_dim]
        gated = v * u            # [batch_size, seq_len, hidden_dim]
        
        a_raw = self.attention_w(gated).squeeze(-1)  # [batch_size, seq_len]
        
        if mask is not None:
            a_raw = a_raw.masked_fill(mask, -1e9)
            
        a_weights = F.softmax(a_raw, dim=-1)  # [batch_size, seq_len]
        
        # Bag representation: weighted sum
        z_bag = torch.bmm(a_weights.unsqueeze(1), h).squeeze(1)  # [batch_size, in_features]
        
        logits = self.classifier(z_bag).squeeze(-1)  # [batch_size]
        return logits, a_weights


class StageBWeakAttributionModel(nn.Module):
    """
    End-to-end Stage B pipeline combining Frozen Stage A Backbone with Gated Attention MIL.
    """
    def __init__(self, backbone: LogTransformerEncoder, hidden_dim: int = 32):
        super().__init__()
        self.backbone = backbone
        # Freeze backbone parameters
        for p in self.backbone.parameters():
            p.requires_grad = False
            
        self.mil = GatedAttentionMIL(in_features=backbone.d_model, hidden_dim=hidden_dim)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        with torch.no_grad():
            h = self.backbone.forward_features(x)
        mask = (x == 0)
        logits, a_weights = self.mil(h, mask=mask)
        return logits, a_weights


def train_stage_b_engine(
    stage_a_checkpoint_path: Path,
    train_data_path: Path,
    val_data_path: Path,
    output_checkpoint_path: Path,
    epochs: int = 8,
    batch_size: int = 64,
    lr: float = 2e-3,
    entropy_weight: float = 1e-3,
    device: str = "cpu",
    seed: int = 42
) -> Dict[str, Any]:
    """
    Trains Stage B Weak Attribution MIL on Train split session bags.
    Evaluates attribution metrics and bag classification on Val split.
    """
    torch.manual_seed(seed)
    output_checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Load Frozen Stage A Backbone
    ckpt = torch.load(stage_a_checkpoint_path, map_location="cpu", weights_only=False)
    vocab_size = ckpt["vocab_size"]
    d_model = ckpt.get("d_model", 64)
    
    backbone = LogTransformerEncoder(vocab_size=vocab_size, d_model=d_model, nhead=4, num_layers=2)
    backbone.load_state_dict(ckpt["model_state_dict"])
    backbone.eval()

    model = StageBWeakAttributionModel(backbone=backbone, hidden_dim=32).to(device)

    # 2. Load Datasets
    tr_data = torch.load(train_data_path, map_location="cpu", weights_only=False)
    val_data = torch.load(val_data_path, map_location="cpu", weights_only=False)

    tr_dataset = SessionBagDataset(tr_data["sequences"], tr_data["labels"], tr_data.get("session_ids"), max_len=100)
    val_dataset = SessionBagDataset(val_data["sequences"], val_data["labels"], val_data.get("session_ids"), max_len=100)

    tr_loader = DataLoader(tr_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    optimizer = torch.optim.AdamW(model.mil.parameters(), lr=lr, weight_decay=1e-4)
    
    # Compute positive class weight for imbalanced data
    pos_count = sum(tr_data["labels"])
    neg_count = len(tr_data["labels"]) - pos_count
    ratio = neg_count / max(1, pos_count)
    pos_weight = torch.tensor([min(20.0, max(1.0, ratio))]).to(device)
    bce_loss = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    start_time = time.time()
    best_val_f1 = 0.0

    print(f"[STAGE B] Training MIL Weak Attribution on {len(tr_dataset)} train bags ({pos_count} positive)...")

    for epoch in range(1, epochs + 1):
        model.mil.train()
        total_loss = 0.0
        batches = 0

        for x, y, _ in tr_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            
            logits, a_weights = model(x)
            cls_loss = bce_loss(logits, y)
            
            # Entropy regularization: prevent uniform attention spread
            eps = 1e-8
            entropy = -(a_weights * torch.log(a_weights + eps)).sum(dim=-1).mean()
            loss = cls_loss + entropy_weight * entropy
            
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            batches += 1

        # Validation loop
        model.mil.eval()
        val_preds, val_targets = [], []
        with torch.no_grad():
            for x, y, _ in val_loader:
                x, y = x.to(device), y.to(device)
                logits, _ = model(x)
                probs = torch.sigmoid(logits)
                val_preds.extend((probs > 0.5).long().cpu().tolist())
                val_targets.extend(y.long().cpu().tolist())

        from sklearn.metrics import f1_score, precision_score, recall_score
        val_f1 = f1_score(val_targets, val_preds, zero_division=0)
        val_prec = precision_score(val_targets, val_preds, zero_division=0)
        val_rec = recall_score(val_targets, val_preds, zero_division=0)

        print(f"  [Stage B Epoch {epoch}/{epochs}] Loss: {total_loss/batches:.4f} | Val Prec: {val_prec:.3f}, Rec: {val_rec:.3f}, F1: {val_f1:.3f}")

    elapsed = time.time() - start_time
    print(f"[STAGE B] Completed in {elapsed:.2f}s. Saving attribution model...")

    torch.save({
        "mil_state_dict": model.mil.state_dict(),
        "stage_a_checkpoint": str(stage_a_checkpoint_path),
        "hidden_dim": 32,
        "val_f1": val_f1,
        "training_time_sec": elapsed,
        "seed": seed
    }, output_checkpoint_path)

    return {
        "status": "STAGE_B_TRAINED",
        "checkpoint_path": str(output_checkpoint_path),
        "val_f1": round(val_f1, 4),
        "val_precision": round(val_prec, 4),
        "val_recall": round(val_rec, 4),
        "training_time_sec": round(elapsed, 2)
    }
