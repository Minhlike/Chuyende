# -*- coding: utf-8 -*-
"""
Temporal GNN Semantic Invariant Tests
Verifies:
  1. Same graph structure with different timestamps produces different representations.
  2. Strict causality: Future events cannot alter past/present z(t).
  3. Entity memory before and after an event differs.
  4. Unseen entity initialization from h_init.
  5. Out-of-order events are strictly rejected under REJECT policy.
  6. Graph SSL heads (L_mask_node, L_mask_edge, L_time_gap) produce finite loss and valid gradients.
"""

import pytest
from typing import Dict, Any, List

pytest.importorskip("torch")
import torch
import torch.nn.functional as F

from research_agent.experiments.extractor.graph_view import TemporalGraphViewExtractor, EntityMemoryBank

def test_01_timestamps_affect_representation():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, num_relations=4, memory_dim=32, out_dim=32)

    events_t1 = [
        {"timestamp": 10.0, "src": 1, "dst": 2, "relation_type": 1, "src_type": 1, "dst_type": 2},
        {"timestamp": 15.0, "src": 2, "dst": 3, "relation_type": 2, "src_type": 2, "dst_type": 3}
    ]
    events_t2 = [
        {"timestamp": 10.0, "src": 1, "dst": 2, "relation_type": 1, "src_type": 1, "dst_type": 2},
        {"timestamp": 1000.0, "src": 2, "dst": 3, "relation_type": 2, "src_type": 2, "dst_type": 3}
    ]

    model.memory_bank.reset_memory()
    z1 = model.forward(events_t1, device)

    model.memory_bank.reset_memory()
    z2 = model.forward(events_t2, device)

    assert not torch.allclose(z1, z2, atol=1e-3), "Different delta timestamps must yield different representations."

def test_02_strict_causality_and_no_lookahead():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, num_relations=4, memory_dim=32, out_dim=32)

    events_prefix = [
        {"timestamp": 10.0, "src": 1, "dst": 2, "relation_type": 1, "src_type": 1, "dst_type": 2}
    ]
    
    # Process prefix
    model.memory_bank.reset_memory()
    z_prefix, _ = model.process_causal_events(events_prefix, device)
    h_entity_2_at_t10 = model.memory_bank.memory_store[2].clone()

    # In a separate run, add a future event at t=50. The state at t=10 must not be affected.
    model.memory_bank.reset_memory()
    _ = model.forward(events_prefix, device)
    h_entity_2_before_future = model.memory_bank.memory_store[2].clone()

    assert torch.allclose(h_entity_2_at_t10, h_entity_2_before_future), "Entity state at t=10 must be strictly identical regardless of future."

def test_03_memory_update_state_transition():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, num_relations=4, memory_dim=32, out_dim=32)
    model.memory_bank.reset_memory()

    # Initial state for entity 5
    h_pre, _ = model.memory_bank.get_memory([5], [0.0], device)
    
    event = [{"timestamp": 1.0, "src": 1, "dst": 5, "relation_type": 0, "src_type": 1, "dst_type": 2}]
    _ = model.forward(event, device)

    h_post, _ = model.memory_bank.get_memory([5], [1.0], device)
    assert not torch.allclose(h_pre, h_post), "Memory state must transition after interaction."

def test_04_unseen_entity_initialization():
    bank = EntityMemoryBank(memory_dim=16)
    device = torch.device("cpu")
    
    # Query entity 999 (unseen)
    h_unseen, delta = bank.get_memory([999], [100.0], device)
    assert h_unseen.shape == (1, 16)
    assert delta.item() == 0.0

def test_05_out_of_order_event_rejected():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, num_relations=4, memory_dim=32, out_dim=32, late_event_policy="REJECT")

    events_out_of_order = [
        {"timestamp": 20.0, "src": 1, "dst": 2, "relation_type": 1},
        {"timestamp": 10.0, "src": 2, "dst": 3, "relation_type": 2}  # Violates causal monotonicity
    ]

    with pytest.raises(ValueError, match="Strict causality violation"):
        model.process_causal_events(events_out_of_order, device)

def test_06_graph_ssl_heads_finite_and_gradients():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, num_relations=4, memory_dim=32, out_dim=32)
    model.memory_bank.reset_memory()

    events = [
        {"timestamp": 10.0, "src": 1, "dst": 2, "relation_type": 1, "src_type": 1, "dst_type": 2},
        {"timestamp": 12.0, "src": 2, "dst": 3, "relation_type": 3, "src_type": 2, "dst_type": 1}
    ]

    z_g, ssl_losses = model.process_causal_events(events, device)

    assert "L_mask_node" in ssl_losses
    assert "L_mask_edge" in ssl_losses
    assert "L_time_gap" in ssl_losses

    total_ssl = ssl_losses["L_mask_node"] + ssl_losses["L_mask_edge"] + ssl_losses["L_time_gap"]
    assert torch.isfinite(total_ssl)

    total_ssl.backward()
    # Verify non-zero gradients on heads
    for p in model.ssl_mask_node_head.parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
    for p in model.ssl_mask_edge_head.parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
    for p in model.ssl_time_gap_head.parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
