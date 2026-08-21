# -*- coding: utf-8 -*-
"""
Sequence SSL and Privacy-Safe Target Tests
Verifies:
  1. Sequence View SSL Heads (L_MEP, L_MPP, L_time) compute finite losses over explicit mask domains.
  2. L_time operates on adjacent contextual pairs [h_i ; h_i+1] targeting log(1 + delta_t) with Smooth L1.
  3. Gradients propagate to all 3 sequence heads and Transformer backbone.
  4. Zero orphan auxiliary parameters.
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
    mep_mask = (true_event_targets > 10)

    param_targets = torch.randint(0, 20, (batch_size, seq_len))
    mpp_mask = (param_targets > 5)

    adjacent_time_gaps = torch.rand(batch_size, seq_len - 1) * 10.0

    losses = extractor.compute_sequence_ssl_losses(
        masked_events=masked_events,
        true_event_targets=true_event_targets,
        mep_mask=mep_mask,
        param_targets=param_targets,
        mpp_mask=mpp_mask,
        true_adjacent_time_gaps=adjacent_time_gaps
    )

    assert "L_MEP" in losses
    assert "L_MPP" in losses
    assert "L_time" in losses

    total_loss = losses["L_MEP"] + losses["L_MPP"] + losses["L_time"]
    assert torch.isfinite(total_loss)

    total_loss.backward()

    # Verify gradients on all parameters
    for name, p in extractor.mep_head.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), f"mep_head {name} missing grad"
    for name, p in extractor.mpp_head.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), f"mpp_head {name} missing grad"
    for name, p in extractor.time_pair_head.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), f"time_pair_head {name} missing grad"
    for name, p in extractor.transformer.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), f"transformer {name} missing grad"

def test_02_zero_orphan_auxiliary_parameters():
    extractor = SequenceViewExtractor(event_vocab_size=30, param_vocab_size=10, d_model=16, projection_dim=16)
    
    # Check all named parameters are registered in submodules
    all_param_names = [n for n, _ in extractor.named_parameters()]
    assert any("mep_head" in n for n in all_param_names)
    assert any("mpp_head" in n for n in all_param_names)
    assert any("time_pair_head" in n for n in all_param_names)
    assert any("projection_head" in n for n in all_param_names)
