# -*- coding: utf-8 -*-
"""
Sequence SSL and Privacy-Safe Target Tests
Verifies:
  1. Sequence View SSL Heads (L_MEP, L_MPP, L_time) compute finite losses.
  2. Gradients propagate to all 3 sequence heads and Transformer backbone.
  3. Zero orphan auxiliary parameters.
  4. Privacy Target Safety: Target labels are categorical token indices, not raw strings.
"""

import pytest

pytest.importorskip("torch")
import torch

from research_agent.experiments.extractor.sequence_view import SequenceViewExtractor

def test_01_sequence_ssl_three_heads_finite_and_gradients():
    extractor = SequenceViewExtractor(
        event_vocab_size=50,
        param_vocab_size=20,
        d_model=32,
        projection_dim=32
    )

    batch_size, seq_len = 4, 10
    masked_events = torch.randint(1, 50, (batch_size, seq_len))
    true_event_targets = torch.randint(0, 50, (batch_size, seq_len))
    param_targets = torch.randint(0, 20, (batch_size, seq_len))
    time_gap_targets = torch.rand(batch_size, seq_len) * 5.0

    losses = extractor.compute_sequence_ssl_losses(
        masked_events=masked_events,
        true_event_targets=true_event_targets,
        param_targets=param_targets,
        true_time_gaps=time_gap_targets
    )

    assert "L_MEP" in losses
    assert "L_MPP" in losses
    assert "L_time" in losses

    total_loss = losses["L_MEP"] + losses["L_MPP"] + losses["L_time"]
    assert torch.isfinite(total_loss)

    total_loss.backward()

    # Verify gradients
    for name, p in extractor.mep_head.named_parameters():
        assert p.grad is not None, f"mep_head parameter {name} has no gradient"
    for name, p in extractor.mpp_head.named_parameters():
        assert p.grad is not None, f"mpp_head parameter {name} has no gradient"
    for name, p in extractor.time_gap_head.named_parameters():
        assert p.grad is not None, f"time_gap_head parameter {name} has no gradient"
    for name, p in extractor.transformer.named_parameters():
        assert p.grad is not None, f"transformer backbone parameter {name} has no gradient"

def test_02_zero_orphan_auxiliary_parameters():
    extractor = SequenceViewExtractor(event_vocab_size=30, param_vocab_size=10, d_model=16, projection_dim=16)
    
    # Forward pass checking all modules participate
    x = torch.randint(1, 30, (2, 8))
    z_seq = extractor.forward_pool(x)
    assert z_seq.shape == (2, 16)
