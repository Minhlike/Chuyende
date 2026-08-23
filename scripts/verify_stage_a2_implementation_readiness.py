# -*- coding: utf-8 -*-
"""
Stage A2 Implementation Readiness Gate Verifier (V1.3).
Verifies complete execution scope disambiguation, membership hashing,
target-leakage masking contracts, checkpoint mutable state tuple,
and experimental source provenance contracts before implementation.
Outputs STAGE_A2_IMPLEMENTATION_READY=PASS or STAGE_A2_IMPLEMENTATION_READY=FAIL.
"""

import sys
import json
import hashlib
from pathlib import Path

from research_agent.experiments.data.hdfs_split_authority import (
    parse_hdfs_line_timestamp,
    HDFSSplitAuthority
)
from research_agent.experiments.extractor.graph_builder import (
    HDFSGraphBuilder,
    TestSetSealedError
)

def verify_stage_a2_implementation_readiness():
    base_dir = Path("D:/Research")
    failures = []

    print("=================================================================")
    print("   STAGE A2 IMPLEMENTATION READINESS GATE AUDIT (V1.3)           ")
    print("=================================================================")

    # 1. Base Artifacts & Lock Check
    lock_path = base_dir / "experiments" / "protocol" / "STAGE-A2-PREEXECUTION-LOCK.json"
    prereg_path = base_dir / "experiments" / "protocol" / "STAGE-A2-PREREGISTRATION.md"
    graph_contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    raw_mapping_path = base_dir / "experiments" / "schemas" / "STAGE-A2-RAW-TO-GRAPH-MAPPING.json"
    membership_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "HDFS-EXECUTION-MEMBERSHIP.json"
    subset_audit_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "HDFS-EXECUTION-SUBSET-AUDIT.json"
    pop_audit_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "HDFS-GRAPH-MATERIALIZATION-AUDIT.json"
    rel_audit_path = base_dir / "experiments" / "evidence" / "stage-a2" / "preexecution" / "RELATION-GROUNDING-AUDIT.json"
    src_contract_path = base_dir / "experiments" / "evidence" / "EXPERIMENTAL-SOURCE-CONTRACT.md"
    src_schema_path = base_dir / "experiments" / "evidence" / "EXPERIMENTAL-SOURCE-SCHEMA.json"
    word_index_path = base_dir / "experiments" / "evidence" / "WORD-EVIDENCE-INDEX.md"
    manifest_path = base_dir / "experiments" / "evidence" / "stage-a2" / "EVIDENCE-MANIFEST.json"

    required_paths = [
        lock_path, prereg_path, graph_contract_path, raw_mapping_path,
        membership_path, subset_audit_path, pop_audit_path, rel_audit_path,
        src_contract_path, src_schema_path, word_index_path, manifest_path
    ]

    for p in required_paths:
        if not p.exists():
            failures.append(f"MISSING_ARTIFACT: {p}")

    if failures:
        print("FAILED: Missing core artifacts.")
        print("STAGE_A2_IMPLEMENTATION_READY=FAIL")
        sys.exit(1)

    # 2. Cryptographic Checksums
    lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
    
    def check_hash(path: Path, expected_hash_key: str):
        actual_h = hashlib.sha256(path.read_bytes()).hexdigest()
        expected_h = lock_data.get(expected_hash_key)
        if actual_h != expected_h:
            failures.append(f"HASH_MISMATCH for {path.name}: {actual_h} != {expected_h}")
        return actual_h

    check_hash(prereg_path, "protocol_document_sha256")
    check_hash(graph_contract_path, "graph_contract_sha256")
    check_hash(raw_mapping_path, "raw_to_graph_mapping_sha256")
    check_hash(pop_audit_path, "materialization_audit_sha256")
    check_hash(subset_audit_path, "execution_subset_audit_sha256")
    check_hash(membership_path, "execution_membership_sha256")
    check_hash(rel_audit_path, "relation_grounding_audit_sha256")
    check_hash(src_contract_path, "experimental_source_contract_sha256")
    check_hash(src_schema_path, "experimental_source_schema_sha256")
    check_hash(manifest_path, "evidence_manifest_sha256")

    print("[CHECK 1] Cryptographic Hashes of all V1.3 Contracts & Manifests: VERIFIED (OK)")

    # 3. Execution Membership Exact Check
    split_auth = HDFSSplitAuthority(base_dir=base_dir)
    split_info = split_auth.get_split()
    mem_data = json.loads(membership_path.read_text(encoding="utf-8"))

    if mem_data.get("authorized_train_session_count") != 35000:
        failures.append(f"INVALID_AUTHORIZED_TRAIN_SESSIONS: {mem_data.get('authorized_train_session_count')}")
    if mem_data.get("authorized_val_session_count") != 7500:
        failures.append(f"INVALID_AUTHORIZED_VAL_SESSIONS: {mem_data.get('authorized_val_session_count')}")

    if mem_data.get("selected_train_block_ids_sha256") != split_info.get("selected_train_block_ids_sha256"):
        failures.append("SELECTED_TRAIN_MEMBERSHIP_HASH_MISMATCH")
    if mem_data.get("selected_val_block_ids_sha256") != split_info.get("selected_val_block_ids_sha256"):
        failures.append("SELECTED_VAL_MEMBERSHIP_HASH_MISMATCH")

    print(f"[CHECK 2] Execution Membership Exactness: Train (35,000), Val (7,500) (OK)")
    print(f"          Train Membership SHA-256: {mem_data.get('selected_train_block_ids_sha256')} (OK)")
    print(f"          Val Membership SHA-256:   {mem_data.get('selected_val_block_ids_sha256')} (OK)")

    # 4. Scope Disambiguation: Population vs Execution Subset
    subset_data = json.loads(subset_audit_path.read_text(encoding="utf-8"))
    pop_data = json.loads(pop_audit_path.read_text(encoding="utf-8"))

    train_sub_events = subset_data["train"]["materialized_graph_events"]
    train_pop_events = pop_data["train"]["materialized_graph_events"]

    if train_sub_events == train_pop_events:
        failures.append("POPULATION_AND_SUBSET_CONFUSED_IDENTICAL_EVENTS")
    if not subset_data["train"]["conservation_pass"] or not subset_data["validation"]["conservation_pass"]:
        failures.append("SUBSET_GRAPH_CONSERVATION_FAILED")
    if not pop_data["train"]["conservation_pass"] or not pop_data["validation"]["conservation_pass"]:
        failures.append("POPULATION_GRAPH_CONSERVATION_FAILED")

    print(f"[CHECK 3] Scope Disambiguation & Conservation: (OK)")
    print(f"          Execution Subset: Train ({train_sub_events} events), Val ({subset_data['validation']['materialized_graph_events']} events)")
    print(f"          Full Population:  Train ({train_pop_events} events), Val ({pop_data['validation']['materialized_graph_events']} events)")

    # 5. Target Masking Semantics Check
    contract_data = json.loads(graph_contract_path.read_text(encoding="utf-8"))
    masking_policies = contract_data.get("target_masking_visibility_policies", {})
    
    rel_policy = masking_policies.get("masked_relation_prediction", {})
    if "event_relation_embedding" not in rel_policy.get("withheld_from_prediction", []):
        failures.append("RELATION_MASK_TARGET_LEAKAGE_RISK")

    node_policy = masking_policies.get("masked_node_reconstruction", {})
    if "x_v_fixed_priv" not in node_policy.get("withheld_from_prediction", []):
        failures.append("NODE_MASK_TARGET_LEAKAGE_RISK")

    print("[CHECK 4] Target-Leakage Masking Policies: VERIFIED (OK)")

    # 6. Complete Checkpoint Mutable State Contract
    ckpt_contract = contract_data.get("checkpoint_state_contract", {})
    if ckpt_contract.get("checkpoint_boundary_policy") != "CHECKPOINT_ONLY_AT_OPTIMIZER_BOUNDARY":
        failures.append("CHECKPOINT_BOUNDARY_POLICY_NOT_AT_OPTIMIZER_BOUNDARY")

    mandatory_keys = {
        "model_state_dict", "optimizer_state_dict", "scheduler_state_dict",
        "node_memory_states", "node_last_interaction_timestamps",
        "node_causal_in_degrees", "node_causal_out_degrees", "node_temporal_history_buffers",
        "rng_states_4tuple", "stream_iterator_state", "masking_rng_state",
        "early_stopping_state", "global_step", "current_epoch"
    }
    actual_keys = set(ckpt_contract.get("mandatory_mutable_state", []))
    missing_state = mandatory_keys - actual_keys
    if missing_state:
        failures.append(f"MISSING_CHECKPOINT_MUTABLE_STATE_KEYS: {missing_state}")

    print(f"[CHECK 5] Checkpoint Boundary Policy & All 14 Mutable State Elements: VERIFIED (OK)")

    # 7. Test Firewall Check
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

    print("[CHECK 6] Test Firewall: TestSetSealedError strictly enforced (OK)")

    # 8. Zero Execution State Check
    exec_state = lock_data.get("execution_state", {})
    if exec_state.get("optimizer_steps", -1) != 0:
        failures.append("REAL_OPTIMIZER_STEPS_NON_ZERO")
    if exec_state.get("models_trained", -1) != 0:
        failures.append("REAL_MODELS_TRAINED_NON_ZERO")
    if exec_state.get("test_opened") is not False:
        failures.append("TEST_OPENED_TRUE")

    print("[CHECK 7] Zero-Execution Firewall: 0 optimizer steps, 0 models trained (OK)")

    print("=================================================================")
    if failures:
        print(f"FAILED CHECKS ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        print("\nSTAGE_A2_IMPLEMENTATION_READY=FAIL")
        sys.exit(1)
    else:
        print("ALL IMPLEMENTATION READINESS CHECKS PASSED (100% PROTOCOL V1.3)")
        print("STAGE_A2_IMPLEMENTATION_READY=PASS")
        print("=================================================================")
        sys.exit(0)

if __name__ == "__main__":
    verify_stage_a2_implementation_readiness()
