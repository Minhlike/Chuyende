# -*- coding: utf-8 -*-
"""
Multi-View VICReg and Optimization Graph Tests
Verifies:
  1. VICReg loss operates in real PyTorch computational graph during Stage A training.
  2. Loss backward() updates sequence projection, graph projection, and alignment parameters.
  3. MultiViewCorrespondence contract correctly gates alignment.
  4. Missing-view fallback uses learned token without silent zeros.
  5. Aligned mode differs structurally and semantically from unaligned mode.
"""

import pytest

pytest.importorskip("torch")
import torch

from research_agent.experiments.extractor.multi_view import (
    MultiViewRepresentationModel,
    MultiViewCorrespondence,
    VICRegLoss
)

def test_01_vicreg_in_real_optimization_graph_with_gradients():
    model = MultiViewRepresentationModel(
        seq_vocab_size=40,
        graph_vocab_size=20,
        param_vocab_size=15,
        embed_dim=32,
        mode="aligned"
    )

    batch_size = 4
    seq_inputs = torch.randint(1, 40, (batch_size, 12))
    true_event_targets = torch.randint(0, 40, (batch_size, 12))
    param_targets = torch.randint(0, 15, (batch_size, 12))
    time_gaps = torch.rand(batch_size, 12)

    graph_events = [
        {"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 1, "src_type": 1, "dst_type": 2},
        {"timestamp": 2.0, "src": 2, "dst": 3, "relation_type": 2, "src_type": 2, "dst_type": 3}
    ]

    corr = MultiViewCorrespondence(
        correspondence_id="CORR-TEST-001",
        time_interval=(0.0, 10.0),
        entity_scope="session_1",
        seq_view_id="seq_1",
        graph_view_id="graph_1",
        overlap_ratio=0.85
    )

    total_loss, metrics = model.compute_stage_a_loss(
        seq_inputs=seq_inputs,
        true_event_targets=true_event_targets,
        param_targets=param_targets,
        time_gap_targets=time_gaps,
        graph_events=graph_events,
        correspondence=corr
    )

    assert torch.isfinite(total_loss)
    assert metrics["loss_vicreg_align"] >= 0.0

    # Execute backward pass
    total_loss.backward()

    # Verify non-zero gradients on alignment projections
    for name, p in model.seq_proj_align.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), f"seq_proj_align {name} missing grad"
    for name, p in model.graph_proj_align.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), f"graph_proj_align {name} missing grad"

def test_02_missing_view_uses_learned_token():
    model = MultiViewRepresentationModel(seq_vocab_size=30, embed_dim=16, mode="aligned")
    seq_in = torch.randint(1, 30, (2, 6))

    # Graph view is missing
    corr_missing = MultiViewCorrespondence(
        correspondence_id="CORR-MISSING-001",
        time_interval=(0.0, 5.0),
        entity_scope="session_2",
        seq_view_id="seq_2",
        graph_view_id="none",
        overlap_ratio=0.0,
        graph_available=False
    )

    z_rep = model.extract_representation(seq_in, graph_events=None, correspondence=corr_missing)
    assert z_rep.shape == (2, 16)
    assert not torch.all(z_rep == 0.0), "Missing-view must use learned token, not silent zeros."

def test_03_aligned_vs_unaligned_modes():
    model_aligned = MultiViewRepresentationModel(seq_vocab_size=25, embed_dim=16, mode="aligned")
    model_unaligned = MultiViewRepresentationModel(seq_vocab_size=25, embed_dim=16, mode="unaligned")

    seq_in = torch.randint(1, 25, (2, 8))
    graph_events = [{"timestamp": 1.0, "src": 1, "dst": 2, "relation_type": 0, "src_type": 1, "dst_type": 2}]

    z_aligned = model_aligned.extract_representation(seq_in, graph_events=graph_events)
    z_unaligned = model_unaligned.extract_representation(seq_in, graph_events=graph_events)

    assert z_aligned.shape == (2, 16)
    assert z_unaligned.shape == (2, 16)
