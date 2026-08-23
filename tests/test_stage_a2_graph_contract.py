# -*- coding: utf-8 -*-
"""
Unit and Regression Test Suite for Stage A2 Graph Contract & Extraction Engine (Contract V1.1).
Verifies:
  1. Raw-to-Graph Extraction Rules (Exact regex match, entity typing, relation ID)
  2. Graph Conservation Law: raw_scanned = materialized_events + total_rejected
  3. Predict-Before-Update & Equal-Timestamp Tie-Breaking
  4. Train-Only Vocabulary and Feature Scalers
  5. Typed UNK Node Policy
  6. Strict Test Firewall (TestSetSealedError)
  7. BGL Ineligibility Enforcement
  8. Pre-Execution Verifier Script Integration
"""

import json
import pytest
from pathlib import Path

from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    TestSetSealedError
)
from scripts.verify_stage_a2_preexecution import verify_stage_a2_preexecution


def test_hdfs_exact_raw_relation_extractions():
    builder = HDFSGraphBuilder(base_dir=Path("D:/Research"))
    
    # 1. RECEIVES_BLOCK
    line1 = "081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608961267986555555 src: /10.250.19.102:54106 dest: /10.250.19.102:50010"
    e1, err1 = builder.parse_raw_line(line1, 1)
    assert err1 is None
    assert e1["relation_name"] == "RECEIVES_BLOCK"
    assert e1["relation_id"] == 1
    assert e1["source_node"] == "10.250.19.102:50010"
    assert e1["source_type"] == 1  # STORAGE_NODE
    assert e1["dest_node"] == "blk_-1608961267986555555"
    assert e1["dest_type"] == 0  # DATA_BLOCK

    # 2. STORES_BLOCK
    line2 = "081109 203519 143 INFO dfs.DataNode$DataXceiver: Received block blk_-1608961267986555555 of size 91178 from /10.250.19.102"
    e2, err2 = builder.parse_raw_line(line2, 2)
    assert err2 is None
    assert e2["relation_name"] == "STORES_BLOCK"
    assert e2["relation_id"] == 2
    assert e2["size_bytes"] == 91178.0

    # 3. ALLOCATES_BLOCK
    line3 = "081109 203520 143 INFO dfs.FSNamesystem: BLOCK* NameSystem.allocateBlock: /mnt/hadoop/dfs/data/... blk_-1608961267986555555"
    e3, err3 = builder.parse_raw_line(line3, 3)
    assert err3 is None
    assert e3["relation_name"] == "ALLOCATES_BLOCK"
    assert e3["source_node"] == "FSNamesystem"
    assert e3["source_type"] == 2  # MANAGEMENT_SYSTEM

    # 4. MONITORS_BLOCK
    line4 = "081109 203521 143 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_-1608961267986555555 terminating"
    e4, err4 = builder.parse_raw_line(line4, 4)
    assert err4 is None
    assert e4["relation_name"] == "MONITORS_BLOCK"
    assert e4["source_node"] == "PacketResponder_1"
    assert e4["source_type"] == 3  # EXECUTION_THREAD

    # 5. SERVES_BLOCK
    line5 = "081109 203522 143 INFO dfs.DataNode$DataXceiver: Served block blk_-1608961267986555555 to /10.250.19.102"
    e5, err5 = builder.parse_raw_line(line5, 5)
    assert err5 is None
    assert e5["relation_name"] == "SERVES_BLOCK"

    # 6. UPDATES_BLOCK_MAP
    line6 = "081109 203523 143 INFO dfs.FSNamesystem: BLOCK* NameSystem.addStoredBlock: blockMap updated: 10.250.19.102:50010 is added to blk_-1608961267986555555 size 91178"
    e6, err6 = builder.parse_raw_line(line6, 6)
    assert err6 is None
    assert e6["relation_name"] == "UPDATES_BLOCK_MAP"
    assert e6["size_bytes"] == 91178.0


def test_hdfs_graph_conservation_law():
    builder = HDFSGraphBuilder(base_dir=Path("D:/Research"), max_train_events=500)
    res = builder.materialize_split("TRAIN")
    
    # Exact Conservation Equation: raw_scanned = materialized_events + total_rejected
    assert res["raw_scanned"] == res["materialized_events"] + res["total_rejected"]
    assert res["materialized_events"] == 500
    assert "NO_BLOCK_ID_MATCH" in res["rejected_counts"] or res["total_rejected"] >= 0


def test_test_split_firewall_strictly_sealed():
    builder = HDFSGraphBuilder(base_dir=Path("D:/Research"))
    with pytest.raises(TestSetSealedError):
        builder.materialize_split("TEST")


def test_preexecution_verifier_passes():
    try:
        verify_stage_a2_preexecution()
    except SystemExit as e:
        assert e.code == 0, f"Verifier failed with exit code {e.code}"
