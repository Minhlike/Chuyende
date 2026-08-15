---
name: m4_argument_graph_construction
id: SKILL-16
category: ARGUMENTATION
version: 1.0.0
inputs:
  - nodes: list[ArgumentNode]
  - edges: list[ArgumentEdge]
  - graph_id: string
  - roadmap_node: Optional[string]
outputs:
  - graph: ArgumentGraph
  - mermaid: string
  - dot: string
---

# SKILL-16: M4 Argument Graph Construction

## 1. Objective
Construct typed DAG argument graphs linking Claims, Evidences, Assumptions, and Counterclaims. Validate absence of circular support loops and export to Mermaid and DOT format.

## 2. Invariants
- `GRAPH-01`: Directed cycles in support/dependency relations must be detected and rejected.
