# -*- coding: utf-8 -*-
"""
Execution script to materialize real Train/Validation splits for HDFS and BGL
with strict interval-causal partitioning, boundary purging, test label vaulting,
and BGL node context tracking.
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

    print("=== MATERIALIZING REAL HDFS DATA (INTERVAL-CAUSAL TRAIN + VAL) ===")
    hdfs_adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)
    hdfs_summary, hdfs_contract = hdfs_adapter.stream_and_materialize(max_lines=None)
    print("HDFS Raw Total Lines:", hdfs_summary["raw_total_line_count"])
    print("HDFS Train Sessions (Materialized):", hdfs_summary["train_sessions"])
    print("HDFS Val Sessions (Materialized):", hdfs_summary["val_sessions"])
    print("HDFS Purged Train-Val Crossing:", hdfs_summary["purged_train_val_count"])
    print("HDFS Purged Val-Test Crossing:", hdfs_summary["purged_val_test_count"])
    print("HDFS Train Min Start:", hdfs_summary["train_min_start"], "Max End:", hdfs_summary["train_max_end"])
    print("HDFS Val Min Start:", hdfs_summary["val_min_start"], "Max End:", hdfs_summary["val_max_end"])
    print("HDFS Test Min Start:", hdfs_summary["test_min_start"], "Max End:", hdfs_summary["test_max_end"])
    print("HDFS Strict Train < Val:", hdfs_summary["train_max_end"] < hdfs_summary["val_min_start"])
    print("HDFS Strict Val < Test:", hdfs_summary["val_max_end"] < hdfs_summary["test_min_start"])
    print("HDFS Template Vocab Size:", hdfs_summary["template_vocab_size"])
    print("HDFS Param Vocab Size:", hdfs_summary["param_vocab_size"])
    print("HDFS Val OOV Rate:", hdfs_summary["val_oov_event_rate"])
    print("HDFS Test Status:", hdfs_contract.test_status)

    print("\n=== MATERIALIZING REAL BGL DATA (TRAIN + VAL) ===")
    bgl_adapter = BGLRealDataAdapter(base_dir=base_dir, seed=42)
    bgl_summary, bgl_contract = bgl_adapter.stream_and_materialize(max_lines=None)
    print("BGL Raw Total Lines:", bgl_summary["raw_total_record_count"])
    print("BGL Pretest Scanned:", bgl_summary["pretest_scanned_record_count"])
    print("BGL Pretest Valid:", bgl_summary["pretest_valid_record_count"])
    print("BGL Pretest Malformed:", bgl_summary["pretest_malformed_count"])
    print("BGL Conservation Check:", bgl_summary["pretest_scanned_record_count"] == bgl_summary["pretest_valid_record_count"] + bgl_summary["pretest_malformed_count"])
    print("BGL Train Windows:", bgl_summary["train_windows"])
    print("BGL Val Windows:", bgl_summary["val_windows"])
    print("BGL Node Context Token Count:", bgl_summary["node_context_token_count"])
    print("BGL Unique Racks:", bgl_summary["unique_rack_count"])
    print("BGL Unique Midplanes:", bgl_summary["unique_midplane_count"])
    print("BGL Test Status:", bgl_contract.test_status)

if __name__ == "__main__":
    main()
