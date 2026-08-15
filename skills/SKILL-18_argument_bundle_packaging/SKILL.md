---
name: argument_bundle_packaging_and_readiness_gate
id: SKILL-18
category: PACKAGING
version: 1.0.0
inputs:
  - roadmap_node: string
  - objective: string
  - claims: list[dict]
  - evidence: list[dict]
  - assumptions: list[dict]
  - counterarguments: list[dict]
outputs:
  - argument_bundle: ArgumentBundle
  - readiness_state: string
---

# SKILL-18: Argument Bundle Packaging & Readiness Gate

## 1. Objective
Package all explicit reasoning artifacts (Claims, Evidence, Assumptions, Inferences, Counterarguments, Falsification Plans, Verification Requests) into an immutable `ArgumentBundle` and evaluate the readiness gate before chapter composition.

## 2. Invariants
- `GATE-01`: Argument bundles with critical issues or open evidence gaps must NOT transition to `READY`.
