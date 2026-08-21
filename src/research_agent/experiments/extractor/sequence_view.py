# -*- coding: utf-8 -*-
"""
Sequence View Extractor: Transformer Semantic-Sequential Backbone
Extracts contextual event sequence embeddings z^(seq) using self-supervised Masked Language Modeling (MLM).
"""

import math
import torch
import torch.nn as nn
from typing import Tuple, Optional

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
    Self-supervised Transformer Backbone for Sequential Log Encodings.
    """
    def __init__(
        self,
        vocab_size: int,
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
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_encoder = PositionalEncoding(d_model, max_len=max_len)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Self-Supervised MLM Head
        self.mlm_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.LayerNorm(d_model),
            nn.Linear(d_model, vocab_size)
        )
        
        # Latent Representation Projection Head for z^(seq)
        self.projection_head = nn.Sequential(
            nn.Linear(d_model, projection_dim),
            nn.LayerNorm(projection_dim)
        )

    def forward_features(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Computes contextual token embeddings."""
        src = self.embedding(x) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        if mask is None:
            mask = (x == 0)
        out = self.transformer(src, src_key_padding_mask=mask)
        return out

    def forward_pool(self, x: torch.Tensor) -> torch.Tensor:
        """Computes pooled sequence representation z^(seq)."""
        padding_mask = (x == 0)
        features = self.forward_features(x, mask=padding_mask)
        
        # Masked average pooling
        mask_expanded = (~padding_mask).unsqueeze(-1).float()
        sum_feats = (features * mask_expanded).sum(dim=1)
        lens = mask_expanded.sum(dim=1).clamp(min=1.0)
        pooled = sum_feats / lens
        
        z_seq = self.projection_head(pooled)
        return z_seq

    def forward_mlm(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass predicting masked token logits."""
        features = self.forward_features(x, mask=mask)
        return self.mlm_head(features)
