---
name: data_and_evaluation_leakage_audit
id: SKILL-11
category: AUDIT
version: 1.0.0
inputs:
  - entity_id: string
  - setup_dict: dict[string, bool]
outputs:
  - issues: list[ReasoningIssue]
---

# SKILL-11: Data & Evaluation Leakage Audit

## 1. Objective
Execute 12-point leakage checklist across parser fitting, vocabulary building, normalization statistics, threshold tuning, and temporal lookahead.

## 2. Invariants
- `LEAK-01`: Preprocessing dictionaries and normalization statistics must be strictly fitted on training splits only.
