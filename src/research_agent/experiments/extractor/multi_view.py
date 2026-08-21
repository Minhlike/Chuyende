# -*- coding: utf-8 -*-
"""
Multi-View Extractor & Optimization Engine
Implements Chapter 2 Frozen Multi-View Representation Contract (Section 2.4 & Bang 2.4):
  - True Per-Sample Correspondence: Each sample i has its own sequence input and graph event list
  - Zero canonical z_graph.repeat(batch_size, 1) broadcast
  - Real Batch VICReg Anti-Collapse Optimization over paired representations [z_seq, z_graph]
  - Explicit Availability Masks & Learned Missing-View Token per sample
  - Gated Fusion Mechanism: z_mv = alpha * z^(seq) + (1 - alpha) * z^(graph)
  - Supports 4 canonical H2 modes: "sequence_only", "graph_only", "unaligned", "aligned"
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

from research_agent.experiments.extractor.sequence_view import SequenceViewExtractor
from research_agent.experiments.extractor.graph_view import TemporalGraphViewExtractor

@dataclass
class MultiViewCorrespondence:
    """
    Explicit correspondence metadata contract linking Sequence and Graph view telemetry per sample.
    """
    correspondence_id: str
    time_interval: Tuple[float, float]
    entity_scope: str
    seq_view_id: str
    graph_view_id: str
    overlap_ratio: float
    seq_available: bool = True
    graph_available: bool = True

    def is_valid_for_alignment(self, min_overlap: float = 0.5) -> bool:
        return self.seq_available and self.graph_available and (self.overlap_ratio >= min_overlap)

class VICRegLoss(nn.Module):
    """
    Variance-Invariance-Covariance Regularization Loss for Multi-View Latent Alignment.
    """
    def __init__(self, sim_coeff: float = 25.0, var_coeff: float = 25.0, cov_coeff: float = 1.0, gamma: float = 1.0):
        super().__init__()
        self.sim_coeff = sim_coeff
        self.var_coeff = var_coeff
        self.cov_coeff = cov_coeff
        self.gamma = gamma

    def forward(
        self,
        z_seq: torch.Tensor,
        z_graph: torch.Tensor,
        valid_mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        z_seq: [B, D]
        z_graph: [B, D]
        valid_mask: [B] boolean mask of corresponding & available pairs
        """
        if valid_mask is not None:
            if not valid_mask.any():
                zero_loss = torch.tensor(0.0, device=z_seq.device, requires_grad=True)
                return zero_loss, {"sim_loss": 0.0, "var_loss": 0.0, "cov_loss": 0.0}
            z_seq = z_seq[valid_mask]
            z_graph = z_graph[valid_mask]

        N, D = z_seq.size()
        if N < 2:
            sim_loss = F.mse_loss(z_seq, z_graph)
            return self.sim_coeff * sim_loss, {"sim_loss": float(sim_loss.item()), "var_loss": 0.0, "cov_loss": 0.0}

        # 1. Invariance / Similarity Loss (MSE)
        sim_loss = F.mse_loss(z_seq, z_graph)

        # 2. Variance Loss (Anti-Collapse)
        std_seq = torch.sqrt(z_seq.var(dim=0) + 1e-04)
        std_graph = torch.sqrt(z_graph.var(dim=0) + 1e-04)
        var_loss = torch.mean(F.relu(self.gamma - std_seq)) + torch.mean(F.relu(self.gamma - std_graph))

        # 3. Covariance Loss (Decorrelation)
        z_seq_centered = z_seq - z_seq.mean(dim=0)
        z_graph_centered = z_graph - z_graph.mean(dim=0)
        
        cov_seq = (z_seq_centered.T @ z_seq_centered) / (N - 1)
        cov_graph = (z_graph_centered.T @ z_graph_centered) / (N - 1)
        
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
            nn.GELU(),
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
    Complete Multi-View Architecture connecting Sequence View, Temporal Graph View,
    VICReg Alignment, and Gated Fusion.
    """
    def __init__(
        self,
        seq_vocab_size: int,
        graph_vocab_size: int = 100,
        param_vocab_size: int = 30,
        embed_dim: int = 64,
        mode: str = "aligned",
        align_lambda: float = 1.0
    ):
        super().__init__()
        valid_modes = ["sequence_only", "graph_only", "unaligned", "aligned"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode {mode}. Must be one of {valid_modes}")
        self.mode = mode
        self.embed_dim = embed_dim
        self.align_lambda = align_lambda

        # Extractors
        self.seq_extractor = SequenceViewExtractor(
            event_vocab_size=seq_vocab_size,
            param_vocab_size=param_vocab_size,
            projection_dim=embed_dim
        )
        self.graph_extractor = TemporalGraphViewExtractor(
            node_vocab_size=graph_vocab_size,
            out_dim=embed_dim
        )

        # Cross-View Latent Alignment & Projections
        self.seq_proj_align = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )
        self.graph_proj_align = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, embed_dim)
        )

        self.vicreg = VICRegLoss()
        self.fusion = GatedMultiViewFusion(embed_dim=embed_dim)
        
        # Missing View Learned Fallback Token
        self.missing_graph_token = nn.Parameter(torch.zeros(1, embed_dim))
        nn.init.normal_(self.missing_graph_token, std=0.02)
        
        self.unaligned_proj = nn.Linear(embed_dim * 2, embed_dim)

    def extract_per_sample_graph_embeddings(
        self,
        graph_events_batch: Optional[List[List[Dict[str, Any]]]],
        batch_size: int,
        correspondence_list: Optional[List[MultiViewCorrespondence]],
        device: torch.device
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extracts genuine per-sample graph embeddings for each item in the batch.
        Returns:
            z_graph_batch: [B, embed_dim]
            valid_mask: [B] bool tensor
        """
        z_graph_list = []
        valid_flags = []

        for i in range(batch_size):
            events_i = graph_events_batch[i] if (graph_events_batch and i < len(graph_events_batch)) else None
            corr_i = correspondence_list[i] if (correspondence_list and i < len(correspondence_list)) else None
            
            is_avail = (corr_i is None or corr_i.graph_available) and bool(events_i)
            if is_avail and events_i:
                # Fresh memory or scoped entity state for item i
                z_g_i = self.graph_extractor.forward(events_i, device=device)
                z_graph_list.append(z_g_i.squeeze(0))
                valid_flags.append(corr_i.is_valid_for_alignment() if corr_i else True)
            else:
                # Learned missing-graph token
                z_graph_list.append(self.missing_graph_token.squeeze(0))
                valid_flags.append(False)

        z_graph_batch = torch.stack(z_graph_list, dim=0)
        valid_mask = torch.tensor(valid_flags, dtype=torch.bool, device=device)
        return z_graph_batch, valid_mask

    def extract_representation(
        self,
        seq_inputs: torch.Tensor,
        graph_events_batch: Optional[List[List[Dict[str, Any]]]] = None,
        correspondence_list: Optional[List[MultiViewCorrespondence]] = None,
        device: Optional[torch.device] = None
    ) -> torch.Tensor:
        """
        Extracts frozen latent representation z under active evaluation mode.
        """
        if device is None:
            device = seq_inputs.device

        batch_size = seq_inputs.size(0)

        if self.mode == "sequence_only":
            return self.seq_extractor.forward_pool(seq_inputs)
        
        z_graph_batch, _ = self.extract_per_sample_graph_embeddings(
            graph_events_batch=graph_events_batch,
            batch_size=batch_size,
            correspondence_list=correspondence_list,
            device=device
        )

        if self.mode == "graph_only":
            return z_graph_batch

        z_seq = self.seq_extractor.forward_pool(seq_inputs)

        if self.mode == "unaligned":
            concat = torch.cat([z_seq, z_graph_batch], dim=-1)
            return self.unaligned_proj(concat)
        
        elif self.mode == "aligned":
            z_mv, _ = self.fusion(z_seq, z_graph_batch)
            return z_mv

        return z_seq

    def compute_stage_a_loss(
        self,
        seq_inputs: torch.Tensor,
        true_event_targets: torch.Tensor,
        mep_mask: Optional[torch.Tensor] = None,
        param_targets: Optional[torch.Tensor] = None,
        mpp_mask: Optional[torch.Tensor] = None,
        time_gap_targets: Optional[torch.Tensor] = None,
        graph_events_batch: Optional[List[List[Dict[str, Any]]]] = None,
        correspondence_list: Optional[List[MultiViewCorrespondence]] = None,
        device: Optional[torch.device] = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Computes Stage A objective over real per-sample paired representations:
          L_StageA = L_seq_ssl + L_graph_ssl + lambda_align * L_VICReg
        """
        if device is None:
            device = seq_inputs.device

        batch_size = seq_inputs.size(0)

        # 1. Sequence SSL Losses
        seq_losses = self.seq_extractor.compute_sequence_ssl_losses(
            masked_events=seq_inputs,
            true_event_targets=true_event_targets,
            mep_mask=mep_mask,
            param_targets=param_targets,
            mpp_mask=mpp_mask,
            true_adjacent_time_gaps=time_gap_targets
        )
        l_seq_total = sum(seq_losses.values())

        # 2. Graph SSL Losses and Per-Sample Extraction
        z_graph_list = []
        graph_loss_list = []
        valid_align_flags = []

        for i in range(batch_size):
            events_i = graph_events_batch[i] if (graph_events_batch and i < len(graph_events_batch)) else None
            corr_i = correspondence_list[i] if (correspondence_list and i < len(correspondence_list)) else None

            is_avail = (corr_i is None or corr_i.graph_available) and bool(events_i)
            if is_avail and events_i:
                z_g_i, ssl_g_i = self.graph_extractor.process_causal_events(events_i, device=device)
                z_graph_list.append(z_g_i.squeeze(0))
                if ssl_g_i:
                    graph_loss_list.append(sum(ssl_g_i.values()))
                valid_align_flags.append(corr_i.is_valid_for_alignment() if corr_i else True)
            else:
                z_graph_list.append(self.missing_graph_token.squeeze(0))
                valid_align_flags.append(False)

        z_graph_batch = torch.stack(z_graph_list, dim=0)
        valid_mask = torch.tensor(valid_align_flags, dtype=torch.bool, device=device)

        if graph_loss_list:
            l_graph_total = torch.stack(graph_loss_list).mean()
        else:
            l_graph_total = torch.tensor(0.0, device=device, requires_grad=True)

        # 3. Real Batch VICReg Alignment Loss
        z_seq_pool = self.seq_extractor.forward_pool(seq_inputs)
        p_seq = self.seq_proj_align(z_seq_pool)
        p_graph = self.graph_proj_align(z_graph_batch)

        l_vicreg, vicreg_metrics = self.vicreg(p_seq, p_graph, valid_mask=valid_mask)

        # 4. Total Combined Stage A Loss
        total_loss = l_seq_total + l_graph_total + self.align_lambda * l_vicreg

        metrics_summary = {
            "loss_stage_a_total": float(total_loss.item()),
            "loss_seq_ssl": float(l_seq_total.item()),
            "loss_graph_ssl": float(l_graph_total.item()),
            "loss_vicreg_align": float(l_vicreg.item())
        }
        for k, v in seq_losses.items():
            metrics_summary[f"seq_{k}"] = float(v.item())
        for k, v in vicreg_metrics.items():
            metrics_summary[f"vicreg_{k}"] = float(v)

        return total_loss, metrics_summary
