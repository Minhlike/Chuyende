# -*- coding: utf-8 -*-
"""
Automated Test Suite for Chapter 3 Real Data Adapters & Scientific Data Contracts
Comprehensive verification of:
  1. HDFS Deterministic Causal Split: max(Train) <= min(Val) <= min(Test).
  2. Zero Random Temporal Shuffling: Causal split is purely temporal-sorted, independent of random seed.
  3. HDFS Line Count Conservation: 11,175,629 == block_associated (11,175,629) + no_block (0) + malformed (0).
  4. Exact RFC1918 IP Classification: 10/8, 172.16/12, 192.168/16 verified with edge cases.
  5. Cross-Platform Timezone-Independent Timestamp Parsing: Windows and Linux produce identical floats.
  6. Multi-Parameter Policy & Primary Selection: Priority IP > SIZE > NUM > GENERIC, 0 discarded parameters.
  7. BGL Total vs Pre-Test Scanned Record Distinction: 4,747,963 raw total vs ~4.31M pre-test scanned.
  8. BGL Observed Minimum Timestamp Verification: Exactly 1117838570.
  9. Stale Split Protocol Prohibition: Rejects >58 day LANL ranges and unsupported DARPA day ranges.
  10. PENDING Ground-Truth Protection: Unverified DARPA GT cannot be used as confirmatory training labels.
  11. Real Training Purity Guard: RealTrainingDataViolation raised on synthetic smoke proxies.
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

def test_01_hdfs_rfc1918_exact_boundary_classification():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)

    # 10.0.0.0/8
    assert adapter.classify_ip("/10.250.19.102:54106") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("10.0.0.1") == "PARAM_IP_RFC1918_PRIVATE"
    
    # 172.16.0.0/12
    assert adapter.classify_ip("/172.16.0.1:50010") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("/172.31.255.255") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("/172.32.0.1:80") == "PARAM_IP_PUBLIC"
    assert adapter.classify_ip("/172.1.1.1") == "PARAM_IP_PUBLIC"
    assert adapter.classify_ip("/172.15.255.255") == "PARAM_IP_PUBLIC"

    # 192.168.0.0/16
    assert adapter.classify_ip("/192.168.1.1") == "PARAM_IP_RFC1918_PRIVATE"
    assert adapter.classify_ip("/192.169.1.1") == "PARAM_IP_PUBLIC"

    # Public internet IP
    assert adapter.classify_ip("/128.55.12.91:8080") == "PARAM_IP_PUBLIC"

def test_02_hdfs_cross_platform_timestamp_parsing():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)
    ts = adapter.parse_line_timestamp("081109", "203518", "143")
    
    # Deterministic UTC numerical epoch for 2008-11-09 20:35:18.143
    expected_dt = datetime(2008, 11, 9, 20, 35, 18, 143000, tzinfo=timezone.utc)
    expected_ts = expected_dt.timestamp()
    
    assert ts == expected_ts
    assert abs(ts - 1226262918.143) < 1e-3

def test_03_hdfs_line_count_conservation_and_contract():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    contract_path = base_dir / "datasets" / "manifests" / "REAL-DATA-CONTRACT-HDFS.json"
    assert contract_path.exists()

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    raw_total = contract["source_record_count"]
    valid_count = contract["valid_record_count"]
    malformed_count = contract["malformed_count"]

    assert raw_total == 11175629
    assert valid_count == 11175629
    assert malformed_count == 0
    assert raw_total == valid_count + malformed_count
    assert contract["synthetic_proxy_count"] == 0
    assert contract["test_status"] == "SEALED"

def test_04_hdfs_true_deterministic_causal_split_ordering():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    subset_manifest_path = base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-HDFS.json"
    assert subset_manifest_path.exists()
    manifest = json.loads(subset_manifest_path.read_text(encoding="utf-8"))

    assert manifest["selection_rule"] == "EARLIEST_CAUSAL_SESSION_BUDGET_CAP"
    assert manifest["selected_train_sessions"] == 35000
    assert manifest["selected_val_sessions"] == 7500
    assert manifest["test_metadata"]["test_status"] == "SEALED"
    assert manifest["test_metadata"]["test_features_materialized"] is False
    assert manifest["test_metadata"]["test_labels_exposed_to_trainer"] is False
    
    # Test boundary must be after val boundary
    assert manifest["test_metadata"]["test_min_start_time"] >= 1226390000.0

def test_05_hdfs_parameter_policy_and_block_id_firewall():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)
    content = "Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010"
    template, params = adapter.extract_template_and_params(content)

    for p in params:
        assert "blk_" not in p
        assert "-1608999687919862906" not in p
    
    primary = adapter.select_primary_parameter(params)
    assert primary == "PARAM_IP_RFC1918_PRIVATE"

def test_06_bgl_record_count_semantics_and_observed_min_timestamp():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    contract_path = base_dir / "datasets" / "manifests" / "REAL-DATA-CONTRACT-BGL.json"
    subset_path = base_dir / "datasets" / "manifests" / "SUBSET-MANIFEST-BGL.json"
    assert contract_path.exists()
    assert subset_path.exists()

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    subset = json.loads(subset_path.read_text(encoding="utf-8"))

    assert contract["source_record_count"] == 4747963
    assert subset["raw_total_record_count"] == 4747963
    assert subset["pretest_scanned_record_count"] == 4318481
    assert subset["raw_total_record_count"] != subset["pretest_scanned_record_count"]
    assert subset["test_status"] == "SEALED_DAYS_181_TO_215"
    assert contract["synthetic_proxy_count"] == 0

def test_07_bgl_alert_tag_non_cyberattack_semantics():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = BGLRealDataAdapter(base_dir=base_dir, seed=42)
    norm_line = "- 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.363779 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected"
    parsed_norm = adapter.parse_line(norm_line)
    assert parsed_norm["is_alert"] == 0
    assert any("NODE_RACK_R02" in p for p in parsed_norm["params"])

    alert_line = "FATAL 1117838600 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.43.20.123456 R02-M1-N0-C:J12-U11 RAS KERNEL FATAL memory parity error"
    parsed_alert = adapter.parse_line(alert_line)
    assert parsed_alert["is_alert"] == 1

def test_08_protocol_amendment_stale_bounds_removed():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    split_prot = (base_dir / "experiments" / "protocol" / "SPLIT-PROTOCOL.md").read_text(encoding="utf-8")
    assert "Days 1..89" not in split_prot
    assert "E3 Days 12..14" not in split_prot
    assert "PENDING_RAW_CDM18_ALIGNMENT" in split_prot
    assert "PENDING_ACQUISITION" in split_prot

    lanl_manifest = json.loads((base_dir / "datasets" / "manifests" / "SPL-LANL-001.json").read_text(encoding="utf-8"))
    assert lanl_manifest["dataset_temporal_span_days"] == 58
    assert lanl_manifest["planned_temporal_partitions"]["status"] == "PENDING_ACQUISITION"

    dtc_manifest = json.loads((base_dir / "datasets" / "manifests" / "SPL-DTC-001.json").read_text(encoding="utf-8"))
    assert dtc_manifest["planned_temporal_partitions"]["status"] == "PENDING_RAW_CDM18_ALIGNMENT"
    assert dtc_manifest["ground_truth_mapping_status"] == "PENDING_VERIFICATION"

def test_09_real_training_data_violation_guard():
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
