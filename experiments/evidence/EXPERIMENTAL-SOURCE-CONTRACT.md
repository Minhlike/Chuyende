# CHAPTER 3 — EXPERIMENTAL SOURCE & EMPIRICAL PROVENANCE CONTRACT

**Document Identifier:** `CONTRACT-EXPERIMENTAL-SOURCE-V1.0`  
**Effective Date:** 2026-08-23  
**Status:** **MANDATORY & ENFORCED FOR ALL EXPERIMENTAL CLAIMS**  
**Governing Standard:** Chapter 3 Empirical Integrity Protocol  

---

## 1. Core Principle: Zero Unreferenced Empirical Claims

Under this contract, **NO numerical result, metric value, event count, loss curve, parameter norm, runtime, or training statistic may appear in any agent response, report, artifact, or publication without a verified machine-readable experimental source manifest**.

Every empirical claim must be traceable to a specific:
1. **Audit/Run Identifier** (`run_id` or `audit_id`)
2. **Exact Git Commit SHA** (`git_commit_sha`)
3. **Artifact File Path & SHA-256 Checksum** (`metrics_artifact_sha256`)
4. **Underlying Source Data Checksum** (`raw_dataset_sha256`, `selected_train_membership_sha256`)
5. **Exact Terminal Command Executed** (`command_executed`)
6. **Execution Environment Metadata** (`environment_sha256` or `ENVIRONMENT.json`)
7. **Evidence Classification** (`REAL_EMPIRICAL`, `PREEXECUTION_AUDIT`, `NON_EMPIRICAL_TEST_FIXTURE`)

---

## 2. Experimental Source Manifest Structure

Every training run (e.g. `experiments/runs/stage-a2/HDFS/seed-<SEED>/`) and pre-execution audit must generate an `EXPERIMENTAL-SOURCE.json` conforming to `experiments/evidence/EXPERIMENTAL-SOURCE-SCHEMA.json`:

```json
{
  "claim_id": "CLAIM-STAGE-A2-HDFS-SEED42-BEST-VAL-LOSS",
  "stage": "STAGE_A2",
  "run_id": "RUN-STAGE-A2-HDFS-SEED42",
  "dataset": "HDFS",
  "split_id": "SPL-HDFS-001",
  "seed": 42,
  "git_commit_sha": "...",
  "git_branch": "train/ch3-stage-a2-preregistration",
  "git_dirty": false,
  "protocol_version": "1.3",
  "protocol_sha256": "...",
  "graph_contract_sha256": "...",
  "raw_to_graph_mapping_sha256": "...",
  "raw_dataset_sha256": "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169",
  "selected_train_membership_sha256": "...",
  "selected_val_membership_sha256": "...",
  "command_executed": "python -m research_agent.experiments.runners.stage_a2_trainer ...",
  "working_directory": "D:/Research",
  "timestamp_start": "2026-08-23T22:00:00Z",
  "timestamp_end": "2026-08-23T22:45:00Z",
  "environment": {
    "python_version": "3.12.3",
    "pytorch_version": "2.6.0+cu124",
    "cuda_version": "12.4",
    "device_name": "NVIDIA GeForce RTX 3050 Ti Laptop GPU",
    "platform": "Linux-5.15.167.4-microsoft-standard-WSL2-x86_64"
  },
  "metrics_artifact_path": "experiments/runs/stage-a2/HDFS/seed-42/METRICS.json",
  "metrics_artifact_sha256": "...",
  "checkpoint_path": "experiments/runs/stage-a2/HDFS/seed-42/best_val_loss.pt",
  "checkpoint_sha256": "...",
  "test_firewall_state": {
    "test_opened": false,
    "test_feature_reads": 0,
    "test_label_reads": 0,
    "test_metrics": 0
  },
  "evidence_class": "REAL_EMPIRICAL"
}
```

---

## 3. Evidence Classification Taxonomy

1. **`REAL_EMPIRICAL`:**
   - Generated from actual execution runs on authorized empirical datasets (e.g. HDFS 35,000 sessions).
   - Serves as confirmatory evidence for Chapter 3 hypotheses (H1–H6).
2. **`PREEXECUTION_AUDIT`:**
   - Generated from static streaming audits of dataset populations or schema verification tools prior to model training.
   - Proves schema coverage, graph conservation, and split boundary validity.
3. **`NON_EMPIRICAL_TEST_FIXTURE`:**
   - Generated from synthetic, mock, or micro-fixtures strictly for unit/integration/deterministic regression testing.
   - **Must NEVER be cited as empirical performance evidence.**
