---
name: contribution_novelty_differentiation
id: SKILL-15
category: NOVELTY
version: 1.0.0
inputs:
  - candidate_id: string
outputs:
  - novelty_state: NoveltyReasoningState
  - differentiation_report: dict[string, any]
  - issues: list[ReasoningIssue]
---

# SKILL-15: Contribution Novelty Differentiation

## 1. Objective
Differentiate candidate contributions (CAND-01..CAND-15) from closest peer-reviewed prior art across 6 technical dimensions, strictly enforcing `OURS != NOVEL`.

## 2. Invariants
- `NOV-01`: Novelty claims without linked peer-reviewed prior art baselines must be flagged as `NOVELTY_OVERCLAIM`.
