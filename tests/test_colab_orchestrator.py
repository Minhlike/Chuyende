# -*- coding: utf-8 -*-
"""
Tests for Stage A2 Colab CLI Automation & Orchestrator.
"""

import sys
import pytest
from pathlib import Path
from scripts.colab_a2.wsl_bridge import ColabCLIBridge
from scripts.colab_a2.remote_prepare import FROZEN_EXECUTION_COMMIT, EXPECTED_HDFS_SHA
from scripts.colab_a2.remote_train import (
    CANONICAL_SEEDS,
    build_dry_run_script,
    build_authorization_payload,
    build_training_script
)
from scripts.colab_a2.archive_run import build_archive_script
from scripts.colab_a2.orchestrator import get_next_canonical_seed

def test_frozen_execution_commit_matches_protocol():
    assert FROZEN_EXECUTION_COMMIT == "d89f09b4039bd368cef60b30ae4b8ad9ba6c5e67"

def test_expected_hdfs_sha_matches_raw_dataset():
    assert EXPECTED_HDFS_SHA == "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"

def test_canonical_seed_sequence():
    assert CANONICAL_SEEDS == [42, 1337, 2024, 7, 999]

def test_get_next_canonical_seed_when_none_completed():
    statuses = {s: {"status": "NOT_STARTED"} for s in CANONICAL_SEEDS}
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

def test_dry_run_script_generation():
    script = build_dry_run_script(1337)
    assert "--seed', '1337'" in script or "--seed', '1337'" in script or "'1337'" in script
    assert "--dry-run" in script
    assert "OptimizerStepsExecuted=0" in script
    assert "TEST_OPENED=false" in script

def test_authorization_payload_binds_frozen_commit():
    payload = build_authorization_payload(1337)
    assert FROZEN_EXECUTION_COMMIT in payload
    assert "SEED1337-COLAB-LAUNCH-AUTHORIZATION-V1.5.json" in payload
    assert "INDEPENDENT_QUALIFICATION_AUDIT_PASS" in payload

def test_training_script_with_resume_args():
    script = build_training_script(1337, resume_checkpoint="/content/drive/last_checkpoint.pt", resume_sha256="abc123def")
    assert "--seed', '1337'" in script or "'1337'" in script
    assert "--resume" in script
    assert "/content/drive/last_checkpoint.pt" in script
    assert "abc123def" in script
    assert "--authorize-real-empirical-execution" in script

def test_archive_script_creates_zip_and_sha256():
    script = build_archive_script(1337)
    assert "STAGE-A2-HDFS-SEED1337-COMPLETED-" in script
    assert ".zip.sha256" in script
    assert "zipfile.ZipFile" in script

def test_colab_bridge_finds_correct_binary():
    bridge = ColabCLIBridge()
    if sys.platform == "win32":
        assert bridge.colab_bin == ["wsl", "-e", "/home/minh123/.local/bin/colab"]
    else:
        assert "colab" in bridge.colab_bin[0]
