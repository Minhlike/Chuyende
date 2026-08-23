# CHAPTER 3 — EXPERIMENTAL SOURCE & EMPIRICAL PROVENANCE CONTRACT (V1.1)

**Document Identifier:** `CONTRACT-EXPERIMENTAL-SOURCE-V1.1`  
**Effective Date:** 2026-08-23  
**Status:** **MANDATORY & ENFORCED FOR ALL EXPERIMENTAL & QUALIFICATION CLAIMS**  
**Governing Standard:** Chapter 3 Empirical Integrity Protocol  

---

## 1. Core Principle: Zero Unreferenced Claims

Under this contract, **NO numerical result, metric value, event count, loss curve, parameter norm, runtime, or training statistic may appear in any agent response, report, artifact, or publication without a verified machine-readable experimental source manifest**.

Every claim must be traceable to a specific:
1. **Audit/Run Identifier** (`run_id` or `audit_id`)
2. **Exact Execution Code Commit SHA** (`execution_code_commit_sha`)
3. **Execution Code Branch & Cleanliness** (`execution_code_branch`, `execution_code_dirty`)
4. **Artifact File Path & SHA-256 Checksum** (`metrics_artifact_sha256`)
5. **Underlying Source Data Checksum** (`raw_dataset_sha256` or `selected_train_membership_sha256`)
6. **Exact Terminal Command Executed** (`command_executed`)
7. **Execution Environment Metadata** (`environment` object)
8. **Evidence Classification** (`REAL_EMPIRICAL`, `PREEXECUTION_AUDIT`, `NON_EMPIRICAL_TEST_FIXTURE`)
9. **Claim Scope** (`PRETRAINING_EMPIRICAL`, `DOWNSTREAM_EXPLORATORY`, `CONFIRMATORY_EVALUATION`, `PREEXECUTION_AUDIT`, `NON_EMPIRICAL_TEST_FIXTURE`)

---

## 2. Experimental Source Manifest Structure

Every training run (e.g. `experiments/runs/stage-a2/HDFS/seed-<SEED>/`) and qualification audit must generate an `EXPERIMENTAL-SOURCE.json` conforming to `experiments/evidence/EXPERIMENTAL-SOURCE-SCHEMA.json`:

```json
{
  "claim_id": "CLAIM-STAGE-A2-HDFS-SEED42-BEST-VAL-LOSS",
  "stage": "STAGE_A2",
  "run_id": "RUN-STAGE-A2-HDFS-SEED42",
  "dataset": "HDFS",
  "split_id": "SPL-HDFS-001",
  "seed": 42,
  "execution_code_commit_sha": "a0dc88360d89e5d400fcad84c894f2bfcfd5038d",
  "execution_code_branch": "train/ch3-stage-a2-implementation",
  "execution_code_dirty": false,
  "protocol_version": "1.3",
  "protocol_sha256": "87a783618c90c85129991e7694632172b26a43ce64f452d0f266f7db70597dfa",
  "graph_contract_sha256": "05f5ab38c4c02e14292b510ac518dd98171732551d032ec0ed09fc96848f5837",
  "raw_to_graph_mapping_sha256": "8c2ecb1504af7ed3e3f74144a0197dec15b4566e505ca5d9ae7e5146486e2208",
  "raw_dataset_sha256": "6ca6c5bc2671c66afecee9369a2fdac606bf33997a2494ac66aa411fe3e95169",
  "selected_train_membership_sha256": "65b76694b0a3cf5c6d684a26899b1e5dca634cfd0985560149feddc12ca8ccfc",
  "selected_val_membership_sha256": "14cf689f9682a354e104463b9f02806629a683dfdf36d72d88daf5b407b0609a",
  "command_executed": "python -m research_agent.experiments.runners.stage_a2_trainer ...",
  "working_directory": "D:/Research",
  "timestamp_start": "2026-08-23T22:00:00Z",
  "timestamp_end": "2026-08-23T22:45:00Z",
  "environment": {
    "python_version": "3.12.8",
    "pytorch_version": "2.13.0",
    "cuda_version": null,
    "device_name": "cpu",
    "platform": "Windows-10-10.0.26100-SP0"
  },
  "stdout_log_path": "experiments/evidence/stage-a2/implementation/deterministic_resume.log",
  "stdout_log_sha256": "...",
  "metrics_artifact_path": "experiments/evidence/stage-a2/implementation/IMPLEMENTATION-QUALIFICATION.json",
  "metrics_artifact_sha256": "...",
  "checkpoint_path": "experiments/runs/stage-a2/fixture/checkpoint.pt",
  "checkpoint_sha256": "...",
  "test_firewall_state": {
    "test_opened": false,
    "test_feature_reads": 0,
    "test_label_reads": 0,
    "test_metrics": 0
  },
  "evidence_class": "NON_EMPIRICAL_TEST_FIXTURE",
  "claim_scope": "NON_EMPIRICAL_TEST_FIXTURE"
}
```

---

## 3. Disambiguation: Execution Code Commit vs Evidence Storage Commit

To prevent self-referential paradoxes:
- **`execution_code_commit_sha`:** The immutable Git commit SHA of the codebase from which the command was executed. Must be verified clean (`execution_code_dirty = false`) and pushed prior to execution.
- **Evidence Storage Commit (`evidence_storage_commit_sha`):** The subsequent Git commit containing the generated evidence manifests and logs. It is cited in external acceptance reports and never placed inside the manifest itself.

---

## 4. Evidence Classification & Claim Scope Taxonomy

1. **`evidence_class`:**
   - `REAL_EMPIRICAL`: Generated from real model training/evaluation runs on authorized empirical datasets (e.g. HDFS 35,000 sessions).
   - `PREEXECUTION_AUDIT`: Generated from static dataset streaming audits or schema verification before training.
   - `NON_EMPIRICAL_TEST_FIXTURE`: Generated from synthetic or micro-fixtures strictly for qualification and regression tests.
2. **`claim_scope`:**
   - `PRETRAINING_EMPIRICAL`: Self-supervised pretraining metrics (representation quality, loss curves). Does not evaluate downstream hypotheses.
   - `DOWNSTREAM_EXPLORATORY`: Exploratory probes and diagnostic ablations.
   - `CONFIRMATORY_EVALUATION`: Confirmatory test metric evaluations for primary hypotheses H1–H6 under formal unsealing gates.
   - `PREEXECUTION_AUDIT`: Pre-execution data, boundary, and split consistency.
   - `NON_EMPIRICAL_TEST_FIXTURE`: Unit, integration, or continuous-vs-resumed deterministic qualifications.
