---
name: experimental_validity_4factor_audit
id: SKILL-13
category: AUDIT
version: 1.0.0
inputs:
  - entity_id: string
  - setup_info: dict[string, any]
outputs:
  - issues: list[ReasoningIssue]
---

# SKILL-13: Experimental Validity 4-Factor Audit

## 1. Objective
Evaluate experiments against the four classical validity dimensions: Construct, Internal, External, and Statistical validity.

## 2. Invariants
- `VAL-01`: Anomaly detection on supercomputer logs (HDFS/BGL) cannot be framed as attack detection without construct validity justification.
