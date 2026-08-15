# ADR-0005: Workspace Containment (PathGuard) and Untrusted Data Isolation

## Status
Accepted

## Date
2026-08-16

## Context
A research system ingests third-party PDFs, code samples, logs, and external files. There are two major security and integrity risks:
1. **Path Traversal & Workspace Escape:** Accidental or malicious write operations attempting to modify files outside `D:\Research`.
2. **Indirect Prompt Injection:** Adversarial text embedded inside academic papers or log samples attempting to execute arbitrary code or hijack LLM reasoning.

## Decision
1. **PathGuard Architecture:** All filesystem I/O operations in `research_agent` must be routed through `PathGuard`, which resolves real canonical paths, ensures root containment within `D:\Research`, and blocks unauthorized write attempts.
2. **Document-as-Data Principle:** All ingested text, PDF content, and log payloads are strictly wrapped in untrusted data containers. They are never directly concatenated into system-level execution contexts without explicit role isolation.

## Consequences
### Positive
- Strict containment ensures safety of the host operating system.
- Immune to directory traversal attacks via malicious dataset filenames.
### Negative / Tradeoffs
- Requires passing all path operations through centralized guard utilities.
