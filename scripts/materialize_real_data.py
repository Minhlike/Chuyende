# -*- coding: utf-8 -*-
"""
Execution script to materialize real Label-Free Stage A1 SSL Pretraining inputs
for HDFS and BGL with true two-pass firewall, interval-causal partitioning,
multi-parameter slots, and separate probe label vaults.
"""

import sys
from pathlib import Path

from research_agent.experiments.data.hdfs_adapter import HDFSRealDataAdapter
from research_agent.experiments.data.bgl_adapter import BGLRealDataAdapter

def main():
    if Path("/mnt/d/Research").exists():
        base_dir = Path("/mnt/d/Research")
    else:
        base_dir = Path(r"D:\Research")

    print("=== MATERIALIZING REAL LABEL-FREE HDFS DATA (STAGE A1 SSL) ===")
    hdfs_adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)
    hdfs_summary, hdfs_contract = hdfs_adapter.stream_and_materialize(max_lines=None)
    print("HDFS Raw Local Count:", hdfs_summary["raw_total_line_count"])
    print("HDFS Official Reference Count:", hdfs_summary["reference_record_count"])
    print("HDFS Count Match:", hdfs_summary["raw_total_line_count"] == hdfs_summary["reference_record_count"])
    print("HDFS Train Sessions (Materialized):", hdfs_summary["train_sessions"])
    print("HDFS Val Sessions (Materialized):", hdfs_summary["val_sessions"])
    print("HDFS Test Sessions (Sealed):", hdfs_summary["test_session_count"])
    print("HDFS Test Feature Parse Count:", hdfs_summary["test_feature_parse_count"])
    print("HDFS Test Param Extraction Count:", hdfs_summary["test_param_extraction_count"])
    print("HDFS Test Vocab Contribution:", hdfs_summary["test_vocab_contribution"])
    print("HDFS Test Labels Exposed to Trainer:", hdfs_summary["test_labels_exposed_to_trainer"])
    print("HDFS Purged Train-Val Crossing:", hdfs_summary["purged_train_val_count"])
    print("HDFS Purged Val-Test Crossing:", hdfs_summary["purged_val_test_count"])
    print("HDFS Train Min Start:", hdfs_summary["train_min_start"], "Max End:", hdfs_summary["train_max_end"])
    print("HDFS Val Min Start:", hdfs_summary["val_min_start"], "Max End:", hdfs_summary["val_max_end"])
    print("HDFS Test Min Start:", hdfs_summary["test_min_start"], "Max End:", hdfs_summary["test_max_end"])
    print("HDFS Strict Train < Val:", hdfs_summary["train_max_end"] < hdfs_summary["val_min_start"])
    print("HDFS Strict Val < Test:", hdfs_summary["val_max_end"] < hdfs_summary["test_min_start"])
    print("HDFS Events with 2+ Params:", hdfs_summary["events_with_2plus_params"])
    print("HDFS Total Parameter Instances:", hdfs_summary["total_parameter_instances"])
    print("HDFS Retained Parameter Instances:", hdfs_summary["retained_parameter_instances"])
    print("HDFS Truncated Parameter Instances:", hdfs_summary["truncated_parameter_instances"])
    print("HDFS Parameter Retention Rate:", hdfs_summary["parameter_retention_rate"])
    print("HDFS Parameter Mode:", hdfs_summary["canonical_parameter_mode"])
    print("HDFS Template Vocab Size:", hdfs_summary["template_vocab_size"])
    print("HDFS Param Vocab Size:", hdfs_summary["param_vocab_size"])
    print("HDFS Val OOV Rate:", hdfs_summary["val_oov_event_rate"])
    print("HDFS Test Status:", hdfs_contract.test_status)

    print("\n=== MATERIALIZING REAL LABEL-FREE BGL DATA (STAGE A1 SSL) ===")
    bgl_adapter = BGLRealDataAdapter(base_dir=base_dir, seed=42)
    bgl_summary, bgl_contract = bgl_adapter.stream_and_materialize(max_lines=None)
    print("BGL Raw Local Count:", bgl_summary["raw_total_record_count"])
    print("BGL Official Reference Count:", bgl_summary["reference_record_count"])
    print("BGL Pretest Scanned:", bgl_summary["pretest_scanned_record_count"])
    print("BGL Pretest Valid:", bgl_summary["pretest_valid_record_count"])
    print("BGL Pretest Malformed:", bgl_summary["pretest_malformed_count"])
    print("BGL Conservation Check:", bgl_summary["pretest_scanned_record_count"] == bgl_summary["pretest_valid_record_count"] + bgl_summary["pretest_malformed_count"])
    print("BGL Train Windows:", bgl_summary["train_windows"])
    print("BGL Val Windows:", bgl_summary["val_windows"])
    print("BGL Events with 2+ Params:", bgl_summary["events_with_2plus_params"])
    print("BGL Total Parameter Instances:", bgl_summary["total_parameter_instances"])
    print("BGL Retained Parameter Instances:", bgl_summary["retained_parameter_instances"])
    print("BGL Parameter Retention Rate:", bgl_summary["parameter_retention_rate"])
    print("BGL Node Context Token Count:", bgl_summary["node_context_token_count"])
    print("BGL Unique Racks:", bgl_summary["unique_rack_count"])
    print("BGL Unique Midplanes:", bgl_summary["unique_midplane_count"])
    print("BGL Test Status:", bgl_contract.test_status)

if __name__ == "__main__":
    main()
