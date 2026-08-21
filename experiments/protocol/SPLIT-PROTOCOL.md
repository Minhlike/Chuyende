# ANTI-LEAKAGE CAUSAL SPLIT PROTOCOL & SPLIT MANIFEST STATE MACHINE

**Document Identifier:** `PROT-SPLIT-20260822-V1.1`  
**Protocol Version:** 1.1.0  
**Status:** **LOCKED & CANONICAL**  
**Governing Standard:** Research Constitution (`RC-10`, `RC-16`), Roadmap Boundary (`BOUNDARY-09`).  

---

## 1. Split Manifest Lifecycle State Machine

To prevent fabricated partition counts and speculative split hashes prior to physical data acquisition, every split manifest follows a strict three-state lifecycle:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SPLIT MANIFEST LIFECYCLE STATE MACHINE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  STATE 1: PLANNED (Pre-Acquisition Specification)                           │
│  - Formal partitioning ratios/strategies defined (Train 70% < Val 15% < Test)│
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
│                                      │ (Trigger: Causal Split & Train Fit)  │
│                                      ▼                                      │
│  STATE 3: SEALED (Locked For Confirmatory Evaluation)                       │
│  - Exact index/timestamp partition boundaries generated deterministically   │
│  - Train/Val materialized tensors frozen; Test partition strictly sealed    │
│  - Test set sealed against any model training or hyperparameter selection   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pre-Acquisition Verification Checklist

Before any split manifest transitions from `PLANNED` to `ACQUIRED` and `SEALED`, the following checklist must be satisfied and recorded in `datasets/manifests/<SPLIT-ID>.json`:
1. Official download URL and verified mirror citation.
2. Exact release version / release date.
3. List of constituent raw files with byte sizes.
4. Cryptographic SHA-256 checksum of every raw file.
5. Parser version and canonicalization script hash.
6. Total raw records, valid parsed records, and malformed/discarded record count satisfying conservation:
   $$\text{raw\_total\_count} = \text{block\_associated\_count} + \text{no\_block\_count} + \text{malformed\_count}$$
7. Exact minimum timestamp $T_{\min}$ and maximum timestamp $T_{\max}$ in event-time.
8. Ground truth label file path and label file SHA-256.
9. Explicit list of excluded hosts/records with formal scientific rationale.

---

## 3. Pre-Registered Partition Specifications (Canonical Master Source)

| Split ID | Dataset | Strategy | Canonical Partition Boundaries & Rules | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`SPL-HDFS-001`** | HDFS LogHub | Strict Causal Time ($\max(\text{Train}) \le \min(\text{Val}) \le \min(\text{Test})$) | Train: Earliest 70% causal block sessions (sorted by `session_start_time`)<br>Val: Next 15% causal sessions<br>Test: Final 15% causal sessions (Sealed, 0 features materialized)<br>Raw Count: 11,175,629 lines | **VALIDATED** |
| **`SPL-BGL-001`** | BGL Supercomputer | Strict Causal Time | Train: Days 1..150 ($t = [1117838570, 1130798570)$)<br>Val: Days 151..180 ($t = [1130798570, 1133390570)$)<br>Test: Days 181..215 ($t = [1133390570, 1136390405]$, Sealed)<br>Raw Count: 4,747,963 lines | **VALIDATED** |
| **`SPL-DTC-001`** | DARPA TC E3 | Causal Scenario + Host Holdout | Exact Train/Val/Test boundaries: **`PENDING_RAW_CDM18_ALIGNMENT`**<br>Pre-registered subset: THEIA, CADETS, FiveDirections (CDM18 only)<br>Ground Truth mapping: `PENDING_VERIFICATION` | **METADATA_ACQUIRED** |
| **`SPL-LANL-001`** | LANL Cyber 1 | Strict Causal Time | Exact Train/Val/Test boundaries: **`PENDING_ACQUISITION`** (Official dataset comprises 58 days total)<br>Labels: Auth exact match only | **USER_ACTION_REQUIRED** |
