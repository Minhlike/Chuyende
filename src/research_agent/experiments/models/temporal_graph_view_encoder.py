# -*- coding: utf-8 -*-
"""
TemporalGraphViewEncoder: Causal Continuous-Time Dynamic Graph Neural Network
for Stage A2 Self-Supervised Pretraining on Event-Entity Logs (Contract V1.3 Amended).

Invariants:
  1. Predict-Before-Update: Auxiliary SSL predictions (L_rel, L_node, L_time) evaluate
     strictly on prior hidden states h(t-) BEFORE memory updates.
  2. Relation Target Firewall: Prediction input [h_v(t-) || h_u(t-) || phi(delta_t)]
     strictly withholds true relation ID and relation embedding. Exactly 8 canonical classes.
  3. Node Target Firewall: Reconstruction head predicts x_v_fixed_priv in R^6 strictly
     from h_v(t-) using Mean Squared Error (MSE), without direct target vector pass-through.
  4. Active Node Type Embeddings: Source and destination node type embeddings actively
     condition the temporal message function Msg().
  5. Causal Degree Targets: Degree features computed at t- prior to edge increment.
  6. Inductive Split Reset: Full dynamic memory and interaction state zeroed on split boundary.
"""

import math
from typing import Dict, Any, List, Optional, Tuple, Set

import torch
import torch.nn as nn
import torch.nn.functional as F

class TimeProjection(nn.Module):
    """Sinusoidal Continuous-Time Projection phi(delta_t) -> R^d_time."""
    def __init__(self, d_time: int = 32):
        super().__init__()
        self.d_time = d_time
        half_dim = d_time // 2
        inv_freq = torch.exp(
            torch.arange(0, half_dim, dtype=torch.float32) * (-math.log(10000.0) / half_dim)
        )
        self.register_buffer("inv_freq", inv_freq)

    def forward(self, delta_t: torch.Tensor) -> torch.Tensor:
        # delta_t: (B, 1) or (B,) or scalar -> return (B, d_time)
        if delta_t.dim() == 0:
            delta_t = delta_t.view(1, 1)
        elif delta_t.dim() == 1:
            delta_t = delta_t.unsqueeze(-1)
        phases = delta_t * self.inv_freq.unsqueeze(0) # (B, half_dim)
        proj = torch.cat([torch.sin(phases), torch.cos(phases)], dim=-1) # (B, d_time)
        return proj

class TemporalGraphViewEncoder(nn.Module):
    """
    Temporal Graph View Encoder using GRUCell dynamic memory, Temporal Multi-Head Attention,
    and multi-task self-supervised auxiliary heads.
    """
    def __init__(
        self,
        d_node: int = 128,
        d_edge: int = 64,
        d_msg: int = 128,
        n_heads: int = 4,
        d_time_proj: int = 32,
        d_rel_emb: int = 32,
        d_type_emb: int = 32,
        dropout: float = 0.10,
        num_canonical_relations: int = 8, # 8 canonical classes (IDs 1..8 -> class indices 0..7)
        num_node_types: int = 4,          # 0: DATA_BLOCK, 1: STORAGE_NODE, 2: MANAGEMENT_SYSTEM, 3: EXECUTION_THREAD
        max_node_history: int = 64,
        lambda_rel: float = 1.0,
        lambda_node: float = 1.0,
        lambda_time: float = 0.1,
        rel_mask_prob: float = 0.15,
        node_mask_prob: float = 0.15
    ):
        super().__init__()
        self.d_node = d_node
        self.d_edge = d_edge
        self.d_msg = d_msg
        self.n_heads = n_heads
        self.d_time_proj = d_time_proj
        self.d_rel_emb = d_rel_emb
        self.d_type_emb = d_type_emb
        self.dropout_p = dropout
        self.num_canonical_relations = num_canonical_relations
        self.num_node_types = num_node_types
        self.max_node_history = max_node_history
        self.lambda_rel = lambda_rel
        self.lambda_node = lambda_node
        self.lambda_time = lambda_time
        self.rel_mask_prob = rel_mask_prob
        self.node_mask_prob = node_mask_prob

        # Embeddings & Projections
        # Relation embedding table has 9 entries (0: UNK/PAD, 1..8: Canonical Relations) for lookup
        self.relation_embedding = nn.Embedding(num_canonical_relations + 1, d_rel_emb)
        self.type_embedding = nn.Embedding(num_node_types, d_type_emb)
        self.edge_proj = nn.Linear(1, d_edge)
        self.time_proj = TimeProjection(d_time_proj)

        # Message Generator: [h_src || h_dst || e_edge || e_rel || e_src_type || e_dst_type || phi(dt)] -> d_msg
        msg_in_dim = d_node + d_node + d_edge + d_rel_emb + d_type_emb + d_type_emb + d_time_proj
        self.msg_mlp = nn.Sequential(
            nn.Linear(msg_in_dim, d_msg),
            nn.LayerNorm(d_msg),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_msg, d_msg)
        )

        # Temporal Multi-Head Self-Attention over History Buffers
        self.history_attn = nn.MultiheadAttention(
            embed_dim=d_msg,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )
        self.norm_history = nn.LayerNorm(d_msg)

        # GRU Dynamic Memory Cell
        self.memory_cell = nn.GRUCell(d_msg, d_node)
        self.norm_memory = nn.LayerNorm(d_node)

        # Auxiliary SSL Prediction Heads (Predict-Before-Update)
        # 1. Relation Classification Head: [h_v(t-) || h_u(t-) || phi(dt)] -> EXACTLY 8 CANONICAL CLASSES
        rel_in_dim = d_node + d_node + d_time_proj
        self.rel_head = nn.Sequential(
            nn.Linear(rel_in_dim, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_canonical_relations)
        )

        # 2. Node Feature Reconstruction Head: h_v(t-) -> 6 (4-dim one-hot type + 2-dim log1p degrees)
        self.node_head = nn.Sequential(
            nn.Linear(d_node, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 6)
        )

        # 3. Continuous Temporal Gap Head: [h_v(t-) || h_u(t-)] -> 1
        time_in_dim = d_node + d_node
        self.time_head = nn.Sequential(
            nn.Linear(time_in_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )

        # Loss Functions: L_rel = CrossEntropy (8 classes), L_node = MSELoss, L_time = SmoothL1Loss
        self.loss_rel_fn = nn.CrossEntropyLoss()
        self.loss_node_fn = nn.MSELoss()
        self.loss_time_fn = nn.SmoothL1Loss(beta=1.0)

        # Mutable Node State Tables (Reset upon split transition)
        self.node_memory: Dict[str, torch.Tensor] = {}
        self.node_last_ts: Dict[str, float] = {}
        self.node_in_degrees: Dict[str, int] = {}
        self.node_out_degrees: Dict[str, int] = {}
        self.node_history_buffers: Dict[str, List[torch.Tensor]] = {}

    def reset_node_states(self):
        """Inductive Split Reset: Clears all dynamic node memory and interaction states."""
        self.node_memory.clear()
        self.node_last_ts.clear()
        self.node_in_degrees.clear()
        self.node_out_degrees.clear()
        self.node_history_buffers.clear()

    def get_node_states(self) -> Dict[str, Any]:
        """Serializes all mutable node state tables for atomic checkpointing."""
        mem_clones = {k: v.detach().cpu().clone() for k, v in self.node_memory.items()}
        hist_clones = {k: [msg.detach().cpu().clone() for msg in msgs] for k, msgs in self.node_history_buffers.items()}
        return {
            "node_memory_states": mem_clones,
            "node_last_interaction_timestamps": dict(self.node_last_ts),
            "node_causal_in_degrees": dict(self.node_in_degrees),
            "node_causal_out_degrees": dict(self.node_out_degrees),
            "node_temporal_history_buffers": hist_clones
        }

    def set_node_states(self, states: Dict[str, Any], device: torch.device):
        """Restores all mutable node state tables from checkpoint."""
        self.node_memory = {k: v.to(device) for k, v in states.get("node_memory_states", {}).items()}
        self.node_last_ts = dict(states.get("node_last_interaction_timestamps", {}))
        self.node_in_degrees = dict(states.get("node_causal_in_degrees", {}))
        self.node_out_degrees = dict(states.get("node_causal_out_degrees", {}))
        self.node_history_buffers = {
            k: [msg.to(device) for msg in msgs]
            for k, msgs in states.get("node_temporal_history_buffers", {}).items()
        }

    def _get_h_prev(self, node_id: str, device: torch.device) -> torch.Tensor:
        """Retrieves h(t-) from dynamic memory table or initializes with zero vector."""
        if node_id not in self.node_memory:
            return torch.zeros(self.d_node, device=device)
        return self.node_memory[node_id]

    def _get_causal_degrees_t_minus(self, node_id: str) -> Tuple[int, int]:
        """Retrieves causal in-degree and out-degree at t-."""
        in_d = self.node_in_degrees.get(node_id, 0)
        out_d = self.node_out_degrees.get(node_id, 0)
        return in_d, out_d

    def _get_temporal_gap_t_minus(self, src: str, dst: str, curr_t: float) -> float:
        """Computes continuous temporal gap delta_t = curr_t - max(last_src, last_dst)."""
        last_src = self.node_last_ts.get(src, None)
        last_dst = self.node_last_ts.get(dst, None)
        if last_src is None and last_dst is None:
            return 0.0
        elif last_src is None:
            last_t = last_dst
        elif last_dst is None:
            last_t = last_src
        else:
            last_t = max(last_src, last_dst)
        return max(0.0, curr_t - last_t)

    def forward_event_window(
        self,
        events: List[Dict[str, Any]],
        mask_generator: Optional[torch.Generator] = None,
        is_training: bool = True
    ) -> Dict[str, Any]:
        """
        Processes a temporal event window sequentially, strictly enforcing:
          1. Predict-Before-Update on h(t-)
          2. Target-leakage firewalls for L_rel and L_node
          3. Causal FIFO history buffers
          4. Active entity type embeddings in Msg()
          5. Post-prediction GRU memory updates
        """
        if not events:
            dummy_zero = torch.tensor(0.0, device=next(self.parameters()).device, requires_grad=True)
            return {
                "loss": dummy_zero,
                "loss_rel": dummy_zero,
                "loss_node": dummy_zero,
                "loss_time": dummy_zero,
                "num_events": 0,
                "masked_rel_count": 0,
                "masked_node_count": 0
            }

        device = next(self.parameters()).device
        loss_rel_list = []
        loss_node_list = []
        loss_time_list = []

        masked_rel_count = 0
        masked_node_count = 0

        for event in events:
            src = event["source_node"]
            dst = event["dest_node"]
            src_type = int(event["source_type"])
            dst_type = int(event["dest_type"])
            rel_id = int(event["relation_id"]) # Canonical relation ID: 1..8
            curr_t = float(event["event_timestamp_utc_exact"])
            size_b = float(event.get("size_bytes", 0.0) or 0.0)

            # NaN / Inf validation on input event
            if math.isnan(curr_t) or math.isinf(curr_t) or math.isnan(size_b) or math.isinf(size_b):
                raise FloatingPointError(
                    f"NaN/Inf detected in event inputs: timestamp={curr_t}, size={size_b}"
                )

            # Map raw relation_id 1..8 -> class index 0..7
            target_class_idx = rel_id - 1
            if not (0 <= target_class_idx < self.num_canonical_relations):
                raise ValueError(
                    f"Invalid relation_id {rel_id}. Expected canonical ID in [1..{self.num_canonical_relations}]."
                )

            # -------------------------------------------------------------
            # STEP 1: PREDICT-BEFORE-UPDATE (Evaluate strictly on h(t-))
            # -------------------------------------------------------------
            h_src_prev = self._get_h_prev(src, device)  # (d_node,)
            h_dst_prev = self._get_h_prev(dst, device)  # (d_node,)

            h_src_2d = h_src_prev.unsqueeze(0)          # (1, d_node)
            h_dst_2d = h_dst_prev.unsqueeze(0)          # (1, d_node)

            # Causal temporal gap at t-
            dt_raw = self._get_temporal_gap_t_minus(src, dst, curr_t)
            dt_log1p_val = math.log1p(dt_raw)
            dt_tensor = torch.tensor([[dt_log1p_val]], dtype=torch.float32, device=device) # (1, 1)
            phi_dt = self.time_proj(dt_tensor)                                             # (1, d_time_proj)

            # Causal degree targets at t-
            in_src_prev, out_src_prev = self._get_causal_degrees_t_minus(src)
            in_dst_prev, out_dst_prev = self._get_causal_degrees_t_minus(dst)

            # Target representations for node reconstruction (MSE)
            x_src_target = torch.zeros(6, dtype=torch.float32, device=device)
            x_src_target[src_type] = 1.0
            x_src_target[4] = math.log1p(in_src_prev)
            x_src_target[5] = math.log1p(out_src_prev)

            x_dst_target = torch.zeros(6, dtype=torch.float32, device=device)
            x_dst_target[dst_type] = 1.0
            x_dst_target[4] = math.log1p(in_dst_prev)
            x_dst_target[5] = math.log1p(out_dst_prev)

            # Decide masking deterministically via RNG generator
            if is_training:
                mask_rel = torch.rand(1, generator=mask_generator).item() < self.rel_mask_prob
                mask_node_src = torch.rand(1, generator=mask_generator).item() < self.node_mask_prob
                mask_node_dst = torch.rand(1, generator=mask_generator).item() < self.node_mask_prob
            else:
                mask_rel = True
                mask_node_src = True
                mask_node_dst = True

            # 1a. Masked Edge Relation Prediction Head (Target withheld from input, 8 output classes)
            rel_in = torch.cat([h_src_2d, h_dst_2d, phi_dt], dim=-1) # (1, rel_in_dim)
            rel_logits = self.rel_head(rel_in)                       # (1, 8)
            if mask_rel:
                target_rel_tensor = torch.tensor([target_class_idx], dtype=torch.long, device=device)
                loss_rel_list.append(self.loss_rel_fn(rel_logits, target_rel_tensor))
                masked_rel_count += 1

            # 1b. Masked Node Feature Reconstruction Head (MSE loss, Target withheld from input)
            if mask_node_src:
                node_src_pred = self.node_head(h_src_2d) # (1, 6)
                loss_node_list.append(self.loss_node_fn(node_src_pred.squeeze(0), x_src_target))
                masked_node_count += 1
            if mask_node_dst:
                node_dst_pred = self.node_head(h_dst_2d) # (1, 6)
                loss_node_list.append(self.loss_node_fn(node_dst_pred.squeeze(0), x_dst_target))
                masked_node_count += 1

            # 1c. Continuous Temporal Gap Prediction Head
            time_in = torch.cat([h_src_2d, h_dst_2d], dim=-1)      # (1, 2*d_node)
            time_pred = F.relu(self.time_head(time_in)).squeeze(0) # (1,)
            loss_time_list.append(self.loss_time_fn(time_pred, dt_tensor.squeeze(0)))

            # -------------------------------------------------------------
            # STEP 2: TEMPORAL MESSAGE PASSING & MEMORY UPDATE (Post-Loss)
            # -------------------------------------------------------------
            size_norm = math.log1p(max(0.0, size_b))
            size_tensor = torch.tensor([[size_norm]], dtype=torch.float32, device=device)
            e_edge = self.edge_proj(size_tensor)                                    # (1, d_edge)
            
            rel_tensor = torch.tensor([rel_id], dtype=torch.long, device=device)
            e_rel = self.relation_embedding(rel_tensor)                             # (1, d_rel_emb)

            src_type_t = torch.tensor([src_type], dtype=torch.long, device=device)
            dst_type_t = torch.tensor([dst_type], dtype=torch.long, device=device)
            e_src_type = self.type_embedding(src_type_t)                            # (1, d_type_emb)
            e_dst_type = self.type_embedding(dst_type_t)                            # (1, d_type_emb)

            # Active condition with entity type embeddings in message generator
            msg_src_in = torch.cat([h_src_2d, h_dst_2d, e_edge, e_rel, e_src_type, e_dst_type, phi_dt], dim=-1)
            msg_dst_in = torch.cat([h_dst_2d, h_src_2d, e_edge, e_rel, e_dst_type, e_src_type, phi_dt], dim=-1)

            raw_m_src = self.msg_mlp(msg_src_in) # (1, d_msg)
            raw_m_dst = self.msg_mlp(msg_dst_in) # (1, d_msg)

            # Historical Attention Aggregation (if buffer non-empty)
            m_src = self._aggregate_history(src, raw_m_src, device) # (1, d_msg)
            m_dst = self._aggregate_history(dst, raw_m_dst, device) # (1, d_msg)

            # GRU Dynamic Memory State Update
            h_src_new = self.norm_memory(self.memory_cell(m_src, h_src_2d)).squeeze(0) # (d_node,)
            h_dst_new = self.norm_memory(self.memory_cell(m_dst, h_dst_2d)).squeeze(0) # (d_node,)

            # Save updated states (carries autograd graph across interactions within this window)
            self.node_memory[src] = h_src_new
            self.node_memory[dst] = h_dst_new
            self.node_last_ts[src] = curr_t
            self.node_last_ts[dst] = curr_t
            self.node_out_degrees[src] = out_src_prev + 1
            self.node_in_degrees[dst] = in_dst_prev + 1

            # Append to FIFO historical interaction buffers
            self._append_history(src, raw_m_src.squeeze(0).detach())
            self._append_history(dst, raw_m_dst.squeeze(0).detach())

        # Truncated BPTT Boundary: Detach memory states across window boundaries
        self.node_memory = {k: v.detach() for k, v in self.node_memory.items()}
        self.node_history_buffers = {k: [msg.detach() for msg in msgs] for k, msgs in self.node_history_buffers.items()}

        # Compute composite loss
        loss_rel = torch.stack(loss_rel_list).mean() if loss_rel_list else torch.tensor(0.0, device=device)
        loss_node = torch.stack(loss_node_list).mean() if loss_node_list else torch.tensor(0.0, device=device)
        loss_time = torch.stack(loss_time_list).mean() if loss_time_list else torch.tensor(0.0, device=device)

        total_loss = self.lambda_rel * loss_rel + self.lambda_node * loss_node + self.lambda_time * loss_time

        return {
            "loss": total_loss,
            "loss_rel": loss_rel,
            "loss_node": loss_node,
            "loss_time": loss_time,
            "num_events": len(events),
            "masked_rel_count": masked_rel_count,
            "masked_node_count": masked_node_count
        }

    def _aggregate_history(self, node_id: str, current_msg: torch.Tensor, device: torch.device) -> torch.Tensor:
        """Aggregates historical interaction messages using Multi-Head Self-Attention."""
        hist = self.node_history_buffers.get(node_id, [])
        if not hist:
            return current_msg
        
        hist_tensor = torch.stack(hist).unsqueeze(0).to(device) # (1, seq_len, d_msg)
        query = current_msg.unsqueeze(1)                        # (1, 1, d_msg)
        attn_out, _ = self.history_attn(query, hist_tensor, hist_tensor)
        agg = self.norm_history(current_msg + attn_out.squeeze(1))
        return agg

    def _append_history(self, node_id: str, msg: torch.Tensor):
        """Appends message to FIFO queue respecting max_node_history = 64."""
        if node_id not in self.node_history_buffers:
            self.node_history_buffers[node_id] = []
        buf = self.node_history_buffers[node_id]
        buf.append(msg)
        if len(buf) > self.max_node_history:
            buf.pop(0)
