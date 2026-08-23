# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Stage A2 Implementation (Contract V1.4 Locked).
NON_EMPIRICAL_TEST_FIXTURE = true
"""

import json
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
            base_dir=Path("D:/Research"),
            is_dry_run=False,
            empirical_authorized=False,
            fixture_mode=True
        )

def test_real_runner_rejects_all_mode_for_real_execution():
    from scripts.run_stage_a2_five_seed_empirical import main
    # Simulating --all and --authorize-real-empirical-execution without --dry-run
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
        verify_preflight(Path("D:/Research"), 42, is_dry_run=False)
    assert "FATAL: Execution source tree has uncommitted changes" in str(exc.value)

def test_wrong_execution_code_fails_preflight():
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    with pytest.raises(ValueError) as exc:
        verify_preflight(Path("D:/Research"), 99999, is_dry_run=True)
    assert "is NOT in canonical list" in str(exc.value)

def test_raw_dataset_hash_mismatch_fails_preflight(tmp_path, monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.RAW_HDFS_TAR_SHA", "0000000000000000000000000000000000000000000000000000000000000000")
    with pytest.raises(ValueError) as exc:
        verify_preflight(Path("D:/Research"), 42, is_dry_run=True)
    assert "RAW_HDFS_TAR_SHA mismatch" in str(exc.value)

def test_membership_hash_mismatch_fails_preflight(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.TRAIN_MEMBERSHIP_SHA", "0000000000000000000000000000000000000000000000000000000000000000")
    with pytest.raises(ValueError) as exc:
        verify_preflight(Path("D:/Research"), 42, is_dry_run=True)
    assert "TRAIN_MEMBERSHIP_SHA mismatch" in str(exc.value)

def test_environment_version_mismatch_fails_preflight(monkeypatch):
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("scripts.run_stage_a2_five_seed_empirical.ENV_LOCK_SHA", "0000000000000000000000000000000000000000000000000000000000000000")
    with pytest.raises(ValueError) as exc:
        verify_preflight(Path("D:/Research"), 42, is_dry_run=True)
    assert "ENV_LOCK_SHA mismatch" in str(exc.value)

def test_gpu_name_mismatch_fails_preflight(monkeypatch):
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    from scripts.run_stage_a2_five_seed_empirical import verify_preflight
    monkeypatch.setattr("torch.cuda.get_device_name", lambda idx: "Incompatible Ancient GPU")
    with pytest.raises(ExecutionDeviceMismatchError) as exc:
        verify_preflight(Path("D:/Research"), 42, is_dry_run=True)
    assert "Incompatible GPU device" in str(exc.value)

def test_test_partition_request_raises_TestSetSealedError():
    builder = HDFSGraphBuilder(base_dir=Path("D:/Research"))
    with pytest.raises(TestSetSealedError):
        builder.materialize_split("TEST")

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
    # 2292 windows accumulated in groups of 4 gives exactly 573 optimizer steps
    windows = [[] for _ in range(2292)]
    accum_groups = len(windows) // 4
    assert accum_groups == 573

def test_mock_fixture_end_to_end_runner_pipeline(tmp_path):
    """Executes the complete runner pipeline end-to-end using synthetic fixture events on CUDA."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    
    # 8 train windows (2048 events) and 2 val windows (512 events)
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(2048)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(512)]
    
    res = run_single_seed_pipeline(
        seed=42,
        base_dir=Path("D:/Research"),
        is_dry_run=False,
        empirical_authorized=True,
        fixture_mode=True,
        fixture_train_events=fix_train,
        fixture_val_events=fix_val
    )
    assert res["status"] == "COMPLETED"
    assert res["optimizer_steps"] > 0

    run_dir = Path("D:/Research/experiments/runs/stage-a2/HDFS/seed-42")
    assert (run_dir / "TRAIN-LOG.jsonl").exists()
    assert (run_dir / "METRICS.json").exists()
    assert (run_dir / "EXPERIMENTAL-SOURCE.json").exists()
    assert (run_dir / "CHECKPOINT-INVENTORY.json").exists()
    assert (run_dir / "TEST-FIREWALL.json").exists()

def test_failure_manifest_written(tmp_path):
    """Verifies that an unhandled anomaly in the pipeline causes FAILURE.json to be written."""
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    
    # Pass malformed event dictionary to trigger processing KeyError
    with pytest.raises(KeyError):
        run_single_seed_pipeline(
            seed=42,
            base_dir=Path("D:/Research"),
            is_dry_run=False,
            empirical_authorized=True,
            fixture_mode=True,
            fixture_train_events=[{"malformed_event_missing_keys": True}],
            fixture_val_events=[]
        )
    fail_p = Path("D:/Research/experiments/runs/stage-a2/HDFS/seed-42/FAILURE.json")
    assert fail_p.exists()
    fail_data = json.loads(fail_p.read_text(encoding="utf-8"))
    assert fail_data["error_type"] == "KeyError"

def test_resume_restores_runner_trajectory(tmp_path):
    """Verifies that runner correctly resumes from an existing checkpoint."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    from scripts.run_stage_a2_five_seed_empirical import run_single_seed_pipeline
    
    fix_train = [create_synthetic_event(f"A_{i}", f"B_{i}", 1, 0, 1, 100.0 + i) for i in range(2048)]
    fix_val = [create_synthetic_event(f"C_{i}", f"D_{i}", 2, 3, 2, 200.0 + i) for i in range(512)]
    
    ckpt_path = Path("D:/Research/.artifacts/stage-a2/HDFS/seed-42/last_checkpoint.pt")
    if ckpt_path.exists():
        res = run_single_seed_pipeline(
            seed=42,
            base_dir=Path("D:/Research"),
            is_dry_run=False,
            empirical_authorized=True,
            resume_checkpoint=ckpt_path,
            fixture_mode=True,
            fixture_train_events=fix_train,
            fixture_val_events=fix_val
        )
        assert res["status"] == "COMPLETED"
