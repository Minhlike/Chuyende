# -*- coding: utf-8 -*-
"""
Multi-View Extractor & Alignment Engine
Implements Chapter 2 Multi-View Representation Contract:
  - Sequence View Extractor (Transformer)
  - Graph View Extractor (Temporal Relational GNN)
  - Cross-View Projection & Correspondence Alignment
  - VICReg Anti-Collapse Regularization (Invariance, Variance, Covariance)
  - Gated Fusion Mechanism z_mv
Supports 4 modes required for canonical H2 testing:
  1. "sequence_only"
  2. "graph_only"
  3. "unaligned"
  4. "aligned"
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple, Optional

from research_agent.experiments.extractor.sequence_view import SequenceViewExtractor
from research_agent.experiments.extractor.graph_view import GraphViewExtractor

class VICRegLoss(nn.Module):
    """
    Variance-Invariance-Covariance Regularization Loss for Multi-View Latent Alignment.
    Prevents dimensional and informational representation collapse without negative pairs.
    """
    def __init__(self, sim_coeff: float = 25.0, var_coeff: float = 25.0, cov_coeff: float = 1.0, gamma: float = 1.0):
        super().__init__()
        self.sim_coeff = sim_coeff
        self.var_coeff = var_coeff
        self.cov_coeff = cov_coeff
        self.gamma = gamma

    def forward(self, z_seq: torch.Tensor, z_graph: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, float]]:
        # 1. Invariance / Similarity Loss (MSE)
        sim_loss = F.mse_loss(z_seq, z_graph)

        # 2. Variance Loss (Anti-Collapse)
        std_seq = torch.sqrt(z_seq.var(dim=0) + 1e-04)
        std_graph = torch.sqrt(z_graph.var(dim=0) + 1e-04)
        var_loss = torch.mean(F.relu(self.gamma - std_seq)) + torch.mean(F.relu(self.gamma - std_graph))

        # 3. Covariance Loss (Decorrelation)
        N, D = z_seq.size()
        z_seq_centered = z_seq - z_seq.mean(dim=0)
        z_graph_centered = z_graph - z_graph.mean(dim=0)
        
        cov_seq = (z_seq_centered.T @ z_seq_centered) / (N - 1)
        cov_graph = (z_graph_centered.T @ z_graph_centered) / (N - 1)
        
        # Off-diagonal elements
        diag = torch.eye(D, device=z_seq.device).bool()
        cov_loss = (cov_seq[~diag].pow(2).sum() / D) + (cov_graph[~diag].pow(2).sum() / D)

        total_loss = self.sim_coeff * sim_loss + self.var_coeff * var_loss + self.cov_coeff * cov_loss
        
        metrics = {
            "sim_loss": float(sim_loss.item()),
            "var_loss": float(var_loss.item()),
            "cov_loss": float(cov_loss.item()),
            "mean_std_seq": float(std_seq.mean().item()),
            "mean_std_graph": float(std_graph.mean().item())
        }
        return total_loss, metrics

class GatedMultiViewFusion(nn.Module):
    """
    Gated Dynamic Fusion mechanism:
    alpha = sigmoid(W_gate [z^(seq); z^(graph)])
    z_mv = alpha * z^(seq) + (1 - alpha) * z^(graph)
    """
    def __init__(self, embed_dim: int):
        super().__init__()
        self.gate_net = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim),
            nn.Sigmoid()
        )

    def forward(self, z_seq: torch.Tensor, z_graph: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        concat = torch.cat([z_seq, z_graph], dim=-1)
        alpha = self.gate_net(concat)
        z_mv = alpha * z_seq + (1.0 - alpha) * z_graph
        return z_mv, alpha

class MultiViewRepresentationModel(nn.Module):
    """
    Complete Chapter 2 Multi-View Architecture supporting all test modes.
    """
    def __init__(
        self,
        seq_vocab_size: int,
        graph_vocab_size: int = 100,
        embed_dim: int = 64,
        mode: str = "aligned"
    ):
        super().__init__()
        valid_modes = ["sequence_only", "graph_only", "unaligned", "aligned"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode {mode}. Must be one of {valid_modes}")
        self.mode = mode
        self.embed_dim = embed_dim

        self.seq_extractor = SequenceViewExtractor(vocab_size=seq_vocab_size, projection_dim=embed_dim)
        self.graph_extractor = GraphViewExtractor(node_vocab_size=graph_vocab_size, out_dim=embed_dim)
        
        self.vicreg = VICRegLoss()
        self.fusion = GatedMultiViewFusion(embed_dim=embed_dim)
        
        # Linear projection for unaligned concatenation
        self.unaligned_proj = nn.Linear(embed_dim * 2, embed_dim)

    def extract_representation(
        self,
        seq_inputs: torch.Tensor,
        node_ids: Optional[torch.Tensor] = None,
        edge_index: Optional[torch.Tensor] = None,
        edge_type: Optional[torch.Tensor] = None,
        batch_index: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Extracts frozen latent representation z under the active evaluation mode.
        """
        if self.mode == "sequence_only":
            return self.seq_extractor.forward_pool(seq_inputs)
        
        if self.mode == "graph_only":
            if node_ids is None or edge_index is None or edge_type is None:
                raise ValueError("Graph inputs required for graph_only mode")
            return self.graph_extractor(node_ids, edge_index, edge_type, batch_index)
        
        # Multi-view modes require both views
        z_seq = self.seq_extractor.forward_pool(seq_inputs)
        if node_ids is not None and edge_index is not None and edge_type is not None:
            z_graph = self.graph_extractor(node_ids, edge_index, edge_type, batch_index)
        else:
            # Fallback zero-graph when graph view is missing
            z_graph = torch.zeros_like(z_seq)

        if self.mode == "unaligned":
            # Simple concatenation without VICReg anti-collapse alignment
            concat = torch.cat([z_seq, z_graph], dim=-1)
            return self.unaligned_proj(concat)
        
        elif self.mode == "aligned":
            # Aligned representation via Gated Fusion
            z_mv, _ = self.fusion(z_seq, z_graph)
            return z_mv

        return z_seq
