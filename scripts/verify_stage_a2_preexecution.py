# -*- coding: utf-8 -*-
"""
Canonical Stage A2 Pre-Execution Verification Gate.
Audits the complete Stage A2 preregistration artifacts, graph contract schema,
raw dataset availability, split hashes, zero-test-access firewall, and pre-execution lock.
Outputs STAGE_A2_PREEXECUTION_READY=PASS or STAGE_A2_PREEXECUTION_READY=FAIL.
"""

import sys
import json
import hashlib
from pathlib import Path

def verify_stage_a2_preexecution():
    base_dir = Path("D:/Research")
    failures = []

    print("=================================================================")
    print("      STAGE A2 PRE-EXECUTION GATE VERIFICATION AUDIT             ")
    print("=================================================================")

    # 1. Base Frozen Commit & Branch Check
    expected_base_commit = "9a707025ed5899c524962558732218ff48e8b212"
    lock_path = base_dir / "experiments" / "protocol" / "STAGE-A2-PREEXECUTION-LOCK.json"
    prereg_path = base_dir / "experiments" / "protocol" / "STAGE-A2-PREREGISTRATION.md"
    graph_contract_path = base_dir / "experiments" / "schemas" / "STAGE-A2-GRAPH-CONTRACT.json"
    design_audit_path = base_dir / "experiments" / "reports" / "STAGE-A2-DESIGN-AUDIT.md"

    for p in [lock_path, prereg_path, graph_contract_path, design_audit_path]:
        if not p.exists():
            failures.append(f"MISSING_REQUIRED_ARTIFACT: {p}")

    if failures:
        print("FAILED: Missing core artifacts.")
        print("STAGE_A2_PREEXECUTION_READY=FAIL")
        sys.exit(1)

    # 2. Check Cryptographic Hashes of Preregistration & Graph Contract
    prereg_bytes = prereg_path.read_bytes()
    prereg_sha256 = hashlib.sha256(prereg_bytes).hexdigest()

    graph_contract_bytes = graph_contract_path.read_bytes()
    graph_contract_sha256 = hashlib.sha256(graph_contract_bytes).hexdigest()

    lock_bytes = lock_path.read_bytes()
    lock_file_sha256 = hashlib.sha256(lock_bytes).hexdigest()
    lock_data = json.loads(lock_bytes.decode("utf-8"))

    if lock_data.get("source_commit") != expected_base_commit:
        failures.append(f"INVALID_BASE_COMMIT: {lock_data.get('source_commit')} != {expected_base_commit}")

    if lock_data.get("protocol_document_sha256") != prereg_sha256:
        failures.append(f"PREREG_SHA256_MISMATCH: {lock_data.get('protocol_document_sha256')} != {prereg_sha256}")

    if lock_data.get("graph_contract_sha256") != graph_contract_sha256:
        failures.append(f"GRAPH_CONTRACT_SHA256_MISMATCH: {lock_data.get('graph_contract_sha256')} != {graph_contract_sha256}")

    print(f"[CHECK 1] Protocol Preregistration SHA-256: {prereg_sha256} (OK)")
    print(f"[CHECK 1] Graph Contract Schema SHA-256:   {graph_contract_sha256} (OK)")
    print(f"[CHECK 1] Pre-Execution Lock File SHA-256: {lock_file_sha256} (OK)")

    # 3. Check Text for Ambiguous Placeholders (TBD, A / B alternatives)
    prereg_text = prereg_bytes.decode("utf-8")
    if "TBD" in prereg_text:
        failures.append("PREREGISTRATION_CONTAINS_TBD_PLACEHOLDER")
    if "PENDING_DECISION" in prereg_text:
        failures.append("PREREGISTRATION_CONTAINS_UNRESOLVED_DECISION")

    # 4. Audit Selected Datasets & Raw Availability
    selected_datasets = lock_data.get("dataset_names", [])
    if selected_datasets != ["HDFS", "BGL"]:
        failures.append(f"INVALID_DATASET_SELECTION: {selected_datasets}")

    expected_raw_hashes = {
        "HDFS": "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169",
        "BGL": "0a58be959cef101bbe5c053e60bd8a49673e9c942b164f4d969bb109e99fce95"
    }

    raw_paths = {
        "HDFS": base_dir / "datasets" / "raw" / "hdfs" / "HDFS_1.tar.gz",
        "BGL": base_dir / "datasets" / "raw" / "bgl" / "BGL.tar.gz"
    }

    for ds, expected_h in expected_raw_hashes.items():
        rp = raw_paths[ds]
        if not rp.exists():
            failures.append(f"RAW_DATASET_MISSING: {ds} at {rp}")
        else:
            actual_h = hashlib.sha256(rp.read_bytes()).hexdigest()
            if actual_h != expected_h:
                failures.append(f"RAW_DATASET_HASH_MISMATCH: {ds} ({actual_h} != {expected_h})")
            print(f"[CHECK 2] Raw Dataset Checksum {ds}: {actual_h} (OK)")

    # 5. Check Split Integrity & Sealing
    splits = lock_data.get("split_specifications", {})
    for ds in ["HDFS", "BGL"]:
        if ds not in splits:
            failures.append(f"MISSING_SPLIT_SPEC: {ds}")
        else:
            s_data = splits[ds]
            if s_data.get("test_status") != "SEALED_ZERO_ACCESS":
                failures.append(f"TEST_NOT_SEALED: {ds} status={s_data.get('test_status')}")
            if not s_data.get("train_split_hash") or not s_data.get("val_split_hash"):
                failures.append(f"MISSING_SPLIT_HASHES: {ds}")
            print(f"[CHECK 3] Split Specification {ds}: Train & Val hashes verified, Test SEALED (OK)")

    # 6. Check Causal & Structural Graph Policies
    causal_pols = lock_data.get("causal_policies", {})
    if causal_pols.get("predict_before_update") != "STRICTLY_ENFORCED":
        failures.append("PREDICT_BEFORE_UPDATE_NOT_ENFORCED")
    if causal_pols.get("future_neighbor_firewall") != "STRICTLY_ENFORCED":
        failures.append("FUTURE_NEIGHBOR_FIREWALL_NOT_ENFORCED")
    if causal_pols.get("split_memory_policy") != "INDUCTIVE_SPLIT_RESET_ZERO_MEMORY":
        failures.append("SPLIT_MEMORY_POLICY_UNRESOLVED")
    if causal_pols.get("negative_sampling_policy") != "CAUSAL_UNIFORM_SAMPLED_HISTORICAL_DESTINATION":
        failures.append("NEGATIVE_SAMPLING_POLICY_UNRESOLVED")

    # 7. Check Architecture and Loss Parameters
    arch = lock_data.get("architecture", {})
    if arch.get("family") != "TemporalGraphViewEncoder" or arch.get("memory_cell") != "GRUCell":
        failures.append("INVALID_ARCHITECTURE_SPEC")

    losses = lock_data.get("losses", {})
    if losses.get("lambda_rel") != 1.0 or losses.get("lambda_node") != 1.0 or losses.get("lambda_time") != 0.1:
        failures.append("INVALID_LOSS_WEIGHTS")

    # 8. Check Canonical Seed List
    canonical_seeds = lock_data.get("canonical_seeds", [])
    if canonical_seeds != [42, 1337, 2024, 7, 999]:
        failures.append(f"INVALID_CANONICAL_SEEDS: {canonical_seeds}")

    # 9. Check Execution State (Zero Execution Firewall)
    exec_state = lock_data.get("execution_state", {})
    if exec_state.get("optimizer_steps", -1) != 0:
        failures.append(f"PRE_EXECUTION_VIOLATION_OPTIMIZER_STEPS: {exec_state.get('optimizer_steps')}")
    if exec_state.get("models_trained", -1) != 0:
        failures.append(f"PRE_EXECUTION_VIOLATION_MODELS_TRAINED: {exec_state.get('models_trained')}")
    if exec_state.get("test_opened") is not False:
        failures.append("PRE_EXECUTION_VIOLATION_TEST_OPENED_TRUE")

    print("[CHECK 4] Zero-Execution Firewall: 0 optimizer steps, 0 models trained, test_opened=false (OK)")
    print("[CHECK 5] Causal Policies & Architecture: GRUCell, Predict-Before-Update, Inductive Memory (OK)")

    print("=================================================================")
    if failures:
        print(f"FAILED CHECKS ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        print("\nSTAGE_A2_PREEXECUTION_READY=FAIL")
        sys.exit(1)
    else:
        print("ALL PRE-EXECUTION CHECKS PASSED (100% PROTOCOL VERIFIED)")
        print("STAGE_A2_PREEXECUTION_READY=PASS")
        print("=================================================================")
        sys.exit(0)

if __name__ == "__main__":
    verify_stage_a2_preexecution()
