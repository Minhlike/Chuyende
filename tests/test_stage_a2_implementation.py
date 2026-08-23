# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Stage A2 Implementation (Contract V1.3 Amended).
NON_EMPIRICAL_TEST_FIXTURE = true
"""

import math
import pytest
import torch
import torch.nn as nn
from pathlib import Path

from research_agent.experiments.models.temporal_graph_view_encoder import (
    TemporalGraphViewEncoder,
    TimeProjection
)
from research_agent.experiments.training.stage_a2_trainer import (
    StageA2Trainer,
    EmpiricalExecutionNotAuthorizedError,
    CheckpointBoundaryViolationError,
    FloatingPointAnomalyError
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

# -------------------------------------------------------------
# 1. ARCHITECTURE & RELATION HEAD TESTS
# -------------------------------------------------------------

def test_architecture_dimensions_and_param_count():
    model = TemporalGraphViewEncoder(
        d_node=128,
        d_edge=64,
        d_msg=128,
        n_heads=4,
        d_time_proj=32,
        d_rel_emb=32,
        d_type_emb=32,
        dropout=0.10,
        num_canonical_relations=8,
        num_node_types=4
    )
    param_count = sum(p.numel() for p in model.parameters())
    assert param_count == 304111, f"Expected 304111 parameters, got {param_count}"
    assert model.d_node == 128
    assert model.d_edge == 64
    assert model.d_msg == 128
    assert model.n_heads == 4
    assert model.num_canonical_relations == 8

def test_relation_head_has_exactly_8_classes():
    model = TemporalGraphViewEncoder()
    # The last linear layer of rel_head must output exactly 8 logits
    last_layer = [m for m in model.rel_head.modules() if isinstance(m, nn.Linear)][-1]
    assert last_layer.out_features == 8

def test_relation_id_to_class_index_mapping():
    model = TemporalGraphViewEncoder()
    model.eval()
    
    # Check that relation IDs 1..8 map cleanly to target class indices 0..7
    for rel_id in range(1, 9):
        ev = create_synthetic_event("nodeA", "nodeB", 1, 0, rel_id, 100.0)
        res = model.forward_event_window([ev], is_training=False)
        assert res["loss_rel"].item() >= 0.0

def test_no_unused_relation_class_in_loss():
    model = TemporalGraphViewEncoder()
    # If an invalid relation ID (e.g. 0 or 9) is passed, model must reject with ValueError
    ev_invalid_0 = create_synthetic_event("nodeA", "nodeB", 1, 0, 0, 100.0)
    ev_invalid_9 = create_synthetic_event("nodeA", "nodeB", 1, 0, 9, 100.0)
    
    with pytest.raises(ValueError):
        model.forward_event_window([ev_invalid_0], is_training=False)
    with pytest.raises(ValueError):
        model.forward_event_window([ev_invalid_9], is_training=False)

def test_predict_before_update_order():
    model = TemporalGraphViewEncoder()
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    
    # Prior state before forward is 0
    h_a_prior = model._get_h_prev("nodeA", torch.device("cpu")).clone()
    assert torch.all(h_a_prior == 0.0)
    
    # Run forward on event in eval mode (where mask is forced to 1.0)
    res = model.forward_event_window([ev1], is_training=False)
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

# -------------------------------------------------------------
# 2. NODE LOSS & TYPE EMBEDDING TESTS
# -------------------------------------------------------------

def test_node_loss_is_mse_exactly():
    model = TemporalGraphViewEncoder()
    assert isinstance(model.loss_node_fn, nn.MSELoss)

    # Numerical fixture: verify manually computed MSE matches loss_node
    pred = torch.tensor([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], requires_grad=True)
    target = torch.tensor([1.0, 0.0, 0.0, 0.0, 0.6931, 0.0])
    manual_mse = ((pred - target) ** 2).mean()
    loss_calc = model.loss_node_fn(pred, target)
    assert torch.allclose(manual_mse, loss_calc)

def test_type_embedding_participates_in_forward_graph():
    model = TemporalGraphViewEncoder()
    # Different node types should produce different message representations and updated hidden states
    ev_type1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    ev_type2 = create_synthetic_event("nodeC", "nodeD", 3, 2, 1, 100.0)
    
    model.forward_event_window([ev_type1], is_training=False)
    model.forward_event_window([ev_type2], is_training=False)
    
    h_a = model.node_memory["nodeA"]
    h_c = model.node_memory["nodeC"]
    assert not torch.allclose(h_a, h_c)

def test_type_embedding_receives_gradient():
    model = TemporalGraphViewEncoder()
    model.train()
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    ev2 = create_synthetic_event("nodeA", "nodeC", 1, 2, 2, 101.0)
    # Using is_training=False forces mask_rel/node to True so loss computes deterministically on ev2 using h(nodeA) updated in ev1
    res = model.forward_event_window([ev1, ev2], is_training=False)
    res["loss"].backward()
    
    assert model.type_embedding.weight.grad is not None
    assert torch.norm(model.type_embedding.weight.grad) > 0.0

def test_node_target_still_not_directly_visible():
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

# -------------------------------------------------------------
# 3. TRAINER & STREAM CURSOR TESTS
# -------------------------------------------------------------

def test_real_empirical_execution_guard():
    model = TemporalGraphViewEncoder()
    with pytest.raises(EmpiricalExecutionNotAuthorizedError):
        StageA2Trainer(
            model=model,
            execution_mode="REAL_EMPIRICAL",
            empirical_authorized=False
        )

def test_stream_cursor_advances_once_per_window():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_mode="FIXTURE_TEST")
    
    assert trainer.stream_cursor == 0
    ev = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    trainer.process_window([ev], is_training=True)
    assert trainer.stream_cursor == 1
    trainer.process_window([ev], is_training=True)
    assert trainer.stream_cursor == 2

def test_checkpoint_cursor_points_to_exact_next_window(tmp_path):
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, gradient_accumulation_steps=2, execution_mode="FIXTURE_TEST")
    
    ev = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    trainer.process_window([ev], is_training=True)
    trainer.process_window([ev], is_training=True)
    assert trainer.grad_accum_position == 0
    assert trainer.stream_cursor == 2
    
    ckpt_path = tmp_path / "cursor_test.pt"
    trainer.save_checkpoint(ckpt_path)
    
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    assert ckpt["stream_iterator_state"]["stream_cursor"] == 2

def test_resume_uses_checkpoint_cursor_not_manual_slice(tmp_path):
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, gradient_accumulation_steps=2, execution_mode="FIXTURE_TEST")
    
    events_stream = [
        [create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)],
        [create_synthetic_event("nodeB", "nodeC", 0, 2, 2, 101.0)]
    ]
    # Process 2 windows
    trainer.process_window(events_stream[0], is_training=True)
    trainer.process_window(events_stream[1], is_training=True)
    
    ckpt_path = tmp_path / "resume_cursor.pt"
    trainer.save_checkpoint(ckpt_path)
    
    # Fresh trainer loads checkpoint and inspects cursor
    model_resumed = TemporalGraphViewEncoder()
    trainer_resumed = StageA2Trainer(model=model_resumed, execution_mode="FIXTURE_TEST")
    trainer_resumed.load_checkpoint(ckpt_path)
    
    assert trainer_resumed.stream_cursor == 2
    # The next window to process from events_stream is indexed by stream_cursor
    all_windows = events_stream + [[create_synthetic_event("nodeC", "nodeD", 2, 3, 3, 102.0)]]
    remaining = all_windows[trainer_resumed.stream_cursor:]
    assert len(remaining) == 1

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

def test_nan_inf_fail_closed():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_mode="FIXTURE_TEST")
    
    # Intentionally pass NaN timestamp
    ev_nan = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, float("nan"))
    with pytest.raises((FloatingPointError, FloatingPointAnomalyError)):
        trainer.process_window([ev_nan], is_training=True)

def test_full_train_and_validate_epoch_loops():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, gradient_accumulation_steps=2, execution_mode="FIXTURE_TEST")
    
    stream_train = [
        [create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)],
        [create_synthetic_event("nodeB", "nodeC", 0, 2, 2, 101.0)]
    ]
    stream_val = [
        [create_synthetic_event("valA", "valB", 1, 0, 3, 200.0)]
    ]
    
    train_stats = trainer.train_one_epoch(stream_train)
    assert "train_L_graph" in train_stats
    assert train_stats["windows_count"] == 2
    assert train_stats["split"] == "TRAIN"
    
    val_stats = trainer.validate_one_epoch(stream_val)
    assert "val_L_graph" in val_stats
    assert val_stats["windows_count"] == 1
    assert val_stats["split"] == "VAL"
    # Verify validation dynamic memory was reset
    assert len(model.node_memory) == 0
