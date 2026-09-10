# -*- coding: utf-8 -*-
"""
Automated Acceptance Test: Stage A2 Raw Evidence Parity Check
Verifies 100% exact parity between raw snapshot evidence files
(METRICS.json, RUN-STATE.json, CHECKPOINT-INVENTORY.json, TRAIN-LOG.jsonl)
and derived reconciliation artifacts (STAGE-A2-FIVE-SEED-RECONCILIATION.json).
"""

import json
import hashlib
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_DIR = REPO_ROOT / "experiments" / "evidence" / "stage-a2" / "run-snapshots"
RECON_JSON = REPO_ROOT / "experiments" / "evidence" / "stage-a2" / "reconciliation" / "STAGE-A2-FIVE-SEED-RECONCILIATION.json"

@pytest.fixture(scope="module")
def reconciliation_data():
    assert RECON_JSON.exists(), f"Reconciliation file not found at {RECON_JSON}"
    return json.loads(RECON_JSON.read_text(encoding="utf-8"))

def test_reconciliation_metadata_integrity(reconciliation_data):
    meta = reconciliation_data["metadata"]
    assert meta["final_max_epochs"] == 12
    assert meta["optimizer_steps_per_epoch"] == 573
    assert meta["final_max_optimizer_steps"] == 6876
    assert meta["final_warmup_steps"] == 343
    assert meta["canonical_seeds"] == [999]
    assert set(meta["protocol_deviation_seeds"]) == {42, 7}
    assert set(meta["noncanonical_seeds"]) == {1337, 2024}
    assert meta["test_opened"] is False
    assert meta["test_read_count"] == 0
    assert meta["new_optimizer_steps"] == 0
    assert meta["authoritative_plan_file"] == "experiments/plans/STAGE-A2-FINAL-12-EPOCH-AUTHORITY.json"

@pytest.mark.parametrize("seed", [999, 42, 7, 1337, 2024])
def test_seed_raw_evidence_exact_parity(reconciliation_data, seed):
    recon_seeds = {s["seed"]: s for s in reconciliation_data["seeds"]}
    assert seed in recon_seeds, f"Seed {seed} missing in reconciliation JSON"
    r = recon_seeds[seed]

    s_dir = SNAPSHOTS_DIR / f"seed-{seed}"
    assert s_dir.exists(), f"Snapshot directory missing for seed {seed}: {s_dir}"

    state_path = s_dir / "RUN-STATE.json"
    metrics_path = s_dir / "METRICS.json"
    inv_path = s_dir / "CHECKPOINT-INVENTORY.json"
    log_path = s_dir / "TRAIN-LOG.jsonl"

    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    inv = json.loads(inv_path.read_text(encoding="utf-8")) if inv_path.exists() else {}
    
    ckpts = {c["logical_name"]: c for c in inv.get("checkpoints", [])}
    best_c = ckpts.get("best_val_loss.pt", {})
    last_c = ckpts.get("last_checkpoint.pt", {})

    log_lines = []
    if log_path.exists():
        log_lines = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    last_train_line = log_lines[-1] if log_lines else {}

    # Expected exact values from raw evidence
    raw_epochs_completed = metrics.get("epochs_completed", state.get("completed_epoch"))
    raw_optimizer_steps = metrics.get("optimizer_steps_completed", state.get("global_step"))
    raw_best_epoch = metrics.get("best_epoch", state.get("best_epoch"))
    raw_best_val_L_graph = metrics.get("best_val_L_graph", state.get("best_val_loss"))

    raw_final_train_L_graph = metrics.get("final_train_L_graph", last_train_line.get("train_L_graph"))
    raw_final_val_L_graph = metrics.get("final_val_L_graph", last_c.get("val_L_graph", last_train_line.get("val_L_graph")))

    raw_best_checkpoint_sha256 = best_c.get("sha256", state.get("best_checkpoint_sha256"))
    raw_last_checkpoint_sha256 = last_c.get("sha256", state.get("last_checkpoint_sha256"))

    # Assert exact integer / hash parity
    assert r["epochs_completed"] == raw_epochs_completed, f"Seed {seed}: epochs_completed mismatch"
    assert r["optimizer_steps"] == raw_optimizer_steps, f"Seed {seed}: optimizer_steps mismatch"
    assert r["best_epoch"] == raw_best_epoch, f"Seed {seed}: best_epoch mismatch"
    assert r["best_checkpoint_sha256"] == raw_best_checkpoint_sha256, f"Seed {seed}: best_checkpoint_sha256 mismatch"
    assert r["last_checkpoint_sha256"] == raw_last_checkpoint_sha256, f"Seed {seed}: last_checkpoint_sha256 mismatch"

    # Assert exact floating point equality (zero tolerance)
    assert r["best_val_L_graph"] == raw_best_val_L_graph, f"Seed {seed}: best_val_L_graph mismatch ({r['best_val_L_graph']} != {raw_best_val_L_graph})"
    assert r["final_train_L_graph"] == raw_final_train_L_graph, f"Seed {seed}: final_train_L_graph mismatch ({r['final_train_L_graph']} != {raw_final_train_L_graph})"
    assert r["final_val_L_graph"] == raw_final_val_L_graph, f"Seed {seed}: final_val_L_graph mismatch ({r['final_val_L_graph']} != {raw_final_val_L_graph})"

    # Verify snapshot file hashes match actual disk contents
    r_hashes = r.get("evidence_hashes", {})
    for fpath in s_dir.glob("*"):
        actual_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
        recorded_hash = r_hashes.get(fpath.name)
        assert recorded_hash == actual_hash, f"Seed {seed}: File hash mismatch for {fpath.name} ({recorded_hash} != {actual_hash})"

def test_seed999_authorization_provenance_precedes_run(reconciliation_data):
    recon_seeds = {s["seed"]: s for s in reconciliation_data["seeds"]}
    s999 = recon_seeds[999]

    # Required exact commit hash
    expected_commit = "244e81a576bf49d7a58c7f2c69bbb16fc8e304fe"
    assert s999["authorization_commit"] == expected_commit

    # Authorization timestamp vs run launch timestamp
    auth_time = s999["authorization_committed_at"]
    run_start = s999["execution_started_at"]
    assert auth_time == "2026-09-08T16:11:15Z"
    assert run_start.startswith("2026-09-08T16:12:43")
    assert auth_time < run_start, f"Authorization ({auth_time}) must precede run start ({run_start})"

def test_authoritative_plan_file_exists_and_matches():
    p = REPO_ROOT / "experiments" / "plans" / "STAGE-A2-FINAL-12-EPOCH-AUTHORITY.json"
    assert p.exists(), f"Missing authoritative plan {p}"
    data = json.loads(p.read_text(encoding="utf-8"))

    assert data["execution_provider"] == "LOCAL_WINDOWS_GPU"
    hp = data["training_hyperparameters"]
    assert hp["max_epochs"] == 12
    assert hp["steps_per_epoch"] == 573
    assert hp["max_optimizer_steps"] == 6876
    assert hp["warmup_steps"] == 343
    assert hp["min_lr"] == 1e-05

    env = data["environment_lock"]
    assert env["execution_provider"] == "LOCAL_WINDOWS_GPU"
    assert env["python_version"] == "3.12.8"
    assert env["pytorch_version"] == "2.6.0+cu124"
    assert env["cuda_runtime"] == "12.4"
    assert env["environment_lock_sha256"] == "81d3ca4865a95c75cc2345695091265f948ad58e705865a3f8f780a9bf09f362"

    dm = data["dataset_membership"]
    assert dm["dataset"] == "HDFS"
    assert dm["raw_dataset_sha256"] == "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169"
    assert dm["train"]["membership_sha256"] == "65b76694b0a3cf5c6d684a26899b1e5dca634cfd0985560149feddc12ca8ccfc"
    assert dm["validation"]["membership_sha256"] == "14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a"
    assert dm["test_firewall"]["test_opened"] is False
    assert dm["test_firewall"]["test_reads"] == 0
