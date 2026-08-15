---
name: implicit_explicit_assumption_audit
id: SKILL-05
category: METHODOLOGY
version: 1.0.0
inputs:
  - entity_id: string
  - text: string
outputs:
  - assumptions: list[AssumptionRecord]
---

# SKILL-05: Implicit & Explicit Assumption Audit

## 1. Objective
Extract unstated theoretical, environmental, and statistical assumptions behind claims and models. Evaluate testability and consequence of violation.

## 2. Invariants
- `ASSUME-01`: Implicit domain assumptions (e.g. clock sync, entity resolution, hub over-squashing) must be surfaced explicitly.
- `ASSUME-02`: Every assumption must be classified as `TESTABLE_BY_EXPERIMENT`, `TESTABLE_BY_AUDIT`, `AXIOMATIC`, or `UNTESTABLE`.
