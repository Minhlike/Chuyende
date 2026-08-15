# ADR-0003: Multi-Valued Epistemic Status and Contradiction Preservation

## Status
Accepted

## Date
2026-08-16

## Context
Scientific progress is non-monotonic: new experimental data may contradict prior literature or falsify internal hypotheses. Standard AI systems often collapse truth values into binary True/False or discard conflicting findings to create smooth textual narratives.

## Decision
1. Claims must maintain a discrete 6-state epistemic status: `UNVERIFIED`, `SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTESTED`, `FALSIFIED`, `SUPERSEDED`.
2. Contradictory evidence does not trigger deletion or overwriting of previous records; instead, it generates an explicit `ContradictionRecord` linking conflicting claims, and transitions claim status to `CONTESTED`.
3. Negative and falsifying results are preserved permanently.

## Consequences
### Positive
- Fully honors scientific method and research ethics (RC-07, RC-13, RC-14).
- Prevents premature convergence on flawed feature representations.
### Negative / Tradeoffs
- Downstream synthesis engines must handle multi-valued epistemic branches and explicitly synthesize contradictions.
