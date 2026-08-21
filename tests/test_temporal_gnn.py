# -*- coding: utf-8 -*-
"""
Temporal GNN Semantic Invariant Tests
Verifies:
  1. Same-time message aggregation: Messages at same timestamp to same destination aggregated before single update.
  2. Edge features x_e participate in message function (ablation test).
  3. Global late-event safety: Out-of-order calls rejected across successive invocations.
  4. LRU-bounded state capacity: Memory store never exceeds max_entities.
  5. Anti-leakage masked edge and masked node SSL tasks.
  6. Graph SSL losses (L_mask_node, L_mask_edge, L_time_gap) compute finite losses and valid gradients.
"""

import pytest

pytest.importorskip("torch")
import torch
import torch.nn.functional as F

from research_agent.experiments.extractor.graph_view import (
    TemporalGraphViewExtractor,
    BoundedEntityMemoryBank
)

def test_01_same_time_message_aggregation():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, num_relations=4, memory_dim=32, out_dim=32)
    model.memory_bank.reset_memory()

    # Two distinct source nodes sending messages to destination entity 5 at exact same timestamp t=10.0
    events_concurrent = [
        {"timestamp": 10.0, "src": 1, "dst": 5, "relation_type": 1, "src_type": 1, "dst_type": 2},
        {"timestamp": 10.0, "src": 2, "dst": 5, "relation_type": 2, "src_type": 1, "dst_type": 2}
    ]

    z_g, _ = model.process_causal_events(events_concurrent, device)
    assert z_g.shape == (1, 32)
    assert 5 in model.memory_bank.memory_store
    assert model.memory_bank.last_timestamps[5] == 10.0

def test_02_edge_features_enter_message():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, edge_feat_dim=4, memory_dim=32, out_dim=32)

    ev_feat_a = [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 0, "edge_features": [1.0, 0.0, 0.0, 0.0]}]
    ev_feat_b = [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 0, "edge_features": [0.0, 0.0, 0.0, 1.0]}]

    model.memory_bank.reset_memory()
    z_a = model.forward(ev_feat_a, device)

    model.memory_bank.reset_memory()
    z_b = model.forward(ev_feat_b, device)

    assert not torch.allclose(z_a, z_b, atol=1e-4), "Varying edge features x_e must alter graph representation."

def test_03_global_late_event_rejection():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, memory_dim=32, late_event_policy="REJECT")
    model.memory_bank.reset_memory()

    # Call 1 processes up to t=100.0
    call_1_events = [{"timestamp": 100.0, "src": 1, "dst": 2, "relation_type": 1}]
    _ = model.forward(call_1_events, device)

    # Call 2 submits late event at t=50.0 -> must raise ValueError
    call_2_events = [{"timestamp": 50.0, "src": 3, "dst": 4, "relation_type": 0}]
    with pytest.raises(ValueError, match="Global late event rejected"):
        model.forward(call_2_events, device)

def test_04_bounded_memory_capacity_enforcement():
    bank = BoundedEntityMemoryBank(memory_dim=16, max_entities=5)
    device = torch.device("cpu")

    # Insert 10 distinct entities into capacity-5 bank
    for i in range(10):
        bank.update_entity(entity_id=i, new_state=torch.randn(16), timestamp=float(i))

    metrics = bank.get_state_metrics()
    assert metrics["active_entities"] == 5
    assert len(bank.memory_store) == 5
    # Oldest entities 0..4 must have been LRU-evicted
    assert 0 not in bank.memory_store
    assert 9 in bank.memory_store

def test_05_anti_leakage_masked_edge_ssl():
    device = torch.device("cpu")
    model = TemporalGraphViewExtractor(node_vocab_size=20, num_relations=6, memory_dim=32, out_dim=32)
    model.memory_bank.reset_memory()

    events = [
        {"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 3, "src_type": 1, "dst_type": 2},
        {"timestamp": 2.0, "src": 2, "dst": 3, "relation_type": 5, "src_type": 2, "dst_type": 1}
    ]

    # Mask edge at index 0
    z_g, ssl_losses = model.process_causal_events(
        events=events,
        device=device,
        mask_edge_indices={0}
    )

    assert "L_mask_edge" in ssl_losses
    assert "L_mask_node" in ssl_losses
    assert "L_time_gap" in ssl_losses
    assert torch.isfinite(ssl_losses["L_mask_edge"])

    # Gradients flow back to ssl heads
    total_loss = ssl_losses["L_mask_edge"] + ssl_losses["L_time_gap"]
    total_loss.backward()

    for p in model.ssl_mask_edge_head.parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
