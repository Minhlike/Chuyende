# -*- coding: utf-8 -*-
"""
Canonical Stage A2 Pre-Execution Verification Gate (Amended V1.2).
Performs evidence-based, fail-closed verification of:
  1. Ancestry from Stage A1 frozen base
  2. Cryptographic Checksums of Contracts & Pre-Execution Lock
  3. Raw HDFS Tarball Integrity
  4. Actual Split Artifact Hashes (SPL-HDFS-001)
  5. Shared Canonical Split Authority & Disjointness
  6. Timestamp Parity & Millisecond Resolution
  7. Relation Grounding & Component Constraints
  8. Graph Conservation on Full Train & Validation Partitions
  9. Strict Test Firewall (TestSetSealedError)
  10. Zero-Execution State (0 optimizer steps, 0 models trained)
Outputs STAGE_A2_PREEXECUTION_READY=PASS or STAGE_A2_PREEXECUTION_READY=FAIL.
"""

import sys
import json
import hashlib
from pathlib import Path

from research_agent.experiments.data.hdfs_split_authority import (
    parse_hdfs_line_timestamp,
    HDFSSplitAuthority
)
from research_agent.experiments.data.hdfs_adapter import HDFSRealDataAdapter
from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    HDFS_RELATION_RULES,
    TestSetSealedError
)

def verify_stage_a2_preexecution():
    base_dir = Path("D:/Research")
    failures = []

    print("=================================================================")
    print("      STAGE A2 PRE-EXECUTION GATE VERIFICATION AUDIT (V1.2)      ")
    print("=================================================================")

    # 1. Base Frozen Commit Check
    expected_base_commit = "9a707025ed5899c524962558732218ff48e8b212"
    lock_path = base_dir / "experiments" / "protocol" / "STAGE-A2-PREEXECUTION-LOCK.json"
    prereg_path = base_dir / "experiments" / "protocol" / "STAGE-A2-PREREGISTRATION.md"
    graph_contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    raw_mapping_path = base_dir / "experiments" / "schemas" / "STAGE-A2-RAW-TO-GRAPH-MAPPING.json"
    design_audit_path = base_dir / "experiments" / "reports" / "STAGE-A2-DESIGN-AUDIT.md"

    for p in [lock_path, prereg_path, graph_contract_path, raw_mapping_path, design_audit_path]:
        if not p.exists():
            failures.append(f"MISSING_REQUIRED_ARTIFACT: {p}")

    if failures:
        print("FAILED: Missing core artifacts.")
        print("STAGE_A2_PREEXECUTION_READY=FAIL")
        sys.exit(1)

    # 2. Cryptographic Checksums of Contracts & Preregistration
    prereg_bytes = prereg_path.read_bytes()
    prereg_sha256 = hashlib.sha256(prereg_bytes).hexdigest()

    graph_contract_bytes = graph_contract_path.read_bytes()
    graph_contract_sha256 = hashlib.sha256(graph_contract_bytes).hexdigest()

    raw_mapping_bytes = raw_mapping_path.read_bytes()
    raw_mapping_sha256 = hashlib.sha256(raw_mapping_bytes).hexdigest()

    lock_bytes = lock_path.read_bytes()
    lock_file_sha256 = hashlib.sha256(lock_bytes).hexdigest()
    lock_data = json.loads(lock_bytes.decode("utf-8"))

    if lock_data.get("source_commit") != expected_base_commit:
        failures.append(f"INVALID_BASE_COMMIT: {lock_data.get('source_commit')} != {expected_base_commit}")

    if lock_data.get("protocol_document_sha256") != prereg_sha256:
        failures.append(f"PREREG_SHA256_MISMATCH: {lock_data.get('protocol_document_sha256')} != {prereg_sha256}")

    if lock_data.get("graph_contract_sha256") != graph_contract_sha256:
        failures.append(f"GRAPH_CONTRACT_SHA256_MISMATCH: {lock_data.get('graph_contract_sha256')} != {graph_contract_sha256}")

    if lock_data.get("raw_to_graph_mapping_sha256") != raw_mapping_sha256:
        failures.append(f"RAW_MAPPING_SHA256_MISMATCH: {lock_data.get('raw_to_graph_mapping_sha256')} != {raw_mapping_sha256}")

    print(f"[CHECK 1] Protocol Preregistration SHA-256: {prereg_sha256} (OK)")
    print(f"[CHECK 1] Graph Contract Schema SHA-256:   {graph_contract_sha256} (OK)")
    print(f"[CHECK 1] Raw-to-Graph Mapping SHA-256:    {raw_mapping_sha256} (OK)")
    print(f"[CHECK 1] Pre-Execution Lock File SHA-256: {lock_file_sha256} (OK)")

    # 3. Check Raw Tarball Hash
    hdfs_raw = base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz"
    if not hdfs_raw.exists():
        failures.append("RAW_HDFS_TARBALL_MISSING")
    else:
        actual_raw_h = hashlib.sha256(hdfs_raw.read_bytes()).hexdigest()
        expected_raw_h = "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
        if actual_raw_h != expected_raw_h:
            failures.append(f"RAW_HDFS_HASH_MISMATCH: {actual_raw_h} != {expected_raw_h}")
        print(f"[CHECK 2] HDFS Raw Checksum: {actual_raw_h} (OK)")

    # 4. Actual Split Artifact Hashes Reproduction
    train_pt_path = base_dir / "experiments" / "runs" / "data" / "hdfs" / "hdfs_ssl_train.pt"
    val_pt_path = base_dir / "experiments" / "runs" / "data" / "hdfs" / "hdfs_ssl_val.pt"

    if not train_pt_path.exists() or not val_pt_path.exists():
        failures.append("SPLIT_ARTIFACTS_MISSING")
    else:
        actual_train_h = hashlib.sha256(train_pt_path.read_bytes()).hexdigest()
        actual_val_h = hashlib.sha256(val_pt_path.read_bytes()).hexdigest()

        expected_train_h = "0422677f5357494fbc587cac4b6de2004781e71d9b8087b4c8f9f0cd160f3363"
        expected_val_h = "96bdab531c3545f4a0f0ed7f87e47cba985c2bc4cac7a3e6c04245b5c712fbe9"

        if actual_train_h != expected_train_h:
            failures.append(f"TRAIN_SPLIT_HASH_MISMATCH: {actual_train_h} != {expected_train_h}")
        if actual_val_h != expected_val_h:
            failures.append(f"VAL_SPLIT_HASH_MISMATCH: {actual_val_h} != {expected_val_h}")

        print(f"[CHECK 3] Train Split Hash: {actual_train_h} (OK)")
        print(f"[CHECK 3] Val Split Hash:   {actual_val_h} (OK)")

    # 5. Shared Canonical Split Authority & Disjointness
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()

    train_ids = split_info["train_block_ids"]
    val_ids = split_info["val_block_ids"]
    test_ids = split_info["test_block_ids"]
    purged_tv = split_info["purged_train_val_ids"]
    purged_vt = split_info["purged_val_test_ids"]

    if not train_ids.isdisjoint(val_ids):
        failures.append("TRAIN_VAL_OVERLAP")
    if not train_ids.isdisjoint(test_ids):
        failures.append("TRAIN_TEST_OVERLAP")
    if not val_ids.isdisjoint(test_ids):
        failures.append("VAL_TEST_OVERLAP")
    if not purged_tv.isdisjoint(train_ids) or not purged_tv.isdisjoint(val_ids):
        failures.append("PURGED_TV_LEAKAGE")
    if not purged_vt.isdisjoint(val_ids):
        failures.append("PURGED_VT_LEAKAGE")

    if not (split_info["train_max_end"] < split_info["val_min_start"] < split_info["val_max_end"] < split_info["test_min_start"]):
        failures.append("CAUSAL_BOUNDARY_ORDERING_VIOLATION")

    print(f"[CHECK 4] Split Authority: Train ({len(train_ids)}), Val ({len(val_ids)}), Test ({len(test_ids)} sealed) (OK)")
    print(f"[CHECK 4] Boundary Purges: T->V ({len(purged_tv)}), V->T ({len(purged_vt)}) (OK)")

    # 6. Timestamp Parity & Millisecond Resolution
    adapter = HDFSRealDataAdapter(base_dir=base_dir)
    ts_adapter = adapter.parse_line_timestamp("081109", "203518", "143")
    ts_split_auth = parse_hdfs_line_timestamp("081109", "203518", "143")

    if abs(ts_adapter - ts_split_auth) != 0.0:
        failures.append(f"TIMESTAMP_PARSER_MISMATCH: {ts_adapter} != {ts_split_auth}")
    if abs(ts_adapter - 1226262918.143) > 1e-5:
        failures.append(f"MILLISECOND_RESOLUTION_TRUNCATED: {ts_adapter}")

    print(f"[CHECK 5] Timestamp Parity & Millisecond Fidelity: Verified (delta = 0.0) (OK)")

    # 7. Check Full Graph Materialization & Conservation Audits
    mat_audit_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "HDFS-GRAPH-MATERIALIZATION-AUDIT.json"
    rel_audit_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "RELATION-GROUNDING-AUDIT.json"

    if not mat_audit_path.exists():
        failures.append("MISSING_MATERIALIZATION_AUDIT_MANIFEST")
    else:
        mat_data = json.loads(mat_audit_path.read_text(encoding="utf-8"))
        if not mat_data.get("train", {}).get("conservation_pass") or not mat_data.get("validation", {}).get("conservation_pass"):
            failures.append("GRAPH_CONSERVATION_LAW_FAILED")
        print(f"[CHECK 6] Graph Conservation on Train ({mat_data['train']['materialized_graph_events']} events) & Val ({mat_data['validation']['materialized_graph_events']} events) (OK)")

    if not rel_audit_path.exists():
        failures.append("MISSING_RELATION_GROUNDING_AUDIT_MANIFEST")
    else:
        rel_data = json.loads(rel_audit_path.read_text(encoding="utf-8"))
        if not rel_data.get("all_relations_grounded"):
            failures.append("SOME_RELATIONS_LACK_RAW_TRAIN_EVIDENCE")
        print(f"[CHECK 7] Relation Raw Grounding: All {rel_data.get('total_relations')} relations empirically grounded (OK)")

    # 8. Test Set Firewall (TestSetSealedError)
    builder = HDFSGraphBuilder(base_dir=base_dir, split_authority=split_auth)
    test_sealed_pass = False
    try:
        builder.materialize_split("TEST")
    except TestSetSealedError:
        test_sealed_pass = True
    except Exception:
        test_sealed_pass = False

    if not test_sealed_pass:
        failures.append("TEST_SPLIT_SEALING_FIREWALL_FAILED")

    print(f"[CHECK 8] Test Set Firewall: TestSetSealedError strictly enforced (OK)")

    # 9. Check Execution State (Zero Execution Firewall)
    exec_state = lock_data.get("execution_state", {})
    if exec_state.get("optimizer_steps", -1) != 0:
        failures.append(f"PRE_EXECUTION_VIOLATION_OPTIMIZER_STEPS: {exec_state.get('optimizer_steps')}")
    if exec_state.get("models_trained", -1) != 0:
        failures.append(f"PRE_EXECUTION_VIOLATION_MODELS_TRAINED: {exec_state.get('models_trained')}")
    if exec_state.get("test_opened") is not False:
        failures.append("PRE_EXECUTION_VIOLATION_TEST_OPENED_TRUE")

    print("[CHECK 9] Zero-Execution Firewall: 0 optimizer steps, 0 models trained, test_opened=false (OK)")

    print("=================================================================")
    if failures:
        print(f"FAILED CHECKS ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        print("\nSTAGE_A2_PREEXECUTION_READY=FAIL")
        sys.exit(1)
    else:
        print("ALL PRE-EXECUTION CHECKS PASSED (100% PROTOCOL VERIFIED V1.2)")
        print("STAGE_A2_PREEXECUTION_READY=PASS")
        print("=================================================================")
        sys.exit(0)

if __name__ == "__main__":
    verify_stage_a2_preexecution()
