# ADR-0002: Deterministic Typed Stable Identifiers

## Status
Accepted

## Date
2026-08-16

## Context
Research entities (claims, evidence, equations, runs) must be referenced across documents, code comments, thesis prose, and database records. Relying purely on file paths or random UUIDs causes fragile references and hinders human auditability.

## Decision
All canonical entities use prefixed, zero-padded, sequential stable identifiers (e.g., `SRC-000001`, `CLM-000001`, `EVD-000001`, `ARG-000001`, `EQ-000001`, `RUN-000001`, `DEC-000001`).
- Identifiers are assigned deterministically via an atomic sequence registry in SQLite.
- Identifiers are immutable once allocated.
- Internal UUIDs may optionally be recorded for distributed sync, but the canonical audit reference is the stable ID.

## Consequences
### Positive
- Highly readable in academic writing, diffs, and verification reports.
- Unambiguous parsing in regular expressions and citation linkers.
### Negative / Tradeoffs
- Requires centralized sequence coordination during entity creation.
