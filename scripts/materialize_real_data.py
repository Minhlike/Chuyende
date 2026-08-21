# -*- coding: utf-8 -*-
"""
Execution script to materialize real Train/Validation splits for HDFS and BGL
without opening the Test split or using any synthetic proxies.
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

    print("=== MATERIALIZING REAL HDFS DATA (TRAIN + VAL) ===")
    hdfs_adapter = HDFSRealDataAdapter(base_dir=base_dir, seed=42)
    hdfs_summary, hdfs_contract = hdfs_adapter.stream_and_materialize(max_lines=None)
    print("HDFS Train Sessions:", hdfs_summary["train_sessions"])
    print("HDFS Val Sessions:", hdfs_summary["val_sessions"])
    print("HDFS Template Vocab:", hdfs_summary["template_vocab_size"])
    print("HDFS Param Vocab:", hdfs_summary["param_vocab_size"])
    print("HDFS Val OOV Rate:", hdfs_summary["val_oov_event_rate"])
    print("HDFS Synthetic Proxy Count:", hdfs_contract.synthetic_proxy_count)
    print("HDFS Test Status:", hdfs_contract.test_status)

    print("\n=== MATERIALIZING REAL BGL DATA (TRAIN + VAL) ===")
    bgl_adapter = BGLRealDataAdapter(base_dir=base_dir, seed=42)
    bgl_summary, bgl_contract = bgl_adapter.stream_and_materialize(max_lines=None)
    print("BGL Train Windows:", bgl_summary["train_windows"])
    print("BGL Val Windows:", bgl_summary["val_windows"])
    print("BGL Template Vocab:", bgl_summary["template_vocab_size"])
    print("BGL Param Vocab:", bgl_summary["param_vocab_size"])
    print("BGL Val OOV Rate:", bgl_summary["val_oov_event_rate"])
    print("BGL Synthetic Proxy Count:", bgl_contract.synthetic_proxy_count)
    print("BGL Test Status:", bgl_contract.test_status)

if __name__ == "__main__":
    main()
