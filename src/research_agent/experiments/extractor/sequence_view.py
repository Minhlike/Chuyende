# -*- coding: utf-8 -*-
"""
Sequence View Extractor: Transformer Semantic-Sequential Backbone
Implements Chapter 2 Frozen Specification (Section 2.1 & Bang 2.1):
  - Contextual Transformer Backbone for Sequential Log Encodings
  - Three Explicit Self-Supervised Learning (SSL) Heads:
      1. L_MEP: Masked Event Prediction (strictly over masked positions M_MEP)
      2. L_MPP: Masked Security Parameter Prediction (strictly over masked positions M_MPP on privacy-transformed parameters)
      3. L_time: Relative Adjacent Temporal Gap Prediction on concatenated pairs [h_i ; h_i+1] targeting log(1 + delta_t_i,i+1) with Smooth L1 loss
  - Zero raw private string reconstruction targets.
"""

import math
from typing import Dict, Any, List, Optional, Tuple, Set
import torch
import torch.nn as nn
import torch.nn.functional as F

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1), :]

class SequenceViewExtractor(nn.Module):
    """
    Self-Supervised Transformer Backbone with 3 Explicit SSL Heads (L_MEP, L_MPP, L_time).
    """
    def __init__(
        self,
        event_vocab_size: int,
        param_vocab_size: int = 30,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        dim_feedforward: int = 128,
        dropout: float = 0.1,
        max_len: int = 200,
        projection_dim: int = 64
    ):
        super().__init__()
        self.d_model = d_model
        self.event_vocab_size = event_vocab_size
        self.param_vocab_size = param_vocab_size

        self.event_embedding = nn.Embedding(event_vocab_size, d_model, padding_idx=0)
        self.pos_encoder = PositionalEncoding(d_model, max_len=max_len)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # 1. L_MEP: Masked Event Prediction Head
        self.mep_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.LayerNorm(d_model),
            nn.Linear(d_model, event_vocab_size)
        )
        
        # 2. L_MPP: Masked Security Parameter Prediction Head (Categorical privacy-safe parameters)
        self.mpp_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.LayerNorm(d_model),
            nn.Linear(d_model, param_vocab_size)
        )

        # 3. L_time: Relative Adjacent Temporal Gap Prediction Head on Pair [h_i ; h_i+1]
        self.time_pair_head = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.GELU(),
            nn.LayerNorm(d_model),
            nn.Linear(d_model, 1)
        )

        # Latent Representation Projection Head for z^(seq)
        self.projection_head = nn.Sequential(
            nn.Linear(d_model, projection_dim),
            nn.LayerNorm(projection_dim)
        )

    def forward_features(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        src = self.event_embedding(x) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        if mask is None:
            mask = (x == 0)
        out = self.transformer(src, src_key_padding_mask=mask)
        return out

    def forward_pool(self, x: torch.Tensor) -> torch.Tensor:
        padding_mask = (x == 0)
        features = self.forward_features(x, mask=padding_mask)
        
        mask_expanded = (~padding_mask).unsqueeze(-1).float()
        sum_feats = (features * mask_expanded).sum(dim=1)
        lens = mask_expanded.sum(dim=1).clamp(min=1.0)
        pooled = sum_feats / lens
        
        z_seq = self.projection_head(pooled)
        return z_seq

    def compute_sequence_ssl_losses(
        self,
        masked_events: torch.Tensor,
        true_event_targets: torch.Tensor,
        mep_mask: Optional[torch.Tensor] = None,
        param_targets: Optional[torch.Tensor] = None,
        mpp_mask: Optional[torch.Tensor] = None,
        true_adjacent_time_gaps: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Computes the 3 Chapter 2 Sequence SSL Losses:
          1. L_MEP over mep_mask
          2. L_MPP over mpp_mask
          3. L_time over adjacent pairs [h_i ; h_i+1] targeting log(1 + delta_t_i,i+1) with Smooth L1
        """
        padding_mask = (masked_events == 0)
        features = self.forward_features(masked_events, mask=padding_mask)
        batch_size, seq_len, d_model = features.shape

        losses = {}

        # 1. L_MEP: Masked Event Prediction
        mep_logits = self.mep_head(features)
        if mep_mask is None:
            mep_mask = (true_event_targets != 0)
        
        if mep_mask.any():
            l_mep = F.cross_entropy(mep_logits[mep_mask], true_event_targets[mep_mask])
        else:
            l_mep = torch.tensor(0.0, device=masked_events.device, requires_grad=True)
        losses["L_MEP"] = l_mep

        # 2. L_MPP: Masked Parameter Prediction
        if param_targets is not None:
            mpp_logits = self.mpp_head(features)
            if mpp_mask is None:
                mpp_mask = (param_targets != 0)
            if mpp_mask.any():
                l_mpp = F.cross_entropy(mpp_logits[mpp_mask], param_targets[mpp_mask])
            else:
                l_mpp = torch.tensor(0.0, device=masked_events.device, requires_grad=True)
            losses["L_MPP"] = l_mpp

        # 3. L_time: Adjacent Pair [h_i ; h_i+1] targeting log(1 + delta_t) with Smooth L1
        if true_adjacent_time_gaps is not None and seq_len > 1:
            h_i = features[:, :-1, :]       # [B, L-1, D]
            h_next = features[:, 1:, :]     # [B, L-1, D]
            pair_feat = torch.cat([h_i, h_next], dim=-1)  # [B, L-1, 2D]
            pred_log_gaps = self.time_pair_head(pair_feat).squeeze(-1)  # [B, L-1]

            valid_pairs = (~padding_mask[:, :-1]) & (~padding_mask[:, 1:])
            if valid_pairs.any():
                gaps = true_adjacent_time_gaps[:, :seq_len - 1]
                target_log = torch.log1p(torch.clamp(gaps, min=0.0))
                l_time = F.smooth_l1_loss(pred_log_gaps[valid_pairs], target_log[valid_pairs])
            else:
                l_time = torch.tensor(0.0, device=masked_events.device, requires_grad=True)
            losses["L_time"] = l_time

        return losses
