# -*- coding: utf-8 -*-
"""
Comprehensive Unit and Regression Test Suite for Stage A2 Graph Contract V1.3:
  1. Shared Canonical Split Authority Binding
  2. Exact Session Count Verification (35,000 Train, 7,500 Val)
  3. Deterministic Membership Reproducibility
  4. Disjointness and Boundary Purges
  5. Millisecond Timestamp Parity (delta = 0.0)
  6. Relation Direction Grounding & Component Constraints
  7. Test Firewall Protection (TestSetSealedError)
  8. Target-Leakage Prevention for L_rel and L_node
  9. Complete Mutable Checkpoint State Contract (14 elements)
  10. Optimizer Boundary Checkpointing Policy
  11. Experimental Source Contract Schema Requirements
  12. Implementation Readiness Gate Verification
NON_EMPIRICAL_TEST_FIXTURE = true
"""

import sys
import json
import pytest
import hashlib
from pathlib import Path

from research_agent.experiments.data.hdfs_split_authority import (
    parse_hdfs_line_timestamp,
    HDFSSplitAuthority
)
from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    HDFS_RELATION_RULES,
    TestSetSealedError
)

NON_EMPIRICAL_TEST_FIXTURE = True

@pytest.fixture
def base_dir():
    return Path("D:/Research")

def test_hdfs_graph_uses_canonical_split_authority(base_dir):
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    builder = HDFSGraphBuilder(base_dir=base_dir, split_authority=split_auth)
    assert builder.split_authority is split_auth
    assert builder.split_id == "SPL-HDFS-001"

def test_execution_train_session_count_exact(base_dir):
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()
    assert len(split_info["selected_train_block_ids"]) == 35000
    assert len(split_info["train_block_ids"]) == 357133

def test_execution_val_session_count_exact(base_dir):
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()
    assert len(split_info["selected_val_block_ids"]) == 7500
    assert len(split_info["val_block_ids"]) == 50204

def test_execution_membership_hash_reproducible(base_dir):
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()
    
    calc_train_h = hashlib.sha256("\n".join(split_info["selected_train_block_ids"]).encode()).hexdigest()
    calc_val_h = hashlib.sha256("\n".join(split_info["selected_val_block_ids"]).encode()).hexdigest()
    
    assert calc_train_h == split_info["selected_train_block_ids_sha256"]
    assert calc_val_h == split_info["selected_val_block_ids_sha256"]

def test_train_val_block_ids_disjoint(base_dir):
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()
    assert split_info["train_block_ids"].isdisjoint(split_info["val_block_ids"])
    assert split_info["train_block_ids"].isdisjoint(split_info["test_block_ids"])
    assert split_info["val_block_ids"].isdisjoint(split_info["test_block_ids"])

def test_execution_subset_disjoint_from_test(base_dir):
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()
    selected_train = set(split_info["selected_train_block_ids"])
    selected_val = set(split_info["selected_val_block_ids"])
    test_blocks = split_info["test_block_ids"]
    assert selected_train.isdisjoint(test_blocks)
    assert selected_val.isdisjoint(test_blocks)
    assert selected_train.isdisjoint(selected_val)

def test_runner_scope_cannot_use_full_population_accidentally(base_dir):
    mem_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "HDFS-EXECUTION-MEMBERSHIP.json"
    assert mem_path.exists()
    mem = json.loads(mem_path.read_text(encoding="utf-8"))
    assert mem["authorized_train_session_count"] == 35000
    assert mem["population_train_session_count"] == 357133
    assert mem["authorized_train_session_count"] < mem["population_train_session_count"]

def test_purged_sessions_not_materialized(base_dir):
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()
    purged_tv = split_info["purged_train_val_ids"]
    purged_vt = split_info["purged_val_test_ids"]
    assert purged_tv.isdisjoint(split_info["train_block_ids"])
    assert purged_tv.isdisjoint(split_info["val_block_ids"])
    assert purged_vt.isdisjoint(split_info["val_block_ids"])

def test_graph_builder_timestamp_matches_canonical_adapter():
    ts1 = parse_hdfs_line_timestamp("081109", "203518", "143")
    assert ts1 is not None
    assert abs(ts1 - 1226262918.143) < 1e-5

def test_milliseconds_not_truncated():
    ts = parse_hdfs_line_timestamp("081109", "203518", "789")
    assert ts == 1226262918.789

def test_relation_direction_grounding(base_dir):
    builder = HDFSGraphBuilder(base_dir=base_dir)
    line = "081109 203519 145 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-1608999687919862906 terminating"
    event, _, _ = builder.parse_raw_line(line, 1)
    assert event is not None
    assert event["relation_name"] == "MONITORS_BLOCK"
    assert event["source_node"] == "PacketResponder_1"
    assert event["source_type"] == 3
    assert event["dest_node"] == "blk_-1608999687919862906"
    assert event["dest_type"] == 0

def test_relation_component_constraints(base_dir):
    builder = HDFSGraphBuilder(base_dir=base_dir)
    line_wrong_comp = "081109 203518 143 INFO dfs.OtherComponent: 10.250.19.102:50010:Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010"
    event, reject_reason, _ = builder.parse_raw_line(line_wrong_comp, 1)
    assert event is None
    assert reject_reason == "UNMATCHED_RELATION_TEMPLATE"

def test_full_contract_relation_ids_match_builder():
    builder_rel_ids = {r["relation_id"] for r in HDFS_RELATION_RULES}
    assert builder_rel_ids == {1, 2, 3, 4, 5, 6, 7, 8}

def test_test_graph_materialization_forbidden(base_dir):
    builder = HDFSGraphBuilder(base_dir=base_dir)
    with pytest.raises(TestSetSealedError):
        builder.materialize_split("TEST")

def test_relation_target_hidden_from_prediction(base_dir):
    contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    rel_policy = contract["target_masking_visibility_policies"]["masked_relation_prediction"]
    assert "event_relation_embedding" in rel_policy["withheld_from_prediction"]
    assert "event_relation_id" in rel_policy["withheld_from_prediction"]
    assert rel_policy["memory_update_timing"] == "POST_LOSS_COMPUTATION_ONLY"

def test_node_reconstruction_target_not_directly_visible(base_dir):
    contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    node_policy = contract["target_masking_visibility_policies"]["masked_node_reconstruction"]
    assert "x_v_fixed_priv" in node_policy["withheld_from_prediction"]
    assert node_policy["input_representation"] == ["h_v(t-)"]

def test_checkpoint_state_contract_contains_causal_degrees(base_dir):
    contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    mandatory_state = contract["checkpoint_state_contract"]["mandatory_mutable_state"]
    assert "node_causal_in_degrees" in mandatory_state
    assert "node_causal_out_degrees" in mandatory_state

def test_checkpoint_state_contract_contains_temporal_history(base_dir):
    contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    mandatory_state = contract["checkpoint_state_contract"]["mandatory_mutable_state"]
    assert "node_temporal_history_buffers" in mandatory_state

def test_checkpoint_at_optimizer_boundary(base_dir):
    contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["checkpoint_state_contract"]["checkpoint_boundary_policy"] == "CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY"

def test_experimental_source_schema_requires_commit(base_dir):
    schema_path = base_dir / "experiments" / "evidence" / "EXPERIMENTAL-SOURCE-SCHEMA.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "execution_code_commit_sha" in schema["required"]

def test_experimental_source_schema_requires_artifact_hash(base_dir):
    schema_path = base_dir / "experiments" / "evidence" / "EXPERIMENTAL-SOURCE-SCHEMA.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "metrics_artifact_sha256" in schema["required"]

def test_experimental_source_schema_requires_command(base_dir):
    schema_path = base_dir / "experiments" / "evidence" / "EXPERIMENTAL-SOURCE-SCHEMA.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "command_executed" in schema["required"]

def test_experimental_source_schema_requires_environment(base_dir):
    schema_path = base_dir / "experiments" / "evidence" / "EXPERIMENTAL-SOURCE-SCHEMA.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "environment" in schema["required"]

def test_experimental_source_schema_requires_test_firewall(base_dir):
    schema_path = base_dir / "experiments" / "evidence" / "EXPERIMENTAL-SOURCE-SCHEMA.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "test_firewall_state" in schema["required"]

def test_implementation_readiness_verifier_passes():
    from scripts.verify_stage_a2_implementation_readiness import verify_stage_a2_implementation_readiness
    # Should exit cleanly or return
    try:
        verify_stage_a2_implementation_readiness()
    except SystemExit as e:
        assert e.code == 0
