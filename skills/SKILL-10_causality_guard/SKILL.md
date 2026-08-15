---
name: causality_and_graph_inflation_guard
id: SKILL-10
category: AUDIT
version: 1.0.0
inputs:
  - entity_id: string
  - text: string
  - is_interventional: bool
outputs:
  - issues: list[ReasoningIssue]
---

# SKILL-10: Causality & Graph Inflation Guard

## 1. Objective
Detect unwarranted causal assertions and enforce the fundamental architectural principle: `DEPENDS_ON != CAUSES` in host audit provenance graphs.

## 2. Invariants
- `CAUS-01`: Observational and correlational findings must not use deterministic causal verbs ("causes", "leads to").
- `CAUS-02`: Provenance graphs represent observable dataflow dependencies, not interventional causal mechanisms.
