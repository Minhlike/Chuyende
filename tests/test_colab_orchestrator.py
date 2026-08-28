# -*- coding: utf-8 -*-
"""
Tests for Stage A2 Colab CLI Automation & Orchestrator.
"""

import sys
import json
import pytest
from pathlib import Path
from scripts.colab_a2.wsl_bridge import ColabCLIBridge
from scripts.colab_a2.remote_prepare import build_prepare_script, EXPECTED_HDFS_SHA
from scripts.colab_a2.remote_train import (
    CANONICAL_SEEDS,
    RAW_HDFS_TAR_SHA,
    TRAIN_MEMBERSHIP_SHA,
    VAL_MEMBERSHIP_SHA,
    build_dry_run_script,
    build_authorization_payload,
    build_training_script
)
from scripts.colab_a2.archive_run import build_archive_script
from scripts.colab_a2.orchestrator import get_next_canonical_seed

MOCK_COMMIT = "d89f09b4039bd368cef60b30ae4b8ad9ba6c5e67"

def test_expected_hdfs_sha_matches_raw_dataset():
    assert EXPECTED_HDFS_SHA == "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
    assert RAW_HDFS_TAR_SHA == "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"

def test_canonical_seed_sequence():
    assert CANONICAL_SEEDS == [42, 1337, 2024, 7, 999]

def test_get_next_canonical_seed_when_none_completed():
    statuses = {s: {"status": "NOT_STARTED"} for s in CANONICAL_SEEDS}
    assert get_next_canonical_seed(statuses) == 42

def test_get_next_canonical_seed_when_seed42_incomplete():
    statuses = {
        42: {"status": "RUNNING"},
        1337: {"status": "NOT_STARTED"},
        2024: {"status": "NOT_STARTED"},
        7: {"status": "NOT_STARTED"},
        999: {"status": "NOT_STARTED"}
    }
    assert get_next_canonical_seed(statuses) == 42

def test_get_next_canonical_seed_when_seed42_completed():
    statuses = {
        42: {"status": "COMPLETED"},
        1337: {"status": "NOT_STARTED"},
        2024: {"status": "NOT_STARTED"},
        7: {"status": "NOT_STARTED"},
        999: {"status": "NOT_STARTED"}
    }
    assert get_next_canonical_seed(statuses) == 1337

def test_get_next_canonical_seed_when_all_completed():
    statuses = {s: {"status": "COMPLETED"} for s in CANONICAL_SEEDS}
    assert get_next_canonical_seed(statuses) is None

def test_prepare_script_requires_40_hex_commit():
    with pytest.raises(ValueError, match="APPROVED EXECUTION COMMIT REQUIRED"):
        build_prepare_script("not_a_valid_sha")

def test_dry_run_script_generation_passes_canonical_durable_root():
    script = build_dry_run_script(1337)
    assert "durable_runs = Path('/content/drive/MyDrive/Chuyende-stage-a2/runs/HDFS')" in script
    assert "'--durable-root', str(durable_runs)" in script
    assert "'--dry-run'" in script
    assert "OptimizerStepsExecuted=0" in script

def test_authorization_payload_schema_matches_real_preflight():
    payload_code = build_authorization_payload(1337, MOCK_COMMIT)
    assert f'"expected_execution_code_commit_sha": "{MOCK_COMMIT}"' in payload_code
    assert '"authorization_status": "AUTHORIZED"' in payload_code
    assert '"split_id": "SPL-HDFS-001"' in payload_code
    assert '"train_sessions_count": 35000' in payload_code
    assert '"val_sessions_count": 7500' in payload_code
    assert '"train_graph_events_count": 586577' in payload_code
    assert '"val_graph_events_count": 119531' in payload_code
    assert '"optimizer_steps_per_epoch": 573' in payload_code
    assert '"test_opened": False' in payload_code

def test_training_script_explicitly_passes_authorization():
    script = build_training_script(1337)
    assert "'--authorization', str(auth_path)" in script
    assert "SEED1337-COLAB-LAUNCH-AUTHORIZATION-V1.5.json" in script
    assert "'--authorize-real-empirical-execution'" in script
    assert "durable_runs = Path('/content/drive/MyDrive/Chuyende-stage-a2/runs/HDFS')" in script
    assert "'--durable-root', str(durable_runs)" in script

def test_archive_script_creates_zip_and_sha256():
    script = build_archive_script(1337)
    assert "STAGE-A2-HDFS-SEED1337-COMPLETED-" in script
    assert ".zip.sha256" in script
    assert "zipfile.ZipFile" in script
