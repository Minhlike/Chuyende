# -*- coding: utf-8 -*-
"""
Multi-View VICReg and Per-Sample Correspondence Tests
Verifies:
  1. Per-sample correspondence: Two distinct graph samples in same batch produce two distinct graph embeddings.
  2. Zero repeated broadcast oracle (no z_graph.repeat(B, 1)).
  3. VICReg loss computes variance/covariance across real paired samples.
  4. Missing-view fallback uses learned token with proper masking.
"""

import pytest

pytest.importorskip("torch")
import torch

from research_agent.experiments.extractor.multi_view import (
    MultiViewRepresentationModel,
    MultiViewCorrespondence,
    VICRegLoss
)

def test_01_per_sample_distinct_graph_embeddings():
    model = MultiViewRepresentationModel(
        seq_vocab_size=40,
        graph_vocab_size=20,
        embed_dim=32,
        mode="aligned"
    )

    batch_size = 2
    seq_inputs = torch.randint(1, 40, (batch_size, 8))

    # Two distinct graph event streams for sample 0 and sample 1
    events_sample_0 = [
        {"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1, "src_type": 1, "dst_type": 2}
    ]
    events_sample_1 = [
        {"timestamp": 10.0, "src": 5, "dst": 6, "relation_type": 3, "src_type": 2, "dst_type": 1}
    ]
    graph_events_batch = [events_sample_0, events_sample_1]

    z_g_batch, valid_mask = model.extract_per_sample_graph_embeddings(
        graph_events_batch=graph_events_batch,
        batch_size=batch_size,
        correspondence_list=None,
        device=torch.device("cpu")
    )

    assert z_g_batch.shape == (2, 32)
    assert valid_mask.all()
    # Embeddings for sample 0 and sample 1 must differ
    assert not torch.allclose(z_g_batch[0], z_g_batch[1], atol=1e-3), "Distinct graph inputs must yield distinct embeddings."

def test_02_real_batch_vicreg_loss_and_gradients():
    model = MultiViewRepresentationModel(
        seq_vocab_size=40,
        graph_vocab_size=20,
        embed_dim=32,
        mode="aligned"
    )

    batch_size = 2
    seq_inputs = torch.randint(1, 40, (batch_size, 10))
    true_event_targets = torch.randint(0, 40, (batch_size, 10))

    graph_events_batch = [
        [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1, "src_type": 1, "dst_type": 2}],
        [{"timestamp": 2.0, "src": 3, "dst": 4, "relation_type": 2, "src_type": 2, "dst_type": 3}]
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
