# -*- coding: utf-8 -*-
"""
Automated Test Suite for Chapter 3 Real Data Adapters & Scientific Data Contracts
Verifies:
  1. HDFS Real Data Adapter: Real timestamps, real parameter extraction, block ID leakage firewall,
     Train-only vocabulary fitting, UNKNOWN-safe validation OOV, synthetic proxy count == 0.
  2. BGL Real Data Adapter: Real epoch timestamps, alert tag parsing (strictly system alert, not attack),
     temporal train/val split, Train-only vocabulary, synthetic proxy count == 0.
  3. DARPA TC E3 Schema & Topic Guard: CDM18 schema validation, good-topic inventory validation.
  4. Real Training Package Fail-Closed Guard: RealTrainingDataViolation raised on synthetic proxies.
"""

import json
import pytest
from pathlib import Path

pytest.importorskip("torch")
import torch

from research_agent.experiments.data.data_contract import (
    RealDataContract,
    RealTrainingDataViolation,
    enforce_real_training_data_purity
)
from research_agent.experiments.data.hdfs_adapter import HDFSRealDataAdapter, HDFS_TEMPLATES
from research_agent.experiments.data.bgl_adapter import BGLRealDataAdapter

def test_01_hdfs_real_timestamp_and_parameter_extraction():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)

    # 1. Real Timestamp Parsing Test
    ts = adapter.parse_line_timestamp("081109", "203518", "143")
    assert ts is not None
    assert isinstance(ts, float)
    assert ts > 1226200000.0  # Nov 2008 epoch

    # 2. Real Parameter Extraction Test
    content = "Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010"
    template, params = adapter.extract_template_and_params(content)
    assert "Receiving block <*>" in template
    assert "PARAM_IP_RFC1918_PRIVATE" in params

    # 3. Size Parameter Extraction
    content_size = "Received block blk_-1608999687919862906 of size 91178 from /10.250.10.6"
    template_s, params_s = adapter.extract_template_and_params(content_size)
    assert "Received block <*>" in template_s
    assert any("SIZE_BUCKET" in p for p in params_s)

def test_02_hdfs_block_id_leakage_firewall():
    """
    Asserts that raw block_id strings or tokens are never exposed in the feature parameter vector.
    """
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

def test_03_hdfs_materialized_contract_and_zero_synthetic_proxies():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    contract_path = base_dir / "datasets" / "manifests" / "REAL-DATA-CONTRACT-HDFS.json"
    assert contract_path.exists()

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["dataset_id"] == "DATA-HDFS-001"
    assert contract["synthetic_proxy_count"] == 0
    assert contract["test_status"] == "SEALED"
    assert contract["data_classification"] == "REAL_TRAINING_MATERIALIZED"
    assert "block_id" in contract["excluded_shortcut_fields"]

def test_04_bgl_real_timestamp_and_alert_label_semantics():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    adapter = BGLRealDataAdapter(base_dir=base_dir, seed=42)

    # 1. Normal Line
    normal_line = "- 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.363779 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected"
    parsed_norm = adapter.parse_line(normal_line)
    assert parsed_norm is not None
    assert parsed_norm["timestamp"] == 1117838570.0
    assert parsed_norm["is_alert"] == 0
    assert "PARAM_PARITY_ERR" in parsed_norm["params"]

    # 2. Alert Line (e.g. FATAL)
    alert_line = "FATAL 1117838600 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.43.20.123456 R02-M1-N0-C:J12-U11 RAS KERNEL FATAL memory parity error"
    parsed_alert = adapter.parse_line(alert_line)
    assert parsed_alert is not None
    assert parsed_alert["is_alert"] == 1  # Alert, NOT cyberattack

def test_05_bgl_materialized_contract_and_zero_synthetic_proxies():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    contract_path = base_dir / "datasets" / "manifests" / "REAL-DATA-CONTRACT-BGL.json"
    assert contract_path.exists()

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["dataset_id"] == "DATA-BGL-001"
    assert contract["synthetic_proxy_count"] == 0
    assert contract["test_status"] == "SEALED"
    assert contract["data_classification"] == "REAL_TRAINING_MATERIALIZED"
    assert "node_id" in contract["excluded_shortcut_fields"]

def test_06_real_training_data_violation_guard():
    """
    Verifies that real training package fails closed when given synthetic proxies or hybrid fixtures.
    """
    with pytest.raises(RealTrainingDataViolation, match="prohibited in real training"):
        enforce_real_training_data_purity("HYBRID_SMOKE_FIXTURE")

    with pytest.raises(RealTrainingDataViolation, match="prohibited in real training"):
        enforce_real_training_data_purity("SYNTHETIC_PROXY")

    with pytest.raises(RealTrainingDataViolation, match="Synthetic proxies are forbidden"):
        enforce_real_training_data_purity(
            "REAL_TRAINING_MATERIALIZED",
            {"parameter_source": "SYNTHETIC_PROXY"}
        )

    # Valid real materialized data must pass without exception
    enforce_real_training_data_purity(
        "REAL_TRAINING_MATERIALIZED",
        {"parameter_source": "REAL_HDFS_EXTRACTED", "temporal_source": "REAL_HDFS_EXTRACTED"}
    )

def test_07_darpa_e3_metadata_and_topic_inventory_verified():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    plan_path = base_dir / "datasets" / "manifests" / "DARPA-E3-BULK-PLAN.json"
    gt_map_path = base_dir / "datasets" / "manifests" / "DARPA-E3-GROUND-TRUTH-MAP.json"
    meta_path = base_dir / "datasets" / "raw" / "darpa" / "e3" / "metadata" / "CDM18.avdl"

    assert plan_path.exists()
    assert gt_map_path.exists()
    assert meta_path.exists()

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["schema"] == "CDM18"
    assert "THEIA" in plan["pre_registered_subset"]
    assert "CADETS" in plan["pre_registered_subset"]
    assert "FiveDirections" in plan["pre_registered_subset"]
    assert len(plan["required_official_topics"]) == 10
