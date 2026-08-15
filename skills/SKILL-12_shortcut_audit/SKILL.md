---
name: dataset_shortcut_learning_audit
id: SKILL-12
category: AUDIT
version: 1.0.0
inputs:
  - entity_id: string
  - feature_description: string
outputs:
  - issues: list[ReasoningIssue]
---

# SKILL-12: Dataset Shortcut Learning Audit

## 1. Objective
Audit feature representations for superficial dataset shortcuts such as unmasked hostnames, static usernames, campaign scenario IDs, and rare formatting tokens.

## 2. Invariants
- `SHORT-01`: Representation contracts must mandate masking or exclusion of trivial environmental identifiers (CTRL-01).
