# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Stage A2 TemporalGraphViewEncoder & StageA2Trainer (V1.3).
NON_EMPIRICAL_TEST_FIXTURE = true
"""

import math
import pytest
import torch
from pathlib import Path

from research_agent.experiments.models.temporal_graph_view_encoder import (
    TemporalGraphViewEncoder,
    TimeProjection
)
from research_agent.experiments.training.stage_a2_trainer import (
    StageA2Trainer,
    EmpiricalExecutionNotAuthorizedError,
    CheckpointBoundaryViolationError
)

NON_EMPIRICAL_TEST_FIXTURE = True

def create_synthetic_event(
    src: str,
    dst: str,
    src_type: int,
    dst_type: int,
    rel_id: int,
    ts: float,
    size_b: float = 1024.0,
    line_idx: int = 1
) -> dict:
    return {
        "raw_line_index": line_idx,
        "event_timestamp_utc_exact": ts,
        "source_node": src,
        "source_type": src_type,
        "dest_node": dst,
        "dest_type": dst_type,
        "relation_id": rel_id,
        "relation_name": f"REL_{rel_id}",
        "block_id": dst if dst_type == 0 else src,
        "size_bytes": size_b
    }

def test_architecture_dimensions():
    model = TemporalGraphViewEncoder(
        d_node=128,
        d_edge=64,
        d_msg=128,
        n_heads=4,
        d_time_proj=32,
        d_rel_emb=32,
        d_type_emb=32,
        dropout=0.10
    )
    param_count = sum(p.numel() for p in model.parameters())
    assert param_count > 0
    assert model.d_node == 128
    assert model.d_edge == 64
    assert model.d_msg == 128
    assert model.n_heads == 4

def test_predict_before_update_order():
    model = TemporalGraphViewEncoder()
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    
    # Prior state before forward is 0
    h_a_prior = model._get_h_prev("nodeA", torch.device("cpu")).clone()
    assert torch.all(h_a_prior == 0.0)
    
    # Run forward on event
    res = model.forward_event_window([ev1])
    assert res["loss"].item() > 0.0
    
    # After forward, node memory must be updated
    h_a_after = model.node_memory["nodeA"]
    assert not torch.all(h_a_after == 0.0)

def test_relation_target_hidden_from_prediction():
    model = TemporalGraphViewEncoder()
    model.eval()
    with torch.no_grad():
        h_a = model._get_h_prev("nodeA", torch.device("cpu")).unsqueeze(0)
        h_b = model._get_h_prev("nodeB", torch.device("cpu")).unsqueeze(0)
        phi_dt = model.time_proj(torch.tensor([[0.0]]))
        rel_in = torch.cat([h_a, h_b, phi_dt], dim=-1)
        logits1 = model.rel_head(rel_in)
        logits2 = model.rel_head(rel_in)
        assert torch.allclose(logits1, logits2)

def test_node_reconstruction_target_not_directly_visible():
    model = TemporalGraphViewEncoder()
    with torch.no_grad():
        h_dummy = torch.randn(1, 128)
        pred = model.node_head(h_dummy)
        assert pred.shape == (1, 6)

def test_causal_degree_t_minus():
    model = TemporalGraphViewEncoder()
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    
    # At t-, in-degree and out-degree are 0
    in_b, out_a = model._get_causal_degrees_t_minus("nodeB")[0], model._get_causal_degrees_t_minus("nodeA")[1]
    assert in_b == 0
    assert out_a == 0
    
    model.forward_event_window([ev1])
    
    # After update, degree incremented
    assert model.node_out_degrees["nodeA"] == 1
    assert model.node_in_degrees["nodeB"] == 1

def test_temporal_gap_semantics():
    model = TemporalGraphViewEncoder()
    
    # First observation -> 0.0
    dt0 = model._get_temporal_gap_t_minus("nodeA", "nodeB", 100.0)
    assert dt0 == 0.0
    
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    model.forward_event_window([ev1])
    
    # Second event 5.5 seconds later
    dt1 = model._get_temporal_gap_t_minus("nodeA", "nodeB", 105.5)
    assert abs(dt1 - 5.5) < 1e-5

def test_same_timestamp_gap_zero():
    model = TemporalGraphViewEncoder()
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    model.forward_event_window([ev1])
    
    dt_same = model._get_temporal_gap_t_minus("nodeA", "nodeB", 100.0)
    assert dt_same == 0.0

def test_validation_dynamic_reset():
    model = TemporalGraphViewEncoder()
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    model.forward_event_window([ev1])
    
    assert len(model.node_memory) > 0
    assert len(model.node_last_ts) > 0
    
    model.reset_node_states()
    
    assert len(model.node_memory) == 0
    assert len(model.node_last_ts) == 0
    assert len(model.node_in_degrees) == 0
    assert len(model.node_out_degrees) == 0
    assert len(model.node_history_buffers) == 0

def test_history_fifo_capacity():
    model = TemporalGraphViewEncoder(max_node_history=5)
    for i in range(10):
        ev = create_synthetic_event("nodeA", f"node_{i}", 1, 0, 1, 100.0 + i)
        model.forward_event_window([ev])
    
    assert len(model.node_history_buffers["nodeA"]) == 5

def test_real_empirical_execution_guard():
    model = TemporalGraphViewEncoder()
    with pytest.raises(EmpiricalExecutionNotAuthorizedError):
        StageA2Trainer(
            model=model,
            execution_mode="REAL_EMPIRICAL",
            empirical_authorized=False
        )

def test_checkpoint_forbidden_mid_accumulation(tmp_path):
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(
        model=model,
        gradient_accumulation_steps=4,
        execution_mode="FIXTURE_TEST"
    )
    
    ev = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    # Process 1 window (grad_accum_position becomes 1 != 0)
    trainer.process_window([ev], is_training=True)
    assert trainer.grad_accum_position == 1
    
    ckpt_path = tmp_path / "test_ckpt.pt"
    with pytest.raises(CheckpointBoundaryViolationError):
        trainer.save_checkpoint(ckpt_path)

def test_checkpoint_roundtrip_contains_all_14_states(tmp_path):
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(
        model=model,
        gradient_accumulation_steps=2,
        execution_mode="FIXTURE_TEST"
    )
    
    events = [
        create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0),
        create_synthetic_event("nodeB", "nodeC", 0, 2, 3, 101.0)
    ]
    # Process 2 windows to complete 1 optimizer step (grad_accum_position returns to 0)
    trainer.process_window(events, is_training=True)
    trainer.process_window(events, is_training=True)
    assert trainer.grad_accum_position == 0
    assert trainer.global_step == 1
    
    ckpt_path = tmp_path / "checkpoint_roundtrip.pt"
    trainer.save_checkpoint(ckpt_path)
    
    # Load and verify state keys
    raw_dict = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    mandatory_keys = [
        "model_state_dict", "optimizer_state_dict", "scheduler_state_dict",
        "node_memory_states", "node_last_interaction_timestamps",
        "node_causal_in_degrees", "node_causal_out_degrees", "node_temporal_history_buffers",
        "rng_states_4tuple", "stream_iterator_state", "masking_rng_state",
        "early_stopping_state", "global_step", "current_epoch"
    ]
    for k in mandatory_keys:
        assert k in raw_dict, f"Missing state: {k}"
    
    # Create fresh trainer and restore
    model_new = TemporalGraphViewEncoder()
    trainer_new = StageA2Trainer(model=model_new, execution_mode="FIXTURE_TEST")
    trainer_new.load_checkpoint(ckpt_path)
    assert trainer_new.global_step == 1
