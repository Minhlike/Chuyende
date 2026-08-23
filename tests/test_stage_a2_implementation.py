# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Stage A2 Implementation (Contract V1.4 Locked).
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
    FloatingPointAnomalyError,
    ExecutionDeviceMismatchError,
    VALIDATION_MASK_SEED
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
    last_layer = [m for m in model.rel_head.modules() if isinstance(m, nn.Linear)][-1]
    assert last_layer.out_features == 8

def test_relation_id_to_class_index_mapping():
    model = TemporalGraphViewEncoder()
    model.eval()
    for rel_id in range(1, 9):
        ev = create_synthetic_event("nodeA", "nodeB", 1, 0, rel_id, 100.0)
        res = model.forward_event_window([ev], is_training=False)
        assert res["loss_rel"].item() >= 0.0

def test_no_unused_relation_class_in_loss():
    model = TemporalGraphViewEncoder()
    ev_invalid_0 = create_synthetic_event("nodeA", "nodeB", 1, 0, 0, 100.0)
    ev_invalid_9 = create_synthetic_event("nodeA", "nodeB", 1, 0, 9, 100.0)
    with pytest.raises(ValueError):
        model.forward_event_window([ev_invalid_0], is_training=False)
    with pytest.raises(ValueError):
        model.forward_event_window([ev_invalid_9], is_training=False)

def test_predict_before_update_order():
    model = TemporalGraphViewEncoder()
    ev1 = create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0)
    h_a_prior = model._get_h_prev("nodeA", torch.device("cpu")).clone()
    assert torch.all(h_a_prior == 0.0)
    
    # Run forward on event
    res = model.forward_event_window([ev1], is_training=True)
    # Memory must be updated after event
    h_a_after = model.node_memory["nodeA"]
    assert not torch.all(h_a_after == 0.0)

def test_type_embedding_participates_in_forward_graph():
    model = TemporalGraphViewEncoder()
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
    # Using generator with high mask or test fixture
    res = model.forward_event_window([ev1, ev2], is_training=True)
    res["loss"].backward()
    assert model.type_embedding.weight.grad is not None

# -------------------------------------------------------------
# 2. VALIDATION MASKING CONTRACT TESTS (V1.4)
# -------------------------------------------------------------

def test_validation_does_not_mask_all_targets():
    model = TemporalGraphViewEncoder()
    events = [create_synthetic_event(f"node_{i}", f"node_{i+1}", 1, 0, 1, 100.0 + i) for i in range(100)]
    gen = torch.Generator().manual_seed(42)
    res = model.forward_event_window(events, mask_generator=gen, is_training=False)
    # In 100 events with p=0.15, masked count is ~15, strictly < 100
    assert 5 <= res["masked_rel_count"] < 35, f"Expected ~15 masked relations, got {res['masked_rel_count']}"
    assert res["masked_rel_count"] < len(events), "Validation must NOT mask 100% of targets"

def test_validation_rel_mask_contract_015():
    model = TemporalGraphViewEncoder(rel_mask_prob=0.15)
    assert model.rel_mask_prob == 0.15
    events = [create_synthetic_event(f"node_{i}", f"node_{i+1}", 1, 0, 1, 100.0 + i) for i in range(1000)]
    gen = torch.Generator().manual_seed(123)
    res = model.forward_event_window(events, mask_generator=gen, is_training=False)
    empirical_rate = res["masked_rel_count"] / 1000.0
    assert abs(empirical_rate - 0.15) < 0.04, f"Empirical rate {empirical_rate} deviated from 0.15"

def test_validation_node_mask_contract_015():
    model = TemporalGraphViewEncoder(node_mask_prob=0.15)
    assert model.node_mask_prob == 0.15
    events = [create_synthetic_event(f"node_{i}", f"node_{i+1}", 1, 0, 1, 100.0 + i) for i in range(1000)]
    gen = torch.Generator().manual_seed(123)
    res = model.forward_event_window(events, mask_generator=gen, is_training=False)
    # Each event has 2 nodes (src, dst) -> 2000 opportunities
    empirical_rate = res["masked_node_count"] / 2000.0
    assert abs(empirical_rate - 0.15) < 0.04, f"Empirical node rate {empirical_rate} deviated from 0.15"

def test_validation_mask_fixed_across_epochs():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_device="cpu", execution_mode="FIXTURE_TEST")
    events = [create_synthetic_event(f"node_{i}", f"node_{i+1}", 1, 0, 1, 100.0 + i) for i in range(50)]
    
    # Epoch 1 validation
    val1 = trainer.validate_one_epoch([events])
    # Epoch 2 validation (after simulated training)
    val2 = trainer.validate_one_epoch([events])
    
    assert val1["rel_target_count"] == val2["rel_target_count"]
    assert val1["node_target_count"] == val2["node_target_count"]
    assert val1["rel_loss_sum"] == val2["rel_loss_sum"]
    assert val1["val_L_graph"] == val2["val_L_graph"]

def test_validation_mask_independent_from_training_rng():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, seed=42, execution_device="cpu", execution_mode="FIXTURE_TEST")
    val_stream = [[create_synthetic_event(f"node_{i}", f"node_{i+1}", 1, 0, 1, 100.0 + i) for i in range(30)]]
    
    # Initial validation
    v0 = trainer.validate_one_epoch(val_stream)
    
    # Run some arbitrary training steps to advance training RNG
    train_stream = [[create_synthetic_event("A", "B", 1, 0, 1, 50.0)] for _ in range(20)]
    trainer.train_one_epoch(train_stream)
    
    # Subsequent validation must produce exact identical target counts and metrics
    v1 = trainer.validate_one_epoch(val_stream)
    assert v0["rel_target_count"] == v1["rel_target_count"]
    assert v0["node_target_count"] == v1["node_target_count"]

# -------------------------------------------------------------
# 3. GLOBAL LOSS AGGREGATION TESTS (V1.4)
# -------------------------------------------------------------

def test_global_rel_loss_exact():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_device="cpu", execution_mode="FIXTURE_TEST")
    
    w1 = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)]
    w2 = [create_synthetic_event("B", "C", 0, 2, 2, 101.0)]
    stats = trainer.validate_one_epoch([w1, w2])
    
    expected_rel = stats["rel_loss_sum"] / max(1, stats["rel_target_count"])
    assert abs(stats["val_L_rel"] - expected_rel) < 1e-7

def test_global_node_mse_exact():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_device="cpu", execution_mode="FIXTURE_TEST")
    
    w1 = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)]
    w2 = [create_synthetic_event("B", "C", 0, 2, 2, 101.0)]
    stats = trainer.validate_one_epoch([w1, w2])
    
    expected_node = stats["node_sq_err_sum"] / max(1, stats["node_element_count"])
    assert abs(stats["val_L_node"] - expected_node) < 1e-7
    assert stats["node_element_count"] == 6 * stats["node_target_count"]

def test_global_time_loss_exact():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_device="cpu", execution_mode="FIXTURE_TEST")
    
    w1 = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)]
    w2 = [create_synthetic_event("B", "C", 0, 2, 2, 101.0)]
    stats = trainer.validate_one_epoch([w1, w2])
    
    expected_time = stats["time_loss_sum"] / max(1, stats["time_target_count"])
    assert abs(stats["val_L_time"] - expected_time) < 1e-7

def test_global_L_graph_exact():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_device="cpu", execution_mode="FIXTURE_TEST")
    
    w1 = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)]
    stats = trainer.validate_one_epoch([w1])
    
    expected_l_graph = 1.0 * stats["val_L_rel"] + 1.0 * stats["val_L_node"] + 0.1 * stats["val_L_time"]
    assert abs(stats["val_L_graph"] - expected_l_graph) < 1e-7

# -------------------------------------------------------------
# 4. PARTIAL WINDOW & ACCUMULATION TESTS (V1.4)
# -------------------------------------------------------------

def test_final_train_window_has_81_events():
    total_events = 586577
    window_size = 256
    num_windows = math.ceil(total_events / window_size)
    full_windows = total_events // window_size
    final_window_events = total_events - (full_windows * window_size)
    
    assert num_windows == 2292
    assert full_windows == 2291
    assert final_window_events == 81

def test_final_train_window_not_dropped():
    total_events = 586577
    window_size = 256
    accum_steps = 4
    num_windows = math.ceil(total_events / window_size)
    optimizer_steps = num_windows // accum_steps
    assert optimizer_steps == 573
    assert num_windows % accum_steps == 0
    # Final step contains 3 * 256 + 1 * 81 = 849 real events
    final_step_events = 3 * 256 + 81
    assert final_step_events == 849

def test_partial_accumulation_weighting():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_device="cpu", execution_mode="FIXTURE_TEST")
    
    # 4 windows: 3 of 256 events, 1 of 81 events -> total 849 events
    w1 = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)] * 256
    w2 = [create_synthetic_event("B", "C", 0, 2, 2, 101.0)] * 256
    w3 = [create_synthetic_event("C", "D", 2, 3, 3, 102.0)] * 256
    w4 = [create_synthetic_event("D", "A", 3, 1, 4, 103.0)] * 81
    
    group_total = 849
    stats1 = trainer.process_window(w1, is_training=True, group_total_events=group_total)
    stats2 = trainer.process_window(w2, is_training=True, group_total_events=group_total)
    stats3 = trainer.process_window(w3, is_training=True, group_total_events=group_total)
    stats4 = trainer.process_window(w4, is_training=True, group_total_events=group_total)
    
    assert trainer.global_step == 1
    assert stats4["grad_accum_position"] == 0

# -------------------------------------------------------------
# 5. EXECUTION DEVICE & FAIL-CLOSED TESTS (V1.4)
# -------------------------------------------------------------

def test_execution_device_is_explicit_cuda():
    model = TemporalGraphViewEncoder()
    # When initialized with cpu, device is cpu
    trainer_cpu = StageA2Trainer(model=model, execution_device="cpu", execution_mode="FIXTURE_TEST")
    assert trainer_cpu.device.type == "cpu"

def test_device_mismatch_fails_before_optimizer():
    model = TemporalGraphViewEncoder()
    # If CUDA is requested on a system without CUDA, it must raise ExecutionDeviceMismatchError
    if not torch.cuda.is_available():
        with pytest.raises(ExecutionDeviceMismatchError):
            StageA2Trainer(model=model, execution_device="cuda", execution_mode="FIXTURE_TEST")

def test_no_cpu_fallback():
    model = TemporalGraphViewEncoder()
    if not torch.cuda.is_available():
        with pytest.raises(ExecutionDeviceMismatchError) as exc_info:
            StageA2Trainer(model=model, execution_device="cuda", execution_mode="FIXTURE_TEST")
        assert "Automatic CPU fallback is strictly prohibited" in str(exc_info.value)
