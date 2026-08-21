# -*- coding: utf-8 -*-
"""
Automated Test Suite for Dataset Acquisition, Storage Policy, and Integrity Validation
Tests streaming checksums, archive integrity, timestamp monotonic ordering, and storage cleanliness.
"""

import os
import gzip
import json
import pytest
from pathlib import Path

from research_agent.verification.datasets.streaming_validator import (
    compute_streaming_sha256,
    line_stream_reader,
    StreamingDatasetValidator
)

@pytest.fixture
def workspace_root():
    return Path(r"D:\Research")

@pytest.fixture
def validator(workspace_root):
    return StreamingDatasetValidator(workspace_root)

def test_01_storage_manifest_d_drive_allocation(workspace_root):
    manifest_path = workspace_root / "experiments" / "environment" / "STORAGE-MANIFEST.json"
    assert manifest_path.exists(), "STORAGE-MANIFEST.json must exist."
    
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["wsl_physical_storage_allocation"]["distro_vhdx_on_d"] is True
    assert data["wsl_physical_storage_allocation"]["wsl_swap_on_d"] is True
    assert data["cleanliness_audit"]["research_heavy_storage_on_d_gate"] == "PASS"

def test_02_storage_cleanliness_c_drive(validator):
    cleanliness = validator.audit_storage_cleanliness()
    assert cleanliness["status"] == "PASS"
    assert cleanliness["large_research_artifacts_on_c"] == 0

def test_03_hdfs_raw_artifact_and_labels_exist(workspace_root):
    hdfs_tar = workspace_root / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz"
    hdfs_labels = workspace_root / "datasets" / "raw" / "hdfs" / "anomaly_label.csv"
    
    assert hdfs_tar.exists(), "HDFS_1.tar.gz must exist on D: drive."
    assert hdfs_labels.exists(), "anomaly_label.csv must exist on D: drive."
    
    sha256, size = compute_streaming_sha256(hdfs_tar)
    assert size > 100 * 1024 * 1024, "HDFS raw tarball must be > 100 MiB."
    assert sha256 == "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"

def test_04_bgl_raw_artifact_exists_and_valid(workspace_root, validator):
    bgl_tar = workspace_root / "datasets" / "raw" / "bgl" / "BGL.tar.gz"
    assert bgl_tar.exists(), "BGL.tar.gz must exist on D: drive."
    
    sha256, size = compute_streaming_sha256(bgl_tar)
    assert size > 50 * 1024 * 1024, "BGL tarball must be > 50 MiB."
    assert sha256 == "0a58be959cef101bbe5c053e60bd8a49673e9c942b164f4d969bb109e99fce95"

def test_05_darpa_e3_e5_metadata_schema_versions(workspace_root):
    e3_cdm = workspace_root / "datasets" / "raw" / "darpa" / "e3" / "metadata" / "CDM18.avdl"
    e5_cdm = workspace_root / "datasets" / "raw" / "darpa" / "e5" / "metadata" / "CDM20.avdl"
    
    assert e3_cdm.exists(), "CDM18.avdl must exist for DARPA E3."
    assert e5_cdm.exists(), "CDM20.avdl must exist for DARPA E5."
    
    assert "cdm18" in e3_cdm.read_text(encoding="utf-8").lower()
    assert "cdm20" in e5_cdm.read_text(encoding="utf-8").lower()

def test_06_split_manifests_lifecycle_states(workspace_root):
    manifests_dir = workspace_root / "datasets" / "manifests"
    
    spl_hdfs = json.loads((manifests_dir / "SPL-HDFS-001.json").read_text(encoding="utf-8"))
    spl_bgl = json.loads((manifests_dir / "SPL-BGL-001.json").read_text(encoding="utf-8"))
    spl_dtc = json.loads((manifests_dir / "SPL-DTC-001.json").read_text(encoding="utf-8"))
    spl_lanl = json.loads((manifests_dir / "SPL-LANL-001.json").read_text(encoding="utf-8"))
    
    assert spl_hdfs["status"] == "VALIDATED"
    assert spl_bgl["status"] == "VALIDATED"
    assert spl_dtc["status"] in ["PLANNED", "METADATA_ACQUIRED"]
    assert spl_lanl["status"] == "USER_ACTION_REQUIRED"
    assert spl_lanl["redteam_record_count"] == "PENDING_VERIFICATION"

def test_07_corrupted_archive_detection(tmp_path):
    corrupted_file = tmp_path / "corrupted.tar.gz"
    corrupted_file.write_bytes(b"NOT_A_VALID_GZIP_OR_TAR_DATA_12345")
    
    with pytest.raises(Exception):
        for _ in line_stream_reader(corrupted_file):
            pass

def test_08_timestamp_inversion_detection(tmp_path, validator):
    sample_bgl = tmp_path / "sample_bgl.log"
    # Create artificial log with intentional timestamp inversion (1000 -> 900)
    sample_bgl.write_text(
        "- 1000 2005-06-03 R02-M1-N0-C:J12-U11 RAS KERNEL INFO message1\n"
        "APPRIS 900 2005-06-03 R02-M1-N0-C:J12-U11 RAS KERNEL INFO message2\n",
        encoding="utf-8"
    )
    res = validator.validate_bgl(sample_bgl)
    assert res["timestamp_inversions"] == 1
