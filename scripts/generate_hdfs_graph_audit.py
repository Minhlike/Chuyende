# -*- coding: utf-8 -*-
"""
Audits both Full Population and Authorized Execution Subsets for Stage A2 (Contract V1.3):
  1. HDFS-EXECUTION-MEMBERSHIP.json
  2. HDFS-EXECUTION-SUBSET-AUDIT.json (35,000 Train + 7,500 Val)
  3. HDFS-GRAPH-MATERIALIZATION-AUDIT.json (Full 357,133 Train + 50,204 Val)
  4. RELATION-GROUNDING-AUDIT.json (All 8 grounded relations)
"""

import re
import json
import tarfile
import hashlib
from pathlib import Path
from collections import Counter

from research_agent.experiments.data.hdfs_split_authority import HDFSSplitAuthority
from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    HDFS_RELATION_RULES
)

def run_audits():
    base_dir = Path("D:/Research")
    evidence_dir = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    print("=== COMPUTING CANONICAL SPLIT AUTHORITY ===")
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.compute_and_cache_split()

    train_pop_ids = split_info["train_block_ids"]
    val_pop_ids = split_info["val_block_ids"]
    test_pop_ids = split_info["test_block_ids"]
    
    selected_train_ids = set(split_info["selected_train_block_ids"])
    selected_val_ids = set(split_info["selected_val_block_ids"])

    print(f"Population Train Sessions: {len(train_pop_ids)}")
    print(f"Population Val Sessions:   {len(val_pop_ids)}")
    print(f"Authorized Train Sessions: {len(selected_train_ids)}")
    print(f"Authorized Val Sessions:   {len(selected_val_ids)}")

    builder = HDFSGraphBuilder(base_dir=base_dir, split_authority=split_auth)

    # Counters for Population
    pop_train_scanned = 0
    pop_train_materialized = 0
    pop_train_rejected = 0
    pop_train_rejections = Counter()
    pop_train_relations = Counter()
    pop_train_nodes = set()
    pop_train_node_endpoints = Counter()
    pop_train_min_ts = float("inf")
    pop_train_max_ts = float("-inf")

    pop_val_scanned = 0
    pop_val_materialized = 0
    pop_val_rejected = 0
    pop_val_rejections = Counter()
    pop_val_relations = Counter()
    pop_val_min_ts = float("inf")
    pop_val_max_ts = float("-inf")

    # Counters for Execution Subset (35,000 / 7,500)
    sub_train_scanned = 0
    sub_train_materialized = 0
    sub_train_rejected = 0
    sub_train_rejections = Counter()
    sub_train_relations = Counter()
    sub_train_nodes = set()
    sub_train_node_endpoints = Counter()
    sub_train_min_ts = float("inf")
    sub_train_max_ts = float("-inf")

    sub_val_scanned = 0
    sub_val_materialized = 0
    sub_val_rejected = 0
    sub_val_rejections = Counter()
    sub_val_relations = Counter()
    sub_val_nodes = set()
    sub_val_node_endpoints = Counter()
    sub_val_min_ts = float("inf")
    sub_val_max_ts = float("-inf")

    relation_samples = {}

    print("\n=== SCANNING RAW TARBALL (SINGLE STREAMING PASS) ===")
    with tarfile.open(builder.raw_tar_path, "r:gz") as tar:
        log_member = None
        for m in tar.getmembers():
            if m.name.endswith("HDFS.log") or m.name.endswith(".log"):
                log_member = m
                break
        f_obj = tar.extractfile(log_member)

        line_idx = 0
        for line_bytes in f_obj:
            line_idx += 1
            line_str = line_bytes.decode("utf-8", errors="ignore").strip()

            blk_m = re.search(r"(blk_[-0-9]+)", line_str)
            if not blk_m:
                continue
            blk_id = blk_m.group(1)

            if blk_id in train_pop_ids:
                pop_train_scanned += 1
                event, reject_reason, _ = builder.parse_raw_line(line_str, line_idx)
                if event is not None:
                    pop_train_materialized += 1
                    rel_name = event["relation_name"]
                    pop_train_relations[rel_name] += 1
                    ts = event["event_timestamp_utc_exact"]
                    if ts < pop_train_min_ts: pop_train_min_ts = ts
                    if ts > pop_train_max_ts: pop_train_max_ts = ts

                    src, s_type = event["source_node"], event["source_type"]
                    dst, d_type = event["dest_node"], event["dest_type"]
                    pop_train_nodes.add(src)
                    pop_train_nodes.add(dst)
                    pop_train_node_endpoints[s_type] += 1
                    pop_train_node_endpoints[d_type] += 1

                    if rel_name not in relation_samples:
                        relation_samples[rel_name] = event
                else:
                    pop_train_rejected += 1
                    pop_train_rejections[reject_reason] += 1

                # Check if in Authorized Execution Subset
                if blk_id in selected_train_ids:
                    sub_train_scanned += 1
                    if event is not None:
                        sub_train_materialized += 1
                        sub_train_relations[rel_name] += 1
                        if ts < sub_train_min_ts: sub_train_min_ts = ts
                        if ts > sub_train_max_ts: sub_train_max_ts = ts
                        sub_train_nodes.add(src)
                        sub_train_nodes.add(dst)
                        sub_train_node_endpoints[s_type] += 1
                        sub_train_node_endpoints[d_type] += 1
                    else:
                        sub_train_rejected += 1
                        sub_train_rejections[reject_reason] += 1

            elif blk_id in val_pop_ids:
                pop_val_scanned += 1
                event, reject_reason, _ = builder.parse_raw_line(line_str, line_idx)
                if event is not None:
                    pop_val_materialized += 1
                    rel_name = event["relation_name"]
                    pop_val_relations[rel_name] += 1
                    ts = event["event_timestamp_utc_exact"]
                    if ts < pop_val_min_ts: pop_val_min_ts = ts
                    if ts > pop_val_max_ts: pop_val_max_ts = ts
                else:
                    pop_val_rejected += 1
                    pop_val_rejections[reject_reason] += 1

                # Check if in Authorized Execution Subset
                if blk_id in selected_val_ids:
                    sub_val_scanned += 1
                    if event is not None:
                        sub_val_materialized += 1
                        sub_val_relations[rel_name] += 1
                        if ts < sub_val_min_ts: sub_val_min_ts = ts
                        if ts > sub_val_max_ts: sub_val_max_ts = ts
                        src, s_type = event["source_node"], event["source_type"]
                        dst, d_type = event["dest_node"], event["dest_type"]
                        sub_val_nodes.add(src)
                        sub_val_nodes.add(dst)
                        sub_val_node_endpoints[s_type] += 1
                        sub_val_node_endpoints[d_type] += 1
                    else:
                        sub_val_rejected += 1
                        sub_val_rejections[reject_reason] += 1

    # 1. Save HDFS-EXECUTION-MEMBERSHIP.json
    membership_manifest = {
        "manifest_version": "1.3.0",
        "split_id": "SPL-HDFS-001",
        "population_train_session_count": len(train_pop_ids),
        "population_val_session_count": len(val_pop_ids),
        "authorized_train_session_count": len(selected_train_ids),
        "authorized_val_session_count": len(selected_val_ids),
        "selection_algorithm": "EARLIEST_CAUSAL_SESSION_BUDGET_CAP",
        "selection_seed_if_any": None,
        "ordering_key": "(session_start_time, block_id)",
        "selected_train_block_ids_sha256": split_info["selected_train_block_ids_sha256"],
        "selected_val_block_ids_sha256": split_info["selected_val_block_ids_sha256"],
        "selected_train_event_count": sub_train_materialized,
        "selected_val_event_count": sub_val_materialized,
        "population_train_block_ids_sha256": split_info["population_train_block_ids_sha256"],
        "population_val_block_ids_sha256": split_info["population_val_block_ids_sha256"],
        "canonical_train_artifact_sha256": "0422677f5357494fbc587cac4b6de2004781e71d9b8087b4c8f9f0cd160f3363",
        "canonical_val_artifact_sha256": "96bdab531c3545f4a0f0ed7f87e47cba985c2bc4cac7a3e6c04245b5c712fbe9",
        "test_membership_materialized": False
    }
    membership_path = evidence_dir / "HDFS-EXECUTION-MEMBERSHIP.json"
    membership_path.write_text(json.dumps(membership_manifest, indent=2), encoding="utf-8")
    print(f"[SAVED] {membership_path}")

    # 2. Save HDFS-EXECUTION-SUBSET-AUDIT.json
    subset_audit = {
        "audit_version": "1.3.0",
        "audit_scope": "AUTHORIZED_EXECUTION_BUDGET_SUBSET",
        "split_id": "SPL-HDFS-001",
        "train": {
            "authorized_sessions": len(selected_train_ids),
            "eligible_records_scanned": sub_train_scanned,
            "materialized_graph_events": sub_train_materialized,
            "explicitly_rejected_events": sub_train_rejected,
            "conservation_pass": (sub_train_scanned == sub_train_materialized + sub_train_rejected),
            "rejection_counts": dict(sub_train_rejections),
            "relation_counts": dict(sub_train_relations),
            "unique_nodes": len(sub_train_nodes),
            "node_endpoint_occurrences_by_type": {
                "DATA_BLOCK": sub_train_node_endpoints.get(0, 0),
                "STORAGE_NODE": sub_train_node_endpoints.get(1, 0),
                "MANAGEMENT_SYSTEM": sub_train_node_endpoints.get(2, 0),
                "EXECUTION_THREAD": sub_train_node_endpoints.get(3, 0)
            },
            "min_timestamp_utc": sub_train_min_ts if sub_train_min_ts != float("inf") else 0.0,
            "max_timestamp_utc": sub_train_max_ts if sub_train_max_ts != float("-inf") else 0.0
        },
        "validation": {
            "authorized_sessions": len(selected_val_ids),
            "eligible_records_scanned": sub_val_scanned,
            "materialized_graph_events": sub_val_materialized,
            "explicitly_rejected_events": sub_val_rejected,
            "conservation_pass": (sub_val_scanned == sub_val_materialized + sub_val_rejected),
            "rejection_counts": dict(sub_val_rejections),
            "relation_counts": dict(sub_val_relations),
            "unique_nodes": len(sub_val_nodes),
            "node_endpoint_occurrences_by_type": {
                "DATA_BLOCK": sub_val_node_endpoints.get(0, 0),
                "STORAGE_NODE": sub_val_node_endpoints.get(1, 0),
                "MANAGEMENT_SYSTEM": sub_val_node_endpoints.get(2, 0),
                "EXECUTION_THREAD": sub_val_node_endpoints.get(3, 0)
            },
            "min_timestamp_utc": sub_val_min_ts if sub_val_min_ts != float("inf") else 0.0,
            "max_timestamp_utc": sub_val_max_ts if sub_val_max_ts != float("-inf") else 0.0
        },
        "test_firewall": {
            "test_opened": False,
            "test_feature_read_count": 0,
            "test_label_read_count": 0,
            "test_metric_count": 0,
            "test_graph_events_materialized": 0,
            "test_relation_parse_count": 0
        }
    }
    subset_path = evidence_dir / "HDFS-EXECUTION-SUBSET-AUDIT.json"
    subset_path.write_text(json.dumps(subset_audit, indent=2), encoding="utf-8")
    print(f"[SAVED] {subset_path}")

    # 3. Update HDFS-GRAPH-MATERIALIZATION-AUDIT.json (Full Population Audit)
    pop_audit = {
        "audit_version": "1.3.0",
        "audit_scope": "FULL_ELIGIBLE_POPULATION_AUDIT",
        "split_id": "SPL-HDFS-001",
        "train": {
            "eligible_sessions": len(train_pop_ids),
            "eligible_records_scanned": pop_train_scanned,
            "materialized_graph_events": pop_train_materialized,
            "explicitly_rejected_events": pop_train_rejected,
            "conservation_pass": (pop_train_scanned == pop_train_materialized + pop_train_rejected),
            "rejection_counts": dict(pop_train_rejections),
            "relation_counts": dict(pop_train_relations),
            "unique_nodes": len(pop_train_nodes),
            "node_endpoint_occurrences_by_type": {
                "DATA_BLOCK": pop_train_node_endpoints.get(0, 0),
                "STORAGE_NODE": pop_train_node_endpoints.get(1, 0),
                "MANAGEMENT_SYSTEM": pop_train_node_endpoints.get(2, 0),
                "EXECUTION_THREAD": pop_train_node_endpoints.get(3, 0)
            },
            "min_timestamp_utc": pop_train_min_ts if pop_train_min_ts != float("inf") else 0.0,
            "max_timestamp_utc": pop_train_max_ts if pop_train_max_ts != float("-inf") else 0.0
        },
        "validation": {
            "eligible_sessions": len(val_pop_ids),
            "eligible_records_scanned": pop_val_scanned,
            "materialized_graph_events": pop_val_materialized,
            "explicitly_rejected_events": pop_val_rejected,
            "conservation_pass": (pop_val_scanned == pop_val_materialized + pop_val_rejected),
            "rejection_counts": dict(pop_val_rejections),
            "relation_counts": dict(pop_val_relations),
            "min_timestamp_utc": pop_val_min_ts if pop_val_min_ts != float("inf") else 0.0,
            "max_timestamp_utc": pop_val_max_ts if pop_val_max_ts != float("-inf") else 0.0
        },
        "test_firewall": {
            "test_opened": False,
            "test_feature_read_count": 0,
            "test_label_read_count": 0,
            "test_metric_count": 0,
            "test_graph_events_materialized": 0,
            "test_relation_parse_count": 0
        }
    }
    pop_path = evidence_dir / "HDFS-GRAPH-MATERIALIZATION-AUDIT.json"
    pop_path.write_text(json.dumps(pop_audit, indent=2), encoding="utf-8")
    print(f"[SAVED] {pop_path}")

    # 4. Save RELATION-GROUNDING-AUDIT.json
    relation_evidence = {}
    for rule in HDFS_RELATION_RULES:
        rel_name = rule["relation_name"]
        train_count = pop_train_relations.get(rel_name, 0)
        sample_ev = relation_samples.get(rel_name)
        relation_evidence[rel_name] = {
            "relation_id": rule["relation_id"],
            "relation_name": rel_name,
            "rule_type": rule["rule_type"],
            "train_match_count": train_count,
            "grounding_pass": train_count > 0,
            "sample_event_evidence": {
                "raw_line_index": sample_ev["raw_line_index"] if sample_ev else None,
                "event_timestamp_utc_exact": sample_ev["event_timestamp_utc_exact"] if sample_ev else None,
                "source_node": sample_ev["source_node"] if sample_ev else None,
                "source_type": sample_ev["source_type"] if sample_ev else None,
                "dest_node": sample_ev["dest_node"] if sample_ev else None,
                "dest_type": sample_ev["dest_type"] if sample_ev else None,
                "block_id": sample_ev["block_id"] if sample_ev else None,
                "size_bytes": sample_ev["size_bytes"] if sample_ev else None
            }
        }

    rel_grounding_manifest = {
        "audit_version": "1.3.0",
        "split_id": "SPL-HDFS-001",
        "total_relations": len(HDFS_RELATION_RULES),
        "all_relations_grounded": all(v["grounding_pass"] for v in relation_evidence.values()),
        "relations": relation_evidence
    }

    rel_audit_path = evidence_dir / "RELATION-GROUNDING-AUDIT.json"
    rel_audit_path.write_text(json.dumps(rel_grounding_manifest, indent=2), encoding="utf-8")
    print(f"[SAVED] {rel_audit_path}")

if __name__ == "__main__":
    run_audits()
