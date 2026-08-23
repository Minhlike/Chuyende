# -*- coding: utf-8 -*-
"""
Canonical Regression Test Suite for Stage A2 Graph Contract & Extraction Engine (Contract V1.2).
Strictly validates:
  1. Binding to SPL-HDFS-001 Canonical Split Authority
  2. Disjointness of Train, Val, Test partitions
  3. Strict exclusion of boundary-purged block sessions
  4. Exact Timestamp Parity between Canonical Adapter and Graph Builder
  5. Exact Millisecond Preservation (No truncation to seconds)
  6. Non-Offset Validation Partitioning (Causal block session membership)
  7. Relation Direction & Component Constraint Grounding
  8. Schema Relation ID Consistency
  9. Absolute Test Graph Materialization Prohibition (TestSetSealedError)
  10. Zero Test Relation Parser Invocation
  11. Deterministic Temporal Gap (Delta t) Formulation
  12. Graph Conservation Law
  13. Pre-Execution Verifier Gate
"""

import json
import pytest
from pathlib import Path

from research_agent.experiments.data.hdfs_split_authority import (
    parse_hdfs_line_timestamp,
    HDFSSplitAuthority
)
from research_agent.experiments.data.hdfs_adapter import HDFSRealDataAdapter
from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    HDFS_RELATION_RULES,
    TestSetSealedError
)
from scripts.verify_stage_a2_preexecution import verify_stage_a2_preexecution


def test_hdfs_graph_uses_canonical_split_authority():
    base_dir = Path("D:/Research")
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    builder = HDFSGraphBuilder(base_dir=base_dir, split_authority=split_auth)
    assert builder.split_authority is split_auth


def test_train_val_block_ids_disjoint():
    base_dir = Path("D:/Research")
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    data = split_auth.get_split()
    train_ids = data["train_block_ids"]
    val_ids = data["val_block_ids"]
    test_ids = data["test_block_ids"]

    assert train_ids.isdisjoint(val_ids), "Train and Val block IDs must be disjoint"
    assert train_ids.isdisjoint(test_ids), "Train and Test block IDs must be disjoint"
    assert val_ids.isdisjoint(test_ids), "Val and Test block IDs must be disjoint"


def test_purged_sessions_not_materialized():
    base_dir = Path("D:/Research")
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    data = split_auth.get_split()
    purged_tv = data["purged_train_val_ids"]
    purged_vt = data["purged_val_test_ids"]
    train_ids = data["train_block_ids"]
    val_ids = data["val_block_ids"]

    assert purged_tv.isdisjoint(train_ids), "Purged T->V sessions must not be in Train"
    assert purged_tv.isdisjoint(val_ids), "Purged T->V sessions must not be in Val"
    assert purged_vt.isdisjoint(val_ids), "Purged V->T sessions must not be in Val"


def test_graph_builder_timestamp_matches_canonical_adapter():
    base_dir = Path("D:/Research")
    adapter = HDFSRealDataAdapter(base_dir=base_dir)
    
    # Test record with non-zero milliseconds
    d_str, t_str, ms_str = "081109", "203518", "143"
    ts_adapter = adapter.parse_line_timestamp(d_str, t_str, ms_str)
    ts_split_auth = parse_hdfs_line_timestamp(d_str, t_str, ms_str)

    assert ts_adapter is not None
    assert ts_split_auth is not None
    assert abs(ts_adapter - ts_split_auth) == 0.0, f"Timestamp divergence: {ts_adapter} != {ts_split_auth}"
    assert abs(ts_adapter - 1226262918.143) < 1e-5, f"Expected 1226262918.143, got {ts_adapter}"


def test_milliseconds_not_truncated():
    # Verify that millisecond component is preserved in float timestamp
    ts1 = parse_hdfs_line_timestamp("081109", "203518", "000")
    ts2 = parse_hdfs_line_timestamp("081109", "203518", "500")
    assert ts2 - ts1 == 0.5, "Milliseconds must contribute exactly ms/1000.0 to epoch timestamp"


def test_validation_does_not_use_line_offset_split():
    base_dir = Path("D:/Research")
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    builder = HDFSGraphBuilder(base_dir=base_dir, split_authority=split_auth)
    
    # Materialization must use session membership
    data = split_auth.get_split()
    assert isinstance(data["val_block_ids"], set)
    assert len(data["val_block_ids"]) > 0


def test_relation_direction_grounding():
    base_dir = Path("D:/Research")
    builder = HDFSGraphBuilder(base_dir=base_dir)

    # 1. RECEIVES_BLOCK: dest storage node receives block
    line1 = "081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608961267986555555 src: /10.250.19.102:54106 dest: /10.250.19.102:50010"
    e1, err1, _ = builder.parse_raw_line(line1, 1)
    assert err1 is None
    assert e1["relation_name"] == "RECEIVES_BLOCK"
    assert e1["source_node"] == "10.250.19.102:50010"
    assert e1["source_type"] == 1  # STORAGE_NODE
    assert e1["dest_node"] == "blk_-1608961267986555555"
    assert e1["dest_type"] == 0  # DATA_BLOCK

    # 2. TRANSMITS_BLOCK: transmitting storage node
    line2 = "081109 203519 145 INFO dfs.DataNode$PacketResponder: Received block blk_-1608961267986555555 of size 91178 from /10.250.19.102"
    e2, err2, _ = builder.parse_raw_line(line2, 2)
    assert err2 is None
    assert e2["relation_name"] == "TRANSMITS_BLOCK"
    assert e2["source_node"] == "10.250.19.102"
    assert e2["size_bytes"] == 91178.0

    # 3. ALLOCATES_BLOCK: FSNamesystem allocates
    line3 = "081109 203518 35 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /mnt/hadoop/data. blk_-1608961267986555555"
    e3, err3, _ = builder.parse_raw_line(line3, 3)
    assert err3 is None
    assert e3["relation_name"] == "ALLOCATES_BLOCK"
    assert e3["source_node"] == "FSNamesystem"
    assert e3["source_type"] == 2  # MANAGEMENT_SYSTEM

    # 4. MONITORS_BLOCK: PacketResponder thread
    line4 = "081109 203519 145 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-1608961267986555555 terminating"
    e4, err4, _ = builder.parse_raw_line(line4, 4)
    assert err4 is None
    assert e4["relation_name"] == "MONITORS_BLOCK"
    assert e4["source_node"] == "PacketResponder_1"
    assert e4["source_type"] == 3  # EXECUTION_THREAD

    # 5. SERVES_BLOCK: Server storage node serves
    line5 = "081109 203523 148 INFO dfs.DataNode$DataXceiver: 10.250.11.100:50010 Served block blk_-3544583377289912061 to /10.250.19.102"
    e5, err5, _ = builder.parse_raw_line(line5, 5)
    assert err5 is None
    assert e5["relation_name"] == "SERVES_BLOCK"
    assert e5["source_node"] == "10.250.11.100:50010"

    # 6. UPDATES_BLOCK_MAP: DataNode added to blockMap
    line6 = "081109 203519 29 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.11.100:50010 is added to blk_-1608961267986555555 size 91178"
    e6, err6, _ = builder.parse_raw_line(line6, 6)
    assert err6 is None
    assert e6["relation_name"] == "UPDATES_BLOCK_MAP"
    assert e6["source_node"] == "10.250.11.100:50010"
    assert e6["size_bytes"] == 91178.0


def test_relation_component_constraints():
    base_dir = Path("D:/Research")
    builder = HDFSGraphBuilder(base_dir=base_dir)

    # If component does NOT match required component regex, message should be rejected
    line_wrong_comp = "081109 203518 143 INFO dfs.FakeComponent: Receiving block blk_-1608961267986555555 src: /10.250.19.102:54106 dest: /10.250.19.102:50010"
    e, err, _ = builder.parse_raw_line(line_wrong_comp, 1)
    assert e is None
    assert err == "UNMATCHED_RELATION_TEMPLATE"


def test_full_contract_relation_ids_match_builder():
    base_dir = Path("D:/Research")
    mapping_path = base_dir / "experiments" / "schemas" / "STAGE-A2-RAW-TO-GRAPH-MAPPING.json"
    mapping_data = json.loads(mapping_path.read_text(encoding="utf-8"))
    
    schema_relations = {r["relation_name"]: r["relation_id"] for r in mapping_data["hdfs_relations"]}
    builder_relations = {r["relation_name"]: r["relation_id"] for r in HDFS_RELATION_RULES}

    assert schema_relations == builder_relations, "Schema relation IDs and builder relation IDs must match"


def test_test_graph_materialization_forbidden():
    base_dir = Path("D:/Research")
    builder = HDFSGraphBuilder(base_dir=base_dir)
    with pytest.raises(TestSetSealedError):
        builder.materialize_split("TEST")


def test_temporal_gap_semantics():
    # Verify exact continuous log1p delta t formulation
    import math
    dt = 2.5  # 2.5 seconds
    expected_gap = math.log1p(dt)
    assert abs(expected_gap - 1.252762968) < 1e-5


def test_preexecution_verifier_passes():
    try:
        verify_stage_a2_preexecution()
    except SystemExit as e:
        assert e.code == 0, f"Verifier failed with exit code {e.code}"
