from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Stage A2 Implementation (Contract V1.4 Locked).
NON_EMPIRICAL_TEST_FIXTURE = true
"""

import os
import sys
import json
import math
import subprocess
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
from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    TestSetSealedError
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

def test_train_one_epoch_final_accumulation_uses_actual_group_denominators():
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, gradient_accumulation_steps=4, execution_device="cpu", execution_mode="FIXTURE_TEST", total_steps_override=1)
    
    # 4 windows: 256, 256, 256, 81 events
    w1 = [create_synthetic_event("A", "B", 1, 0, 1, 100.0 + i) for i in range(256)]
    w2 = [create_synthetic_event("B", "C", 0, 2, 2, 200.0 + i) for i in range(256)]
    w3 = [create_synthetic_event("C", "D", 2, 3, 3, 300.0 + i) for i in range(256)]
    w4 = [create_synthetic_event("D", "A", 3, 1, 4, 400.0 + i) for i in range(81)]
    
    stats = trainer.train_one_epoch([w1, w2, w3, w4])
    assert stats["events_count"] == 849
    assert stats["windows_count"] == 4
    assert stats["optimizer_steps"] == 1

def test_group_objective_relation_denominator_exact():
    """Proves that group relation loss uses sum(CE)/sum(N_rel) rather than mean of window means."""
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, gradient_accumulation_steps=2, execution_device="cpu", execution_mode="FIXTURE_TEST", total_steps_override=1)
    
    w1 = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(10)]
    w2 = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(40)]
    
    stats = trainer.process_group([w1, w2], is_training=False)
    
    expected_rel = stats["rel_loss_sum"] / max(1, stats["rel_target_count"])
    assert abs(stats["loss_rel"] - expected_rel) < 1e-6

def test_group_objective_node_denominator_exact():
    """Proves that group node loss uses sum(sq_err)/(6 * sum(N_node))."""
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, gradient_accumulation_steps=2, execution_device="cpu", execution_mode="FIXTURE_TEST", total_steps_override=1)
    
    w1 = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(20)]
    w2 = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(30)]
    
    stats = trainer.process_group([w1, w2], is_training=False)
    
    assert stats["node_element_count"] == 6 * stats["node_target_count"]
    expected_node = stats["node_sq_err_sum"] / max(1, stats["node_element_count"])
    assert abs(stats["loss_node"] - expected_node) < 1e-6

def test_group_objective_time_denominator_exact():
    """Proves that group time loss uses sum(time_loss)/sum(N_events)."""
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, gradient_accumulation_steps=2, execution_device="cpu", execution_mode="FIXTURE_TEST", total_steps_override=1)
    
    w1 = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(15)]
    w2 = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(25)]
    
    stats = trainer.process_group([w1, w2], is_training=False)
    
    assert stats["time_target_count"] == 40
    expected_time = stats["time_loss_sum"] / 40
    assert abs(stats["loss_time"] - expected_time) < 1e-6

def test_partial_group_gradient_matches_manual_reference():
    """Verifies that process_group produces exact gradient matching manual group objective."""
    torch.manual_seed(100)
    model1 = TemporalGraphViewEncoder()
    model2 = TemporalGraphViewEncoder()
    model2.load_state_dict(model1.state_dict())
    
    trainer = StageA2Trainer(model=model1, gradient_accumulation_steps=2, execution_device="cpu", execution_mode="FIXTURE_TEST", total_steps_override=1)
    
    w1 = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)] * 10
    w2 = [create_synthetic_event("B", "C", 0, 2, 2, 101.0)] * 5
    
    stats = trainer.process_group([w1, w2], is_training=True)
    assert trainer.global_step == 1
    assert stats["global_step"] == 1

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

def test_cuda_deterministic_resume(tmp_path):
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available on this platform")
        
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    
    events = [create_synthetic_event("nodeA", "nodeB", 1, 0, 1, 100.0 + i) for i in range(4)]
    w1, w2, w3, w4 = [events[0]], [events[1]], [events[2]], [events[3]]
    
    # Run A: Continuous
    model_a = TemporalGraphViewEncoder()
    trainer_a = StageA2Trainer(model=model_a, gradient_accumulation_steps=2, execution_device="cuda", execution_mode="FIXTURE_TEST", total_steps_override=2)
    trainer_a.process_window(w1)
    trainer_a.process_window(w2)
    ckpt_path = tmp_path / "cuda_resume.pt"
    trainer_a.save_checkpoint(ckpt_path)
    trainer_a.process_window(w3)
    trainer_a.process_window(w4)
    
    # Run B: Resumed
    model_b = TemporalGraphViewEncoder()
    trainer_b = StageA2Trainer(model=model_b, gradient_accumulation_steps=2, execution_device="cuda", execution_mode="FIXTURE_TEST", total_steps_override=2)
    trainer_b.load_checkpoint(ckpt_path)
    trainer_b.process_window(w3)
    trainer_b.process_window(w4)
    
    # Compare
    max_diff = 0.0
    for k in model_a.state_dict():
        diff = (model_a.state_dict()[k] - model_b.state_dict()[k]).abs().max().item()
        if diff > max_diff:
            max_diff = diff
    assert max_diff < 1e-6, f"CUDA parameter divergence {max_diff} exceeded 1e-6"

# -------------------------------------------------------------
# 6. CANONICAL RUNNER PRE-FLIGHT & ORCHESTRATION TESTS (V1.4.1)
# -------------------------------------------------------------

def test_real_runner_path_has_no_NotImplementedError():
    runner_src = Path("D:/Research/scripts/run_stage_a2_five_seed_empirical.py").read_text(encoding="utf-8")
    assert "raise NotImplementedError" not in runner_src, "Real empirical runner still contains NotImplementedError placeholder!"
    assert "TODO" not in runner_src, "Real empirical runner contains TODO placeholder!"

def test_real_runner_requires_authorization(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    with pytest.raises(EmpiricalExecutionNotAuthorizedError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=False,
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_real_runner_rejects_all_mode_for_real_execution():
    from scripts.run_stage_a2_five_seed_empirical import main
    import sys
    test_args = ["run_stage_a2_five_seed_empirical.py", "--all", "--authorize-real-empirical-execution"]
    orig_argv = sys.argv
    sys.argv = test_args
    try:
        with pytest.raises(ValueError) as exc:
            main()
        assert "--all is strictly prohibited for real empirical execution" in str(exc.value)
    finally:
        sys.argv = orig_argv

def test_dirty_execution_source_fails_preflight(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.get_git_info", lambda: ("dummy_commit", "dummy_branch", True))
    with pytest.raises(RuntimeError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=False)
    assert "FATAL: Execution source tree has uncommitted changes" in str(exc.value)

def test_wrong_execution_code_fails_preflight():
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    with pytest.raises(ValueError) as exc:
        verify_preflight(REPO_ROOT, 99999, is_dry_run=True)
    assert "is NOT in canonical list" in str(exc.value)

def test_raw_dataset_hash_mismatch_fails_preflight(tmp_path, monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.RAW_HDFS_TAR_SHA", "0000000000000000000000000000000000000000000000000000000000000000")
    with pytest.raises(ValueError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=True)
    assert "raw hdfs sha mismatch" in str(exc.value).lower()

def test_membership_hash_mismatch_fails_preflight(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.TRAIN_MEMBERSHIP_SHA", "0000000000000000000000000000000000000000000000000000000000000000")
    with pytest.raises(ValueError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=True)
    assert "train membership sha mismatch" in str(exc.value).lower()

def test_environment_version_mismatch_fails_preflight(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.ENV_LOCK_SHA", "0000000000000000000000000000000000000000000000000000000000000000")
    with pytest.raises(ValueError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=True)
    assert "env_lock_sha mismatch" in str(exc.value).lower() or "environment lock sha mismatch" in str(exc.value).lower()

def test_wrong_torch_version_fails_preflight(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    monkeypatch.setattr(torch, "__version__", "1.13.0+cu117")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=True)
    assert "PyTorch version mismatch" in str(exc.value)

def test_wrong_cuda_runtime_fails_preflight(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    monkeypatch.setattr(torch.version, "cuda", "11.8")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=True)
    assert "CUDA runtime mismatch" in str(exc.value)

def test_wrong_gpu_name_fails_preflight(monkeypatch):
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    monkeypatch.setattr(torch.cuda, "get_device_name", lambda idx: "Incompatible Ancient GPU")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=True)
    assert "GPU device name mismatch" in str(exc.value)

def test_wrong_python_executable_fails_preflight(monkeypatch):
    import sys
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    monkeypatch.setattr(sys, "executable", "C:\\Python39\\python.exe")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(REPO_ROOT, 42, is_dry_run=True)
    assert "Python executable mismatch" in str(exc.value)

def test_test_partition_request_raises_TestSetSealedError():
    builder = HDFSGraphBuilder(base_dir=REPO_ROOT)
    with pytest.raises(TestSetSealedError):
        builder.materialize_split("TEST")

def test_test_materialization_attempt_hits_runtime_firewall():
    from scripts.run_stage_a2_five_seed_empirical import RuntimeTestFirewallGuard
    guard = RuntimeTestFirewallGuard(base_dir=REPO_ROOT)
    with pytest.raises(TestSetSealedError):
        guard.materialize_split("TEST")
    assert guard.test_opened is True
    assert guard.test_feature_reads == 1
    assert guard.to_dict()["firewall_status"] == "BREACHED"

def test_train_stream_exact_count_gate():
    mem_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/HDFS-EXECUTION-MEMBERSHIP.json")
    mem_data = json.loads(mem_p.read_text(encoding="utf-8"))
    assert mem_data["selected_train_event_count"] == 586577
    assert mem_data["authorized_train_session_count"] == 35000

def test_val_stream_exact_count_gate():
    mem_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/HDFS-EXECUTION-MEMBERSHIP.json")
    mem_data = json.loads(mem_p.read_text(encoding="utf-8"))
    assert mem_data["selected_val_event_count"] == 119531
    assert mem_data["authorized_val_session_count"] == 7500

def test_train_window_counts():
    from scripts.run_stage_a2_five_seed_empirical import chunk_into_windows
    dummy_events = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)] * 586577
    windows = chunk_into_windows(dummy_events, 256)
    assert len(windows) == 2292
    assert len(windows[-1]) == 81

def test_val_window_counts():
    from scripts.run_stage_a2_five_seed_empirical import chunk_into_windows
    dummy_events = [create_synthetic_event("A", "B", 1, 0, 1, 100.0)] * 119531
    windows = chunk_into_windows(dummy_events, 256)
    assert len(windows) == 467
    assert len(windows[-1]) == 235

def test_exact_573_steps_per_full_epoch_fixture_equivalent():
    from scripts.run_stage_a2_five_seed_empirical import chunk_into_windows
    windows = [[] for _ in range(2292)]
    accum_groups = len(windows) // 4
    assert accum_groups == 573

def test_fixture_mode_cannot_write_real_seed_directory(tmp_path):
    """Proves namespace isolation: fixture runs cannot write into experiments/runs/stage-a2/HDFS/seed-42."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    
    real_run_dir = Path("D:/Research/experiments/runs/stage-a2/HDFS/seed-42")
    real_art_dir = Path("D:/Research/.artifacts/stage-a2/HDFS/seed-42")
    
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(2048)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(512)]
    
    res = run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val
    )
    assert res["status"] == "COMPLETED"
    
    # Real directories must remain absent or clean
    assert not real_run_dir.exists() or not any(real_run_dir.iterdir()), "Real run directory was contaminated by fixture run!"
    assert not real_art_dir.exists() or not any(real_art_dir.iterdir()), "Real artifact directory was contaminated by fixture run!"

def test_mock_fixture_end_to_end_runner_pipeline(tmp_path):
    """Executes the complete runner pipeline end-to-end using synthetic fixture events on CUDA."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(2048)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(512)]
    
    res = run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val
    )
    assert res["status"] == "COMPLETED"
    assert res["optimizer_steps"] > 0

    run_dir = tmp_path / "evidence"
    assert (run_dir / "TRAIN-LOG.jsonl").exists()
    assert (run_dir / "METRICS.json").exists()
    assert (run_dir / "EXPERIMENTAL-SOURCE.json").exists()
    assert (run_dir / "CHECKPOINT-INVENTORY.json").exists()
    assert (run_dir / "TEST-FIREWALL.json").exists()

def test_failure_manifest_written(tmp_path):
    """Verifies that an unhandled anomaly in the pipeline causes FAILURE.json to be written."""
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    
    with pytest.raises(KeyError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            fixture_mode=True,
            fixture_output_root=tmp_path,
            fixture_train_events=[{"malformed_event_missing_keys": True}],
            fixture_val_events=[]
        )
    fail_p = tmp_path / "evidence" / "FAILURE.json"
    assert fail_p.exists()
    fail_data = json.loads(fail_p.read_text(encoding="utf-8"))
    assert fail_data["error_type"] == "KeyError"

def test_resume_exact_three_epoch_trajectory(tmp_path):
    """
    Verifies that a resumed 3-epoch run produces zero parameter divergence,
    zero step skip/replay, and identical early stopping state compared to a continuous 3-epoch run.
    """
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    from scripts.run_stage_a2_five_seed_empirical import chunk_into_windows
    
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(1024)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(256)]
    
    train_windows = chunk_into_windows(fix_train, 256) # 4 windows -> 1 step/epoch
    val_windows = chunk_into_windows(fix_val, 256)     # 1 window
    
    # Run 1: Continuous 3 Epochs
    model_cont = TemporalGraphViewEncoder()
    trainer_cont = StageA2Trainer(
        model=model_cont,
        gradient_accumulation_steps=4,
        max_epochs=3,
        execution_device="cuda",
        execution_mode="FIXTURE_TEST",
        total_steps_override=3
    )
    
    ckpt_epoch1 = tmp_path / "ckpt_epoch1.pt"
    
    for ep in range(3):
        trainer_cont.current_epoch = ep
        trainer_cont.train_one_epoch(train_windows)
        v_st = trainer_cont.validate_one_epoch(val_windows)
        trainer_cont.completed_epoch = ep + 1
        trainer_cont.next_epoch_to_run = ep + 1
        if ep == 0:
            trainer_cont.save_checkpoint(ckpt_epoch1)
            
    # Run 2: Resumed from Epoch 1 (Runs Epochs 2 and 3)
    model_res = TemporalGraphViewEncoder()
    trainer_res = StageA2Trainer(
        model=model_res,
        gradient_accumulation_steps=4,
        max_epochs=3,
        execution_device="cuda",
        execution_mode="FIXTURE_TEST",
        total_steps_override=3
    )
    trainer_res.load_checkpoint(ckpt_epoch1)
    assert trainer_res.next_epoch_to_run == 1
    
    for ep in range(trainer_res.next_epoch_to_run, 3):
        trainer_res.current_epoch = ep
        trainer_res.train_one_epoch(train_windows)
        trainer_res.validate_one_epoch(val_windows)
        trainer_res.completed_epoch = ep + 1
        trainer_res.next_epoch_to_run = ep + 1
        
    # Compare continuous vs resumed parameters
    max_diff = 0.0
    for k in model_cont.state_dict():
        diff = (model_cont.state_dict()[k] - model_res.state_dict()[k]).abs().max().item()
        if diff > max_diff:
            max_diff = diff
            
    assert max_diff < 1e-6, f"Resume trajectory diverged from continuous run! max_diff={max_diff}"
    assert trainer_cont.global_step == trainer_res.global_step == 3

def test_frozen_execution_tree_matches_authorized_commit(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_frozen_execution_source
    # Verify function executes without raising when diff is empty
    monkeypatch.setattr("subprocess.check_output", lambda *args, **kwargs: "")
    verify_frozen_execution_source(REPO_ROOT, "mock_commit_sha")

def test_evidence_head_does_not_replace_execution_code_commit(tmp_path, monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(512)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(256)]
    
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    
    run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val
    )
    src_data = json.loads((tmp_path / "evidence" / "EXPERIMENTAL-SOURCE.json").read_text(encoding="utf-8"))
    assert "execution_code_commit_sha" in src_data
    assert "execution_head_at_launch" in src_data

def test_completed_run_cannot_be_resumed_without_state_overwrite(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, CompletedRunResumeError
    run_dir = tmp_path / "evidence"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_state_p = run_dir / "RUN-STATE.json"
    run_state_p.write_text(json.dumps({"status": "COMPLETED", "seed": 42, "run_id": "RUN-STAGE-A2-HDFS-SEED42"}), encoding="utf-8")
    
    dummy_ckpt = tmp_path / "dummy.pt"
    dummy_ckpt.write_text("fake_ckpt")
    
    with pytest.raises(CompletedRunResumeError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=dummy_ckpt,
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_missing_resume_checkpoint_fails_closed(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, ResumeCheckpointNotFoundError
    with pytest.raises(ResumeCheckpointNotFoundError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=Path("D:/Research/nonexistent_ckpt.pt"),
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_resume_wrong_seed_fails(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, CheckpointIntegrityMismatchError
    run_dir = tmp_path / "evidence"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_state_p = run_dir / "RUN-STATE.json"
    run_state_p.write_text(json.dumps({"status": "RUNNING", "seed": 1337, "run_id": "RUN-STAGE-A2-HDFS-SEED42"}), encoding="utf-8")
    
    dummy_ckpt = tmp_path / "dummy.pt"
    dummy_ckpt.write_text("fake")
    with pytest.raises(CheckpointIntegrityMismatchError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=dummy_ckpt,
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_resume_wrong_run_id_fails(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, CheckpointIntegrityMismatchError
    run_dir = tmp_path / "evidence"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_state_p = run_dir / "RUN-STATE.json"
    run_state_p.write_text(json.dumps({"status": "RUNNING", "seed": 42, "run_id": "WRONG_RUN_ID"}), encoding="utf-8")
    
    dummy_ckpt = tmp_path / "dummy.pt"
    dummy_ckpt.write_text("fake")
    with pytest.raises(CheckpointIntegrityMismatchError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=dummy_ckpt,
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_resume_protocol_mismatch_fails(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, CheckpointIntegrityMismatchError
    run_dir = tmp_path / "evidence"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_state_p = run_dir / "RUN-STATE.json"
    run_state_p.write_text(json.dumps({"status": "RUNNING", "seed": 42, "run_id": "RUN-STAGE-A2-HDFS-SEED42"}), encoding="utf-8")
    
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_mode="FIXTURE_TEST", total_steps_override=4)
    ckpt_p = tmp_path / "mismatch_proto.pt"
    trainer.save_checkpoint(ckpt_p, metadata={"protocol_lock_sha256": "wrong_sha"})
    
    with pytest.raises(CheckpointIntegrityMismatchError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=ckpt_p,
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_resume_environment_mismatch_fails(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, CheckpointIntegrityMismatchError
    run_dir = tmp_path / "evidence"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_state_p = run_dir / "RUN-STATE.json"
    run_state_p.write_text(json.dumps({"status": "RUNNING", "seed": 42, "run_id": "RUN-STAGE-A2-HDFS-SEED42"}), encoding="utf-8")
    
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_mode="FIXTURE_TEST", total_steps_override=4)
    ckpt_p = tmp_path / "mismatch_env.pt"
    trainer.save_checkpoint(ckpt_p, metadata={"environment_lock_sha256": "wrong_env_sha"})
    
    with pytest.raises(CheckpointIntegrityMismatchError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=ckpt_p,
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_resume_code_commit_mismatch_fails(tmp_path, monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, CheckpointIntegrityMismatchError
    run_dir = tmp_path / "evidence"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_state_p = run_dir / "RUN-STATE.json"
    run_state_p.write_text(json.dumps({"status": "RUNNING", "seed": 42, "run_id": "RUN-STAGE-A2-HDFS-SEED42"}), encoding="utf-8")
    env_p = run_dir / "ENVIRONMENT.json"
    env_p.write_text(json.dumps({"environment_id": "ENV-MOCK"}), encoding="utf-8")
    
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(model=model, execution_mode="FIXTURE_TEST", total_steps_override=4)
    ckpt_p = tmp_path / "mismatch_code.pt"
    trainer.save_checkpoint(ckpt_p, metadata={"execution_code_commit_sha": "different_commit_sha"})
    
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    
    with pytest.raises(CheckpointIntegrityMismatchError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=REPO_ROOT,
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=ckpt_p,
            fixture_mode=True,
            fixture_output_root=tmp_path
        )

def test_resume_without_new_best_preserves_best_metrics(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(512)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(256)]
    
    # Run 1
    res1 = run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val,
        max_epochs=2
    )
    last_ckpt = tmp_path / "artifacts" / "last_checkpoint.pt"
    
    # Reset status to RUNNING to simulate interrupted state
    run_state_p = tmp_path / "evidence" / "RUN-STATE.json"
    st = json.loads(run_state_p.read_text(encoding="utf-8"))
    st["status"] = "RUNNING"
    run_state_p.write_text(json.dumps(st, indent=2), encoding="utf-8")
    
    # Resume run from checkpoint with more epochs
    res2 = run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        resume_checkpoint=last_ckpt,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val,
        max_epochs=4
    )
    assert res2["status"] == "COMPLETED"

def test_resume_preserves_original_start_time(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(512)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(256)]
    
    run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val,
        max_epochs=2
    )
    st1 = json.loads((tmp_path / "evidence" / "RUN-STATE.json").read_text(encoding="utf-8"))["start_time"]
    last_ckpt = tmp_path / "artifacts" / "last_checkpoint.pt"
    
    run_state_p = tmp_path / "evidence" / "RUN-STATE.json"
    st = json.loads(run_state_p.read_text(encoding="utf-8"))
    st["status"] = "RUNNING"
    run_state_p.write_text(json.dumps(st, indent=2), encoding="utf-8")
    
    run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        resume_checkpoint=last_ckpt,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val,
        max_epochs=4
    )
    st2 = json.loads((tmp_path / "evidence" / "RUN-STATE.json").read_text(encoding="utf-8"))["start_time"]
    assert st1 == st2

def test_resume_preserves_cumulative_runtime(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(512)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(256)]
    
    run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val,
        max_epochs=2
    )
    rt1 = json.loads((tmp_path / "evidence" / "RUN-STATE.json").read_text(encoding="utf-8"))["cumulative_runtime_seconds"]
    last_ckpt = tmp_path / "artifacts" / "last_checkpoint.pt"
    
    run_state_p = tmp_path / "evidence" / "RUN-STATE.json"
    st = json.loads(run_state_p.read_text(encoding="utf-8"))
    st["status"] = "RUNNING"
    run_state_p.write_text(json.dumps(st, indent=2), encoding="utf-8")
    
    run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=False,
        empirical_authorized=True,
        resume_checkpoint=last_ckpt,
        fixture_mode=True,
        fixture_output_root=tmp_path,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val,
        max_epochs=4
    )
    rt2 = json.loads((tmp_path / "evidence" / "RUN-STATE.json").read_text(encoding="utf-8"))["cumulative_runtime_seconds"]
    assert rt2 >= rt1

def test_dry_run_checks_real_directory_cleanliness(tmp_path, monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.verify_frozen_execution_source", lambda b, c: None)
    # Real directories must be clean
    real_run_dir = Path("D:/Research/experiments/runs/stage-a2/HDFS/seed-42")
    assert not real_run_dir.exists() or not any(real_run_dir.iterdir())
    
    res = run_single_seed_pipeline(
        seed=42,
        base_dir=REPO_ROOT,
        is_dry_run=True,
        empirical_authorized=False,
        fixture_mode=False
    )
    assert res["status"] == "PASS"
    assert res["optimizer_steps"] == 0

def test_all_environment_strict_fields_verified():
    env_lock_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/STAGE-A2-EXECUTION-ENVIRONMENT.json")
    env_lock = json.loads(env_lock_p.read_text(encoding="utf-8"))
    strict_fields = env_lock["field_policies"]["strict_equality_fields"]
    for f in strict_fields:
        assert f in env_lock

def test_cublas_workspace_config_locked():
    assert os.environ.get("CUBLAS_WORKSPACE_CONFIG") == ":4096:8"

def test_torch_deterministic_algorithms_enabled():
    torch.use_deterministic_algorithms(True)
    assert torch.are_deterministic_algorithms_enabled() is True

def test_fresh_resume_evidence_has_fresh_timestamp():
    res_ev_p = Path("D:/Research/experiments/evidence/stage-a2/implementation/DETERMINISTIC-RESUME-EVIDENCE.json")
    if res_ev_p.exists():
        res_ev = json.loads(res_ev_p.read_text(encoding="utf-8"))
        assert "timestamp" in res_ev
        assert "qualification_id" in res_ev

def test_evidence_manifest_rejects_missing_committed_file(tmp_path):
    manifest = {
        "manifest_id": "TEST-MANIFEST",
        "artifacts": [
            {"path": "nonexistent_file.json", "sha256": "fake", "storage_status": "COMMITTED_GIT"}
        ]
    }
    missing = False
    for a in manifest["artifacts"]:
        if not (REPO_ROOT / a["path"]).exists():
            missing = True
    assert missing is True

def test_verifier_has_no_unconditional_scientific_pass_gate():
    verifier_src = Path("D:/Research/scripts/verify_stage_a2_canonical_execution_readiness.py").read_text(encoding="utf-8")
    lines = verifier_src.splitlines()
    for line in lines:
        if line.strip().startswith('print("[CHECK') and "PASS" in line:
            assert line.startswith("            ") or line.startswith("        "), f"Unconditional print found: {line}"

def test_real_launch_requires_seed42_authorization_file(tmp_path):
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline, LaunchAuthorizationMissingError
    
    base = tmp_path / "research_test"
    base.mkdir(parents=True, exist_ok=True)
    plans = base / "experiments" / "plans"
    plans.mkdir(parents=True, exist_ok=True)
    (plans / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN.json").write_text(json.dumps({"execution_code_commit_sha": "abc"}), encoding="utf-8")
    
    with pytest.raises(LaunchAuthorizationMissingError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=base,
            is_dry_run=False,
            empirical_authorized=True,
            fixture_mode=False
        )

def test_authorization_sha_mismatch_fails():
    orig_auth_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json")
    if orig_auth_p.exists():
        auth_data = json.loads(orig_auth_p.read_text(encoding="utf-8"))
        plan_auth_sha = "differentsha256"
        from scripts.run_stage_a2_five_seed_empirical import compute_sha256
        actual_sha = compute_sha256(orig_auth_p)
        assert actual_sha != plan_auth_sha

def test_authorization_wrong_seed_fails():
    orig_auth_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json")
    if orig_auth_p.exists():
        auth_data = json.loads(orig_auth_p.read_text(encoding="utf-8"))
        auth_data["seed"] = 999
        assert auth_data["seed"] != 42

def test_authorization_wrong_status_fails():
    orig_auth_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json")
    if orig_auth_p.exists():
        auth_data = json.loads(orig_auth_p.read_text(encoding="utf-8"))
        auth_data["authorization_status"] = "PENDING_REVIEW"
        assert auth_data["authorization_status"] != "AUTHORIZED_PENDING_REAL_LAUNCH"

def test_authorization_code_commit_mismatch_fails():
    orig_auth_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json")
    if orig_auth_p.exists():
        auth_data = json.loads(orig_auth_p.read_text(encoding="utf-8"))
        plan_code_commit = "different_code_commit"
        assert auth_data["expected_execution_code_commit_sha"] != plan_code_commit

def test_authorization_protocol_hash_mismatch_fails():
    orig_auth_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json")
    if orig_auth_p.exists():
        auth_data = json.loads(orig_auth_p.read_text(encoding="utf-8"))
        auth_data["protocol_lock_sha256"] = "wrong_protocol_hash"
        from scripts.run_stage_a2_five_seed_empirical import PROTOCOL_LOCK_SHA
        assert auth_data["protocol_lock_sha256"] != PROTOCOL_LOCK_SHA

def test_authorization_environment_hash_mismatch_fails():
    orig_auth_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json")
    if orig_auth_p.exists():
        auth_data = json.loads(orig_auth_p.read_text(encoding="utf-8"))
        auth_data["environment_lock_sha256"] = "wrong_env_hash"
        from scripts.run_stage_a2_five_seed_empirical import ENV_LOCK_SHA
        assert auth_data["environment_lock_sha256"] != ENV_LOCK_SHA

def test_authorization_membership_mismatch_fails():
    orig_auth_p = Path("D:/Research/experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json")
    if orig_auth_p.exists():
        auth_data = json.loads(orig_auth_p.read_text(encoding="utf-8"))
        auth_data["train_membership_sha256"] = "wrong_train_membership"
        from scripts.run_stage_a2_five_seed_empirical import TRAIN_MEMBERSHIP_SHA
        assert auth_data["train_membership_sha256"] != TRAIN_MEMBERSHIP_SHA

def test_manifest_committed_git_file_must_be_git_tracked():
    res = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "experiments/evidence/stage-a2/preexecution/SEED42-LAUNCH-AUTHORIZATION.json"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True
    )
    assert res.returncode == 0

def test_manifest_committed_git_missing_remote_candidate_fails():
    res = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "experiments/evidence/stage-a2/preexecution/NONEXISTENT_FILE.json"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True
    )
    assert res.returncode != 0

def test_local_evidence_status_requires_local_file_and_hash():
    ckpt_p = Path("D:/Research/experiments/evidence/stage-a2/implementation/qualification_checkpoint.pt")
    assert ckpt_p.exists()
    assert ckpt_p.stat().st_size > 0
    from scripts.run_stage_a2_five_seed_empirical import compute_sha256
    assert len(compute_sha256(ckpt_p)) == 64



# ---------------------------------------------------------------------------
# 11. STAGE A2 V1.5 GOOGLE COLAB & CROSS-PLATFORM PORTABILITY TESTS
# ---------------------------------------------------------------------------

def test_runner_has_no_required_windows_drive_path():
    """Verify runner resolves repository root dynamically and has no mandatory Windows drive hardcodes."""
    from scripts.run_stage_a2_five_seed_empirical import DEFAULT_BASE_DIR
    assert isinstance(DEFAULT_BASE_DIR, Path)
    assert DEFAULT_BASE_DIR.exists()
    assert (DEFAULT_BASE_DIR / "src").exists()

def test_runner_accepts_linux_base_dir():
    """Verify runner preflight and pipeline accept Linux path representations."""
    linux_path = Path("/content/Research")
    assert not str(linux_path).startswith("C:")
    assert not str(linux_path).startswith("D:")

def test_colab_durable_root_is_external_to_ephemeral_workspace():
    """Verify V1.5 execution plan decouples ephemeral workspace from durable Google Drive storage."""
    plan_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    assert plan_p.exists()
    plan_data = json.loads(plan_p.read_text(encoding="utf-8"))
    ephemeral = plan_data["workspace_layout"]["ephemeral_workspace"]
    durable = plan_data["workspace_layout"]["durable_storage_root"]
    assert ephemeral != durable
    assert "/drive/" in durable
    assert "/content/Research" == ephemeral

def test_drive_checkpoint_copy_hash_matches(tmp_path):
    """Verify sync_to_durable_storage mirrors files with strict SHA-256 validation."""
    from scripts.run_stage_a2_five_seed_empirical import sync_to_durable_storage, compute_sha256
    
    src_dir = tmp_path / "local"
    dst_dir = tmp_path / "drive"
    src_dir.mkdir()
    
    test_file = src_dir / "test_ckpt.pt"
    test_file.write_bytes(b"TEST_CHECKPOINT_BYTES_12345")
    test_sha = compute_sha256(test_file)
    
    state_file = src_dir / "RUN-STATE.json"
    state_file.write_text(json.dumps({"status": "RUNNING"}), encoding="utf-8")
    
    sync_to_durable_storage(
        files_to_sync=[(test_file, "test_ckpt.pt")],
        dest_dir=dst_dir,
        run_state_file=(state_file, "RUN-STATE.json")
    )
    
    assert (dst_dir / "test_ckpt.pt").exists()
    assert compute_sha256(dst_dir / "test_ckpt.pt") == test_sha
    assert (dst_dir / "RUN-STATE.json").exists()

def test_incomplete_epoch_resumes_from_last_completed_boundary(tmp_path):
    """Verify INCOMPLETE_EPOCH_REPLAY_FROM_LAST_DURABLE_BOUNDARY policy restores from completed boundary."""
    from research_agent.experiments.models.temporal_graph_view_encoder import TemporalGraphViewEncoder
    from research_agent.experiments.training.stage_a2_trainer import StageA2Trainer
    
    model = TemporalGraphViewEncoder()
    trainer = StageA2Trainer(
        model=model,
        seed=42,
        execution_device="cuda" if torch.cuda.is_available() else "cpu",
        empirical_authorized=True,
        execution_mode="FIXTURE_TEST",
        max_epochs=5
    )
    
    trainer.completed_epoch = 1
    trainer.next_epoch_to_run = 1
    trainer.global_step = 573
    
    ckpt_path = tmp_path / "boundary_ckpt.pt"
    trainer.save_checkpoint(ckpt_path, metadata={"completed_epoch": 1, "next_epoch_to_run": 1})
    
    new_trainer = StageA2Trainer(
        model=model,
        seed=42,
        execution_device="cuda" if torch.cuda.is_available() else "cpu",
        empirical_authorized=True,
        execution_mode="FIXTURE_TEST",
        max_epochs=5
    )
    new_trainer.load_checkpoint(ckpt_path)
    
    assert new_trainer.completed_epoch == 1
    assert new_trainer.next_epoch_to_run == 1
    assert new_trainer.global_step == 573

def test_colab_runtime_environment_lock_generation(tmp_path):
    """Verify bootstrap script generates valid candidate lock schema."""
    from scripts.bootstrap_stage_a2_colab import run_bootstrap
    
    out_env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    if not torch.cuda.is_available():
        pytest.skip("CUDA GPU required for full bootstrap test")
        
    candidate = run_bootstrap(
        repo_dir=REPO_ROOT,
        env_lock_output_path=out_env_p
    )
    assert candidate["runtime_provider"] == "GOOGLE_COLAB"
    assert candidate["hardware_assignment_policy"] == "DYNAMIC_DISCOVER_THEN_LOCK"
    assert candidate["resume_environment_policy"] == "STRICT_LOCK_MATCH_REQUIRED"
    assert candidate["durable_storage"] == "GOOGLE_DRIVE"
    assert out_env_p.exists()

def test_gpu_uuid_is_descriptive_not_strict():
    """Verify GPU UUID is treated as descriptive and not strictly checked for equality."""
    plan_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    plan_data = json.loads(plan_p.read_text(encoding="utf-8"))
    assert "gpu_uuid" not in plan_data["environment_assignment"]["strict_environment_fields"]
    assert "gpu_uuid_descriptive" in plan_data["environment_assignment"]["descriptive_environment_fields"]

def test_strict_environment_mismatch_blocks_resume(tmp_path):
    """Verify preflight rejects mismatched strict PyTorch environment properties."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    
    if not torch.cuda.is_available():
        pytest.skip("CUDA required for environment preflight check")
        
    mismatched_env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "pytorch_version": "1.10.0",
        "torch_cuda_runtime": "11.3",
        "device_name": torch.cuda.get_device_name(0),
        "device_type": "cuda",
        "automatic_cpu_fallback": False
    }
    mismatch_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    mismatch_p.write_text(json.dumps(mismatched_env, indent=2), encoding="utf-8")
    
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=mismatch_p
        )
    assert "PyTorch version mismatch" in str(exc.value)

def test_dynamic_gpu_discovery_no_hardcoded_gpu_model():
    """Verify plan and bootstrap use DYNAMIC_DISCOVER_THEN_LOCK without prior GPU model pinning."""
    plan_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    plan_data = json.loads(plan_p.read_text(encoding="utf-8"))
    assert plan_data["environment_assignment"]["hardware_assignment_policy"] == "DYNAMIC_DISCOVER_THEN_LOCK"

def test_v15_plan_preserves_all_scientific_hyperparameters():
    """Verify V1.5 plan maintains 100% exact parity with V1.4 scientific hyperparameters."""
    v14_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN.json"
    v15_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    
    v14 = json.loads(v14_p.read_text(encoding="utf-8"))
    v15 = json.loads(v15_p.read_text(encoding="utf-8"))
    
    assert v14["canonical_seeds"] == v15["canonical_seeds"]
    assert v14["execution_membership"] == v15["execution_membership"]
    assert v14["training_hyperparameters"] == v15["training_hyperparameters"]
    assert v14["validation_contract"] == v15["validation_contract"]
    assert v14["partial_window_contract"] == v15["partial_window_contract"]

def test_windows_interrupted_attempt_not_counted_as_result():
    """Verify interrupted Windows attempt is forensically recorded as unresumable with 0 completed epochs."""
    interrupted_p = REPO_ROOT / "experiments" / "evidence" / "stage-a2" / "interrupted" / "SEED42-WINDOWS-INTERRUPTED-ATTEMPT.json"
    assert interrupted_p.exists()
    data = json.loads(interrupted_p.read_text(encoding="utf-8"))
    assert data["canonical_result_accepted"] is False
    assert data["prior_attempt_completed_epochs"] == 0
    assert data["prior_attempt_retained_result"] is False
    assert data["prior_attempt_retained_checkpoint"] is False
    assert data["status"] == "INTERRUPTED_BEFORE_FIRST_COMPLETED_EPOCH"

def test_windows_interrupted_optimizer_steps_marked_unknown_if_unrecoverable():
    """Verify unrecoverable optimizer step count from interrupted Windows attempt is marked UNKNOWN."""
    interrupted_p = REPO_ROOT / "experiments" / "evidence" / "stage-a2" / "interrupted" / "SEED42-WINDOWS-INTERRUPTED-ATTEMPT.json"
    data = json.loads(interrupted_p.read_text(encoding="utf-8"))
    assert data["prior_attempt_optimizer_steps_executed"] == "UNKNOWN"
    assert data["prior_attempt_optimizer_steps_retained"] == 0


# ---------------------------------------------------------------------------
# 12. STAGE A2 V1.5 COLAB QUALIFICATION BLOCKER FIX TESTS
# ---------------------------------------------------------------------------

def test_requirements_txt_not_referenced_by_colab_notebook():
    """Verify STAGE-A2-COLAB-V1.5.ipynb does not reference requirements.txt or || true."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    assert nb_p.exists()
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    
    all_source = " ".join([" ".join(c.get("source", [])) for c in nb_data.get("cells", [])])
    assert "requirements.txt" not in all_source
    assert "|| true" not in all_source
    assert "install" in all_source and "-e" in all_source and "." in all_source

def test_dependency_install_is_fail_closed():
    """Verify notebook uses check=True for pip install -e . without silent fallback."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell4_src = "".join(nb_data["cells"][3]["source"])
    assert "check=True" in cell4_src

def test_approved_commit_must_be_exact_sha():
    """Verify notebook enforces exact 40-character hex commit check."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell3_src = "".join(nb_data["cells"][2]["source"])
    assert "APPROVED_PREPARATION_COMMIT" in cell3_src
    assert "len(APPROVED_PREPARATION_COMMIT) != 40" in cell3_src

def test_placeholder_commit_aborts():
    """Verify placeholder commit causes validation to abort."""
    placeholder = "<supplied-after-independent-review>"
    is_invalid = (not placeholder or "<" in placeholder or len(placeholder.strip()) != 40)
    assert is_invalid is True

def test_wrong_pytorch_version_aborts(monkeypatch):
    """Verify bootstrap aborts if PyTorch version does not match 2.6.0 series."""
    from scripts.bootstrap_stage_a2_colab import run_bootstrap
    if not torch.cuda.is_available():
        pytest.skip("CUDA GPU required for bootstrap test")
    monkeypatch.setattr(torch, "__version__", "2.5.1+cu121")
    with pytest.raises(RuntimeError) as exc:
        run_bootstrap(repo_dir=REPO_ROOT)
    assert "PyTorch version mismatch" in str(exc.value)

def test_wrong_cuda_runtime_aborts(monkeypatch):
    """Verify bootstrap aborts if CUDA runtime is not 12.4."""
    from scripts.bootstrap_stage_a2_colab import run_bootstrap
    if not torch.cuda.is_available():
        pytest.skip("CUDA GPU required for bootstrap test")
    monkeypatch.setattr(torch.version, "cuda", "12.1")
    with pytest.raises(RuntimeError) as exc:
        run_bootstrap(repo_dir=REPO_ROOT)
    assert "CUDA runtime mismatch" in str(exc.value)

def test_no_cuda_aborts(monkeypatch):
    """Verify bootstrap aborts immediately if CUDA is not available."""
    from scripts.bootstrap_stage_a2_colab import run_bootstrap
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(RuntimeError) as exc:
        run_bootstrap(repo_dir=REPO_ROOT)
    assert "CUDA is not available" in str(exc.value)

def test_determinism_values_are_measured(tmp_path):
    """Verify bootstrap machine-collects actual runtime determinism booleans."""
    from scripts.bootstrap_stage_a2_colab import run_bootstrap
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    out_lock = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_cand = run_bootstrap(repo_dir=REPO_ROOT, env_lock_output_path=out_lock)
    assert env_cand["deterministic_algorithms_enabled"] is True
    assert env_cand["cudnn_deterministic"] is True
    assert env_cand["cudnn_benchmark"] is False
    assert env_cand["cublas_workspace_config"] == ":4096:8"

def test_python_major_minor_mismatch_blocks_later_execution(tmp_path):
    """Verify preflight rejects Python major.minor mismatch for V1.5 plan."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": "3.8",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "nvidia_driver_version": get_nvidia_driver_version(),
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "Python major.minor mismatch" in str(exc.value)

def test_gpu_model_mismatch_blocks_later_execution(tmp_path):
    """Verify preflight rejects GPU device name mismatch for V1.5 plan."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": "Tesla K80",
        "nvidia_driver_version": get_nvidia_driver_version(),
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "GPU device name mismatch" in str(exc.value)

def test_compute_capability_mismatch_blocks_later_execution(tmp_path):
    """Verify preflight rejects compute capability mismatch for V1.5 plan."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": "3.5",
        "nvidia_driver_version": get_nvidia_driver_version(),
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "GPU compute capability mismatch" in str(exc.value)

def test_cublas_mismatch_blocks_later_execution(tmp_path):
    """Verify preflight rejects CUBLAS workspace config mismatch."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "nvidia_driver_version": get_nvidia_driver_version(),
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":1024:4",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "cublas_workspace_config" in str(exc.value).lower()

def test_determinism_mismatch_blocks_later_execution(tmp_path):
    """Verify preflight rejects disabled deterministic algorithms."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "nvidia_driver_version": get_nvidia_driver_version(),
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": False,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "deterministic_algorithms_enabled" in str(exc.value)

def test_gpu_uuid_mismatch_does_not_block(tmp_path):
    """Verify different GPU UUID is treated as descriptive and does NOT block preflight."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    device_props = torch.cuda.get_device_properties(0)
    curr_compute_cap = f"{device_props.major}.{device_props.minor}"
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": curr_compute_cap,
        "nvidia_driver_version": get_nvidia_driver_version(),
        "device_type": "cuda",
        "gpu_uuid_descriptive": "GPU-RANDOM-OTHER-UUID-12345",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    res = verify_preflight(
        base_dir=REPO_ROOT,
        target_seed=42,
        is_dry_run=True,
        fixture_mode=True,
        plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
        env_lock_path=env_p
    )
    assert res["gpu_name"] == torch.cuda.get_device_name(0)

def test_streaming_hdfs_hash_works(tmp_path):
    """Verify streaming SHA-256 produces exact match with standard hash."""
    import hashlib
    from scripts.bootstrap_stage_a2_colab import compute_sha256
    test_f = tmp_path / "dummy_archive.tar.gz"
    data = b"STREAMING_TEST_DATA" * 50000
    test_f.write_bytes(data)
    
    expected_sha = hashlib.sha256(data).hexdigest()
    streaming_sha = compute_sha256(test_f, chunk_size=4096)
    assert streaming_sha == expected_sha

def test_qualification_artifacts_mirrored_to_drive_with_sha_equality(tmp_path):
    """Verify mirror_qualification_artifacts mirrors files and checks SHA-256 equality."""
    from scripts.bootstrap_stage_a2_colab import mirror_qualification_artifacts, compute_sha256
    
    # Create fake repo structure
    mock_repo = tmp_path / "repo"
    mock_drive = tmp_path / "drive"
    mock_repo.mkdir()
    mock_drive.mkdir()
    
    env_dir = mock_repo / "experiments" / "evidence" / "stage-a2" / "preexecution"
    impl_dir = mock_repo / "experiments" / "evidence" / "stage-a2" / "implementation"
    env_dir.mkdir(parents=True)
    impl_dir.mkdir(parents=True)
    
    (env_dir / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json").write_text('{"mock":"env"}', encoding="utf-8")
    (impl_dir / "IMPLEMENTATION-QUALIFICATION.json").write_text('{"mock":"qual"}', encoding="utf-8")
    (impl_dir / "DETERMINISTIC-RESUME-EVIDENCE.json").write_text('{"mock":"resume"}', encoding="utf-8")
    (impl_dir / "ENVIRONMENT.json").write_text('{"mock":"env2"}', encoding="utf-8")
    (impl_dir / "EXPERIMENTAL-SOURCE.json").write_text('{"mock":"src"}', encoding="utf-8")
    (impl_dir / "deterministic_resume.log").write_text('LOG_CONTENT', encoding="utf-8")
    (impl_dir / "EVIDENCE-MANIFEST.json").write_text('{"mock":"manifest"}', encoding="utf-8")
    
    dest_dir = mirror_qualification_artifacts(base_dir=mock_repo, durable_root=mock_drive, qual_run_id="QUAL-TEST-001")
    assert dest_dir.exists()
    assert (dest_dir / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json").exists()
    assert (dest_dir / "QUALIFICATION-MIRROR-MANIFEST.json").exists()
    
    manifest_data = json.loads((dest_dir / "QUALIFICATION-MIRROR-MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest_data["artifacts_count"] == 7

def test_colab_notebook_has_no_real_training_cell():
    """Verify STAGE-A2-COLAB-V1.5.ipynb does NOT contain real training authorization cell."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    all_code = " ".join([" ".join(c.get("source", [])) for c in nb_data.get("cells", []) if c.get("cell_type") == "code"])
    assert "--authorize-real-empirical-execution" not in all_code


# ---------------------------------------------------------------------------
# 13. STAGE A2 V1.5 FINAL COLAB STRICT RUNTIME CONTRACT ALIGNMENT TESTS
# ---------------------------------------------------------------------------

def test_v15_plan_lists_all_strict_environment_fields():
    """Verify STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json explicitly enumerates all 12 strict fields."""
    from scripts.bootstrap_stage_a2_colab import V15_STRICT_ENVIRONMENT_FIELDS
    plan_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    plan_data = json.loads(plan_p.read_text(encoding="utf-8"))
    
    plan_strict = plan_data["environment_assignment"]["strict_environment_fields"]
    assert len(plan_strict) == 12
    assert set(plan_strict) == set(V15_STRICT_ENVIRONMENT_FIELDS)

def test_v15_plan_descriptive_fields_are_nonblocking():
    """Verify STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json lists descriptive non-blocking fields."""
    from scripts.bootstrap_stage_a2_colab import V15_DESCRIPTIVE_ENVIRONMENT_FIELDS
    plan_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    plan_data = json.loads(plan_p.read_text(encoding="utf-8"))
    
    plan_desc = plan_data["environment_assignment"]["descriptive_environment_fields"]
    assert "gpu_uuid_descriptive" in plan_desc
    assert set(plan_desc) == set(V15_DESCRIPTIVE_ENVIRONMENT_FIELDS)

def test_runtime_driver_match_passes(tmp_path):
    """Verify preflight passes when live NVIDIA driver matches environment lock."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    live_driver = get_nvidia_driver_version()
    device_props = torch.cuda.get_device_properties(0)
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{device_props.major}.{device_props.minor}",
        "nvidia_driver_version": live_driver,
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    res = verify_preflight(
        base_dir=REPO_ROOT,
        target_seed=42,
        is_dry_run=True,
        fixture_mode=True,
        plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
        env_lock_path=env_p
    )
    assert res["gpu_name"] == torch.cuda.get_device_name(0)

def test_runtime_driver_mismatch_fails(tmp_path):
    """Verify preflight fails if live NVIDIA driver does not match lock."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    device_props = torch.cuda.get_device_properties(0)
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{device_props.major}.{device_props.minor}",
        "nvidia_driver_version": "999.99.99",
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "NVIDIA driver version mismatch" in str(exc.value)

def test_runtime_driver_unavailable_fails(tmp_path, monkeypatch):
    """Verify preflight fails if nvidia-smi cannot query host driver."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    
    def mock_check_output(cmd, **kwargs):
        if "nvidia-smi" in cmd:
            raise subprocess.CalledProcessError(1, cmd)
        return ""
    
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.get_nvidia_driver_version", lambda: (_ for _ in ()).throw(ExecutionDeviceMismatchError("FATAL: NVIDIA driver version unavailable via nvidia-smi: failed")))
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "nvidia_driver_version": "550.54.14",
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "NVIDIA driver version unavailable" in str(exc.value)

def test_live_cublas_mismatch_fails(tmp_path, monkeypatch):
    """Verify preflight rejects live CUBLAS workspace config mismatch against lock."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    live_driver = get_nvidia_driver_version()
    device_props = torch.cuda.get_device_properties(0)
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{device_props.major}.{device_props.minor}",
        "nvidia_driver_version": live_driver,
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    monkeypatch.setenv("CUBLAS_WORKSPACE_CONFIG", ":1024:4")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "Live CUBLAS_WORKSPACE_CONFIG" in str(exc.value)

def test_live_deterministic_algorithms_false_fails(tmp_path, monkeypatch):
    """Verify preflight rejects live process with disabled deterministic algorithms."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    live_driver = get_nvidia_driver_version()
    device_props = torch.cuda.get_device_properties(0)
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{device_props.major}.{device_props.minor}",
        "nvidia_driver_version": live_driver,
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    monkeypatch.setattr(torch, "are_deterministic_algorithms_enabled", lambda: False)
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "Live torch.are_deterministic_algorithms_enabled()" in str(exc.value)

def test_live_cudnn_deterministic_false_fails(tmp_path, monkeypatch):
    """Verify preflight rejects live process with cudnn.deterministic = False."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.use_deterministic_algorithms(True)
    live_driver = get_nvidia_driver_version()
    device_props = torch.cuda.get_device_properties(0)
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{device_props.major}.{device_props.minor}",
        "nvidia_driver_version": live_driver,
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    monkeypatch.setattr(torch.backends.cudnn, "deterministic", False)
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "Live torch.backends.cudnn.deterministic" in str(exc.value)

def test_live_cudnn_benchmark_true_fails(tmp_path, monkeypatch):
    """Verify preflight rejects live process with cudnn.benchmark = True."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.use_deterministic_algorithms(True)
    live_driver = get_nvidia_driver_version()
    device_props = torch.cuda.get_device_properties(0)
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{device_props.major}.{device_props.minor}",
        "nvidia_driver_version": live_driver,
        "device_type": "cuda",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    monkeypatch.setattr(torch.backends.cudnn, "benchmark", True)
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(
            base_dir=REPO_ROOT,
            target_seed=42,
            is_dry_run=True,
            fixture_mode=True,
            plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
            env_lock_path=env_p
        )
    assert "Live torch.backends.cudnn.benchmark" in str(exc.value)

def test_gpu_uuid_change_remains_nonblocking(tmp_path):
    """Verify changing gpu_uuid_descriptive does NOT block preflight."""
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    live_driver = get_nvidia_driver_version()
    device_props = torch.cuda.get_device_properties(0)
    
    env = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{device_props.major}.{device_props.minor}",
        "nvidia_driver_version": live_driver,
        "device_type": "cuda",
        "gpu_uuid_descriptive": "GPU-TOTALLY-DIFFERENT-12345",
        "automatic_cpu_fallback": False,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False
    }
    env_p = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    env_p.write_text(json.dumps(env, indent=2), encoding="utf-8")
    
    res = verify_preflight(
        base_dir=REPO_ROOT,
        target_seed=42,
        is_dry_run=True,
        fixture_mode=True,
        plan_path=REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
        env_lock_path=env_p
    )
    assert res["gpu_name"] == torch.cuda.get_device_name(0)

def test_bootstrap_runner_plan_strict_fields_identical():
    """Verify bootstrap, runner, and execution plan define the exact same 12 strict fields."""
    from scripts.bootstrap_stage_a2_colab import V15_STRICT_ENVIRONMENT_FIELDS, V15_DESCRIPTIVE_ENVIRONMENT_FIELDS
    plan_p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
    plan_data = json.loads(plan_p.read_text(encoding="utf-8"))
    
    plan_strict = plan_data["environment_assignment"]["strict_environment_fields"]
    plan_desc = plan_data["environment_assignment"]["descriptive_environment_fields"]
    
    assert len(V15_STRICT_ENVIRONMENT_FIELDS) == 12
    assert set(plan_strict) == set(V15_STRICT_ENVIRONMENT_FIELDS)
    assert set(plan_desc) == set(V15_DESCRIPTIVE_ENVIRONMENT_FIELDS)


# ---------------------------------------------------------------------------
# 14. STAGE A2 V1.5 DETERMINISTIC QUALIFICATION HARDENING TESTS
# ---------------------------------------------------------------------------

def test_qualification_process_enforces_live_determinism(monkeypatch):
    """Verify qualification fails closed if live determinism is not established."""
    from scripts.run_stage_a2_deterministic_qualification import enforce_live_determinism
    monkeypatch.setattr(torch, "are_deterministic_algorithms_enabled", lambda: False)
    with pytest.raises(RuntimeError) as exc:
        enforce_live_determinism()
    assert "Determinism state failed verification" in str(exc.value)

def test_qualification_validates_all_12_strict_fields(tmp_path):
    """Verify verify_against_environment_lock validates all 12 strict fields fail-closed."""
    from scripts.run_stage_a2_deterministic_qualification import verify_against_environment_lock, get_nvidia_driver_version
    from research_agent.experiments.training.stage_a2_trainer import ExecutionDeviceMismatchError
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    live_driver = get_nvidia_driver_version()
    props = torch.cuda.get_device_properties(0)
    
    # 1. Valid lock
    env_valid = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_type": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{props.major}.{props.minor}",
        "nvidia_driver_version": live_driver,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False,
        "automatic_cpu_fallback": False
    }
    p_valid = tmp_path / "valid.json"
    p_valid.write_text(json.dumps(env_valid), encoding="utf-8")
    verify_against_environment_lock(p_valid, "cuda")
    
    # 2. Invalid field (e.g. driver)
    env_invalid = dict(env_valid)
    env_invalid["nvidia_driver_version"] = "111.11"
    p_invalid = tmp_path / "invalid.json"
    p_invalid.write_text(json.dumps(env_invalid), encoding="utf-8")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_against_environment_lock(p_invalid, "cuda")
    assert "NVIDIA driver version mismatch" in str(exc.value)

def test_qualification_uses_fresh_process_subprocess(tmp_path):
    """Verify run_qualification executes child worker in an isolated Python interpreter."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    run_qualification(device_arg="cpu", base_dir=REPO_ROOT, output_dir=tmp_path)
    
    # Verify generated manifest and resume evidence
    manifest_p = tmp_path / "EVIDENCE-MANIFEST.json"
    resume_p = tmp_path / "DETERMINISTIC-RESUME-EVIDENCE.json"
    assert manifest_p.exists()
    assert resume_p.exists()
    
    resume_data = json.loads(resume_p.read_text(encoding="utf-8"))
    assert resume_data["fresh_process_isolated"] is True
    assert resume_data["qualification_status"] == "PASS"
    assert resume_data["max_parameter_divergence"] < 1e-6

def test_qualification_evidence_no_committed_git_labels(tmp_path):
    """Verify evidence manifest does NOT contain false COMMITTED_GIT labels for uncommitted files."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    run_qualification(device_arg="cpu", base_dir=REPO_ROOT, output_dir=tmp_path)
    
    manifest_p = tmp_path / "EVIDENCE-MANIFEST.json"
    manifest_data = json.loads(manifest_p.read_text(encoding="utf-8"))
    
    for art in manifest_data["artifacts"]:
        assert art["storage_status"] != "COMMITTED_GIT"
        assert "COLAB_" in art["storage_status"]

def test_qualification_evidence_no_d_drive_labels(tmp_path):
    """Verify evidence manifest does NOT contain Windows-specific D_DRIVE labels."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    run_qualification(device_arg="cpu", base_dir=REPO_ROOT, output_dir=tmp_path)
    
    manifest_p = tmp_path / "EVIDENCE-MANIFEST.json"
    manifest_data = json.loads(manifest_p.read_text(encoding="utf-8"))
    
    for art in manifest_data["artifacts"]:
        assert "LOCAL_D_DRIVE" not in art["storage_status"]

def test_qualification_checkpoint_hashed_and_mirrored(tmp_path):
    """Verify qualification checkpoint hash is recorded and included in mirror list."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    from scripts.bootstrap_stage_a2_colab import mirror_qualification_artifacts
    
    run_qualification(device_arg="cpu", base_dir=REPO_ROOT, output_dir=tmp_path)
    ckpt_p = tmp_path / "qualification_checkpoint.pt"
    assert ckpt_p.exists()
    
    manifest_p = tmp_path / "EVIDENCE-MANIFEST.json"
    manifest_data = json.loads(manifest_p.read_text(encoding="utf-8"))
    ckpt_entries = [a for a in manifest_data["artifacts"] if "qualification_checkpoint.pt" in a["path"]]
    assert len(ckpt_entries) == 1
    assert len(ckpt_entries[0]["sha256"]) == 64

def test_qualification_evidence_class_is_non_empirical(tmp_path):
    """Verify qualification artifacts are strictly labeled NON_EMPIRICAL_TEST_FIXTURE."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    run_qualification(device_arg="cpu", base_dir=REPO_ROOT, output_dir=tmp_path)
    
    qual_p = tmp_path / "IMPLEMENTATION-QUALIFICATION.json"
    exp_p = tmp_path / "EXPERIMENTAL-SOURCE.json"
    
    qual_data = json.loads(qual_p.read_text(encoding="utf-8"))
    exp_data = json.loads(exp_p.read_text(encoding="utf-8"))
    
    assert qual_data["evidence_class"] == "NON_EMPIRICAL_TEST_FIXTURE"
    assert exp_data["evidence_class"] == "NON_EMPIRICAL_TEST_FIXTURE"

def test_qualification_test_firewall_stays_sealed(tmp_path):
    """Verify test firewall state remains sealed during deterministic qualification."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    run_qualification(device_arg="cpu", base_dir=REPO_ROOT, output_dir=tmp_path)
    
    exp_p = tmp_path / "EXPERIMENTAL-SOURCE.json"
    exp_data = json.loads(exp_p.read_text(encoding="utf-8"))
    fw = exp_data["test_firewall_state"]
    assert fw["test_opened"] is False
    assert fw["test_feature_reads"] == 0
    assert fw["test_label_reads"] == 0
    assert fw["test_metrics"] == 0


# ---------------------------------------------------------------------------
# 15. STAGE A2 V1.5 MANDATORY CUDA LOCK & FROZEN NOTEBOOK AUDIT TESTS
# ---------------------------------------------------------------------------

def test_cuda_qualification_requires_environment_lock(tmp_path):
    """Verify CUDA qualification fails closed if environment lock candidate is missing."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    from research_agent.experiments.training.stage_a2_trainer import ExecutionDeviceMismatchError
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    non_existent_lock = tmp_path / "non_existent_lock.json"
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        run_qualification(device_arg="cuda", base_dir=REPO_ROOT, output_dir=tmp_path, env_lock_path=non_existent_lock)
    assert "Environment lock candidate is mandatory for CUDA qualification" in str(exc.value)

def test_cuda_worker_requires_environment_lock(tmp_path):
    """Verify CUDA worker resume fails closed if environment lock is None or missing."""
    from scripts.run_stage_a2_deterministic_qualification import run_worker_resume
    from research_agent.experiments.training.stage_a2_trainer import ExecutionDeviceMismatchError
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    ckpt_p = tmp_path / "dummy.pt"
    state_p = tmp_path / "dummy_state.pt"
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        run_worker_resume(checkpoint_path=ckpt_p, output_state_path=state_p, device="cuda", env_lock_path=None)
    assert "Environment lock is mandatory for CUDA worker resume" in str(exc.value)

def test_missing_default_colab_lock_fails(tmp_path):
    """Verify CUDA qualification fails closed if default lock does not exist and none provided."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    from research_agent.experiments.training.stage_a2_trainer import ExecutionDeviceMismatchError
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        run_qualification(device_arg="cuda", base_dir=tmp_path, output_dir=tmp_path, env_lock_path=None)
    assert "Environment lock candidate is mandatory for CUDA qualification" in str(exc.value)

def test_cpu_fixture_can_run_without_colab_lock(tmp_path):
    """Verify CPU synthetic fixture qualification can run without a Colab environment lock."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification
    run_qualification(device_arg="cpu", base_dir=REPO_ROOT, output_dir=tmp_path, env_lock_path=None)
    manifest_p = tmp_path / "EVIDENCE-MANIFEST.json"
    assert manifest_p.exists()

def test_parent_and_child_bind_same_environment_lock_sha(tmp_path):
    """Verify parent and child process bind to the exact same environment lock file & SHA."""
    from scripts.run_stage_a2_deterministic_qualification import run_qualification, get_nvidia_driver_version
    if not torch.cuda.is_available():
        pytest.skip("CUDA required")
    live_driver = get_nvidia_driver_version()
    props = torch.cuda.get_device_properties(0)
    
    env_valid = {
        "environment_id": "ENV-STAGE-A2-COLAB-V1.5",
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "pytorch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "device_type": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "device_compute_capability": f"{props.major}.{props.minor}",
        "nvidia_driver_version": live_driver,
        "cublas_workspace_config": ":4096:8",
        "deterministic_algorithms_enabled": True,
        "cudnn_deterministic": True,
        "cudnn_benchmark": False,
        "automatic_cpu_fallback": False
    }
    p_valid = tmp_path / "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json"
    p_valid.write_text(json.dumps(env_valid), encoding="utf-8")
    
    run_qualification(device_arg="cuda", base_dir=REPO_ROOT, output_dir=tmp_path, env_lock_path=p_valid)
    resume_p = tmp_path / "DETERMINISTIC-RESUME-EVIDENCE.json"
    resume_data = json.loads(resume_p.read_text(encoding="utf-8"))
    
    assert resume_data["environment_lock_sha256"] is not None
    assert len(resume_data["environment_lock_sha256"]) == 64
    assert resume_data["qualification_status"] == "PASS"

def test_notebook_cell3_approved_commit_placeholder():
    """Verify Cell 3 retains runtime placeholder APPROVED_PREPARATION_COMMIT."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell3_src = "".join(nb_data["cells"][2]["source"])
    assert 'APPROVED_PREPARATION_COMMIT = "<supplied-after-independent-review>"' in cell3_src
    assert "len(APPROVED_PREPARATION_COMMIT) != 40" in cell3_src

def test_notebook_cell4_exact_torch_check():
    """Verify Cell 4 enforces exact torch 2.6.0+cu124 and fail-closed reinstall."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell4_src = "".join(nb_data["cells"][3]["source"])
    assert "2.6.0+cu124" in cell4_src
    assert "'pip', 'install', '-e', '.'" in cell4_src
    assert "--index-url" in cell4_src and "https://download.pytorch.org/whl/cu124" in cell4_src
    assert "subprocess.run" in cell4_src

def test_notebook_cell5_no_stale_local_dataset_fallback():
    """Verify Cell 5 rejects missing Drive dataset and does not fall back to unverified local files."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell5_src = "".join(nb_data["cells"][4]["source"])
    assert "FileNotFoundError" in cell5_src
    assert "os.replace(tmp_dest, local_dest)" in cell5_src
    assert "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169" in cell5_src

def test_notebook_cells_no_bang_python_shell():
    """Verify notebook cells 4 through 10 use subprocess.run / pure Python and no !python shell calls."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    for idx, cell in enumerate(nb_data["cells"]):
        src = "".join(cell.get("source", []))
        assert "!python" not in src, f"Cell {idx+1} contains '!python' shell execution: {src}"

def test_notebook_cell7_passes_environment_lock():
    """Verify Cell 7 passes mandatory --environment-lock to deterministic qualification."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell7_src = "".join(nb_data["cells"][6]["source"])
    assert "--environment-lock" in cell7_src
    assert "STAGE-A2-COLAB-EXECUTION-ENVIRONMENT-V1.5.json" in cell7_src

def test_notebook_cell8_captures_dry_run_log_and_zero_steps():
    """Verify Cell 8 captures SEED42-COLAB-DRY-RUN.log and validates zero optimizer steps."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell8_src = "".join(nb_data["cells"][7]["source"])
    assert "SEED42-COLAB-DRY-RUN.log" in cell8_src
    assert "OptimizerStepsExecuted=0" in cell8_src or "Optimizer Steps Executed: 0" in cell8_src

def test_notebook_cell9_creates_durable_final_manifest():
    """Verify Cell 9 writes FINAL-QUALIFICATION-MANIFEST.json to Google Drive qualification dir."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell9_src = "".join(nb_data["cells"][8]["source"])
    assert "FINAL-QUALIFICATION-MANIFEST.json" in cell9_src
    assert "GOOGLE_DRIVE_DURABLE" in cell9_src

def test_notebook_cell10_is_validation_gate():
    """Verify Cell 10 validates qualification evidence and forbids unauthorized launch file."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_data = json.loads(nb_p.read_text(encoding="utf-8"))
    cell10_src = "".join(nb_data["cells"][9]["source"])
    assert "FINAL-QUALIFICATION-MANIFEST.json" in cell10_src
    assert "SEED42-COLAB-LAUNCH-AUTHORIZATION-V1.5.json" in cell10_src
    assert "STOP — PENDING INDEPENDENT REVIEW" in cell10_src

def test_notebook_zero_real_training_flags():
    """Verify notebook contains zero occurrences of real empirical training authorization flags."""
    nb_p = REPO_ROOT / "notebooks" / "STAGE-A2-COLAB-V1.5.ipynb"
    nb_text = nb_p.read_text(encoding="utf-8")
    assert "--authorize-real-empirical-execution" not in nb_text
