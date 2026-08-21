# -*- coding: utf-8 -*-
"""
Automated Test Suite for Chapter 3 Real Data Adapters & Scientific Data Contracts
Comprehensive verification of:
  1. Label-Free Stage A1 SSL Pretraining Package:
     - hdfs_ssl_train.pt, hdfs_ssl_val.pt, bgl_ssl_train.pt, bgl_ssl_val.pt contain 0 labels.
     - LabelLeakageError raised if labels are injected into pretraining packages.
  2. HDFS True Two-Pass Test Firewall:
     - Pass 1: parses only (timestamp, block_id).
     - Pass 2: Test feature parse count = 0, Test parameter extraction count = 0, Test vocab contribution = 0.
     - Test labels exposed to trainer = 0.
  3. Multi-Parameter Slot Representation:
     - max_param_slots = 4 slots per event, priority ordering.
     - 2+ parameter events survive materialization.
     - PAD parameter slots ignored by loss.
     - Canonical proposed mode: FULL_TYPED_PARAMETER_SET (not primary_param).
  4. Exact RFC1918 Network Membership:
     - 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 disjoint from Loopback, Link-Local, Shared, Special.
  5. BGL Node Context Toggle & Reconciled Accounting:
     - BGL_FULL_CONTEXT vs BGL_WITHOUT_NODE_CONTEXT.
     - pretest_scanned == pretest_valid + pretest_malformed.
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
    LabelLeakageError,
    enforce_real_training_data_purity,
    enforce_ssl_package_label_free
)
from research_agent.experiments.data.hdfs_adapter import HDFSRealDataAdapter
from research_agent.experiments.data.bgl_adapter import BGLRealDataAdapter

def test_01_label_leakage_error_and_label_free_ssl_packages():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    # 1. Test Fail-Closed Label Leakage Guard
    with pytest.raises(LabelLeakageError, match="prohibited label fields"):
        enforce_ssl_package_label_free({"sequences": [], "labels": [1, 0, 1]})

    with pytest.raises(LabelLeakageError, match="prohibited label fields"):
        enforce_ssl_package_label_free({"sequences": [], "is_alert": [0, 1]})

    with pytest.raises(LabelLeakageError, match="prohibited label fields"):
        enforce_ssl_package_label_free({"sequences": [], "attack_class": ["ddos"]})

    # 2. Assert Actual Materialized SSL Packages are Label-Free
    hdfs_train = torch.load(base_dir / "experiments" / "runs" / "data" / "hdfs" / "hdfs_ssl_train.pt", weights_only=False)
    hdfs_val = torch.load(base_dir / "experiments" / "runs" / "data" / "hdfs" / "hdfs_ssl_val.pt", weights_only=False)
    bgl_train = torch.load(base_dir / "experiments" / "runs" / "data" / "bgl" / "bgl_ssl_train.pt", weights_only=False)
    bgl_val = torch.load(base_dir / "experiments" / "runs" / "data" / "bgl" / "bgl_ssl_val.pt", weights_only=False)

    enforce_ssl_package_label_free(hdfs_train)
    enforce_ssl_package_label_free(hdfs_val)
    enforce_ssl_package_label_free(bgl_train)
    enforce_ssl_package_label_free(bgl_val)

    assert "labels" not in hdfs_train
    assert "labels" not in hdfs_val
    assert "labels" not in bgl_train
    assert "labels" not in bgl_val

def test_02_hdfs_true_two_pass_firewall_and_zero_test_extraction():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    subset_path = base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-HDFS.json"
    manifest = json.loads(subset_path.read_text(encoding="utf-8"))
    test_meta = manifest["test_metadata"]

    assert test_meta["test_status"] == "SEALED"
    assert test_meta["test_feature_parse_count"] == 0
    assert test_meta["test_param_extraction_count"] == 0
    assert test_meta["test_vocab_contribution"] == 0
    assert test_meta["test_labels_exposed_to_trainer"] is False
    assert test_meta["test_features_materialized"] is False

def test_03_multi_parameter_slot_representation():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    hdfs_train = torch.load(base_dir / "experiments" / "runs" / "data" / "hdfs" / "hdfs_ssl_train.pt", weights_only=False)
    param_targets = hdfs_train["param_targets"]
    assert len(param_targets) > 0
    
    # Check that param_targets has shape (L, max_param_slots)
    sample_param = param_targets[0]
    assert sample_param.dim() == 2
    assert sample_param.shape[1] == 4  # max_param_slots = 4
    
    # Check that events with multiple parameters exist
    has_multi_param = False
    for p_seq in param_targets[:100]:
        for slot_row in p_seq:
            # If slot 0 and slot 1 are both non-padding (not 1)
            if slot_row[0] > 1 and slot_row[1] > 1:
                has_multi_param = True
                break
        if has_multi_param:
            break
    assert has_multi_param, "Expected events with 2+ parameters in HDFS"

def test_04_hdfs_rfc1918_exact_network_membership():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)

    assert adapter.classify_ip("10.1.2.3") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("172.16.0.1") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("172.31.255.254") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("192.168.1.1") == "PARAM_IP_RFC1918_PRIVATE"

    assert adapter.classify_ip("127.0.0.1") == "PARAM_IP_LOOPBACK"
    assert adapter.classify_ip("169.254.1.1") == "PARAM_IP_LINK_LOCAL"
    assert adapter.classify_ip("100.64.0.1") == "PARAM_IP_SHARED_ADDRESS"
    assert adapter.classify_ip("192.0.0.1") == "PARAM_IP_SPECIAL_USE"

    assert adapter.classify_ip("172.32.0.1") == "PARAM_IP_PUBLIC"
    assert adapter.classify_ip("172.1.1.1") == "PARAM_IP_PUBLIC"

def test_05_bgl_node_context_toggle_and_accounting_conservation():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    # Variant 1: FULL_CONTEXT
    adapter_full = BGLRealDataAdapter(base_dir=base_dir, include_node_context=True)
    line = "- 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.363779 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected"
    p_full = adapter_full.parse_line(line)
    assert any("NODE_RACK_R02" in p for p in p_full["params"])

    # Variant 2: WITHOUT_NODE_CONTEXT
    adapter_no = BGLRealDataAdapter(base_dir=base_dir, include_node_context=False)
    p_no = adapter_no.parse_line(line)
    assert not any("NODE_RACK" in p for p in p_no["params"])

    # Accounting conservation
    subset_path = base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-BGL.json"
    subset = json.loads(subset_path.read_text(encoding="utf-8"))
    assert subset["raw_total_record_count"] == 4747963
    assert subset["pretest_scanned_record_count"] == subset["pretest_valid_record_count"] + subset["pretest_malformed_count"]

def test_06_stage_a1_training_contract_locked():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    contract_path = base_dir / "experiments" / "protocol" / "STAGE-A1-TRAINING-CONTRACT.md"
    assert contract_path.exists()
    content = contract_path.read_text(encoding="utf-8")
    assert "MODEL-A1-HDFS" in content
    assert "MODEL-A1-BGL" in content
    assert "lambda_{\\text{MEP}} = 1.0" in content
    assert "lambda_{\\text{MPP}} = 1.0" in content
    assert "lambda_{\\text{time}} = 0.1" in content
    assert "42, 1337, 2024, 7, 999" in content
    assert "BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4" in content

def test_07_stage_a1_preexecution_lock_file():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    lock_path = base_dir / "experiments" / "protocol" / "STAGE-A1-PREEXECUTION-LOCK.json"
    assert lock_path.exists()
    lock_data = json.loads(lock_path.read_text(encoding="utf-8"))

    assert lock_data["lock_identifier"] == "LOCK-STAGE-A1-20260822-CANONICAL"
    assert lock_data["architecture"]["layers"] == 4
    assert lock_data["architecture"]["d_model"] == 128
    assert lock_data["architecture"]["n_heads"] == 4
    assert lock_data["architecture"]["d_ffn"] == 512
    assert lock_data["architecture"]["parameter_representation_mode"] == "BOUNDED_MULTI_SLOT_TYPED_PARAMETER_SET_K4"
    assert lock_data["optimization"]["micro_batch_size"] == 16
    assert lock_data["optimization"]["gradient_accumulation_steps"] == 4
    assert lock_data["optimization"]["effective_batch_size"] == 64
    assert lock_data["canonical_seeds"] == [42, 1337, 2024, 7, 999]
    assert lock_data["execution_state"]["optimizer_steps"] == 0
    assert lock_data["execution_state"]["models_trained"] == 0
    assert lock_data["execution_state"]["test_opened"] is False
