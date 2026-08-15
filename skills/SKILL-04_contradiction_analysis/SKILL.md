---
name: contradiction_analysis_10pt
id: SKILL-04
category: DIALECTIC
version: 1.0.0
inputs:
  - claim_a: Claim
  - claim_b: Claim
  - notes: Optional[string]
outputs:
  - contradiction_type: ContradictionType
  - checklist: dict[string, bool]
  - diagnosis: string
  - resolution_strategy: string
---

# SKILL-04: 10-Point Contradiction Analysis

## 1. Objective
Analyze conflicting empirical findings across 10 methodological dimensions (dataset, metric, split, threat model, etc.) to determine true vs apparent contradictions.

## 2. Invariants
- `CONTRA-01`: Divergence due to differing datasets or metrics must be classified as `DATASET_DIFFERENCE` or `METRIC_DIFFERENCE`, not falsely labeled a reproducibility collapse.
