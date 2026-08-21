# EXPERIMENTAL PROTOCOL AMENDMENT LEDGER

**Document Identifier:** `LEDGER-AMD-20260821`  
**Status:** **ACTIVE & AUDITED**  
**Governing Rule:** Research Constitution (`RC-15` — No Silent Reinterpretation).  

---

## 1. Amendment Governance Policy

Any modification to the locked pre-registration protocol after registration date (2026-08-21) must be logged in this ledger with:
1. `amendment_id`: Sequential identifier (e.g. `AMD-001`, `AMD-002`).
2. `timestamp`: ISO-8601 UTC timestamp of amendment adoption.
3. `reason`: Comprehensive scientific or operational justification.
4. `files_changed`: Exact paths of modified protocol documents.
5. `before_after_diff`: Explicit textual and mathematical diffs.
6. `test_opened`: `YES` or `NO` indicating whether test split was unsealed.
7. `results_seen`: `YES` or `NO` indicating whether empirical results influenced the change.
8. `impact_on_confirmatory_status`: If an amendment is introduced after seeing test results, the affected hypothesis test **loses pure confirmatory status** and must be classified as **`EXPLORATORY / POST-HOC`** in thesis prose.

---

## 2. Canonical Amendment Registry

### Amendment AMD-001: Initial Pre-Registration Audit & Baseline Locking
- **Timestamp:** `2026-08-21T07:16:00Z`
- **Author:** Research Engineering System / Auditor
- **Reason:** Recomputed Chapter 1 and Chapter 2 hashes directly from canonical Master DOCX (`Chuyên đề chuyên sâu.docx`), formalized split manifest state machine (`PLANNED` $	o$ `ACQUIRED` $	o$ `SEALED`), and registered initial protocol suite.
- **Files Changed:** `experiments/protocol/*.md`
- **Test Set Opened:** `NO`
- **Results Seen:** `NO`
- **Impact on Confirmatory Status:** `CONFIRMATORY_PRESERVED`.

---

### Amendment AMD-002: DARPA TC Schema Correction, LANL Boundary & Statistical Protocol Hardening
- **Timestamp:** `2026-08-21T07:26:00Z`
- **Author:** Research Engineering System / Auditor
- **Reason:** Comprehensive audit corrections:
  1. Corrected DARPA TC Engagement 3 schema from CDM19 to official **CDM18**; confirmed Engagement 5 as **CDM20**.
  2. Disambiguated DARPA TC Official Performer Universe (CADETS, ClearScope, FiveDirections, THEIA, TRACE) from Our Pre-Registered Experimental Subset (THEIA, CADETS, FiveDirections).
  3. Formatted LANL `redteam.txt` record count as `PENDING_VERIFICATION` prior to physical dataset acquisition.
  4. Removed underpowered Shapiro-Wilk normality decision gate on $K=5$ seed differences; established **Paired Cluster Bootstrap** ($B=2000$, seed 10007) as primary confirmatory inference method.
  5. Established Cluster Resampling Unit Audit for EXP-01 through EXP-06 with non-overlap and temporal leakage rules.
  6. Formatted effect sizes with absolute difference as primary metric.
- **Files Changed:**
  - `experiments/protocol/CH3-PRE-REGISTRATION.md`
  - `experiments/protocol/DATASET-CARDS.md`
  - `experiments/protocol/SPLIT-PROTOCOL.md`
  - `experiments/protocol/STATISTICAL-PLAN.md`
  - `experiments/protocol/EXPERIMENT-MATRIX.md`
  - `experiments/protocol/PROTOCOL-AMENDMENTS.md`
  - `experiments/protocol/generate_split_manifests.py`
  - `datasets/manifests/SPL-HDFS-001.json`
  - `datasets/manifests/SPL-BGL-001.json`
  - `datasets/manifests/SPL-DTC-001.json`
  - `datasets/manifests/SPL-LANL-001.json`
- **Test Set Opened:** `NO`
- **Results Seen:** `NO`
- **Impact on Confirmatory Status:** `CONFIRMATORY_PRESERVED`.
