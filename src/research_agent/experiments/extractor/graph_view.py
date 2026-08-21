# -*- coding: utf-8 -*-
"""
Graph View Extractor: Temporal & Relational Provenance Graph Backbone
Extracts relational topological embeddings z^(graph) from provenance interaction graphs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, List, Optional, Tuple

class RelationalGraphConvLayer(nn.Module):
    """
    Relational Graph Convolution layer supporting directed heterogeneous edge types:
    (READ, WRITE, EXECUTE, CONNECT, FORK, LOAD).
    """
    def __init__(self, in_dim: int, out_dim: int, num_relations: int = 6):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.num_relations = num_relations
        self.rel_weights = nn.Parameter(torch.Tensor(num_relations, in_dim, out_dim))
        self.self_loop = nn.Linear(in_dim, out_dim, bias=False)
        self.bias = nn.Parameter(torch.zeros(out_dim))
        
        nn.init.xavier_uniform_(self.rel_weights)

    def forward(
        self,
        node_features: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor
    ) -> torch.Tensor:
        """
        node_features: [N, in_dim]
        edge_index: [2, E] (src, dst)
        edge_type: [E] (relation id)
        """
        N = node_features.size(0)
        out = self.self_loop(node_features)
        
        if edge_index.numel() == 0 or edge_index.size(1) == 0:
            return out + self.bias

        src, dst = edge_index[0], edge_index[1]
        
        # Message computation per relation
        for r in range(self.num_relations):
            mask = (edge_type == r)
            if not mask.any():
                continue
            r_src = src[mask]
            r_dst = dst[mask]
            
            # Linear transform for relation r
            w_r = self.rel_weights[r]  # [in_dim, out_dim]
            msg = torch.matmul(node_features[r_src], w_r)  # [E_r, out_dim]
            
            # Scatter add to destination nodes
            out.index_add_(0, r_dst, msg)

        return F.relu(out + self.bias)

class GraphViewExtractor(nn.Module):
    """
    Temporal & Relational Provenance GNN Extractor for Graph View.
    Produces pooled graph representation z^(graph).
    """
    def __init__(
        self,
        node_vocab_size: int = 100,
        node_dim: int = 64,
        hidden_dim: int = 64,
        out_dim: int = 64,
        num_relations: int = 6,
        num_layers: int = 2
    ):
        super().__init__()
        self.node_embedding = nn.Embedding(node_vocab_size, node_dim, padding_idx=0)
        self.layers = nn.ModuleList([
            RelationalGraphConvLayer(node_dim if i == 0 else hidden_dim, hidden_dim, num_relations=num_relations)
            for i in range(num_layers)
        ])
        
        self.graph_proj = nn.Sequential(
            nn.Linear(hidden_dim, out_dim),
            nn.LayerNorm(out_dim)
        )
        
        # Self-supervised link prediction head
        self.link_pred_head = nn.Bilinear(hidden_dim, hidden_dim, 1)

    def forward(
        self,
        node_ids: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
        batch_index: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        node_ids: [N]
        edge_index: [2, E]
        edge_type: [E]
        batch_index: [N] indicating graph membership for each node
        Returns: z^(graph) of shape [Batch, out_dim]
        """
        h = self.node_embedding(node_ids)
        for layer in self.layers:
            h = layer(h, edge_index, edge_type)

        # Graph Readout / Pooling
        if batch_index is None:
            # Single graph pooling
            z_g = h.mean(dim=0, keepdim=True)
        else:
            num_graphs = int(batch_index.max().item()) + 1
            z_g = torch.zeros(num_graphs, h.size(1), device=h.device)
            counts = torch.zeros(num_graphs, 1, device=h.device)
            
            z_g.index_add_(0, batch_index, h)
            counts.index_add_(0, batch_index, torch.ones_like(batch_index.unsqueeze(-1), dtype=torch.float))
            z_g = z_g / counts.clamp(min=1.0)

        return self.graph_proj(z_g)
