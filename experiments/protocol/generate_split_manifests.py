# -*- coding: utf-8 -*-
"""
Deterministic Split Manifest Generator (Pre-Acquisition State: PLANNED)
Version: 1.1.0 (CDM18 for E3, CDM20 for E5, Pending LANL Verification)
"""

import json
import hashlib
from pathlib import Path

def generate_planned_split_manifests():
    manifests_dir = Path(r"D:\Research\datasets\manifests")
    manifests_dir.mkdir(parents=True, exist_ok=True)

    planned_splits = [
        {
            "split_id": "SPL-HDFS-001",
            "dataset_id": "DATA-HDFS-001",
            "dataset_name": "HDFS LogHub Benchmark",
            "version": "v1.0",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "STRICT_CAUSAL_TIME",
            "planned_ratios": {"train": 0.70, "val": 0.15, "test": 0.15},
            "holdout_specification": {"oov_anomaly_template_ratio": 0.10},
            "seed": 42,
            "acquisition_requirements": [
                "Verify LogHub HDFS raw log archive checksum",
                "Fit Drain/Spell template parser strictly on Train split",
                "Extract session IDs and compute causal timestamp bounds"
            ]
        },
        {
            "split_id": "SPL-BGL-001",
            "dataset_id": "DATA-BGL-001",
            "dataset_name": "BGL Supercomputer Log",
            "version": "v1.0",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "STRICT_CAUSAL_TIME",
            "planned_temporal_partitions": {
                "train_days": [1, 150],
                "val_days": [151, 180],
                "test_days": [181, 215]
            },
            "seed": 42,
            "acquisition_requirements": [
                "Verify LLNL BGL raw log checksum",
                "Validate 214.7 day timestamp monotonic sequence",
                "Isolate Days 181+ failure codes for template drift evaluation"
            ]
        },
        {
            "split_id": "SPL-DTC-001",
            "dataset_id": "DATA-DTC-001",
            "dataset_name": "DARPA Transparent Computing E3/E5",
            "version": "v1.1",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "CAUSAL_SCENARIO_HOST_HOLDOUT",
            "official_schemas": {
                "engagement_3": "CDM18",
                "engagement_5": "CDM20"
            },
            "official_performer_universe": [
                "CADETS", "ClearScope", "FiveDirections", "MARPLE", "THEIA", "TRACE"
            ],
            "pre_registered_experimental_subset": [
                "THEIA", "CADETS", "FiveDirections"
            ],
            "ground_truth_mapping_status": "PENDING_ARTIFACT_PARSE",
            "seed": 42,
            "acquisition_requirements": [
                "Verify official DARPA CDM18 (E3) and CDM20 (E5) checksums",
                "Extract attack ground truth matching official engagement reports",
                "Verify zero test ground-truth leakage into train plane"
            ]
        },
        {
            "split_id": "SPL-LANL-001",
            "dataset_id": "DATA-LANL-001",
            "dataset_name": "LANL Cyber Security Data Set 2015",
            "version": "v1.1",
            "status": "PLANNED",
            "raw_dataset_acquired": False,
            "partition_strategy": "STRICT_CAUSAL_TIME",
            "planned_temporal_partitions": {
                "train_seconds": [1, 5184000],
                "val_seconds": [5184001, 6393600],
                "test_seconds": [6393601, 7776000]
            },
            "redteam_record_count": "PENDING_VERIFICATION",
            "redteam_label_boundary": "AUTH_EVENT_EXACT_MATCH_ONLY",
            "seed": 42,
            "acquisition_requirements": [
                "Verify LANL auth.txt.gz and redteam.txt.gz official checksums",
                "Enforce strict non-propagation of redteam labels to proc/flow",
                "Build host-day authentication bags for Stage B MIL"
            ]
        }
    ]

    for sp in planned_splits:
        sp_bytes = json.dumps(sp, indent=2, sort_keys=True).encode("utf-8")
        sp["specification_sha256"] = hashlib.sha256(sp_bytes).hexdigest()
        out_path = manifests_dir / f"{sp['split_id']}.json"
        out_path.write_text(json.dumps(sp, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[OK] Exported PLANNED split manifest: {out_path.name}")

if __name__ == "__main__":
    generate_planned_split_manifests()
