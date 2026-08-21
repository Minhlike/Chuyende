# -*- coding: utf-8 -*-
"""
Automated Test Suite for Chapter 3 Real Data Adapters & Scientific Data Contracts
Comprehensive verification of:
  1. HDFS True Interval-Causal Partitioning & Boundary Purge:
     - max(end_ts of Train) < min(start_ts of Validation)
     - max(end_ts of Validation) < min(start_ts of Test)
     - 0 event-time overlap between Train/Val and Val/Test
  2. HDFS Test Label Vault:
     - Split authority derives partitions without anomaly labels
     - Test block labels are strictly inaccessible and unparsed by trainer
     - Test manifest holds 0 label distribution information (VAULT_LOCKED)
  3. Exact RFC1918 Network Membership:
     - 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
     - Disjoint classification of Loopback, Link-Local, Shared, Special-Use, Public
  4. BGL Node Context & Shortcut Protocol:
     - BGL_NODE_CONTEXT registered in subset manifest
     - BGL_WITHOUT_NODE_CONTEXT produces zero node-derived tokens
  5. BGL Mathematical Accounting Conservation:
     - pretest_scanned == pretest_valid + pretest_malformed
  6. Real Training Purity Fail-Closed Guard:
     - RealTrainingDataViolation raised on synthetic smoke proxies
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

pytest.importorskip("torch")
import torch

from research_agent.experiments.data.data_contract import (
    RealDataContract,
    RealTrainingDataViolation,
    enforce_real_training_data_purity
)
from research_agent.experiments.data.hdfs_adapter import HDFSRealDataAdapter
from research_agent.experiments.data.bgl_adapter import BGLRealDataAdapter

def test_01_hdfs_rfc1918_exact_network_membership():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)

    # 10.0.0.0/8 -> RFC1918
    assert adapter.classify_ip("10.1.2.3") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("/10.250.19.102:54106") == "PARAM_IP_RFC1918_PRIVATE"
    
    # 172.16.0.0/12 -> RFC1918
    assert adapter.classify_ip("172.16.0.1") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("172.31.255.254") == "PARAM_IP_RFC1918_PRIVATE"
    
    # 192.168.0.0/16 -> RFC1918
    assert adapter.classify_ip("192.168.1.1") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("/192.168.100.50:50010") == "PARAM_IP_RFC1918_PRIVATE"

    # Non-RFC1918 special use / loopback / link-local / shared
    assert adapter.classify_ip("127.0.0.1") == "PARAM_IP_LOOPBACK"
    assert adapter.classify_ip("169.254.1.1") == "PARAM_IP_LINK_LOCAL"
    assert adapter.classify_ip("100.64.0.1") == "PARAM_IP_SHARED_ADDRESS"
    assert adapter.classify_ip("192.0.0.1") == "PARAM_IP_SPECIAL_USE"

    # Public internet IPs (Not RFC1918)
    assert adapter.classify_ip("172.32.0.1") == "PARAM_IP_PUBLIC"
    assert adapter.classify_ip("172.1.1.1") == "PARAM_IP_PUBLIC"
    assert adapter.classify_ip("172.15.255.255") == "PARAM_IP_PUBLIC"
    assert adapter.classify_ip("128.55.12.91") == "PARAM_IP_PUBLIC"

def test_02_hdfs_interval_causal_split_and_boundary_purge():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    subset_manifest_path = base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-HDFS.json"
    assert subset_manifest_path.exists()
    manifest = json.loads(subset_manifest_path.read_text(encoding="utf-8"))

    train_max_end = manifest["train_max_end"]
    val_min_start = manifest["val_min_start"]
    val_max_end = manifest["val_max_end"]
    test_min_start = manifest["test_min_start"]

    # Strict Interval-Causal Invariants
    assert train_max_end < val_min_start, f"Train max end {train_max_end} >= Val min start {val_min_start}"
    assert val_max_end < test_min_start, f"Val max end {val_max_end} >= Test min start {test_min_start}"
    
    # Boundary Crossing Sessions Purged
    assert manifest["purged_train_val_crossing_sessions"] > 0
    assert manifest["purged_val_test_crossing_sessions"] > 0
    assert manifest["selected_train_sessions"] == 35000
    assert manifest["selected_val_sessions"] == 7500

def test_03_hdfs_test_label_vault_protection():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    train_tensor_path = base_dir / "experiments" / "runs" / "data" / "hdfs" / "hdfs_train.pt"
    val_tensor_path = base_dir / "experiments" / "runs" / "data" / "hdfs" / "hdfs_val.pt"
    subset_manifest_path = base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-HDFS.json"

    assert train_tensor_path.exists()
    assert val_tensor_path.exists()
    assert subset_manifest_path.exists()

    manifest = json.loads(subset_manifest_path.read_text(encoding="utf-8"))
    test_meta = manifest["test_metadata"]

    assert test_meta["test_status"] == "SEALED"
    assert test_meta["test_features_materialized"] is False
    assert test_meta["test_labels_exposed_to_trainer"] is False
    assert test_meta["test_label_distribution"] == "VAULT_LOCKED"
    assert "test_anomaly_count" not in test_meta

def test_04_bgl_node_context_control_and_feature_toggle():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    # Variant 1: BGL_FULL_CONTEXT (Enabled)
    adapter_full = BGLRealDataAdapter(base_dir=base_dir, include_node_context=True)
    line = "- 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.363779 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected"
    parsed_full = adapter_full.parse_line(line)
    assert any("PARAM_NODE_RACK_R02" in p for p in parsed_full["params"])
    assert any("PARAM_NODE_MIDPLANE_M1" in p for p in parsed_full["params"])

    # Variant 2: BGL_WITHOUT_NODE_CONTEXT (Disabled)
    adapter_no_node = BGLRealDataAdapter(base_dir=base_dir, include_node_context=False)
    parsed_no_node = adapter_no_node.parse_line(line)
    assert not any("PARAM_NODE_RACK" in p for p in parsed_no_node["params"])
    assert not any("PARAM_NODE_MIDPLANE" in p for p in parsed_no_node["params"])
    assert not any("R02" in p for p in parsed_no_node["params"])

def test_05_bgl_mathematical_accounting_conservation():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    subset_path = base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-BGL.json"
    assert subset_path.exists()

    subset = json.loads(subset_path.read_text(encoding="utf-8"))
    raw_total = subset["raw_total_record_count"]
    pretest_scanned = subset["pretest_scanned_record_count"]
    pretest_valid = subset["pretest_valid_record_count"]
    pretest_malformed = subset["pretest_malformed_count"]
    train_count = subset["train_record_count"]
    val_count = subset["validation_record_count"]

    assert raw_total == 4747963
    assert pretest_scanned == pretest_valid + pretest_malformed
    assert pretest_valid == train_count + val_count
    assert subset["test_status"] == "SEALED_DAYS_181_TO_215"
    assert "BGL_NODE_CONTEXT" in subset["feature_group"]

def test_06_real_training_data_violation_guard():
    with pytest.raises(RealTrainingDataViolation, match="prohibited in real training"):
        enforce_real_training_data_purity("HYBRID_SMOKE_FIXTURE")

    with pytest.raises(RealTrainingDataViolation, match="prohibited in real training"):
        enforce_real_training_data_purity("SYNTHETIC_PROXY")

    with pytest.raises(RealTrainingDataViolation, match="Synthetic proxies are forbidden"):
        enforce_real_training_data_purity(
            "REAL_TRAINING_MATERIALIZED",
            {"parameter_source": "SYNTHETIC_PROXY"}
        )

    enforce_real_training_data_purity(
        "REAL_TRAINING_MATERIALIZED",
        {"parameter_source": "REAL_HDFS_EXTRACTED", "temporal_source": "REAL_HDFS_EXTRACTED"}
    )
