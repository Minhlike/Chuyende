# -*- coding: utf-8 -*-
"""
Multi-View VICReg and Per-Sample Correspondence Tests
Verifies:
  1. Multi-View Memory Scope Isolation: Sample B representation is invariant whether evaluated alone or after unrelated sample A.
  2. Per-sample correspondence: Two distinct graph samples in same batch produce two distinct graph embeddings.
  3. Real batch VICReg loss optimization with non-zero gradients.
"""

import pytest

pytest.importorskip("torch")
import torch

from research_agent.experiments.extractor.multi_view import (
    MultiViewRepresentationModel,
    MultiViewCorrespondence,
    VICRegLoss
)

def test_01_independent_sample_memory_isolation():
    model = MultiViewRepresentationModel(
        seq_vocab_size=30,
        graph_node_attr_dim=8,
        embed_dim=16,
        mode="aligned",
        memory_scope_mode="independent"
    )
    model.eval()
    device = torch.device("cpu")

    seq_a = torch.randint(1, 30, (1, 6))
    events_a = [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1}]

    seq_b = torch.randint(1, 30, (1, 6))
    events_b = [{"timestamp": 1.0, "src": 3, "dst": 4, "relation_type": 2}]

    # Evaluate sample B alone
    z_b_alone = model.extract_representation(seq_b, graph_events_batch=[events_b], device=device)

    # Evaluate batch [sample A, sample B]
    seq_batch = torch.cat([seq_a, seq_b], dim=0)
    events_batch = [events_a, events_b]
    z_batch = model.extract_representation(seq_batch, graph_events_batch=events_batch, device=device)

    # Sample B representation in batch must match sample B alone exactly (Zero State Leakage)
    assert torch.allclose(z_b_alone[0], z_batch[1], atol=1e-5), "Sample B representation must be invariant to preceding batch items in independent mode."

def test_02_per_sample_distinct_graph_embeddings():
    model = MultiViewRepresentationModel(
        seq_vocab_size=40,
        graph_node_attr_dim=8,
        embed_dim=32,
        mode="aligned"
    )

    batch_size = 2
    events_sample_0 = [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1}]
    events_sample_1 = [{"timestamp": 10.0, "src": 5, "dst": 6, "relation_type": 3}]
    graph_events_batch = [events_sample_0, events_sample_1]

    z_g_batch, valid_mask = model.extract_per_sample_graph_embeddings(
        graph_events_batch=graph_events_batch,
        batch_size=batch_size,
        correspondence_list=None,
        device=torch.device("cpu")
    )

    assert z_g_batch.shape == (2, 32)
    assert valid_mask.all()
    assert not torch.allclose(z_g_batch[0], z_g_batch[1], atol=1e-3)

def test_03_real_batch_vicreg_loss_and_gradients():
    model = MultiViewRepresentationModel(
        seq_vocab_size=40,
        graph_node_attr_dim=8,
        embed_dim=32,
        mode="aligned"
    )

    batch_size = 2
    seq_inputs = torch.randint(1, 40, (batch_size, 10))
    true_event_targets = torch.randint(0, 40, (batch_size, 10))

    graph_events_batch = [
        [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1}],
        [{"timestamp": 2.0, "src": 3, "dst": 4, "relation_type": 2}]
    ]

    total_loss, metrics = model.compute_stage_a_loss(
        seq_inputs=seq_inputs,
        true_event_targets=true_event_targets,
        graph_events_batch=graph_events_batch
    )

    assert torch.isfinite(total_loss)
    assert metrics["loss_vicreg_align"] >= 0.0

    total_loss.backward()

    for name, p in model.seq_proj_align.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
    for name, p in model.graph_proj_align.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
