# MACHINE-READABLE RESULT PROVENANCE SCHEMA

**Document Identifier:** `SCH-PROV-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-02`, `RC-09`, `RC-10`, `RC-11`), Scientific Verification Architecture (`docs/SCIENTIFIC-VERIFICATION.md`).  

---

## 1. Result Provenance Firewall Contract

To permanently eradicate hallucinated experimental numbers:
> **Hard Rule:** Every number, metric, table cell, and plot coordinate appearing in Chapter 3 must be generated via code directly from a verified `result.json` artifact located in `experiments/runs/<RUN-ID>/`.

If an experiment has not yet been executed in the physical environment, all associated table entries and metrics must remain strictly formatted as:
`PENDING_EXECUTION`

---

## 2. Canonical JSON Schema for `result.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ExperimentRunResult",
  "type": "object",
  "required": [
    "run_id",
    "experiment_id",
    "rq_id",
    "hyp_id",
    "git_commit",
    "dataset_id",
    "dataset_version_sha256",
    "split_manifest_sha256",
    "extractor_config_sha256",
    "environment_manifest_sha256",
    "random_seed",
    "execution_mode",
    "status",
    "layer1_metrics",
    "layer2_metrics",
    "layer3_metrics",
    "provenance_signature"
  ],
  "properties": {
    "run_id": {"type": "string", "pattern": "^RUN-[0-9]{6}$"},
    "experiment_id": {"type": "string", "pattern": "^EXP-[0-9]{2}$"},
    "rq_id": {"type": "string", "pattern": "^RQ-[0-9]{6}$"},
    "hyp_id": {"type": "string", "pattern": "^HYP-[0-9]{6}$"},
    "git_commit": {"type": "string", "minLength": 7},
    "dataset_id": {"type": "string"},
    "dataset_version_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "split_manifest_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "extractor_config_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "environment_manifest_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "random_seed": {"type": "integer"},
    "execution_mode": {"type": "string", "enum": ["RESEARCH_DETERMINISTIC", "PERFORMANCE"]},
    "status": {"type": "string", "enum": ["COMPLETED", "FAILED", "PENDING_EXECUTION"]},
    "timestamps": {
      "type": "object",
      "properties": {
        "started_at": {"type": "string", "format": "date-time"},
        "finished_at": {"type": "string", "format": "date-time"},
        "duration_seconds": {"type": "number"}
      }
    },
    "layer1_metrics": {
      "type": "object",
      "properties": {
        "representation_variance": {"type": "number"},
        "effective_rank": {"type": "number"},
        "cross_view_alignment_cosine": {"type": "number"},
        "temporal_stability": {"type": "number"}
      }
    },
    "layer2_metrics": {
      "type": "object",
      "properties": {
        "linear_probe_macro_f1": {"type": "number"},
        "linear_probe_pr_auc": {"type": "number"},
        "knn_probe_pr_auc": {"type": "number"}
      }
    },
    "layer3_metrics": {
      "type": "object",
      "properties": {
        "precision": {"type": "number"},
        "recall": {"type": "number"},
        "f1_score": {"type": "number"},
        "pr_auc": {"type": "number"},
        "roc_auc": {"type": "number"},
        "fpr": {"type": "number"},
        "recall_at_01_fpr": {"type": "number"},
        "detection_delay_seconds": {"type": "number"},
        "throughput_events_per_sec": {"type": "number"},
        "p95_latency_ms": {"type": "number"},
        "peak_ram_mb": {"type": "number"},
        "peak_vram_mb": {"type": "number"}
      }
    },
    "provenance_signature": {"type": "string", "pattern": "^[a-f0-9]{64}$"}
  }
}
```
