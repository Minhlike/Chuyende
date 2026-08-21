# ANTI-LEAKAGE CAUSAL SPLIT PROTOCOL & SPLIT MANIFEST STATE MACHINE

**Document Identifier:** `PROT-SPLIT-20260821-V1.0`  
**Protocol Version:** 1.0.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-10`, `RC-16`), Roadmap Boundary (`BOUNDARY-09`).  

---

## 1. Split Manifest Lifecycle State Machine

To prevent fabricated partition counts and speculative split hashes prior to physical data acquisition, every split manifest follows a strict three-state lifecycle:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SPLIT MANIFEST LIFECYCLE STATE MACHINE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  STATE 1: PLANNED (Current State — Pre-Acquisition)                         │
│  - Formal partitioning ratios defined (Train 70% < Val 15% < Test 15%)      │
│  - Holdout dimensions and causal boundary rules locked                      │
│  - Raw file hashes and event counts marked strictly PENDING_ACQUISITION     │
├──────────────────────────────────────┬──────────────────────────────────────┤
│                                      │ (Trigger: Raw Data Acquired & SHA256)│
│                                      ▼                                      │
│  STATE 2: ACQUIRED (Data Staging & Integrity Audit)                         │
│  - Raw tarball/files downloaded and verified against official sources       │
│  - SHA-256 hash computed for every raw artifact                             │
│  - Parser version, valid/invalid record counts, and temporal span recorded  │
├──────────────────────────────────────┬──────────────────────────────────────┤
│                                      │ (Trigger: Preprocessors Fit on Train)│
│                                      ▼                                      │
│  STATE 3: SEALED (Locked For Evaluation)                                    │
│  - Exact index/timestamp partition boundaries generated deterministically   │
│  - Train/Val/Test SHA-256 manifests calculated and frozen                   │
│  - Test set sealed against any access until final frozen evaluation         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pre-Acquisition Verification Checklist (Required for Transition to ACQUIRED)

Before any split manifest transitions from `PLANNED` to `ACQUIRED` and `SEALED`, the following checklist must be satisfied and recorded in `datasets/manifests/<SPLIT-ID>.json`:
1. Official download URL and verified mirror citation.
2. Exact release version / release date.
3. List of constituent raw files with byte sizes.
4. Cryptographic SHA-256 checksum of every raw file.
5. Parser version and canonicalization script hash.
6. Total raw records, valid parsed records, and malformed/discarded record count.
7. Exact minimum timestamp $T_{\min}$ and maximum timestamp $T_{\max}$ in event-time.
8. Ground truth label file path and label file SHA-256.
9. Explicit list of excluded hosts/records with formal scientific rationale.

---

## 3. Pre-Registered Partition Specifications (State: PLANNED)

| Split ID | Dataset | Strategy | Planned Partition Ratios | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`SPL-HDFS-001`** | HDFS LogHub | Strict Causal Time + OOV Template Holdout | Train: First 70% block sessions<br>Val: Next 15% sessions<br>Test: Final 15% sessions (Sealed)<br>Holdout: 10% rare anomaly templates | **PLANNED** |
| **`SPL-BGL-001`** | BGL Supercomputer | Strict Causal Time + Temporal Drift Test | Train: Days 1..150 (~70%)<br>Val: Days 151..180 (~15%)<br>Test: Days 181..215 (~15%, Sealed)<br>Stress: Days 181+ unseen failure codes | **PLANNED** |
| **`SPL-DTC-001`** | DARPA TC E3/E5 | Causal Scenario + Host Holdout | Train: E3 Days 1..9 (Baseline)<br>Val: E3 Days 10..11 (Validation redteam)<br>Test: E3 Days 12..14 & E5 Days 15..21 (Sealed)<br>Holdout: 2 designated target hosts | **PLANNED** |
| **`SPL-LANL-001`** | LANL Cyber Security | Strict Causal Time | Train: Days 1..60 ($t = 1 \dots 5.184 	imes 10^6	ext{s}$)<br>Val: Days 61..74 ($t = 5.184 	imes 10^6 \dots 6.393 	imes 10^6	ext{s}$)<br>Test: Days 75..89 (Sealed)<br>Red Team: Test-window occurrences only | **PLANNED** |
